import random
import uuid

from loguru import logger

from src.algorithms.core import get_prompts_by_branching_type
from src.models.generation_context import GenerationContext
from src.models.story_chunk import StoryChunk
from src.models.story_data import StoryData
from src.types.algorithm import BranchingType
from src.utils.openai_ai import append_openai_message


def process_generation_queue(ctx: GenerationContext, story_data: StoryData):
    cnt = 0
    frontiers = ctx.get_frontiers()
    while len(ctx.get_frontiers()) > 0:
        cnt += 1
        current_chapter, used_choice_opportunity, parent_chunk, choice, state = frontiers.pop(0)

        current_num_choices = random.randint(ctx.config.min_num_choices, ctx.config.max_num_choices)
        history = ctx.get_initial_history() if not parent_chunk else parent_chunk.history

        prompt = get_prompts_by_branching_type(choice, ctx, current_chapter, current_num_choices, parent_chunk, state,
                                               story_data, used_choice_opportunity)

        logger.debug(
            f"Current chapter: {current_chapter}, num_opp: {used_choice_opportunity}, state: {state}, choice: {choice}")

        history = append_openai_message(prompt, history=history)

        # Retry chunk generation if failed
        max_retry_attempts = 3
        has_chunk_generation_success, current_attempt = False, 0
        current_chunk, story_chunk_raw = None, None
        while not has_chunk_generation_success and current_attempt < max_retry_attempts:
            try:
                story_chunk_raw, story_chunk_obj = ctx.generation_model.generate_content(ctx, history)
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
                if len(current_chunk.choices) != current_num_choices:
                    logger.warning(f"Choices generated by model ({len(current_chunk.choices)}) not equal to setting "
                                   f"choices ({current_num_choices})")
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
    logger.debug(f"End of story generation for story ID: {ctx.story_id}")
