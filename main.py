import copy
import json
import random
import uuid
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from loguru import logger
from typing_extensions import Annotated

from src.chatgpt import chatgpt
from src.db.Neo4JConnector import Neo4JConnector
from src.models.GenerationConfig import GenerationConfig
from src.models.StoryChunk import StoryChunk
from src.models.StoryData import StoryData
from src.models.story.StoryChoice import StoryChoice
from src.prompts import get_plot_prompt, get_story_until_choices_opportunity_prompt, \
    story_based_on_selected_choice_prompt, story_until_chapter_end_prompt, story_until_game_end_prompt
from src.types import BranchingType
from src.utils import format_openai_message

# TODO: Put back the parameters
"""game_genre: Annotated[Optional[str], typer.Option(help="Game genre")] = 'visual novel',
        themes: Annotated[Optional[list[str]], typer.Option(help="Themes to be provided")] = None,
        num_chapters: Annotated[Optional[int], typer.Option(help="Number of chapters")] = 3,
        num_endings: Annotated[Optional[int], typer.Option(help="Number of story ending")] = 3,
        num_main_characters: Annotated[Optional[int], typer.Option(help="Number of main characters")] = 5,
        num_main_scenes: Annotated[Optional[int], typer.Option(help="Number of scenes (location)")] = 3,
        min_num_choices: Annotated[Optional[int], typer.Option(help="Minimum number of choices")] = 2,
        max_num_choices: Annotated[Optional[int], typer.Option(help="Maximum number of choices")] = 3,
        min_num_choices_opportunity: Annotated[
            Optional[int], typer.Option(help="Minimum number of choice opportunities per chapter")] = 3,
        max_num_choices_opportunity: Annotated[
            Optional[int], typer.Option(help="Maximum number of choice opportunities per chapter")] = 5"""


def main(
        game_genre: Annotated[Optional[str], typer.Option(help="Game genre")] = 'visual novel',
        themes: Annotated[Optional[list[str]], typer.Option(help="Themes to be provided")] = None,
        num_chapters: Annotated[Optional[int], typer.Option(help="Number of chapters")] = 2,
        num_endings: Annotated[Optional[int], typer.Option(help="Number of story ending")] = 2,
        num_main_characters: Annotated[Optional[int], typer.Option(help="Number of main characters")] = 3,
        num_main_scenes: Annotated[Optional[int], typer.Option(help="Number of scenes (location)")] = 2,
        min_num_choices: Annotated[Optional[int], typer.Option(help="Minimum number of choices")] = 2,
        max_num_choices: Annotated[Optional[int], typer.Option(help="Maximum number of choices")] = 2,
        min_num_choices_opportunity: Annotated[
            Optional[int], typer.Option(help="Minimum number of choice opportunities per chapter")] = 2,
        max_num_choices_opportunity: Annotated[
            Optional[int], typer.Option(help="Maximum number of choice opportunities per chapter")] = 2):
    config = GenerationConfig(min_num_choices, max_num_choices, min_num_choices_opportunity,
                              max_num_choices_opportunity, game_genre, themes, num_chapters, num_endings,
                              num_main_characters, num_main_scenes)

    neo4j_connector = Neo4JConnector()

    logger.info(f"Generation config: {config}")

    # story_id = str(uuid.uuid1()) # TODO: uncomment
    story_id = "d8cd3f12-bcdd-11ee-bef0-9a01b5b45ca1"  # TODO: delete

    logger.info(f"Story ID: {story_id}")

    output_path = Path("outputs") / story_id
    output_path.mkdir(exist_ok=True, parents=True)

    logger.debug("Start story plot generation")
    game_story_prompt = get_plot_prompt(config)
    history = format_openai_message(game_story_prompt)

    with open(output_path / 'histories.json', 'w') as file:
        file.write(json.dumps({
            'histories': [history]
        }, indent=2))

    story_data_raw, story_data_obj = chatgpt(history)
    story_data_obj['id'] = story_id
    story_data = StoryData.from_json(story_data_obj)
    neo4j_connector.write(story_data)

    initial_history = format_openai_message(story_data_raw, role="assistant", history=history)
    logger.debug("End story plot generation")

    with open(output_path / 'plot.json', 'w') as file:
        file.write(json.dumps({
            "raw": story_data_raw,
            "parsed": story_data_obj
        }, indent=2))

    queue: list[tuple[int, int, Optional[StoryChunk], Optional[StoryChoice]]] = [(1, 0, None, None)]
    cnt = 0  # TODO: remove
    state = None
    while queue:
        cnt += 1  # TODO: remove
        chapter, num_opp, parent_chunk, choice = queue.pop(0)

        num_choices = random.randint(config.min_num_choices, config.max_num_choices)
        if not choice:
            if num_opp == 0:  # First chunk of the chapter
                prompt = get_story_until_choices_opportunity_prompt(config, story_data, num_choices, num_opp, chapter)
                history = format_openai_message(prompt,
                                                history=initial_history if not parent_chunk else parent_chunk.current_history)
                state = BranchingType.BRANCHING
            elif num_opp == config.max_num_choices_opportunity:
                if chapter == config.num_chapters:  # End of game
                    prompt = story_until_game_end_prompt(config, story_data, parent_chunk)
                    history = format_openai_message(prompt, history=parent_chunk.current_history)
                    state = BranchingType.GAME_END
                else:  # End of chapter
                    prompt = story_until_chapter_end_prompt(config, story_data, parent_chunk)
                    history = format_openai_message(prompt, history=parent_chunk.current_history)
                    state = BranchingType.CHAPTER_END
        else:  # Branch to a choice
            prompt = story_based_on_selected_choice_prompt(config, story_data, choice, num_choices, num_opp, chapter)
            history = format_openai_message(prompt, history=parent_chunk.current_history)
            state = BranchingType.BRANCHING

        logger.debug(f"Current chapter: {chapter}, num_opp: {num_opp}, state: {state}, choice: {choice}")

        story_chunk_raw, story_chunk_obj = chatgpt(history)
        story_chunk_obj['id'] = str(uuid.uuid1())
        story_chunk_obj['chapter'] = chapter
        story_chunk = StoryChunk.from_json(story_chunk_obj)
        history = format_openai_message(story_chunk_raw, role="assistant", history=history)
        story_chunk.current_history = copy.deepcopy(history)

        neo4j_connector.write(story_chunk)
        if not parent_chunk:
            neo4j_connector.with_session(story_data.add_story_chunk_to_db, story_chunk)
        else:
            neo4j_connector.with_session(parent_chunk.branched_timeline_to_db, story_chunk, choice)

        if state is BranchingType.BRANCHING and num_opp < config.max_num_choices_opportunity:  # Branch to multiple choices
            for choice in story_chunk.choices:
                queue.append((chapter, num_opp + 1, story_chunk, choice))
        elif state is BranchingType.BRANCHING and num_opp == config.max_num_choices_opportunity:  # Branch to the end of chapter
            queue.append((chapter, num_opp, story_chunk, None))
        elif state is BranchingType.CHAPTER_END and chapter < config.num_chapters:  # Branch to the next chapter
            queue.append((chapter + 1, 0, story_chunk, None))
        elif state is BranchingType.GAME_END and chapter == config.num_chapters:  # Branch to the end of game
            queue.append((chapter, num_opp, story_chunk, None))

    logger.debug(f"Total number of chunks: {cnt}")  # TODO: remove


if __name__ == '__main__':
    load_dotenv()
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/{time}.log")
    typer.run(main)
