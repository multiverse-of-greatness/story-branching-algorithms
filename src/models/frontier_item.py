from typing import Optional

from pydantic import BaseModel

from src.models.enums.branching_type import BranchingType
from src.models.story.story_choice import StoryChoice
from src.models.story_chunk import StoryChunk


class FrontierItem(BaseModel):
    current_chapter: int
    used_choice_opportunity: int
    state: BranchingType
    parent_chunk: Optional[StoryChunk] = None
    choice: Optional[StoryChoice] = None

    def __str__(self):
        return f"FrontierItem(current_chapter={self.current_chapter}, used_choice_opportunity={self.used_choice_opportunity}, state={self.state.value}, parent_chunk={bool(self.parent_chunk)}, choice={self.choice})"

    def __repr__(self):
        return str(self)
