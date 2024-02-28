import copy
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.databases.Neo4JConnector import Neo4JConnector
from src.llms.llm import LLM
from src.models.generation_config import GenerationConfig
from ..bg_remover.bg_removal_model import BackgroundRemovalModel
from ..image_gen.image_gen_model import ImageGenModel
from ..types.algorithm import Frontiers, BranchingType
from ..types.openai import ConversationHistory


class GenerationContext:
    def __init__(self, db_connector: Neo4JConnector, generation_model: LLM, image_generation_model: ImageGenModel,
                 background_removal_model: BackgroundRemovalModel, config: GenerationConfig, story_id: str = None):
        self.db_connector = db_connector
        self.generation_model = generation_model
        self.image_gen_model = image_generation_model
        self.background_remover_model = background_removal_model
        self.config = config
        self.story_id = story_id if story_id is not None else str(uuid.uuid1())
        self.is_generation_completed = False
        self.output_path = Path("outputs") / self.story_id
        self.output_path.mkdir(exist_ok=True, parents=True)
        self._initial_history: Optional[ConversationHistory] = None
        self._frontiers: Frontiers = [(1, 0, None, None, BranchingType.BRANCHING)]
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at: Optional[datetime] = None

    def sync_file(self):
        with open(self.output_path / "context.json", "w") as file:
            file.write(json.dumps(self.to_json(), indent=2))

    def get_initial_history(self):
        return self._initial_history

    def set_initial_history(self, initial_history):
        self._initial_history = copy.deepcopy(initial_history)
        self.sync_file()

    def get_frontiers(self):
        return self._frontiers

    def set_frontiers(self, frontiers):
        self._frontiers = copy.deepcopy(frontiers)
        self.sync_file()

    def sync_updated_at(self):
        self.updated_at = datetime.now()
        self.sync_file()

    def completed(self):
        self.completed_at = datetime.now()
        self.is_generation_completed = True
        self.sync_file()

    @staticmethod
    def from_json(json_obj: dict, db_connector: Neo4JConnector, generation_model: LLM,
                  image_generation_model: ImageGenModel,
                  background_removal_model: BackgroundRemovalModel) -> 'GenerationContext':
        ctx = GenerationContext(db_connector, generation_model, image_generation_model, background_removal_model,
                                GenerationConfig.from_json(json_obj['config']), json_obj['story_id'])
        ctx.is_generation_completed = json_obj['is_generation_completed']
        ctx.created_at = datetime.fromisoformat(json_obj['created_at'])
        ctx.updated_at = datetime.fromisoformat(json_obj['updated_at'])
        ctx.completed_at = datetime.fromisoformat(json_obj['completed_at']) if not json_obj.get(
            'completed_at') else None
        ctx._initial_history = json_obj['initial_history']
        ctx._frontiers = list(
            map(lambda x: (x[0], x[1], x[2], x[3], BranchingType.from_string(x[4])), json_obj['frontiers']))
        return ctx

    def to_json(self) -> dict:
        return {
            'db_connector': str(self.db_connector),
            'generation_model': str(self.generation_model),
            'image_generation_model': str(self.image_gen_model),
            'background_removal_model': str(self.background_remover_model),
            'config': self.config.to_json(),
            'story_id': self.story_id,
            'is_generation_completed': self.is_generation_completed,
            'output_path': str(self.output_path),
            'initial_history': self._initial_history,
            'frontiers': list(map(lambda x: (x[0], x[1], x[2], x[3], BranchingType.to_string(x[4])), self._frontiers)),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def __str__(self):
        return (f"GenerationContext(db_connector={self.db_connector}, generation_model={self.generation_model}, "
                f"image_generation_model={self.image_gen_model}, "
                f"background_removal_model={self.background_remover_model}, config={self.config}, "
                f"story_id={self.story_id}, output_path={self.output_path}, "
                f"is_generation_completed={self.is_generation_completed}, initial_history={self._initial_history}, "
                f"frontiers={self._frontiers}, created_at={self.created_at}, updated_at={self.updated_at}, "
                f"completed_at={self.completed_at})")
