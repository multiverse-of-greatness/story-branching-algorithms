from neo4j import Session

from src.databases.DBModel import DBModel


class ChapterSynopsis(DBModel):
    def __init__(self, chapter: int, synopsis: str, character_ids: list[int], scene_ids: list[int]):
        self.chapter = chapter
        self.synopsis = synopsis
        self.character_ids = character_ids
        self.scene_ids = scene_ids

    @staticmethod
    def from_json(json_obj: dict):
        return ChapterSynopsis(json_obj['chapter'], json_obj['synopsis'], json_obj['character_ids'],
                               json_obj['scene_ids'])

    def to_json(self) -> dict:
        return {
            'chapter': self.chapter,
            'synopsis': self.synopsis,
            'character_ids': self.character_ids,
            'scene_ids': self.scene_ids
        }

    def __str__(self):
        return (f"ChapterSynopsis(chapter={self.chapter}, synopsis={self.synopsis}, "
                f"character_ids={self.character_ids}, scene_ids={self.scene_ids})")

    def save_to_db(self, session: Session):
        session.run('CREATE (chapterSynopsis:ChapterSynopsis $props)', props=self.to_json())
