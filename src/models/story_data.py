from typing import List

from pydantic import BaseModel

from src.models.enums.generation_approach import GenerationApproach
from src.models.story.chapter_synopsis import ChapterSynopsis
from src.models.story.character_data import CharacterData
from src.models.story.ending_data import EndingData
from src.models.story.scene_data import SceneData


class StoryData(BaseModel):
    id: str
    title: str
    genre: str
    themes: List[str]
    main_scenes: List[SceneData]
    main_characters: List[CharacterData]
    synopsis: str
    chapter_synopses: List[ChapterSynopsis]
    beginning: str
    endings: List[EndingData]
    generated_by: str
    approach: GenerationApproach
