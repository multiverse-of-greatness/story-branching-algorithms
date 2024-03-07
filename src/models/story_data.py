import json

from neo4j import Session

from src.databases.model import DBModel
from src.models.story.chapter_synopsis import ChapterSynopsis
from src.models.story.character_data import CharacterData
from src.models.story.ending_data import EndingData
from src.models.story.scene_data import SceneData
from src.models.story_chunk import StoryChunk


class StoryData(DBModel):
    def __init__(self, id: str, title: str, genre: str, themes: list[str], main_scenes: list[SceneData],
                 main_characters: list[CharacterData], synopsis: str, chapter_synopses: list[ChapterSynopsis],
                 beginning: str, endings: list[EndingData], generated_by: str, approach: str):
        self.id = id
        self.title = title
        self.genre = genre
        self.themes = themes
        self.main_scenes = main_scenes
        self.main_characters = main_characters
        self.synopsis = synopsis
        self.chapter_synopses = chapter_synopses
        self.beginning = beginning
        self.endings = endings
        self.generated_by = generated_by
        self.approach = approach

    @staticmethod
    def from_json(json_obj: dict):
        return StoryData(json_obj['id'], json_obj['title'], json_obj['genre'], json_obj['themes'],
                         [SceneData.from_json(scene) for scene in json_obj['main_scenes']],
                         [CharacterData.from_json(character) for character in json_obj['main_characters']],
                         json_obj['synopsis'], [ChapterSynopsis.from_json(chapter_synopsis) for chapter_synopsis in
                                                json_obj['chapter_synopses']], json_obj['beginning'],
                         [EndingData.from_json(ending) for ending in json_obj['endings']], json_obj['generated_by'],
                         json_obj['approach'])

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'themes': self.themes,
            'main_scenes': [scene.to_json() for scene in self.main_scenes],
            'main_characters': [character.to_json() for character in self.main_characters],
            'synopsis': self.synopsis,
            'chapter_synopses': [chapter_synopsis.to_json() for chapter_synopsis in self.chapter_synopses],
            'beginning': self.beginning,
            'endings': [ending.to_json() for ending in self.endings],
            'generated_by': self.generated_by,
            'approach': self.approach
        }

    def __str__(self):
        return (f"StoryData(id={self.id}, title={self.title}, genre={self.genre}, themes={self.themes}, "
                f"main_scenes={[str(s) for s in self.main_scenes]}, "
                f"main_characters={[str(c) for c in self.main_characters]}, synopsis={self.synopsis}, "
                f"chapter_synopses={[str(cs) for cs in self.chapter_synopses]}, beginning={self.beginning}, "
                f"endings={[str(e) for e in self.endings]}, approach={self.approach})")

    def save_to_db(self, session: Session):
        session.run(
            '''CREATE (storyData:StoryData {id: $id, title: $title, genre: $genre, themes: $themes, 
            main_scenes: $main_scenes, main_characters: $main_characters, 
            synopsis: $synopsis, chapter_synopses: $chapter_synopses, 
            beginning: $beginning, endings: $endings, generated_by: $generated_by, approach: $approach})''',
            id=self.id, title=self.title, genre=self.genre, themes=self.themes,
            main_scenes=json.dumps([s.to_json() for s in self.main_scenes]),
            main_characters=json.dumps([c.to_json() for c in self.main_characters]), synopsis=self.synopsis,
            chapter_synopses=json.dumps([c.to_json() for c in self.chapter_synopses]), beginning=self.beginning,
            endings=json.dumps([e.to_json() for e in self.endings]), generated_by=self.generated_by,
            approach=self.approach
        )

    def add_story_chunk_to_db(self, session: Session, story_chunk: StoryChunk):
        session.run(
            '''MATCH (storyData:StoryData {id: $story_id}), (storyChunk:StoryChunk {id: $chunk_id})
            CREATE (storyData)-[:STARTED_AT]->(storyChunk)''',
            story_id=self.id, chunk_id=story_chunk.id
        )
