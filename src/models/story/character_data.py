from pydantic import BaseModel
from typing_extensions import List, Optional


class CharacterData(BaseModel):
    id: int
    first_name: str
    last_name: str
    species: str
    age: str
    gender: str
    role: str
    background: str
    place_of_birth: str
    physical_appearance: List[str]
    image: Optional[str] = None
    original_image: Optional[str] = None

    def __str__(self):
        return (f"CharacterData(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, "
                f"species={self.species}, age={self.age}, gender={self.gender}, role={self.role}, "
                f"background={self.background}, place_of_birth={self.place_of_birth}, "
                f"physical_appearance={self.physical_appearance}, image={bool(self.image)}, "
                f"original_image={bool(self.original_image)})")
    
    def __repr__(self):
        return str(self)
