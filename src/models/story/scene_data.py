from neo4j import Session

from src.databases.model import DBModel


class SceneData(DBModel):
    def __init__(self, id: int, title: str, location: str, description: str, image: str = None):
        self.id = id
        self.title = title
        self.location = location
        self.description = description
        self.image = image

    @staticmethod
    def from_json(json_obj: dict):
        return SceneData(json_obj['id'], json_obj['title'], json_obj['location'], json_obj['description'],
                         json_obj.get('image'))

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'location': self.location,
            'description': self.description,
            'image': self.image
        }

    def __str__(self):
        return (
            f'SceneData(id={self.id}, title={self.title}, location={self.location}, description={self.description}, '
            f'image={self.image})')

    def save_to_db(self, session: Session):
        session.run('CREATE (sceneData:SceneData $props)', props=self.to_json())
