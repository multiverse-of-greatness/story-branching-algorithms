from dataclasses import dataclass
from typing import Optional


@dataclass
class SceneData:
    id: int
    title: str
    location: str
    description: str
    image: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'location': self.location,
            'description': self.description,
            'image': self.image
        }

    @classmethod
    def from_dict(cls, data_obj: dict):
        return cls(
            id=data_obj.get("id"),
            title=data_obj.get("title"),
            location=data_obj.get("location"),
            description=data_obj.get("description"),
            image=data_obj.get("image")
        )

    def __str__(self):
        return (
            f'SceneData(id={self.id}, title={self.title}, location={self.location}, description={self.description}, '
            f'image={bool(self.image)})')
    
    def __repr__(self):
        return str(self)
