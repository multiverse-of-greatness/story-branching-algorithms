import copy
import uuid
from pathlib import Path
from typing import Optional

from src.databases.Neo4JConnector import Neo4JConnector
from src.llms.llm import LLM
from src.models.GenerationConfig import GenerationConfig
from ..types.algorithm import Frontiers, BranchingType
from ..types.openai import ConversationHistory


class GenerationContext:
    def __init__(self, db_connector: Neo4JConnector, generation_model: LLM, config: GenerationConfig):
        self.db_connector = db_connector
        self.generation_model = generation_model
        self.config = config
        self.story_id = str(uuid.uuid1())
        self.output_path = Path("outputs") / self.story_id
        self.output_path.mkdir(exist_ok=True, parents=True)
        self._initial_history: Optional[ConversationHistory] = None
        self._frontiers: Frontiers = [(1, 0, None, None, BranchingType.BRANCHING)]

    def set_initial_history(self, initial_history):
        self._initial_history = copy.deepcopy(initial_history)

    def set_frontiers(self, frontiers):
        self._frontiers = copy.deepcopy(frontiers)

    def get_initial_history(self):
        return self._initial_history

    def get_frontiers(self):
        return self._frontiers

    @staticmethod
    def from_json(json_obj: dict):
        return GenerationContext(Neo4JConnector(), LLM(), GenerationConfig.from_json(json_obj['config']))

    def to_json(self) -> dict:
        return {
            'db_connector': str(self.db_connector),
            'generation_model': str(self.generation_model),
            'config': self.config.to_json(),
            'story_id': self.story_id,
            'output_path': str(self.output_path),
            'initial_history': self._initial_history,
            'frontiers': self._frontiers
        }

    def __str__(self):
        return f"""GenerationContext(db_connector={self.db_connector}, generation_model={self.generation_model}, 
        config={self.config}, story_id={self.story_id}, output_path={self.output_path}, 
        initial_history={self._initial_history}, frontiers={self._frontiers})"""
