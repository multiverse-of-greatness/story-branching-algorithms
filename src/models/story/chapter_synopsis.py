from typing import List

from pydantic import BaseModel


class ChapterSynopsis(BaseModel):
    chapter: int
    synopsis: str
    character_ids: List[int]
    scene_ids: List[int]
