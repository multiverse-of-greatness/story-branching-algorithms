import os
from pathlib import Path

import ujson
from loguru import logger

import src.algorithms.baseline as baseline
import src.algorithms.proposed as proposed
from src.algorithms.core import initialize_generation
from src.bg_remover.bria import Bria
from src.models.enums.generation_approach import GenerationApproach
from src.models.generation_config import GenerationConfig
from src.models.generation_context import GenerationContext
from src.models.story_data import StoryData
from src.repository import CommonRepository
from src.utils.generative_models import (get_generation_model,
                                         get_image_generation_model)


def run_generation_with(config: GenerationConfig, approach: GenerationApproach) -> StoryData:
    generation_context = GenerationContext(approach, config)
    logger.info(f"Generation context: {generation_context}")

    initialize_context(generation_context)
    initial_history, story_data = initialize_generation(generation_context)
    generation_context.set_initial_history(initial_history)

    if approach is GenerationApproach.BASELINE:
        baseline.process_generation_queue(generation_context, story_data)
    elif approach is GenerationApproach.PROPOSED:
        proposed.process_generation_queue(generation_context, story_data)
    else:
        logger.error(f"Invalid approach: {approach}")
        exit(1)
    return story_data


def run_resume_generation_with(story_id: str, approach: GenerationApproach):
    story_path = Path("outputs") / approach.value / story_id
    with open(story_path / "context.json", "r") as context_file:
        generation_context = GenerationContext.from_dict(ujson.load(context_file))

    if generation_context.is_generation_completed:
        logger.info("Generation already completed")
        return
    
    with open(story_path / "plot.json", "r") as plot_file:
        content = ujson.load(plot_file)
    story_data = StoryData.model_validate(content["parsed"])
    
    logger.info(f"Generation context: {generation_context}")
    initialize_context(generation_context)

    if approach is GenerationApproach.BASELINE:
        baseline.process_generation_queue(generation_context, story_data)
    elif approach is GenerationApproach.PROPOSED:
        proposed.process_generation_queue(generation_context, story_data)
    else:
        logger.error(f"Invalid approach: {approach}")
        exit(1)
    return story_data


def initialize_context(ctx: GenerationContext):
    ctx.repository = CommonRepository()
    ctx.generation_model = get_generation_model(os.getenv("GENERATION_MODEL"), ctx.config.seed)
    ctx.background_remover_model = Bria()
    if ctx.config.enable_image_generation:
        ctx.image_generation_model = get_image_generation_model(os.getenv("IMAGE_GENERATION_MODEL"))
