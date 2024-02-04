import json
import os
from json.decoder import JSONDecodeError
from pathlib import Path
from time import sleep

from loguru import logger
from openai import (APIConnectionError, APIError, APITimeoutError, OpenAI,
                    RateLimitError)
from tiktoken import get_encoding

from .prompts import fix_invalid_json_prompt
from .types import ConversationHistory
from .utils import format_openai_message, parse_json_string


class ChatGPT:
    def __init__(self):
        self.model = os.getenv("GENERATION_MODEL")
        self.encoder = get_encoding("cl100k_base")
        self.client = OpenAI(timeout=60)

    def rolling_history(self, history: ConversationHistory) -> ConversationHistory:
        max_tokens = 16385
        count_tokens = 0
        new_history = []
        for message in history:
            count_tokens += len(self.encoder.encode(message["content"]))

        if count_tokens > max_tokens * 0.8:
            count_tokens = 0
            for message in history[-1:3:-1]:
                count_tokens += len(self.encoder.encode(message["content"]))
                if count_tokens > max_tokens * 0.5:
                    break
                new_history.append(message)

            for message in history[:4][::-1]:
                new_history.append(message)

            new_history.reverse()
            return new_history
        else:
            return history


    def chat_completions(self, messages: ConversationHistory) -> tuple[str, dict]:
        response = None
        messages = self.rolling_history(messages)
        try:
            raw_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
                seed=42
            )

            response = raw_response.choices[0].message.content

            chatgpt_path = Path("outputs/chatgpt.json")
            responses = {"responses": []}

            if chatgpt_path.exists():
                with open(chatgpt_path, "r") as f:
                    responses = json.load(f)

            responses["responses"].append(response)

            with open(chatgpt_path, "w") as f:
                f.write(json.dumps(responses, indent=2))

            return response, parse_json_string(response)
        except (ValueError, JSONDecodeError) as e:
            logger.warning(f"OpenAI API response could not be decoded as JSON: {e}")
            fix_json_prompt = fix_invalid_json_prompt(response, str(e))
            retry_with = format_openai_message("You are a helpful coding AI assistant.", "system")
            retry_with = format_openai_message(fix_json_prompt, "user", retry_with)
            logger.warning(f"Retrying with: {retry_with}")
            return self.chat_completions(retry_with)
        except APITimeoutError as e:
            logger.warning(f"OpenAI API request timed out: {e}")
            sleep(3)
            return self.chat_completions(messages)
        except APIConnectionError as e:
            logger.warning(f"OpenAI API request failed to connect: {e}")
            sleep(3)
            return self.chat_completions(messages)
        except RateLimitError as e:
            logger.warning(f"OpenAI API request exceeded rate limit: {e}")
            sleep(3)
            return self.chat_completions(messages)
        except APIError as e:
            logger.warning(f"OpenAI API returned an API Error: {e}")
            sleep(3)
            return self.chat_completions(messages)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
