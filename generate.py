import json
import random
import uuid
import os
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from loguru import logger
from typing_extensions import Annotated

from src.chatgpt import ChatGPT
from src.core import process_generation_queue
from src.databases.Neo4JConnector import Neo4JConnector
from src.models.GenerationConfig import GenerationConfig
from src.models.StoryChunk import StoryChunk
from src.models.StoryData import StoryData
from src.models.story.StoryChoice import StoryChoice
from src.prompts import get_plot_prompt
from src.types import BranchingType
from src.utils import format_openai_message


def main(
    game_genre: Annotated[
        Optional[str], typer.Option(help="Game genre")
    ] = "visual novel",
    themes: Annotated[
        Optional[list[str]], typer.Option(help="Themes to be provided")
    ] = None,
    num_chapters: Annotated[Optional[int], typer.Option(help="Number of chapters")] = 3,
    num_endings: Annotated[
        Optional[int], typer.Option(help="Number of story ending")
    ] = 3,
    num_main_characters: Annotated[
        Optional[int], typer.Option(help="Number of main characters")
    ] = 5,
    num_main_scenes: Annotated[
        Optional[int], typer.Option(help="Number of scenes (location)")
    ] = 3,
    min_num_choices: Annotated[
        Optional[int], typer.Option(help="Minimum number of choices")
    ] = 2,
    max_num_choices: Annotated[
        Optional[int], typer.Option(help="Maximum number of choices")
    ] = 3,
    min_num_choices_opportunity: Annotated[
        Optional[int],
        typer.Option(help="Minimum number of choice opportunities per chapter"),
    ] = 3,
    max_num_choices_opportunity: Annotated[
        Optional[int],
        typer.Option(help="Maximum number of choice opportunities per chapter"),
    ] = 5,
    dbname: Annotated[
        Optional[str], typer.Option(help="Database name"),
    ] = None,
):
    config = GenerationConfig(
        min_num_choices,
        max_num_choices,
        min_num_choices_opportunity,
        max_num_choices_opportunity,
        game_genre,
        themes,
        num_chapters,
        num_endings,
        num_main_characters,
        num_main_scenes,
    )

    neo4j_connector = Neo4JConnector()
    neo4j_connector.set_database(dbname)

    chatgpt = ChatGPT()

    logger.info(f"Generation config: {config}")

    story_id = str(uuid.uuid1())

    logger.info(f"Story ID: {story_id}")

    output_path = Path("outputs") / story_id
    output_path.mkdir(exist_ok=True, parents=True)

    logger.debug("Start story plot generation")
    game_story_prompt = get_plot_prompt(config)
    history = format_openai_message(game_story_prompt)

    with open(output_path / "histories.json", "w") as file:
        file.write(json.dumps({"histories": [history]}, indent=2))

    story_data_raw, story_data_obj = chatgpt.chat_completions(history)
    story_data_obj["id"] = story_id
    story_data_obj["generated_by"] = os.getenv("GENERATION_MODEL")
    story_data = StoryData.from_json(story_data_obj)
    neo4j_connector.write(story_data)

    initial_history = format_openai_message(story_data_raw, role="assistant", history=history)
    logger.debug("End story plot generation")

    with open(output_path / "plot.json", "w") as file:
        file.write(
            json.dumps({"raw": story_data_raw, "parsed": story_data_obj}, indent=2)
        )

    frontiers: list[tuple[int, int, Optional[StoryChunk], Optional[StoryChoice]]] = [
        (1, 0, None, None, BranchingType.BRANCHING)  # Start from chapter 1
    ]

    process_generation_queue(config, story_id, chatgpt, neo4j_connector, initial_history, story_data, frontiers)
    


if __name__ == "__main__":
    load_dotenv()
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/{time}.log")
    typer.run(main)
