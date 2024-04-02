from pathlib import Path
from typing import Annotated, Optional

import typer
from dotenv import load_dotenv
from loguru import logger

from src.batch_generation.core import (run_batch_generation,
                                       run_batch_generation_with_existing_plot)
from src.generation.core import run_generation_with
from src.models.enums.generation_approach import GenerationApproach
from src.models.generation_config import GenerationConfig
from src.utils.validators import validate_config, validate_existing_plot

app = typer.Typer()


@app.command()
def generate_story_with(
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
        existing_plot: Annotated[
            Optional[str], typer.Option(help="Existing plot to be used"),
        ] = None,
        approach: Annotated[
            Optional[GenerationApproach], typer.Option(help="Approach to be used"),
        ] = "proposed",
        enable_image_generation: Annotated[
            Optional[bool], typer.Option(help="Enable image generation"),
        ] = False,
):
    validate_existing_plot(existing_plot)
    validate_config(min_num_choices, max_num_choices, min_num_choices_opportunity, max_num_choices_opportunity,
                    num_chapters, num_endings, num_main_characters, num_main_scenes)
    
    config = GenerationConfig(min_num_choices, max_num_choices, min_num_choices_opportunity,
                              max_num_choices_opportunity, game_genre, themes, num_chapters, num_endings,
                              num_main_characters, num_main_scenes, enable_image_generation, existing_plot)
    logger.info(f"Generation config: {config}")
    run_generation_with(config, approach)


@app.command()
def batch_generation(
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
        enable_image_generation: Annotated[
            Optional[bool], typer.Option(help="Enable image generation"),
        ] = False,
        n_stories: Annotated[
            Optional[int], typer.Option(help="Number of stories to be generated")
        ] = 50):
    validate_config(min_num_choices, max_num_choices, min_num_choices_opportunity, max_num_choices_opportunity,
                    num_chapters, num_endings, num_main_characters, num_main_scenes)
    
    config = GenerationConfig(min_num_choices, max_num_choices, min_num_choices_opportunity,
                              max_num_choices_opportunity, game_genre, themes, num_chapters, num_endings,
                              num_main_characters, num_main_scenes, enable_image_generation)
    logger.info(f"Generation config: {config}")

    logger.info(f"Generating {n_stories} stories with proposed approach")
    proposed_stories = run_batch_generation(config, n_stories, GenerationApproach.PROPOSED)
    logger.info(f"Generating {n_stories} stories with baseline approach with existing plot")
    _ = run_batch_generation_with_existing_plot(config, proposed_stories, GenerationApproach.BASELINE)
    logger.info(f"Generating {n_stories} stories with baseline approach")
    baseline_stories = run_batch_generation(config, n_stories, GenerationApproach.BASELINE)
    logger.info(f"Generating {n_stories} stories with proposed approach with existing plot")
    _ = run_batch_generation_with_existing_plot(config, baseline_stories, GenerationApproach.PROPOSED)


if __name__ == "__main__":
    load_dotenv()
    Path("logs").mkdir(exist_ok=True)
    logger.add("logs/{time}.log")
    app()
