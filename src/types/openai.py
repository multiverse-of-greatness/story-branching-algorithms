from typing import Union

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionUserMessageParam

type OpenAIRole = Union["user", "assistant", "system"]
type ConversationHistory = list[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam |
                                ChatCompletionAssistantMessageParam]
