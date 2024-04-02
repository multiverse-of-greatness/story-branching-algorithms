from typing import Optional

from src.models.enums.branching_type import BranchingType
from src.models.story.story_choice import StoryChoice
from src.models.story_chunk import StoryChunk

Frontiers = list[tuple[int, int, Optional[StoryChunk], Optional[StoryChoice], BranchingType]]
