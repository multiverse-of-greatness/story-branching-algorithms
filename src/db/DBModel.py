from abc import ABC, abstractmethod

from neo4j import Session


class DBModel(ABC):
    @abstractmethod
    def save_to_db(self, session: Session):
        pass

    @abstractmethod
    def to_json(self) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def from_json(json_obj: dict):
        pass
