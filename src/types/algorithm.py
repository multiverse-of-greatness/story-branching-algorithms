from enum import Enum
from typing import Optional

from src.models.StoryChunk import StoryChunk
from src.models.story.StoryChoice import StoryChoice

type Frontiers = list[tuple[int, int, Optional[StoryChunk], Optional[StoryChoice], BranchingType]]


class BranchingType(Enum):
    BRANCHING = 0
    CHAPTER_END = 1
    GAME_END = 2

    def to_string(self) -> str:
        return self.name.lower()

    def from_string(self, s: str) -> 'BranchingType':
        return BranchingType[s.upper()]
