from enum import Enum
from typing import Union, Optional

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam, \
    ChatCompletionAssistantMessageParam

from src.models.StoryChunk import StoryChunk
from src.models.story.StoryChoice import StoryChoice

type OpenAIRole = Union["user", "assistant", "system"]
type ConversationHistory = list[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam |
                                ChatCompletionAssistantMessageParam]
type Frontiers = list[tuple[int, int, Optional[StoryChunk], Optional[StoryChoice], BranchingType]]


class BranchingType(Enum):
    BRANCHING = 0
    CHAPTER_END = 1
    GAME_END = 2
