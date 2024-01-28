import json

from neo4j import Session

from src.types import ConversationHistory
from .story.StoryChoice import StoryChoice
from .story.StoryNarrative import StoryNarrative


class StoryChunk:
    def __init__(self, id: str, chapter: int, story_so_far: str, narratives: list[StoryNarrative],
                 choices: list[StoryChoice]):
        self.id = id
        self.chapter = chapter
        self.story_so_far = story_so_far
        self.narratives = narratives
        self.choices = choices
        self.current_history: ConversationHistory = []

    @staticmethod
    def from_json(json_obj: dict):
        choices = [] if 'choices' not in json_obj else json_obj['choices']
        return StoryChunk(json_obj['id'], json_obj['chapter'], json_obj['story_so_far'],
                          [StoryNarrative.from_json(narrative) for narrative in json_obj['narratives']],
                          [StoryChoice.from_json(choice) for choice in choices])

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'story_so_far': self.story_so_far,
            'narratives': [narrative.to_json() for narrative in self.narratives],
            'choices': [choice.to_json() for choice in self.choices],
            'chapter': self.chapter
        }

    def __str__(self):
        return f'StoryChunk(id={self.id}, chapter={self.chapter}, story_so_far={self.story_so_far}, narratives={[str(n) for n in self.narratives]}, choices={[str(c) for c in self.choices]})'

    def save_to_db(self, session: Session):
        if len(self.current_history) == 0:
            raise ValueError('current_history is None')

        session.run(
            '''CREATE (storyChunk:StoryChunk {id: $id, chapter: $chapter, story_so_far: $story_so_far, 
            narratives: $narratives, current_history: $current_history})''',
            id=self.id, chapter=self.chapter, story_so_far=self.story_so_far,
            narratives=json.dumps([n.to_json() for n in self.narratives]),
            current_history=json.dumps(self.current_history)
        )

    def branched_timeline_to_db(self, session: Session, story_chunk: 'StoryChunk', choice: StoryChoice = None):
        props = {} if not choice else choice.to_json()
        session.run(
            '''MATCH (source:StoryChunk {id: $source_id}), (branched:StoryChunk {id: $branched_id})
            CREATE (source)-[:BRANCHED_TO $props]->(branched)''',
            source_id=self.id, branched_id=story_chunk.id, props=props
        )
