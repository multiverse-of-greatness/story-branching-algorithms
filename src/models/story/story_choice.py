from pydantic import BaseModel


class StoryChoice(BaseModel):
    id: int
    choice: str
    description: str
