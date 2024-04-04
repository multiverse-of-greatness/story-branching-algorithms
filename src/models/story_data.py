from dataclasses import dataclass
from pathlib import Path

import ujson

from src.models.enums.generation_approach import GenerationApproach
from src.models.story.chapter_synopsis import ChapterSynopsis
from src.models.story.character_data import CharacterData
from src.models.story.ending_data import EndingData
from src.models.story.scene_data import SceneData


@dataclass
class StoryData:
    id: str
    title: str
    genre: str
    themes: list[str]
    main_scenes: list[SceneData]
    main_characters: list[CharacterData]
    synopsis: str
    chapter_synopses: list[ChapterSynopsis]
    beginning: str
    endings: list[EndingData]
    generated_by: str
    approach: GenerationApproach

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'themes': self.themes,
            'main_scenes': [scene.to_dict() for scene in self.main_scenes],
            'main_characters': [character.to_dict() for character in self.main_characters],
            'synopsis': self.synopsis,
            'chapter_synopses': [chapter_synopsis.to_dict() for chapter_synopsis in self.chapter_synopses],
            'beginning': self.beginning,
            'endings': [ending.to_dict() for ending in self.endings],
            'generated_by': self.generated_by,
            'approach': self.approach.value,
        }
    
    @classmethod
    def from_dict(cls, data_obj: dict):
        if isinstance(data_obj.get("main_scenes"), str):
            data_obj["main_scenes"] = ujson.loads(data_obj.get("main_scenes"))
        if isinstance(data_obj.get("main_characters"), str):
            data_obj["main_characters"] = ujson.loads(data_obj.get("main_characters"))
        if isinstance(data_obj.get("chapter_synopses"), str):
            data_obj["chapter_synopses"] = ujson.loads(data_obj.get("chapter_synopses"))
        if isinstance(data_obj.get("endings"), str):
            data_obj["endings"] = ujson.loads(data_obj.get("endings"))
            
        return cls(
            id=data_obj.get("id"),
            title=data_obj.get("title"),
            genre=data_obj.get("genre"),
            themes=data_obj.get("themes"),
            main_scenes=[SceneData.from_dict(s) for s in data_obj.get("main_scenes", [])],
            main_characters=[CharacterData.from_dict(c) for c in data_obj.get("main_characters", [])],
            synopsis=data_obj.get("synopsis"),
            chapter_synopses=[ChapterSynopsis.from_dict(s) for s in data_obj.get("chapter_synopses", [])],
            beginning=data_obj.get("beginning"),
            endings=[EndingData.from_dict(e) for e in data_obj.get("endings", [])],
            generated_by=data_obj.get("generated_by"),
            approach=GenerationApproach(data_obj.get("approach")),
        )
    
    def get_text(self) -> str:
        ending_text = "\n".join([f"{i+1}. {e.ending}" for i, e in enumerate(self.endings)])
        return f"Synopsis:\n{self.synopsis}\nEndings:\n{ending_text}"

    def __str__(self):
        return (f"StoryData(id={self.id}, title={self.title}, genre={self.genre}, themes={self.themes}, "
                f"main_scenes={[str(s) for s in self.main_scenes]}, main_characters={[str(c) for c in self.main_characters]}, "
                f"synopsis={self.synopsis}, chapter_synopses={[str(cs) for cs in self.chapter_synopses]}, beginning={self.beginning}, "
                f"endings={[str(e) for e in self.endings]}, generated_by={self.generated_by}, approach={self.approach.value})")
    
    def __repr__(self):
        return str(self)