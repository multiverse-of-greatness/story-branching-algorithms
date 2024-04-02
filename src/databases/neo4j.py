import os
from typing import Callable

from loguru import logger
from neo4j import GraphDatabase

from src.databases.model import DBModel


class Neo4JConnector:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4JConnector, cls).__new__(cls)
            cls._instance.initialize()
            logger.info(f"Neo4JConnector initialized: {cls._instance}")
        return cls._instance

    def initialize(self):
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
