import json
import os
import random
import uuid

from loguru import logger

from src.models.generation_context import GenerationContext
from src.models.story_chunk import StoryChunk
from src.models.story_data import StoryData
from src.prompts.image_prompts import get_character_image_prompt, get_scene_image_prompt
from src.prompts.story_prompts import (get_story_until_choices_opportunity_prompt,
                                       get_story_based_on_selected_choice_prompt,
                                       get_story_until_chapter_end_prompt,
                                       get_story_until_game_end_prompt, get_plot_prompt)
from src.utils.general import append_openai_message, get_image_from_base64, get_base64_from_image
from .types.algorithm import BranchingType


def initialize_generation(ctx: GenerationContext):
    logger.debug("Start story plot generation")

    game_story_prompt = get_plot_prompt(ctx.config)
    history = append_openai_message(game_story_prompt)

    with open(ctx.output_path / "histories.json", "w") as file:
        file.write(json.dumps({"histories": [history]}, indent=2))

    if not ctx.config.existing_plot:
        story_data_raw, story_data_obj = ctx.generation_model.generate_content(ctx, history)
    else:
        with open(ctx.config.existing_plot, "r") as file:
            content = json.load(file)
            story_data_obj = content["parsed"]
            story_data_raw = story_data_obj["raw"]

    story_data_obj["id"] = ctx.story_id
    story_data_obj["generated_by"] = os.getenv("GENERATION_MODEL")
    story_data = StoryData.from_json(story_data_obj)

    logger.debug("Start character image generation")
    for character in story_data.main_characters:
        logger.debug(f"Generating image for character: {character}")

        prompt = get_character_image_prompt(character)
        image_b64 = ctx.image_gen_model.generate_image_from_text_prompt(prompt)

        character.original_image = image_b64

        image = get_image_from_base64(image_b64)
        removed_bg_image = ctx.background_remover_model.remove_background(image)
        character.removed_bg_image = get_base64_from_image(removed_bg_image)
        logger.debug(f"Generated image for character: {character}")

    logger.debug("Start scene image generation")
    for scene in story_data.main_scenes:
        logger.debug(f"Generating image for scene: {scene}")

        prompt = get_scene_image_prompt(scene)
        image_b64 = ctx.image_gen_model.generate_image_from_text_prompt(prompt, shape="landscape")

        scene.image = image_b64
        logger.debug(f"Generated image for scene: {scene}")

    ctx.db_connector.write(story_data)

    initial_history = append_openai_message(story_data_raw, role="assistant", history=history)
    logger.debug("End story plot generation")

    with open(ctx.output_path / "plot.json", "w") as file:
        file.write(
            json.dumps({"raw": story_data_raw, "parsed": story_data_obj}, indent=2)
        )

    return initial_history, story_data


def process_generation_queue(ctx: GenerationContext, story_data: StoryData):
    cnt = 0
    frontiers = ctx.get_frontiers()
    while len(ctx.get_frontiers()) > 0:
        cnt += 1
        current_chapter, used_choice_opportunity, parent_chunk, choice, state = frontiers.pop(0)

        current_num_choices = random.randint(ctx.config.min_num_choices, ctx.config.max_num_choices)
        history = ctx.get_initial_history() if not parent_chunk else parent_chunk.history

        if state is BranchingType.BRANCHING:
            if not choice:  # Start of chapter
                prompt = get_story_until_choices_opportunity_prompt(ctx.config, story_data, current_num_choices,
                                                                    used_choice_opportunity, current_chapter)
            else:  # In the middle of chapter
                prompt = get_story_based_on_selected_choice_prompt(ctx.config, story_data, choice, current_num_choices,
                                                                   used_choice_opportunity, current_chapter)
        elif state is BranchingType.CHAPTER_END:
            prompt = get_story_until_chapter_end_prompt(ctx.config, story_data, parent_chunk)
        elif state is BranchingType.GAME_END:
            prompt = get_story_until_game_end_prompt(ctx.config, story_data, parent_chunk)
        else:
            logger.error(f"Invalid state: {state}")
            exit(1)

        logger.debug(
            f"Current chapter: {current_chapter}, num_opp: {used_choice_opportunity}, state: {state}, choice: {choice}")

        history = append_openai_message(prompt, history=history)

        # Retry chunk generation if failed
        max_retry_attempts = 3
        has_chunk_generation_success, current_attempt = False, 0
        current_chunk, story_chunk_raw = None, None
        while not has_chunk_generation_success and current_attempt < max_retry_attempts:
            try:
                story_chunk_raw, story_chunk_obj = ctx.generation_model.generate_content(history)
                story_chunk_obj["id"] = str(uuid.uuid1())
                story_chunk_obj["chapter"] = current_chapter
                story_chunk_obj["story_id"] = ctx.story_id
                story_chunk_obj["num_opportunities"] = used_choice_opportunity
                current_chunk = StoryChunk.from_json(story_chunk_obj)
                has_chunk_generation_success = True
            except Exception as e:
                current_attempt += 1
                logger.warning(f"Exception occurred while chat completion: {e}")

        if not has_chunk_generation_success or current_chunk is None or story_chunk_raw is None:
            logger.error(f"Failed to generate story chunk.")
            logger.error(
                f"Story ID: {ctx.story_id}, Chapter: {current_chapter}, Opportunity: {used_choice_opportunity}, State: {state}, Choice: {choice}")
            logger.error("Exiting...")
            exit(1)

        current_chunk.history = append_openai_message(story_chunk_raw, role="assistant", history=history)

        if len(current_chunk.story) == 0:
            logger.warning(f"Story chunk {current_chunk.id} has no story narratives.")

        # Save to DB
        ctx.db_connector.write(current_chunk)
        if not parent_chunk:
            ctx.db_connector.with_session(story_data.add_story_chunk_to_db, current_chunk)
        else:
            ctx.db_connector.with_session(parent_chunk.branched_timeline_to_db, current_chunk, choice)

        child_chunks = []
        if state is BranchingType.BRANCHING:
            if used_choice_opportunity < ctx.config.max_num_choices_opportunity:  # Branch to multiple choices
                for choice in current_chunk.choices:
                    child_chunks.append(
                        (current_chapter, used_choice_opportunity + 1, current_chunk, choice, BranchingType.BRANCHING))
            elif used_choice_opportunity == ctx.config.max_num_choices_opportunity:
                if current_chapter < ctx.config.num_chapters:  # Branch to the end of chapter
                    child_chunks.append(
                        (current_chapter, used_choice_opportunity, current_chunk, None, BranchingType.CHAPTER_END))
                elif current_chapter == ctx.config.num_chapters:  # Branch to the end of game
                    child_chunks.append(
                        (current_chapter, used_choice_opportunity, current_chunk, None, BranchingType.GAME_END))
        elif state is BranchingType.CHAPTER_END:
            if current_chapter < ctx.config.num_chapters:  # Branch to the next chapter
                child_chunks.append((current_chapter + 1, 0, current_chunk, None, BranchingType.BRANCHING))

        frontiers.extend(child_chunks)
        ctx.set_frontiers(frontiers)

    ctx.completed()
    logger.debug(f"Total number of chunks: {cnt}")
    logger.debug("End of story generation")
