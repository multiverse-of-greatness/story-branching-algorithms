import copy
import os
from json.decoder import JSONDecodeError
from time import sleep

from anthropic import Anthropic, APIConnectionError, RateLimitError, APIStatusError, APITimeoutError
from loguru import logger

from src.llms.llm import LLM
from src.models.generation_context import GenerationContext
from src.prompts.utility_prompts import get_fix_invalid_json_prompt
from src.types.openai import ConversationHistory
from src.utils.anthropic_ai import map_openai_history_to_anthropic_history
from src.utils.general import parse_json_string
from src.utils.openai_ai import append_openai_message


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
            input_tokens = chat_completion.usage.input_tokens
            output_tokens = chat_completion.usage.output_tokens

            ctx.append_response_to_file(self.model_name, response, input_tokens, output_tokens)
            ctx.append_history_to_file(copied_messages)

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
