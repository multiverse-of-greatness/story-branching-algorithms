from typing import List

from pydantic import BaseModel

from src.models.story.story_narrative import StoryNarrative
from src.types.openai import ConversationHistory


class StoryChunk(BaseModel):
    id: str
    story_id: str
    chapter: int
    story_so_far: str
    story: List[StoryNarrative]
    num_opportunities: int
    history: ConversationHistory

    def __str__(self):
        return (f"StoryChunk(id={self.id}, story_id={self.story_id}, chapter={self.chapter}, story_so_far={self.story_so_far}, "
                f"story={[str(n) for n in self.story]}, num_opportunities={self.num_opportunities}, history={bool(self.history)})")
    
    def __repr__(self):
        return str(self)
