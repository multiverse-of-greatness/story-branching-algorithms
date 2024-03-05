import copy
import json
import os
from json import JSONDecodeError
from time import sleep

import google.generativeai as genai
from google.ai.generativelanguage_v1beta import Content
from google.api_core.exceptions import ServiceUnavailable, InternalServerError, TooManyRequests, DeadlineExceeded
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from loguru import logger

from src.llms.llm import LLM
from src.models.generation_context import GenerationContext
from src.prompts.utility_prompts import get_fix_invalid_json_prompt
from src.utils.general import append_openai_message, parse_json_string
from ..types.openai import ConversationHistory
from ..utils.google_ai import map_openai_history_to_google_history, map_google_history_to_openai_history


class GoogleModel(LLM):
    def __init__(self, model_name: str, max_tokens: int = 32768):
        super().__init__(max_tokens)
        genai.configure(api_key=os.environ["GOOGLE_AI_API_KEY"])
        self.model_name = model_name
        self.client = genai.GenerativeModel(self.model_name)
        self.max_tokens = max_tokens

    def count_token(self, message: str) -> int:
        count = genai.GenerativeModel(self.model_name).count_tokens(message).total_tokens
        return count

    @staticmethod
    def get_history_message(messages: list[Content]) -> str:
        history = ""
        for message in messages:
            history += f"{message.parts[0].text} "
        return history

    def generate_content(self, ctx: GenerationContext, messages: ConversationHistory) -> tuple[str, dict]:
        logger.debug(f"Starting chat completion with model: {self.model_name}")

        copied_messages = copy.deepcopy(messages)
        copied_messages = self.rolling_history(copied_messages)
        last_message = copied_messages.pop()
        if last_message.get("role") == "system" or last_message.get("role") == "assistant":
            raise ValueError(f"Last message role is not user: {last_message.get('role')}")
        current_message = last_message.get("content")

        copied_messages = map_openai_history_to_google_history(copied_messages)
        chat = self.client.start_chat(history=copied_messages)

        try:
            chat_completion = chat.send_message(current_message, safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
            })

            response = chat_completion.text.strip()

            output_path = ctx.output_path / f"{self.model_name}.json"
            responses = {"responses": [], "prompt_tokens": 0, "completion_tokens": 0}

            if output_path.exists():
                with open(output_path, "r") as f:
                    responses = json.load(f)

            responses["responses"].append(response)

            copied_messages = copied_messages + map_openai_history_to_google_history([last_message])

            prompt_tokens = self.count_token(self.get_history_message(copied_messages))
            responses["prompt_tokens"] += prompt_tokens
            response_tokens = self.count_token(response)
            responses["completion_tokens"] += response_tokens

            with open(output_path, "w") as f:
                f.write(json.dumps(responses, indent=2))

            with open(ctx.output_path / "histories.json", "r+") as file:
                histories = json.load(file)
                histories["histories"].append(map_google_history_to_openai_history(copied_messages))
                file.seek(0)
                file.write(json.dumps(histories, indent=2))

            return response, parse_json_string(response)
        except (ValueError, JSONDecodeError) as e:
            logger.warning(f"Gemini 1.0 Pro response could not be decoded as JSON: {str(e)}")
            raise e
        except (ServiceUnavailable, InternalServerError, TooManyRequests, DeadlineExceeded) as e:
            logger.warning(f"Gemini 1.0 Pro API error: {e}")
            converted_history = map_google_history_to_openai_history(copied_messages)
            sleep(3)
            return self.generate_content(ctx, converted_history)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise e

    def fix_invalid_json_generation(self, ctx: GenerationContext, old_response: str, error_msg: str) -> tuple[
        str, dict]:
        fix_json_prompt = get_fix_invalid_json_prompt(old_response, error_msg)
        retry_history = append_openai_message(fix_json_prompt, "user")
        logger.warning(f"Retrying with: {retry_history}")

        return self.generate_content(ctx, retry_history)

    def __str__(self):
        return f"GeminiOnePro(model_name={self.model_name}, max_tokens={self.max_tokens})"
