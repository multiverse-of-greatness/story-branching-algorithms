import random
import uuid
from typing import Optional

from loguru import logger

from src.chatgpt import ChatGPT
from src.databases.Neo4JConnector import Neo4JConnector
from src.models.GenerationConfig import GenerationConfig
from src.models.story.StoryChoice import StoryChoice
from src.models.StoryChunk import StoryChunk
from src.models.StoryData import StoryData
from src.prompts import (get_story_until_choices_opportunity_prompt,
                         story_based_on_selected_choice_prompt,
                         story_until_chapter_end_prompt,
                         story_until_game_end_prompt)
from src.types import BranchingType, ConversationHistory
from src.utils import format_openai_message


def process_generation_queue(config: GenerationConfig, story_id: str, chatgpt: ChatGPT, neo4j_connector: Neo4JConnector, initial_history: ConversationHistory, story_data: StoryData, frontiers: list[tuple[int, int, Optional[StoryChunk], Optional[StoryChoice]]]):
    cnt = 0
    state = None
    while frontiers:
        cnt += 1
        chapter, used_choice_opportunity, parent_chunk, choice, state = frontiers.pop(0)

        num_choices = random.randint(config.min_num_choices, config.max_num_choices)
        history = initial_history if not parent_chunk else parent_chunk.history

        if state is BranchingType.BRANCHING:
            if not choice:  # Start of chapter
                prompt = get_story_until_choices_opportunity_prompt(config, story_data, num_choices, used_choice_opportunity, chapter)
            else:  # In the middle of chapter
                prompt = story_based_on_selected_choice_prompt(config, story_data, choice, num_choices, used_choice_opportunity, chapter)
        elif state is BranchingType.CHAPTER_END:
            prompt = story_until_chapter_end_prompt(config, story_data, parent_chunk)
        elif state is BranchingType.GAME_END:
            prompt = story_until_game_end_prompt(config, story_data, parent_chunk)

        logger.debug(f"Current chapter: {chapter}, num_opp: {used_choice_opportunity}, state: {state}, choice: {choice}")

        history = format_openai_message(prompt, history=history)

        prompt_success, prompt_attempt = False, 0
        while not prompt_success and prompt_attempt < 3:
            try:
                story_chunk_raw, story_chunk_obj = chatgpt.chat_completions(history)
                story_chunk_obj["id"] = str(uuid.uuid1())
                story_chunk_obj["chapter"] = chapter
                story_chunk_obj["story_id"] = story_id
                story_chunk_obj["num_opportunities"] = used_choice_opportunity
                current_chunk = StoryChunk.from_json(story_chunk_obj)
                prompt_success = True
            except Exception as e:
                prompt_attempt += 1
                logger.warning(f"Exception occurred while chat completion: {e}")

        if not prompt_success:
            logger.error(f"Failed to generate story chunk.")
            logger.error(f"Story ID: {story_id}, Chapter: {chapter}, Opportunity: {used_choice_opportunity}, State: {state}, Choice: {choice}")
            logger.error("Exiting...")
            exit(1)

        current_chunk.history = format_openai_message(story_chunk_raw, role="assistant", history=history)

        if len(current_chunk.story) == 0:
            logger.warning(f"Story chunk {current_chunk.id} has no story narratives.")

        neo4j_connector.write(current_chunk)
        if not parent_chunk:
            neo4j_connector.with_session(story_data.add_story_chunk_to_db, current_chunk)
        else:
            neo4j_connector.with_session(parent_chunk.branched_timeline_to_db, current_chunk, choice)

        child_chunks = []
        if state is BranchingType.BRANCHING:
            if used_choice_opportunity < config.max_num_choices_opportunity:  # Branch to multiple choices
                for choice in current_chunk.choices:
                    child_chunks.append((chapter, used_choice_opportunity + 1, current_chunk, choice, BranchingType.BRANCHING))
            elif used_choice_opportunity == config.max_num_choices_opportunity:
                if chapter < config.num_chapters:  # Branch to the end of chapter
                    child_chunks.append((chapter, used_choice_opportunity, current_chunk, None, BranchingType.CHAPTER_END))
                elif chapter == config.num_chapters:  # Branch to the end of game
                    child_chunks.append((chapter, used_choice_opportunity, current_chunk, None, BranchingType.GAME_END))
        elif state is BranchingType.CHAPTER_END:
            if chapter < config.num_chapters:  # Branch to the next chapter
                child_chunks.append((chapter + 1, 0, current_chunk, None, BranchingType.BRANCHING))

        frontiers.extend(child_chunks)

    logger.debug(f"Total number of chunks: {cnt}")