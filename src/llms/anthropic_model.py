import copy
import json
import os
from json.decoder import JSONDecodeError
from time import sleep

from anthropic import Anthropic, APIConnectionError, RateLimitError, APIStatusError, APITimeoutError
from loguru import logger

from src.llms.llm import LLM
from src.prompts.utility_prompts import get_fix_invalid_json_prompt
from src.utils.general import append_openai_message, parse_json_string
from ..models.generation_context import GenerationContext
from ..types.openai import ConversationHistory
from ..utils.anthropic_ai import map_openai_history_to_anthropic_history


class AnthropicModel(LLM):
    def __init__(self, model_name: str, max_tokens: int = 200000):
        super().__init__(max_tokens)
        self.model_name = model_name
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), timeout=60)
        self.max_tokens = max_tokens

    def count_token(self, message: str) -> int:
        return self.client.count_tokens(message)

    def generate_content(self, ctx: GenerationContext, messages: ConversationHistory) -> tuple[str, dict]:
        logger.debug(f"Starting chat completion with model: {self.model_name}")

        copied_messages = copy.deepcopy(messages)

        copied_messages = self.rolling_history(copied_messages)
        copied_messages = map_openai_history_to_anthropic_history(copied_messages)

        try:
            chat_completion = self.client.messages.create(
                model=self.model_name,
                messages=copied_messages,
                max_tokens=4096
            )

            response = chat_completion.content[0].text.strip()

            output_path = ctx.output_path / f"{self.model_name}.json"
            responses = {"responses": [], "prompt_tokens": 0, "completion_tokens": 0}

            if output_path.exists():
                with open(output_path, "r") as f:
                    responses = json.load(f)

            responses["responses"].append(response)
            responses["prompt_tokens"] += chat_completion.usage.input_tokens
            responses["completion_tokens"] += chat_completion.usage.output_tokens

            with open(output_path, "w") as f:
                f.write(json.dumps(responses, indent=2))

            with open(ctx.output_path / "histories.json", "r+") as file:
                histories = json.load(file)
                histories["histories"].append(copied_messages)
                file.seek(0)
                file.write(json.dumps(histories, indent=2))

            return response, parse_json_string(response)
        except (ValueError, JSONDecodeError) as e:
            logger.warning(f"Anthropic response could not be decoded as JSON: {str(e)}")
            raise e
        except (APITimeoutError, APIConnectionError, RateLimitError, APIStatusError) as e:
            logger.warning(f"Anthropic error: {e}")
            sleep(3)
            return self.generate_content(ctx, messages)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise e

    def fix_invalid_json_generation(self, ctx: GenerationContext, old_response: str, error_msg: str) -> tuple[
        str, dict]:
        fix_json_prompt = get_fix_invalid_json_prompt(old_response, error_msg)
        retry_history = append_openai_message("You are a helpful coding AI assistant.", "system")
        retry_history = append_openai_message(fix_json_prompt, "user", retry_history)
        logger.warning(f"Retrying with: {retry_history}")

        return self.generate_content(ctx, retry_history)

    def __str__(self):
        return f"AnthropicModel(model_name={self.model_name}, max_tokens={self.max_tokens})"
