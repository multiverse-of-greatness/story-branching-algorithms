import json

from neo4j import Session

from ..types.openai import ConversationHistory
from .story.StoryChoice import StoryChoice
from .story.StoryNarrative import StoryNarrative


class StoryChunk:
    def __init__(
        self,
        id: str,
        chapter: int,
        story_so_far: str,
        story: list[StoryNarrative],
        choices: list[StoryChoice],
        story_id: str,
        num_opportunities: int,
    ):
        self.id = id
        self.chapter = chapter
        self.story_so_far = story_so_far
        self.story = story
        self.choices = choices
        self.history: ConversationHistory = []
        self.story_id = story_id
        self.num_opportunities = num_opportunities

    @staticmethod
    def from_json(json_obj: dict):
        narratives = [] if "story" not in json_obj else json_obj["story"]
        choices = [] if "choices" not in json_obj else json_obj["choices"]
        return StoryChunk(
            json_obj["id"],
            json_obj["chapter"],
            json_obj["story_so_far"],
            [StoryNarrative.from_json(narrative) for narrative in narratives],
            [StoryChoice.from_json(choice) for choice in choices],
            json_obj["story_id"],
            json_obj["num_opportunities"],
        )

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "chapter": self.chapter,
            "story_so_far": self.story_so_far,
            "story": [narrative.to_json() for narrative in self.story],
            "choices": [choice.to_json() for choice in self.choices],
            "history": self.history,
            "story_id": self.story_id,
            "num_opportunities": self.num_opportunities,
        }

    def __str__(self):
        return f"StoryChunk(id={self.id}, chapter={self.chapter}, story_so_far={self.story_so_far}, story={[str(n) for n in self.story]}, choices={[str(c) for c in self.choices]})"

    def save_to_db(self, session: Session):
        if len(self.history) == 0:
            raise ValueError("current_history is None")

        session.run(
            """CREATE (storyChunk:StoryChunk {id: $id, chapter: $chapter, story_so_far: $story_so_far, 
            story: $story, history: $history, story_id: $story_id, num_opportunities: $num_opportunities})""",
            id=self.id,
            chapter=self.chapter,
            story_so_far=self.story_so_far,
            story=json.dumps([n.to_json() for n in self.story]),
            history=json.dumps(self.history),
            story_id=self.story_id,
            num_opportunities=self.num_opportunities,
        )

    def branched_timeline_to_db(
        self, session: Session, story_chunk: "StoryChunk", choice: StoryChoice = None
    ):
        props = {} if not choice else choice.to_json()
        session.run(
            """MATCH (source:StoryChunk {id: $source_id}), (branched:StoryChunk {id: $branched_id})
            CREATE (source)-[:BRANCHED_TO $props]->(branched)""",
            source_id=self.id,
            branched_id=story_chunk.id,
            props=props,
        )
