from enum import Enum
from typing import Union

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, \
    ChatCompletionAssistantMessageParam

type OpenAIRole = Union["user", "assistant", "system"]
type ConversationHistory = list[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam |
                                ChatCompletionAssistantMessageParam]


class BranchingType(Enum):
    BRANCHING = 0
    CHAPTER_END = 1
    GAME_END = 2
