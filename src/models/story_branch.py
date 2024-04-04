from dataclasses import dataclass
from typing import Optional

import ujson

from src.models.story.story_choice import StoryChoice


@dataclass
class StoryBranch:
    source_chunk_id: str
    target_chunk_id: str
    choice: Optional[StoryChoice]

    def to_dict(self) -> dict:
        return {
            'source_chunk_id': self.source_chunk_id,
            'target_chunk_id': self.target_chunk_id,
            'choice': None if not self.choice else self.choice.to_dict()
        }

    @classmethod
    def from_dict(cls, data_obj: dict):
        if isinstance(data_obj.get("choice"), str):
            data_obj["choice"] = ujson.loads(data_obj.get("choice"))

        return cls(
            source_chunk_id=data_obj.get("source_chunk_id"),
            target_chunk_id=data_obj.get("target_chunk_id"),
            choice=None if not data_obj.get("choice") else StoryChoice.from_dict(data_obj.get("choice"))
        )

    def __str__(self):
        return f'StoryBranch(source_chunk_id={self.source_chunk_id}, target_chunk_id={self.target_chunk_id}, choice={self.choice})'
    
    def __repr__(self):
        return str(self)
