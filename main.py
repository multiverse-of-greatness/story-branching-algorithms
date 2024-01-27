import json
import random
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
from src.utils import format_openai_message


# TODO: Automatically rolling window story so far in case the token limit exceed (do it in chatgpt -> use tiktoken)

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
    story_id = "d8cd3f12-bcdd-11ee-bef0-9a01b5b45ca4"  # TODO: delete

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

    history = format_openai_message(story_data_raw, role="assistant", history=history)
    logger.debug("End story plot generation")

    with open(output_path / 'plot.json', 'w') as file:
        file.write(json.dumps({
            "raw": story_data_raw,
            "parsed": story_data_obj
        }, indent=2))

    frontiers = []
    for current_chapter in range(1, config.num_chapters + 1):
        logger.debug(f"Start story generation for chapter {current_chapter}")
        num_choices_opportunity = random.randint(config.min_num_choices_opportunity, config.max_num_choices_opportunity)
        logger.info(f"Number of choice opportunities for chapter {current_chapter}: {num_choices_opportunity}")

        visited_in_last_opp = []
        for used_opportunity in range(num_choices_opportunity):
            num_choices = random.randint(config.min_num_choices, config.max_num_choices)
            logger.info(
                f"Number of choices for chapter {current_chapter} and opportunity {used_opportunity}: {num_choices}")

            if len(frontiers) == 0:
                branch_story(config, current_chapter, frontiers, history, neo4j_connector, num_choices, output_path,
                             story_data, used_opportunity)

            temp = []
            while len(frontiers) > 0:
                story_chunk, choice = frontiers.pop(0)
                branch_story(config, current_chapter, temp, history, neo4j_connector, num_choices, output_path,
                             story_data, used_opportunity, story_chunk, choice)

            if used_opportunity == num_choices_opportunity - 1:
                visited_in_last_opp = temp
            else:
                frontiers = temp

        while len(visited_in_last_opp) > 0:
            story_chunk, choice = visited_in_last_opp.pop(0)
            ending_type = "game" if current_chapter == num_chapters - 1 else "chapter"
            close_timeline(config, current_chapter, frontiers, neo4j_connector, output_path, story_data, story_chunk,
                           ending_type)


def close_timeline(config, current_chapter, frontiers, neo4j_connector, output_path,
                   story_data, current_chunk: StoryChunk, ending_type: str = "chapter"):
    logger.debug(f"Start story generation for chapter {current_chapter} for a {ending_type} ending.")
    if ending_type == "chapter":
        end_chunk_prompt = story_until_chapter_end_prompt(config, story_data, current_chunk)
    elif ending_type == "game":
        end_chunk_prompt = story_until_game_end_prompt(config, story_data, current_chunk)
    else:
        raise ValueError(f"Invalid ending type: {ending_type}")

    history = current_chunk.current_history
    history = format_openai_message(end_chunk_prompt, history=history)

    with open(output_path / 'histories.json', 'r+') as file:
        histories = json.load(file)
        file.seek(0)
        histories['histories'].append(history)
        file.write(json.dumps(histories, indent=2))

    story_chunk_raw, story_chunk_obj = chatgpt(history)
    story_chunk_obj['chapter'] = current_chapter
    story_chunk_obj['choices'] = []
    story_chunk = StoryChunk.from_json(story_chunk_obj)

    history = format_openai_message(story_chunk_raw, role="assistant", history=history)
    story_chunk.current_history = history

    neo4j_connector.write(story_chunk)
    neo4j_connector.with_session(current_chunk.branched_timeline_to_db, story_chunk)

    logger.debug(f"End story generation for chapter {current_chapter}")

    story_path = output_path / 'story.json'
    stories = {"story": []}
    if story_path.exists():
        with open(story_path, 'r') as file:
            stories = json.load(file)
    stories['story'].append({
        "chapter": current_chapter,
        "chunk": -1,
        "raw": story_chunk_raw,
        "parsed": story_chunk_obj
    })
    with open(story_path, 'w') as file:
        file.write(json.dumps(stories, indent=2))


def branch_story(config, current_chapter, frontiers, initial_history, neo4j_connector, num_choices, output_path,
                 story_data, used_opportunity, current_chunk: StoryChunk = None, choice: StoryChoice = None):
    logger.debug(f"Start story generation for chapter {current_chapter} and opportunity {used_opportunity}")
    logger.debug(f"Based on choice: {choice}")
    if choice is None:
        story_chunk_choice = get_story_until_choices_opportunity_prompt(config, story_data, num_choices,
                                                                        used_opportunity, current_chapter)
        history = format_openai_message(story_chunk_choice, history=initial_history)
    else:
        story_chunk_choice = story_based_on_selected_choice_prompt(config, choice)
        history = current_chunk.current_history
        history = format_openai_message(story_chunk_choice, history=history)

    with open(output_path / 'histories.json', 'r+') as file:
        histories = json.load(file)
        file.seek(0)
        histories['histories'].append(history)
        file.write(json.dumps(histories, indent=2))

    story_chunk_raw, story_chunk_obj = chatgpt(history)
    story_chunk_obj['chapter'] = current_chapter
    story_chunk = StoryChunk.from_json(story_chunk_obj)

    history = format_openai_message(story_chunk_raw, role="assistant", history=history)
    story_chunk.current_history = history

    neo4j_connector.write(story_chunk)
    if choice is None:
        neo4j_connector.with_session(story_data.add_story_chunk_to_db, story_chunk)
    else:
        neo4j_connector.with_session(current_chunk.branched_timeline_to_db, story_chunk, choice)

    logger.debug(f"End story generation for chapter {current_chapter}")

    story_path = output_path / 'story.json'
    stories = {"story": []}
    if story_path.exists():
        with open(story_path, 'r') as file:
            stories = json.load(file)
    stories['story'].append({
        "chapter": current_chapter,
        "chunk": used_opportunity,
        "raw": story_chunk_raw,
        "parsed": story_chunk_obj
    })
    with open(story_path, 'w') as file:
        file.write(json.dumps(stories, indent=2))

    for choice in story_chunk.choices:
        frontiers.append((story_chunk, choice))


if __name__ == '__main__':
    load_dotenv()
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/{time}.log")
    typer.run(main)

# BFS? frontiers = [CHOICE_1, CHOICE_2, CHOICE_3], visited_in_last_opp = []
# 1. [/] Generate StoryData
# => FOR CHAPTER OF CHAPTERS
# ==> FOR CHOICE_OP OF CHOICE_OPS
#        *** Do in queue & loop the rest
#        2. [/] IF QUEUE IS EMPTY Use StoryData to generate StoryChunk (1) w/ 3 Choices
#        3. Add each choice along with current chunk to queue
#        3.5. IF it is the last loop, add it to visited_in_last_opp
#     4. Do the rest in queue
#    5. Do it one more to connect all branches to the next chapter (loop in visited) (prompt for end chapter if not the last chapter, prompt for end story if the last chapter)

# TODO: Make sure to use and continue history of each chunk
