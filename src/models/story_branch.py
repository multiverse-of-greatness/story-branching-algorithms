from typing import Optional

from pydantic import BaseModel

from src.models.story.story_choice import StoryChoice


class StoryBranch(BaseModel):
    source_chunk_id: str
    target_chunk_id: str
    choice: Optional[StoryChoice]
