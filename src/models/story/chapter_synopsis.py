from pydantic import BaseModel
from typing_extensions import List


class ChapterSynopsis(BaseModel):
    chapter: int
    synopsis: str
    character_ids: List[int]
    scene_ids: List[int]
