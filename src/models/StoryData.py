from neo4j import Session

from src.db.DBModel import DBModel
from .StoryChunk import StoryChunk
from .story.ChapterSynopsis import ChapterSynopsis
from .story.CharacterData import CharacterData
from .story.EndingData import EndingData
from .story.SceneData import SceneData


class StoryData(DBModel):
    def __init__(self, id: str, title: str, genre: str, themes: list[str], main_scenes: list[SceneData],
                 main_characters: list[CharacterData], synopsis: str, chapter_synopses: list[ChapterSynopsis],
                 beginning: str, endings: list[EndingData]):
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

    @staticmethod
    def from_json(json_obj: dict):
        return StoryData(json_obj['id'], json_obj['title'], json_obj['genre'], json_obj['themes'],
                         [SceneData.from_json(scene) for scene in json_obj['main_scenes']],
                         [CharacterData.from_json(character) for character in json_obj['main_characters']],
                         json_obj['synopsis'], [ChapterSynopsis.from_json(chapter_synopsis) for chapter_synopsis in
                                                json_obj['chapter_synopses']], json_obj['beginning'],
                         [EndingData.from_json(ending) for ending in json_obj['endings']])

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
            'endings': [ending.to_json() for ending in self.endings]
        }

    def __str__(self):
        return f"""StoryData(id={self.id}, title={self.title}, genre={self.genre}, themes={self.themes}, main_scenes={[str(s) for s in self.main_scenes]}, main_characters={[str(c) for c in self.main_characters]}, synopsis={self.synopsis}, chapter_synopses={[str(cs) for cs in self.chapter_synopses]}, beginning={self.beginning}, endings={[str(e) for e in self.endings]})"""

    def save_to_db(self, session: Session):
        session.run(
            '''CREATE (storyData:StoryData {id: $id, title: $title, genre: $genre, themes: $themes, 
            synopsis: $synopsis, beginning: $beginning})''',
            id=self.id, title=self.title, genre=self.genre, themes=self.themes,
            synopsis=self.synopsis, beginning=self.beginning
        )
        for scene in self.main_scenes:
            scene.save_to_db(session)
            session.run(
                '''MATCH (storyData:StoryData {id: $story_id}), (sceneData:SceneData {id: $scene_id}) 
                CREATE (storyData)-[:TAKE_PLACE]->(sceneData)''',
                story_id=self.id, scene_id=scene.id
            )
        for character in self.main_characters:
            character.save_to_db(session)
            session.run(
                '''MATCH (storyData:StoryData {id: $story_id}), (characterData:CharacterData {id: $character_id}) 
                CREATE (characterData)-[:ACTED_IN]->(storyData)''',
                story_id=self.id, character_id=character.id
            )

        for chapter_synopsis in self.chapter_synopses:
            chapter_synopsis.save_to_db(session)
            session.run(
                '''MATCH (storyData:StoryData {id: $story_id}), (chapterSynopsis:ChapterSynopsis {chapter: $chapter}) 
                CREATE (storyData)-[:HAS]->(chapterSynopsis)''',
                story_id=self.id, chapter=chapter_synopsis.chapter
            )

        for ending in self.endings:
            ending.save_to_db(session)
            session.run(
                '''MATCH (storyData:StoryData {id: $story_id}), (endingData:EndingData {id: $ending_id}) 
                CREATE (storyData)-[:ENDED_WITH]->(endingData)''',
                story_id=self.id, ending_id=ending.id
            )

    def add_story_chunk_to_db(self, session: Session, story_chunk: StoryChunk):
        session.run(
            '''MATCH (storyData:StoryData {id: $story_id}), (storyChunk:StoryChunk {id: $chunk_id})
            CREATE (storyData)-[:STARTED_AT]->(storyChunk)''',
            story_id=self.id, chunk_id=story_chunk.id
        )
