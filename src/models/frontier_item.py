from dataclasses import dataclass
from typing import Optional

from src.models.enums.branching_type import BranchingType
from src.models.story.story_choice import StoryChoice
from src.models.story_chunk import StoryChunk


@dataclass
class FrontierItem:
    current_chapter: int
    used_choice_opportunity: int
    parent_chunk: Optional[StoryChunk]
    choice: Optional[StoryChoice]
    state: BranchingType

    def to_dict(self) -> dict:
        return {
            "current_chapter": self.current_chapter,
            "used_choice_opportunity": self.used_choice_opportunity,
            "parent_chunk": None if self.parent_chunk is None else self.parent_chunk.to_dict(),
            "choice": None if self.choice is None else self.choice.to_dict(),
            "state": self.state.value
        }

    @classmethod
    def from_dict(cls, data_obj: dict):
        return cls(
            current_chapter=data_obj.get("current_chapter"),
            used_choice_opportunity=data_obj.get("used_choice_opportunity"),
            parent_chunk=None if data_obj.get("parent_chunk") is None else StoryChunk.from_dict(data_obj.get("parent_chunk")),
            choice=None if data_obj.get("choice") is None else StoryChoice.from_dict(data_obj.get("choice")),
            state=BranchingType(data_obj.get("state"))
        )

    def __str__(self):
        return f"FrontierItem(current_chapter={self.current_chapter}, used_choice_opportunity={self.used_choice_opportunity}, parent_chunk={bool(self.parent_chunk)}, choice={self.choice}, state={self.state.value})"

    def __repr__(self):
        return str(self)
