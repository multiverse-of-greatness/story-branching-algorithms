import json
import os
from json.decoder import JSONDecodeError
from pathlib import Path
from time import sleep

from loguru import logger
from openai import (APIConnectionError, APIError, APITimeoutError, OpenAI,
                    RateLimitError)
from tiktoken import get_encoding

from src.llms.llm import LLM
from src.prompts import fix_invalid_json_prompt
from src.utils import append_openai_message, parse_json_string
from ..types.openai import ConversationHistory


class ChatGPT(LLM):
    model_name = os.getenv("GENERATION_MODEL")
    max_tokens = 16385
    encoder = get_encoding("cl100k_base")
    client = OpenAI(timeout=60)

    def generate_content(self, messages: ConversationHistory) -> tuple[str, dict]:
        logger.debug(f"Starting chat completion with model: {self.model_name}")
        response = None
        messages = self.rolling_history(messages)
        try:
            chat_completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
                seed=42
            )

            response = chat_completion.choices[0].message.content

            output_path = Path(f"outputs/{self.model_name}.json")
            responses = {"responses": [], "prompt_tokens": 0, "completion_tokens": 0}

            if output_path.exists():
                with open(output_path, "r") as f:
                    responses = json.load(f)

            responses["responses"].append(response)
            responses["prompt_tokens"] += chat_completion.usage.prompt_tokens
            responses["completion_tokens"] += chat_completion.usage.completion_tokens

            with open(output_path, "w") as f:
                f.write(json.dumps(responses, indent=2))

            return response, parse_json_string(response)
        except (ValueError, JSONDecodeError) as e:
            logger.warning(f"OpenAI API response could not be decoded as JSON: {str(e)}")
            return self.fix_invalid_json_generation(response, str(e))
        except (APITimeoutError, APIConnectionError, RateLimitError, APIError) as e:
            logger.warning(f"OpenAI API error: {e}")
            sleep(3)
            return self.generate_content(messages)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise e

    def fix_invalid_json_generation(self, old_response: str, error_msg: str) -> tuple[str, dict]:
        fix_json_prompt = fix_invalid_json_prompt(old_response, error_msg)
        retry_history = append_openai_message("You are a helpful coding AI assistant.", "system")
        retry_history = append_openai_message(fix_json_prompt, "user", retry_history)
        logger.warning(f"Retrying with: {retry_history}")

        return self.generate_content(retry_history)

    def __str__(self):
        return f"ChatGPT(model_name={self.model_name}, max_tokens={self.max_tokens})"
