from neo4j import Session

from src.databases.DBModel import DBModel


class CharacterData(DBModel):
    def __init__(self, id: int, first_name: str, last_name: str, species: str, age: str, gender: str, role: str,
                 background: str,
                 place_of_birth: str, physical_appearance: list[str]):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.species = species
        self.age = age
        self.gender = gender
        self.role = role
        self.background = background
        self.place_of_birth = place_of_birth
        self.physical_appearance = physical_appearance

    @staticmethod
    def from_json(json_obj: dict):
        return CharacterData(json_obj['id'], json_obj['first_name'], json_obj['last_name'], json_obj['species'],
                             json_obj['age'], json_obj['gender'], json_obj['role'], json_obj['background'],
                             json_obj['place_of_birth'], json_obj['physical_appearance'])

    def to_json(self) -> dict:
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
            'physical_appearance': self.physical_appearance
        }

    def __str__(self):
        return (f"CharacterData(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, "
                f"species={self.species}, age={self.age}, gender={self.gender}, role={self.role}, "
                f"background={self.background}, place_of_birth={self.place_of_birth}, "
                f"physical_appearance={self.physical_appearance})")

    def save_to_db(self, session: Session):
        session.run('CREATE (characterData:CharacterData $props)', props=self.to_json())
