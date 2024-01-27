from neo4j import Session

from src.db.DBModel import DBModel


class ChapterSynopsis(DBModel):
    def __init__(self, chapter, synopsis):
        self.chapter = chapter
        self.synopsis = synopsis

    @staticmethod
    def from_json(json_obj: dict):
        return ChapterSynopsis(json_obj['chapter'], json_obj['synopsis'])

    def to_json(self) -> dict:
        return {
            'chapter': self.chapter,
            'synopsis': self.synopsis
        }

    def __str__(self):
        return f"ChapterSynopsis(chapter={self.chapter}, synopsis={self.synopsis})"

    def save_to_db(self, session: Session):
        session.run('CREATE (chapterSynopsis:ChapterSynopsis $props)', props=self.to_json())
