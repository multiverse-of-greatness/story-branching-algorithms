from dataclasses import dataclass


@dataclass
class StoryChoice:
    id: int
    choice: str
    description: str

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'choice': self.choice,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data_obj: dict):
        return cls(
            id=data_obj.get("id"),
            choice=data_obj.get("choice"),
            description=data_obj.get("description")
        )

    def __str__(self):
        return f'StoryChoice(id={self.id}, choice={self.choice}, description={self.description})'
    
    def __repr__(self):
        return str(self)
