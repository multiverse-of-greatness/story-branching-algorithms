from pathlib import Path
from typing import Optional, Union, Literal

import typer
from dotenv import load_dotenv
from loguru import logger
from typing_extensions import Annotated

from src.bg_remover.bria import Bria
from src.core import process_generation_queue, initialize_generation
from src.databases.Neo4JConnector import Neo4JConnector
from src.image_gen.dall_e_3 import DALL_E_3
from src.llms.chatgpt import ChatGPT
from src.models.generation_config import GenerationConfig
from src.models.generation_context import GenerationContext
from src.utils.validators import validate_existing_plot, validate_config, valida_approach


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
        ] = 5,
        min_num_choices: Annotated[
            Optional[int], typer.Option(help="Minimum number of choices")
        ] = 2,
        max_num_choices: Annotated[
            Optional[int], typer.Option(help="Maximum number of choices")
        ] = 3,
        min_num_choices_opportunity: Annotated[
            Optional[int],
            typer.Option(help="Minimum number of choice opportunities per chapter"),
        ] = 2,
        max_num_choices_opportunity: Annotated[
            Optional[int],
            typer.Option(help="Maximum number of choice opportunities per chapter"),
        ] = 3,
        dbname: Annotated[
            Optional[str], typer.Option(help="Database name"),
        ] = None,
        existing_plot: Annotated[
            Optional[str], typer.Option(help="Existing plot to be used"),
        ] = None,
        approach: Annotated[
            Optional[Union[Literal["proposed"]] | Literal["baseline"]], typer.Option(help="Approach to be used"),
        ] = "proposed",
):
    valida_approach(str(approach))
    validate_existing_plot(existing_plot)
    validate_config(min_num_choices, max_num_choices, min_num_choices_opportunity, max_num_choices_opportunity,
                    num_chapters, num_endings, num_main_characters, num_main_scenes)

    config = GenerationConfig(min_num_choices, max_num_choices, min_num_choices_opportunity,
                              max_num_choices_opportunity, game_genre, themes, num_chapters, num_endings,
                              num_main_characters, num_main_scenes, existing_plot)
    logger.info(f"Generation config: {config}")

    neo4j_connector = Neo4JConnector()
    neo4j_connector.set_database(dbname)

    chatgpt = ChatGPT()
    dall_e_3 = DALL_E_3()
    bria = Bria()

    generation_context = GenerationContext(neo4j_connector, chatgpt, dall_e_3, bria, str(approach), config)
    logger.info(f"Generation context: {generation_context}")

    initial_history, story_data = initialize_generation(generation_context)
    generation_context.set_initial_history(initial_history)

    process_generation_queue(generation_context, story_data)


if __name__ == "__main__":
    load_dotenv()
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/{time}.log")
    typer.run(main)
