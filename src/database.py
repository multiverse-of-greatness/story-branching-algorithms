import os
from typing import Callable

from loguru import logger

from neo4j import GraphDatabase


class Neo4J:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4J, cls).__new__(cls)
            cls._instance._initialize()
            logger.info("Neo4J instance created")
        return cls._instance
    
    def _initialize(self):
        self.uri = os.getenv("NEO4J_URI")
        username, password = os.getenv("NEO4J_AUTH").split("/")
        self.driver = GraphDatabase.driver(self.uri, auth=(username, password))

    def with_session(self, func: Callable, *args, **kwargs):
        with self.driver.session() as session:
            func(session, *args, **kwargs)

    def close(self):
        self.driver.close()

    def __str__(self):
        return f"Neo4J(uri={self.uri})"
