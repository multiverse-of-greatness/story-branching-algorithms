import copy
import json
import re

from .types import OpenAIRole, ConversationHistory


def format_openai_message(message: str,
                          role: OpenAIRole = "user",
                          history: ConversationHistory = None) -> ConversationHistory:
    if history is None:
        history = []

    history = copy.deepcopy(history)

    history.append({
        "role": role,
        "content": message
    })

    return history


def parse_json_string(json_string: str) -> dict:
    if json_string.startswith("{") and json_string.endswith("}"):
        return json.loads(json_string)
    
    pattern = r'.*```(json)?\n((.|\n)*?)\n```.*'
    match = re.search(pattern, json_string, re.DOTALL)

    if match is None:
        raise ValueError("JSON markdown block not found in the message. Please use the following format:\n```json\n{...}\n```")

    json_string = match.group(2)
    return json.loads(json_string)
