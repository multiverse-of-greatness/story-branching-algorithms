import copy
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import ujson
from anthropic.types import MessageParam
from loguru import logger

from src.bg_remover.bg_removal_model import BackgroundRemovalModel
from src.image_gen.image_gen_model import ImageGenModel
from src.llms.llm import LLM
from src.models.enums.branching_type import BranchingType
from src.models.enums.generation_approach import GenerationApproach
from src.models.frontier_item import FrontierItem
from src.models.generation_config import GenerationConfig
from src.prompts.utility_prompts import get_fix_invalid_json_prompt
from src.repository import CommonRepository
from src.types.algorithm import Frontiers
from src.types.openai import ConversationHistory
from src.utils.general import parse_json_string
from src.utils.openai_ai import append_openai_message


class GenerationContext:
    def __init__(self, approach: GenerationApproach, config: GenerationConfig, story_id: str = None):
        self.approach = approach
        self.config = config
        self.story_id = story_id if story_id is not None else str(uuid.uuid1())
        self.is_generation_completed = False
        self.output_path = Path("outputs") / self.approach.value / self.story_id
        self.output_path.mkdir(exist_ok=True, parents=True)
        self._initial_history: Optional[ConversationHistory] = None
        self._frontiers: Frontiers = [FrontierItem(current_chapter=1, used_choice_opportunity=0, state=BranchingType.BRANCHING)]
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.repository: Optional[CommonRepository] = None
        self.generation_model: Optional[LLM] = None
        self.image_generation_model: Optional[ImageGenModel] = None
        self.background_remover_model: Optional[BackgroundRemovalModel] = None
        self.completed_at: Optional[datetime] = None

    def append_response_to_file(self, model_name: str, response: str, prompt_tokens: int, completion_tokens: int):
        file_output_path = self.output_path / f"{model_name}.json"
        responses = {"responses": [], "prompt_tokens": 0, "completion_tokens": 0}

        if file_output_path.exists():
            with open(file_output_path, "r") as file:
                responses = ujson.load(file)

        responses["responses"] += [response]
        responses["prompt_tokens"] += prompt_tokens
        responses["completion_tokens"] += completion_tokens

        with open(file_output_path, "w") as file:
            ujson.dump(responses, file, indent=2)

    def append_history_to_file(self, history: ConversationHistory | Iterable[MessageParam]):
        with open(self.output_path / "histories.json", "r+") as file:
            histories = ujson.load(file)
            histories["histories"] += [history]
            file.seek(0)
            ujson.dump(histories, file, indent=2)

    def generate_content(self, messages: ConversationHistory) -> tuple[str, dict]:
        history, response, input_tokens, output_tokens = self.generation_model.generate_content(messages)

        self.append_response_to_file(self.generation_model.model_name, response, input_tokens, output_tokens)
        self.append_history_to_file(history)

        try:
            return response, parse_json_string(response)
        except ValueError as e:
            raise ValueError(f"Chat completion response could not be decoded as JSON\n{str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise e
    
    def fix_invalid_json_generation(self, old_response: str, error_msg: str) -> tuple[str, dict]:
        fix_json_prompt = get_fix_invalid_json_prompt(old_response, error_msg)
        retry_history = append_openai_message("You are a helpful coding AI assistant.", "system")
        retry_history = append_openai_message(fix_json_prompt, "user", retry_history)
        logger.warning(f"Retrying with: {retry_history}")
        return self.generate_content(retry_history)

    def sync_file(self):
        with open(self.output_path / "context.json", "w") as file:
            ujson.dump(self.to_dict(), file, indent=2)

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
    def from_dict(data_obj: dict):
        ctx = GenerationContext(GenerationApproach(data_obj['approach']),
                                GenerationConfig.model_validate(data_obj['config']),
                                data_obj['story_id'])
        ctx.is_generation_completed = data_obj['is_generation_completed']
        ctx.created_at = datetime.fromisoformat(data_obj['created_at'])
        ctx.updated_at = datetime.fromisoformat(data_obj['updated_at'])
        ctx.completed_at = None if not data_obj.get('completed_at') else datetime.fromisoformat(data_obj['completed_at'])
        ctx._initial_history = data_obj['initial_history']
        ctx._frontiers = [FrontierItem.model_validate(item) for item in data_obj["frontiers"]]
        return ctx

    def to_dict(self) -> dict:
        return {
            'approach': self.approach.value,
            'config': self.config.model_dump(),
            'story_id': self.story_id,
            'is_generation_completed': self.is_generation_completed,
            'output_path': str(self.output_path),
            'initial_history': self._initial_history,
            'frontiers': [item.model_dump() for item in self._frontiers],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': None if not self.completed_at else self.completed_at.isoformat()
        }

    def __str__(self):
        return (f"GenerationContext(approach={self.approach.value}, config={self.config}, story_id={self.story_id}, output_path={self.output_path}, "
                f"is_generation_completed={self.is_generation_completed}, created_at={self.created_at}, updated_at={self.updated_at}, "
                f"completed_at={self.completed_at})")
