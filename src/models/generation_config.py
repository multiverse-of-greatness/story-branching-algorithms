from typing_extensions import List, Optional
from pydantic import BaseModel


class GenerationConfig(BaseModel):
    min_num_choices: int
    max_num_choices: int
    min_num_choices_opportunity: int
    max_num_choices_opportunity: int
    game_genre: str
    themes: List[str]
    num_chapters: int
    num_endings: int
    num_main_characters: int
    num_main_scenes: int
    enable_image_generation: bool
    existing_plot: Optional[str] = None
    seed: Optional[int] = None

    def get_themes_str(self) -> str:
        return ', '.join(self.themes)
    
    @staticmethod
    def copy_from(config: 'GenerationConfig'):
        return GenerationConfig(
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
            existing_plot=config.existing_plot,
            seed=config.seed
        )
