import json
import os
from pathlib import Path
from time import sleep

from loguru import logger
from openai import OpenAI, APITimeoutError, APIConnectionError, APIError, RateLimitError
from tiktoken import encoding_for_model

from .prompts import fix_invalid_json_prompt
from .types import ConversationHistory
from .utils import parse_json_string, format_openai_message


def rolling_history(history: ConversationHistory) -> ConversationHistory:
    encoder = encoding_for_model(os.getenv("GENERATION_MODEL"))
    max_tokens = 16385
    count_tokens = 0
    new_history = []
    for message in history:
        count_tokens += len(encoder.encode(message["content"]))

    if count_tokens > max_tokens * 0.8:
        count_tokens = 0
        for message in history[-1:3:-1]:
            count_tokens += len(encoder.encode(message["content"]))
            if count_tokens > max_tokens * 0.5:
                break
            new_history.append(message)

        for message in history[:4][::-1]:
            new_history.append(message)

        new_history.reverse()
        return new_history
    else:
        return history


def chatgpt(
    messages: ConversationHistory, retry_with: ConversationHistory = None
) -> tuple[str, dict]:
    client = OpenAI(
        timeout=60, base_url="https://permitted-nov-neither-icon.trycloudflare.com/v1"
    )  # TODO: Remove base_url

    if retry_with is not None:
        fix_json_prompt = fix_invalid_json_prompt(retry_with[-1]["content"])
        messages = format_openai_message(fix_json_prompt, retry_with)

    response = None
    messages = rolling_history(messages)
    try:
        raw_response = client.chat.completions.create(
            model=os.getenv("GENERATION_MODEL"), messages=messages, seed=42
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
    except (ValueError, json.decoder.JSONDecodeError) as e:
        logger.warning(f"OpenAI API response could not be decoded as JSON: {e}")
        to_retry = format_openai_message(response, "assistant", messages)
        return chatgpt(messages, to_retry)
    except APITimeoutError as e:
        logger.warning(f"OpenAI API request timed out: {e}")
        sleep(3)
        return chatgpt(messages)
    except APIConnectionError as e:
        logger.warning(f"OpenAI API request failed to connect: {e}")
        sleep(3)
        return chatgpt(messages)
    except RateLimitError as e:
        logger.warning(f"OpenAI API request exceeded rate limit: {e}")
        sleep(3)
        return chatgpt(messages)
    except APIError as e:
        logger.warning(f"OpenAI API returned an API Error: {e}")
        sleep(3)
        return chatgpt(messages)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
