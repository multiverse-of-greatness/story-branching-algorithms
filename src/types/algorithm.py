from enum import Enum
from typing import Optional

from src.models.story.story_choice import StoryChoice
from src.models.story_chunk import StoryChunk

type Frontiers = list[tuple[int, int, Optional[StoryChunk], Optional[StoryChoice], BranchingType]]


class BranchingType(Enum):
    BRANCHING = 0
    CHAPTER_END = 1
    GAME_END = 2

    def to_string(self) -> str:
        return self.name.lower()

    @staticmethod
    def from_string(s: str) -> 'BranchingType':
        return BranchingType[s.upper()]
