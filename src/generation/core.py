import os

from loguru import logger

import src.algorithms.baseline as baseline
import src.algorithms.proposed as proposed
from src.algorithms.core import initialize_generation
from src.bg_remover.bria import Bria
from src.databases.neo4j import Neo4JConnector
from src.models.enums.generation_approach import GenerationApproach
from src.models.generation_config import GenerationConfig
from src.models.generation_context import GenerationContext
from src.models.story_data import StoryData
from src.utils.generative_models import (get_generation_model,
                                         get_image_generation_model)


def run_generation_with(config: GenerationConfig, approach: GenerationApproach) -> StoryData:
    neo4j_connector = Neo4JConnector()
    llm = get_generation_model(os.getenv("GENERATION_MODEL"))
    image_gen = None
    bria = Bria()
    if config.enable_image_generation:
        image_gen = get_image_generation_model(os.getenv("IMAGE_GENERATION_MODEL"))

    generation_context = GenerationContext(neo4j_connector, llm, image_gen, bria, approach, config)
    logger.info(f"Generation context: {generation_context}")
    initial_history, story_data = initialize_generation(generation_context)
    generation_context.set_initial_history(initial_history)

    if approach == "baseline":
        baseline.process_generation_queue(generation_context, story_data)
    elif approach == "proposed":
        proposed.process_generation_queue(generation_context, story_data)
    else:
        logger.error(f"Invalid approach: {approach}")
        exit(1)
    return story_data
