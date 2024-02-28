from neo4j import Session

from src.databases.DBModel import DBModel


class StoryNarrative(DBModel):
    def __init__(self, id: int, speaker: str, speaker_id: int, scene_title: str, scene_id: int, text: str):
        self.id = id
        self.speaker = speaker
        self.speaker_id = speaker_id
        self.scene_title = scene_title
        self.scene_id = scene_id
        self.text = text

    @staticmethod
    def from_json(json_obj: dict):
        return StoryNarrative(json_obj['id'], json_obj['speaker'], json_obj['speaker_id'], json_obj['scene_title'],
                              json_obj['scene_id'], json_obj['text'])

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'speaker': self.speaker,
            'speaker_id': self.speaker_id,
            'scene_title': self.scene_title,
            'scene_id': self.scene_id,
            'text': self.text
        }

    def __str__(self):
        return (f'StoryNarrative(id={self.id}, speaker={self.speaker}, speaker_id={self.speaker_id}, '
                f'scene_title={self.scene_id}, scene_id={self.scene_title}, text={self.text})')

    def save_to_db(self, session: Session):
        session.run('CREATE (storyNarrative:StoryNarrative $props)', props=self.to_json())
