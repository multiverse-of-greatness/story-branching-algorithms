import copy
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Iterable

from anthropic.types import MessageParam

from src.bg_remover.bg_removal_model import BackgroundRemovalModel
from src.databases.neo4j import Neo4JConnector
from src.image_gen.image_gen_model import ImageGenModel
from src.llms.llm import LLM
from src.models.generation_config import GenerationConfig
from src.models.story.story_choice import StoryChoice
from src.models.story_chunk import StoryChunk
from src.types.algorithm import Frontiers, BranchingType
from src.types.openai import ConversationHistory


class GenerationContext:
    def __init__(self, db_connector: Neo4JConnector, generation_model: LLM,
                 image_generation_model: Optional[ImageGenModel], background_removal_model: BackgroundRemovalModel,
                 approach: str, config: GenerationConfig,
                 story_id: str = None):
        self.db_connector = db_connector
        self.generation_model = generation_model
        self.image_gen_model = image_generation_model
        self.background_remover_model = background_removal_model
        self.approach = approach
        self.config = config
        self.story_id = story_id if story_id is not None else str(uuid.uuid1())
        self.is_generation_completed = False
        self.output_path = Path("outputs") / self.approach / self.story_id
        self.output_path.mkdir(exist_ok=True, parents=True)
        self._initial_history: Optional[ConversationHistory] = None
        self._frontiers: Frontiers = [(1, 0, None, None, BranchingType.BRANCHING)]
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at: Optional[datetime] = None

    def append_response_to_file(self, model_name: str, response: str, prompt_tokens: int, completion_tokens: int):
        file_output_path = self.output_path / f"{model_name}.json"
        responses = {"responses": [], "prompt_tokens": 0, "completion_tokens": 0}

        if file_output_path.exists():
            with open(file_output_path, "r") as f:
                responses = json.load(f)

        responses["responses"].append(response)
        responses["prompt_tokens"] += prompt_tokens
        responses["completion_tokens"] += completion_tokens

        with open(file_output_path, "w") as f:
            f.write(json.dumps(responses, indent=2))

    def append_history_to_file(self, history: ConversationHistory | Iterable[MessageParam]):
        with open(self.output_path / "histories.json", "r+") as file:
            histories = json.load(file)
            histories["histories"].append(history)
            file.seek(0)
            file.write(json.dumps(histories, indent=2))

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

    def set_frontiers(self, frontiers: Frontiers):
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
                  image_generation_model: Optional[ImageGenModel],
                  background_removal_model: BackgroundRemovalModel) -> 'GenerationContext':
        ctx = GenerationContext(db_connector, generation_model, image_generation_model, background_removal_model,
                                GenerationConfig.from_json(json_obj['config']), json_obj['approach'],
                                json_obj['story_id'])
        ctx.is_generation_completed = json_obj['is_generation_completed']
        ctx.created_at = datetime.fromisoformat(json_obj['created_at'])
        ctx.updated_at = datetime.fromisoformat(json_obj['updated_at'])
        ctx.completed_at = datetime.fromisoformat(json_obj['completed_at']) if not json_obj.get(
            'completed_at') else None
        ctx._initial_history = json_obj['initial_history']
        ctx._frontiers = list(
            map(lambda x: (
                x[0], x[1], None if x[2] is None else StoryChunk.from_json(x[2]),
                None if x[3] is None else StoryChoice.from_json(x[3]), BranchingType.from_string(x[4])),
                json_obj['frontiers']))
        return ctx

    def to_json(self) -> dict:
        return {
            'db_connector': str(self.db_connector),
            'generation_model': str(self.generation_model),
            'image_generation_model': str(self.image_gen_model) if self.config.enable_image_generation else "N/A",
            'background_removal_model': str(self.background_remover_model),
            'approach': self.approach,
            'config': self.config.to_json(),
            'story_id': self.story_id,
            'is_generation_completed': self.is_generation_completed,
            'output_path': str(self.output_path),
            'initial_history': self._initial_history,
            'frontiers': list(map(lambda x: (
                x[0], x[1], None if x[2] is None else x[2].to_json(), None if x[3] is None else x[3].to_json(),
                BranchingType.to_string(x[4])), self._frontiers)),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

    def __str__(self):
        return (f"GenerationContext(db_connector={self.db_connector}, generation_model={self.generation_model}, "
                f"image_generation_model={self.image_gen_model}, "
                f"background_removal_model={self.background_remover_model}, approach={self.approach}, "
                f"config={self.config}, story_id={self.story_id}, output_path={self.output_path}, "
                f"is_generation_completed={self.is_generation_completed}, initial_history={self._initial_history}, "
                f"frontiers={self._frontiers}, created_at={self.created_at}, updated_at={self.updated_at}, "
                f"completed_at={self.completed_at})")
