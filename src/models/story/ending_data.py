from pydantic import BaseModel


class EndingData(BaseModel):
    id: int
    ending: str
