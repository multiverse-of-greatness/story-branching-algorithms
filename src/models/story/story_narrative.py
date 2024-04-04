from dataclasses import dataclass


@dataclass
class StoryNarrative:
    id: int
    speaker: str
    speaker_id: int
    scene_title: str
    scene_id: int
    text: str

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'speaker': self.speaker,
            'speaker_id': self.speaker_id,
            'scene_title': self.scene_title,
            'scene_id': self.scene_id,
            'text': self.text
        }

    @classmethod
    def from_dict(cls, data_obj: dict):
        return cls(
            id=data_obj.get("id"),
            speaker=data_obj.get("speaker"),
            speaker_id=data_obj.get("speaker_id"),
            scene_title=data_obj.get("scene_title"),
            scene_id=data_obj.get("scene_id"),
            text=data_obj.get("text")
        )

    def __str__(self):
        return (f'StoryNarrative(id={self.id}, speaker={self.speaker}, speaker_id={self.speaker_id}, '
                f'scene_title={self.scene_id}, scene_id={self.scene_title}, text={self.text})')
    
    def __repr__(self):
        return str(self)
