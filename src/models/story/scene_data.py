from pydantic import BaseModel
from typing_extensions import Optional


class SceneData(BaseModel):
    id: int
    title: str
    location: str
    description: str
    image: Optional[str] = None

    def __str__(self):
        return (
            f'SceneData(id={self.id}, title={self.title}, location={self.location}, description={self.description}, '
            f'image={bool(self.image)})')
    
    def __repr__(self):
        return str(self)
