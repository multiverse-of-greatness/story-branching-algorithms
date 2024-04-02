from typing import Literal

from openai.types.chat import (ChatCompletionAssistantMessageParam,
                               ChatCompletionSystemMessageParam,
                               ChatCompletionUserMessageParam)

OpenAIRole = Literal["user", "assistant", "system"]
ConversationHistory = list[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam |
                                ChatCompletionAssistantMessageParam]
