from neo4j import Session

from src.databases.model import DBModel


class StoryChoice(DBModel):
    def __init__(self, id: int, choice: str, description: str):
        self.id = id
        self.choice = choice
        self.description = description

    @staticmethod
    def from_json(json_obj: dict):
        return StoryChoice(json_obj['id'], json_obj['choice'], json_obj['description'])

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'choice': self.choice,
            'description': self.description
        }

    def __str__(self):
        return f'StoryChoice(id={self.id}, choice={self.choice}, description={self.description})'

    def save_to_db(self, session: Session):
        session.run('CREATE (storyChoice:StoryChoice $props)', props=self.to_json())
