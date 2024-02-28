from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from loguru import logger
from typing_extensions import Annotated

from src.core import process_generation_queue, initialize_generation
from src.databases.Neo4JConnector import Neo4JConnector
from src.llms.chatgpt import ChatGPT
from src.models.generation_config import GenerationConfig
from src.models.generation_context import GenerationContext
from src.utils import validate_existing_plot


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
        existing_plot: Annotated[
            Optional[str], typer.Option(help="Existing plot to be used"),
        ] = None,
):
    validate_existing_plot(existing_plot)

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
        existing_plot,
    )
    logger.info(f"Generation config: {config}")

    neo4j_connector = Neo4JConnector()
    neo4j_connector.set_database(dbname)

    chatgpt = ChatGPT()

    generation_context = GenerationContext(neo4j_connector, chatgpt, config)
    logger.info(f"Generation context: {generation_context}")

    initial_history, story_data = initialize_generation(generation_context)
    generation_context.set_initial_history(initial_history)

    process_generation_queue(generation_context, story_data)


if __name__ == "__main__":
    load_dotenv()
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/{time}.log")
    typer.run(main)
