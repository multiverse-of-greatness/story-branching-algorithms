import ujson
from loguru import logger
from pydantic import ValidationError

from src.models.enums.branching_type import BranchingType
from src.models.generation_config import GenerationConfig
from src.models.generation_context import GenerationContext
from src.models.story.story_choice import StoryChoice
from src.models.story_chunk import StoryChunk
from src.models.story_data import StoryData
from src.prompts.image_prompts import (get_character_image_prompt,
                                       get_scene_image_prompt)
from src.prompts.story_prompts import (
    get_plot_prompt, get_story_based_on_selected_choice_prompt,
    get_story_until_chapter_end_prompt,
    get_story_until_choices_opportunity_prompt,
    get_story_until_game_end_prompt)
from src.utils.general import get_base64_from_image, get_image_from_base64
from src.utils.openai_ai import append_openai_message
from src.utils.pydantic import map_validation_errors_to_string


def initialize_generation(ctx: GenerationContext):
    logger.debug("Start story plot generation")

    game_story_prompt = get_plot_prompt(ctx.config)
    history = append_openai_message(game_story_prompt)

    with open(ctx.output_path / "histories.json", "w") as file:
        ujson.dump({"histories": [history]}, file, indent=2)

    story_data_raw, story_data_obj, story_data = None, None, None

    if not ctx.config.existing_plot:
        # Retry plot generation if failed
        max_retry_attempts = 3
        has_plot_generation_success, current_attempt = False, 0
        while not has_plot_generation_success and current_attempt < max_retry_attempts:
            try:
                story_data_raw, story_data_obj = ctx.generate_content(history)
                story_data_obj["id"] = ctx.story_id
                story_data_obj["generated_by"] = ctx.generation_model.model_name
                story_data_obj["approach"] = ctx.approach
                story_data = StoryData.model_validate(story_data_obj)
                validate_story_data(ctx.config, story_data)
                has_plot_generation_success = True
            except ValidationError as e:
                current_attempt += 1
                logger.warning(f"Validation error on chat completion response: {map_validation_errors_to_string(e)}")
            except Exception as e:
                current_attempt += 1
                logger.warning(f"Exception occurred while chat completion: {e}")

        if not has_plot_generation_success:
            logger.error(f"Failed to generate story data.")
            logger.error(f"Story ID: {ctx.story_id}")
            logger.error("Exiting...")
            exit(1)

    else:
        with open(ctx.config.existing_plot, "r") as file:
            content = ujson.load(file)
        story_data_raw = content["raw"]
        story_data_obj = content["parsed"]
        story_data = StoryData.model_validate(story_data_obj)

    if ctx.config.enable_image_generation and not ctx.config.existing_plot:
        logger.debug("Start character image generation")
        for character in story_data.main_characters:
            logger.debug(f"Generating image for character: {character}")

            prompt = get_character_image_prompt(character)
            image_b64 = ctx.image_generation_model.generate_image_from_text_prompt(prompt)

            character.original_image = image_b64

            image = get_image_from_base64(image_b64)
            removed_bg_image = ctx.background_remover_model.remove_background(image)
            character.image = get_base64_from_image(removed_bg_image)
            logger.debug(f"Generated image for character: {character}")

        logger.debug("Start scene image generation")
        for scene in story_data.main_scenes:
            logger.debug(f"Generating image for scene: {scene}")

            prompt = get_scene_image_prompt(scene)
            image_b64 = ctx.image_generation_model.generate_image_from_text_prompt(prompt, shape="landscape")

            scene.image = image_b64
            logger.debug(f"Generated image for scene: {scene}")
    else:
        logger.debug("Image generation is disabled")

    ctx.repository.create_story_data(story_data)

    initial_history = append_openai_message(story_data_raw, role="assistant", history=history)
    logger.debug("End story plot generation")

    with open(ctx.output_path / "plot.json", "w") as file:
        ujson.dump({"raw": story_data_raw, "parsed": story_data.model_dump()}, file, indent=2)

    return initial_history, story_data


def get_prompts_by_branching_type(choice: StoryChoice, ctx: GenerationContext, current_chapter: int, current_num_choices: int,
                                  parent_chunk: StoryChunk, state: BranchingType, story_data: StoryData, used_choice_opportunity: int) -> str:
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
    return prompt


def validate_story_data(config: GenerationConfig, story_data: StoryData):
    if len(story_data.main_scenes) < config.num_main_scenes:
        raise ValueError(f"Main scenes generated by model ({len(story_data.main_scenes)}) less than setting scenes ({config.num_main_scenes})")
    
    if len(story_data.main_characters) < config.num_main_characters:
        raise ValueError(f"Main characters generated by model ({len(story_data.main_characters)}) less than setting characters ({config.num_main_characters})")
    
    if len(story_data.endings) < config.num_endings:
        raise ValueError(f"Endings generated by model ({len(story_data.endings)}) less than setting endings ({config.num_endings})")
    
    if len(story_data.chapter_synopses) < config.num_chapters:
        raise ValueError(f"Chapter synopses generated by model ({len(story_data.chapter_synopses)}) less than setting chapters ({config.num_chapters})")
