import json

from neo4j import Session

from src.chatgpt import ConversationHistory
from .story.StoryChoice import StoryChoice
from .story.StoryNarrative import StoryNarrative


class StoryChunk:
    def __init__(self, id: int, story_so_far: str, story: list[StoryNarrative], choices: list[StoryChoice],
                 chapter: int):
        self.id = id
        self.story_so_far = story_so_far
        self.story = story
        self.choices = choices
        self.chapter = chapter
        self.current_history: ConversationHistory = []

    @staticmethod
    def from_json(json_obj: dict):
        return StoryChunk(json_obj['id'], json_obj['story_so_far'],
                          [StoryNarrative.from_json(narrative) for narrative in json_obj['story']],
                          [StoryChoice.from_json(choice) for choice in json_obj['choices']], json_obj['chapter'])

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'story_so_far': self.story_so_far,
            'story': [narrative.to_json() for narrative in self.story],
            'choices': [choice.to_json() for choice in self.choices],
            'chapter': self.chapter
        }

    def __str__(self):
        return f'StoryChunk(id={self.id}, story_so_far={self.story_so_far}, story={[str(s) for s in self.story]}, choices={[str(c) for c in self.choices]}, chapter={self.chapter})'

    def save_to_db(self, session: Session):
        if len(self.current_history) == 0:
            raise ValueError('current_history is None')

        session.run(
            '''CREATE (storyChunk:StoryChunk {id: $id, story_so_far: $story_so_far, chapter: $chapter, 
            current_history: $current_history})''',
            id=self.id, story_so_far=self.story_so_far, chapter=self.chapter, current_history=json.dumps(self.current_history)
        )

        for narrative in self.story:
            narrative.save_to_db(session)
            session.run('''MATCH (storyChunk:StoryChunk {id: $id}), (storyNarrative:StoryNarrative {id: $story_id}) 
                CREATE (storyChunk)-[:HAS]->(storyNarrative)''', id=self.id, story_id=narrative.id)

        # for choice in self.choices:
        #     choice.save_to_db(session)
        #     session.run('''MATCH (storyChunk:StoryChunk {id: $id}), (storyChoice:StoryChoice {id: $choice_id})
        #     CREATE (storyChunk)-[:HAS]->(storyChoice)''', id=self.id, choice_id=choice.id)

    def branched_timeline_to_db(self, session: Session, story_chunk: 'StoryChunk', choice: StoryChoice = None):
        props = {} if not choice else choice.to_json()
        session.run(
            '''MATCH (source:StoryChunk {id: $source_id}), (branched:StoryChunk {id: $branched_id})
            CREATE (source)-[:BRANCHED_TO $props]->(branched)''',
            source_id=self.id, branched_id=story_chunk.id, props=props
        )
