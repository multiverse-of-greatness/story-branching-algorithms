class GenerationConfig:
    def __init__(self, min_num_choices: int, max_num_choices: int, min_num_choices_opportunity: int,
                 max_num_choices_opportunity: int, game_genre: str, themes: list[str], num_chapters: int,
                 num_endings: int, num_main_characters: int, num_main_scenes: int, existing_plot: str = None):
        self.min_num_choices = min_num_choices
        self.max_num_choices = max_num_choices
        self.min_num_choices_opportunity = min_num_choices_opportunity
        self.max_num_choices_opportunity = max_num_choices_opportunity
        self.game_genre = game_genre
        self.themes = themes
        self.num_chapters = num_chapters
        self.num_endings = num_endings
        self.num_main_characters = num_main_characters
        self.num_main_scenes = num_main_scenes
        self.existing_plot = existing_plot

    def get_themes_str(self) -> str:
        return ', '.join(self.themes)

    @staticmethod
    def from_json(json_obj: dict):
        return GenerationConfig(json_obj['min_num_choices'], json_obj['max_num_choices'],
                                json_obj['min_num_choices_opportunity'], json_obj['max_num_choices_opportunity'],
                                json_obj['game_genre'], json_obj['themes'], json_obj['num_chapters'],
                                json_obj['num_endings'], json_obj['num_main_characters'],
                                json_obj['num_main_scenes'], json_obj.get('existing_plot'))

    def to_json(self) -> dict:
        return {
            'min_num_choices': self.min_num_choices,
            'max_num_choices': self.max_num_choices,
            'min_num_choices_opportunity': self.min_num_choices_opportunity,
            'max_num_choices_opportunity': self.max_num_choices_opportunity,
            'game_genre': self.game_genre,
            'themes': self.themes,
            'num_chapters': self.num_chapters,
            'num_endings': self.num_endings,
            'num_main_characters': self.num_main_characters,
            'num_main_scenes': self.num_main_scenes,
            'existing_plot': self.existing_plot
        }

    def __str__(self):
        return (f"GenerationConfig(min_num_choices={self.min_num_choices}, "
                f"max_num_choices={self.max_num_choices}, "
                f"min_num_choices_opportunity={self.min_num_choices_opportunity}, "
                f"max_num_choices_opportunity={self.max_num_choices_opportunity}, "
                f"game_genre={self.game_genre}, themes={self.themes}, num_chapters={self.num_chapters}, "
                f"num_endings={self.num_endings}, num_main_characters={self.num_main_characters}, "
                f"num_main_scenes={self.num_main_scenes}), existing_plot={self.existing_plot})")
