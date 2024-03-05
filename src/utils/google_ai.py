from google.ai.generativelanguage_v1beta.types.content import Content, Part

from src.types.openai import ConversationHistory, OpenAIRole


def map_openai_role_to_google_role(role: OpenAIRole) -> str:
    if role == "assistant":
        return "model"
    elif role == "user":
        return "user"
    else:
        raise ValueError(f"Unknown role: {role}")


def map_google_role_to_openai_role(role: str) -> OpenAIRole:
    if role == "model":
        return "assistant"
    elif role == "user":
        return "user"
    else:
        raise ValueError(f"Unknown role: {role}")


def map_openai_history_to_google_history(history: ConversationHistory) -> list[Content]:
    converted_history: list[Content] = []
    for message in history:
        if message.get("role") == "system":
            continue
        content = Content()
        part = Part()
        part.text = message.get("content")
        content.parts = [part]
        content.role = map_openai_role_to_google_role(message.get("role"))
        converted_history.append(content)

    return converted_history


def map_google_history_to_openai_history(history: list[Content]) -> ConversationHistory:
    converted_history: ConversationHistory = []
    for message in history:
        converted_history.append(
            {
                "role": map_google_role_to_openai_role(message.role),
                "content": message.parts[0].text
            }
        )

    return converted_history
