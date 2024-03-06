import os
from typing import Callable

from neo4j import GraphDatabase

from .model import DBModel


class Neo4JConnector:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        username, password = os.getenv("NEO4J_AUTH").split("/")
        self.driver = GraphDatabase.driver(self.uri, auth=(username, password))

    def write(self, model: DBModel):
        self.with_session(model.save_to_db)

    def with_session(self, func: Callable, *args, **kwargs):
        with self.driver.session() as session:
            func(session, *args, **kwargs)

    def __str__(self):
        return f"Neo4JConnector(uri={self.uri})"
