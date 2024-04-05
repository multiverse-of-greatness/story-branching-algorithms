from pydantic import BaseModel


class StoryNarrative(BaseModel):
    id: int
    speaker: str
    speaker_id: int
    scene_title: str
    scene_id: int
    text: str
