import os
from typing import Callable

from neo4j import GraphDatabase

from .DBModel import DBModel


class Neo4JConnector:
    def __init__(self):
        self.host = os.getenv("NEO4J_HOST")
        self.port = os.getenv("NEO4J_PORT")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASS")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

        # TODO: Remove this
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    @property
    def uri(self):
        return "bolt://{}:{}".format(self.host, self.port)

    def write(self, model: DBModel):
        self.with_session(model.save_to_db)

    def with_session(self, func: Callable, *args, **kwargs):
        with self.driver.session() as session:
            func(session, *args, **kwargs)
