from typing import Iterable

from anthropic.types import MessageParam

from src.types.openai import ConversationHistory


def map_openai_history_to_anthropic_history(history: ConversationHistory) -> Iterable[MessageParam]:
    converted_history: list[MessageParam] = []
    for message in history:
        if message.get("role") == "system":
            continue
        converted_history.append(message)

    return converted_history


def map_anthropic_history_to_openai_history(history: Iterable[MessageParam]) -> ConversationHistory:
    converted_history: ConversationHistory = []
    for message in history:
        converted_history.append(message)

    return converted_history
