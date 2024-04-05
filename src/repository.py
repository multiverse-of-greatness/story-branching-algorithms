import ujson
from loguru import logger

from src.database import Neo4J
from src.models.story_branch import StoryBranch
from src.models.story_chunk import StoryChunk
from src.models.story_data import StoryData
from src.utils.general import json_dumps_list


class CommonRepository:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommonRepository, cls).__new__(cls)
            cls._instance._initialize()
            logger.info("CommonRepository instance created")
        return cls._instance

    def _initialize(self):
        self.database = Neo4J()
    
    def create_branch(self, branch: StoryBranch):
        with self.database.driver.session() as session:
            session.run(
                ("MATCH (source:StoryChunk {id: $source_id}), (branched:StoryChunk {id: $branched_id}) "
                 "MERGE (source)-[:BRANCHED_TO {choice: $choice}]->(branched)"),
                source_id=branch.source_chunk_id,
                branched_id=branch.target_chunk_id,
                choice='{}' if branch.choice is None else branch.choice.model_dump_json(),
            )
        logger.info(f"Created branch from {branch.source_chunk_id} to {branch.target_chunk_id}")

    def create_story_chunk(self, story_chunk: StoryChunk):
        with self.database.driver.session() as session:
            session.run(
                ("MERGE (storyChunk:StoryChunk {id: $id, chapter: $chapter, story_so_far: $story_so_far, "
                 "story: $story, history: $history, story_id: $story_id, num_opportunities: $num_opportunities})"),
                id=story_chunk.id,
                chapter=story_chunk.chapter,
                story_so_far=story_chunk.story_so_far,
                story=json_dumps_list(story_chunk.story),
                history=ujson.dumps(story_chunk.history),
                story_id=story_chunk.story_id,
                num_opportunities=story_chunk.num_opportunities,
            )
        logger.info(f"StoryChunk {story_chunk.id} created")
    
    def create_story_data(self, story_data: StoryData):
        with self.database.driver.session() as session:
            session.run(
                ("MERGE (storyData:StoryData {id: $id, title: $title, genre: $genre, themes: $themes, "
                 "main_scenes: $main_scenes, main_characters: $main_characters, "
                 "synopsis: $synopsis, chapter_synopses: $chapter_synopses, "
                 "beginning: $beginning, endings: $endings, generated_by: $generated_by, approach: $approach})"),
                id=story_data.id, title=story_data.title, genre=story_data.genre, themes=story_data.themes,
                main_scenes=json_dumps_list(story_data.main_scenes),
                main_characters=json_dumps_list(story_data.main_characters), synopsis=story_data.synopsis,
                chapter_synopses=json_dumps_list(story_data.chapter_synopses), beginning=story_data.beginning,
                endings=json_dumps_list(story_data.endings), generated_by=story_data.generated_by,
                approach=story_data.approach.value
            )
        logger.info(f"StoryData {story_data.id} created")

    def set_start_chunk(self, story_id: str, chunk_id: str):
        with self.database.driver.session() as session:
            session.run(
                ("MATCH (storyData:StoryData {id: $story_id}), (storyChunk:StoryChunk {id: $chunk_id}) "
                 "MERGE (storyData)-[:STARTED_AT]->(storyChunk)"),
                story_id=story_id, chunk_id=chunk_id
            )
        logger.info(f"StoryData {story_id} linked to chunk {chunk_id}")

    def __str__(self):
        return f"CommonRepository(database={self.database})"
