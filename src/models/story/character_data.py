from dataclasses import dataclass
from typing import Optional


@dataclass
class CharacterData:
    id: int
    first_name: str
    last_name: str
    species: str
    age: str
    gender: str
    role: str
    background: str
    place_of_birth: str
    physical_appearance: list[str]
    image: Optional[str] = None
    original_image: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'species': self.species,
            'age': self.age,
            'gender': self.gender,
            'role': self.role,
            'background': self.background,
            'place_of_birth': self.place_of_birth,
            'physical_appearance': self.physical_appearance,
            'image': self.image,
            'original_image': self.original_image
        }

    @classmethod
    def from_dict(cls, data_obj: dict):
        return cls(
            id=data_obj.get("id"),
            first_name=data_obj.get("first_name"),
            last_name=data_obj.get("last_name"),
            species=data_obj.get("species"),
            age=data_obj.get("age"),
            gender=data_obj.get("gender"),
            role=data_obj.get("role"),
            background=data_obj.get("background"),
            place_of_birth=data_obj.get("place_of_birth"),
            physical_appearance=data_obj.get("physical_appearance"),
            image=data_obj.get("image"),
            original_image=data_obj.get("original_image")
        )

    def __str__(self):
        return (f"CharacterData(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, "
                f"species={self.species}, age={self.age}, gender={self.gender}, role={self.role}, "
                f"background={self.background}, place_of_birth={self.place_of_birth}, "
                f"physical_appearance={self.physical_appearance}, image={bool(self.image)}, "
                f"original_image={bool(self.original_image)})")
    
    def __repr__(self):
        return str(self)
