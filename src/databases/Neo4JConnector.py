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
        self.dbname = os.getenv("NEO4J_DBNAME")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    @property
    def uri(self):
        return "bolt://{}:{}".format(self.host, self.port)
    
    def set_database(self, dbname: str):
        if dbname is not None:
            self.dbname = dbname

    def write(self, model: DBModel):
        self.with_session(model.save_to_db)

    def with_session(self, func: Callable, *args, **kwargs):
        with self.driver.session(database=self.dbname) as session:
            func(session, *args, **kwargs)
