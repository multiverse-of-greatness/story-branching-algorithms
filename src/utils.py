import json
import re
import typing

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, \
    ChatCompletionAssistantMessageParam

type OpenAIRole = typing.Union["user", "assistant", "system"]
type ConversationHistory = list[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam |
                                ChatCompletionAssistantMessageParam]


def format_openai_message(message: str,
                          role: OpenAIRole = "user",
                          history: ConversationHistory = None) -> ConversationHistory:
    if history is None:
        history = []

    history.append({
        "role": role,
        "content": message
    })

    return history


def parse_json_string(json_string: str) -> dict:
    pattern = r'.*```(json)?\n((.|\n)*?)\n```.*'
    match = re.search(pattern, json_string)

    if match is None:
        raise ValueError("Invalid JSON string")

    json_string = match.group(2)
    return json.loads(json_string)
