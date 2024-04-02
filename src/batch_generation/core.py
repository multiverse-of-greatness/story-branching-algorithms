from loguru import logger

from src.generation.core import run_generation_with
from src.models.enums.generation_approach import GenerationApproach
from src.models.generation_config import GenerationConfig
from src.models.story_data import StoryData


def run_batch_generation(config: GenerationConfig, n_stories: int, approach: GenerationApproach) -> list[StoryData]:
    generated_stories: list[StoryData] = []
    logger.info("Starting batch generation")
    for _ in range(n_stories):
        story_data = run_generation_with(config, approach)
        generated_stories.append(story_data)
    logger.info("Batch generation completed")
    return generated_stories


def run_batch_generation_with_existing_plot(config: GenerationConfig, existing_stories: list[StoryData], approach: GenerationApproach) -> list[StoryData]:
    generated_stories: list[StoryData] = []
    logger.info("Starting batch generation with existing plot")
    for story_data in existing_stories:
        config_with_existing_plot = GenerationConfig(
            min_num_choices=config.min_num_choices,
            max_num_choices=config.max_num_choices,
            min_num_choices_opportunity=config.min_num_choices_opportunity,
            max_num_choices_opportunity=config.max_num_choices_opportunity,
            game_genre=config.game_genre,
            themes=config.themes,
            num_chapters=config.num_chapters,
            num_endings=config.num_endings,
            num_main_characters=config.num_main_characters,
            num_main_scenes=config.num_main_scenes,
            enable_image_generation=config.enable_image_generation,
            existing_plot=str(story_data.existing_plot_path)
        )
        story_data = run_generation_with(config_with_existing_plot, approach)
        generated_stories.append(story_data)
    logger.info("Batch generation with existing plot completed")
    return generated_stories
