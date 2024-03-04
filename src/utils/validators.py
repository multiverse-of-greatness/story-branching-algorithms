import json
from pathlib import Path

import typer
from loguru import logger

from src.models.story_data import StoryData


def valida_approach(approach: str):
    if approach not in ["proposed", "baseline"]:
        logger.error("Approach must be either 'proposed' or 'baseline'")
        raise typer.Abort()


def validate_existing_plot(existing_plot_path: str):
    if existing_plot_path and not Path(existing_plot_path).exists():
        logger.error(f"Existing plot file not found: {existing_plot_path}")
        raise typer.Abort()

    if existing_plot_path:
        try:
            with open(existing_plot_path, "r") as file:
                content = json.load(file)
                story_data_obj = content["parsed"]
                StoryData.from_json(story_data_obj)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Existing plot file not valid: {existing_plot_path}")
            logger.error(e)
            raise typer.Abort()


def validate_config(min_num_choices: int, max_num_choices: int, min_num_choices_opportunity: int,
                    max_num_choices_opportunity: int, num_chapters: int, num_endings: int, num_main_characters: int,
                    num_main_scenes: int):
    if min_num_choices < 1 or max_num_choices < 1 or min_num_choices_opportunity < 1 or max_num_choices_opportunity < 1 or \
            num_chapters < 1 or num_endings < 1 or num_main_characters < 1 or num_main_scenes < 1:
        logger.error("All config values must be greater than one")
        raise typer.Abort()

    if min_num_choices > max_num_choices:
        logger.error("Minimum number of choices must be less than or equal to maximum number of choices")
        raise typer.Abort()

    if min_num_choices_opportunity > max_num_choices_opportunity:
        logger.error(
            "Minimum number of choice opportunities must be less than or equal to maximum number of choice opportunities")
        raise typer.Abort()
