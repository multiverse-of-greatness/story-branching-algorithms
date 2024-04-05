import copy
import os
from time import sleep

from anthropic import (Anthropic, APIConnectionError, APIStatusError,
                       APITimeoutError, RateLimitError)
from loguru import logger

from src.llms.llm import LLM
from src.types.openai import (ConversationHistory, InputTokenCount,
                              ModelResponse, OutputTokenCount)
from src.utils.anthropic_ai import map_openai_history_to_anthropic_history


class AnthropicModel(LLM):
    def __init__(self, model_name: str, max_tokens: int = 200000):
        super().__init__(model_name, max_tokens)
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), timeout=60)
        self.max_tokens = max_tokens

    def count_token(self, message: str) -> int:
        return self.client.count_tokens(message)

    def generate_content(self, messages: ConversationHistory) -> tuple[ConversationHistory, ModelResponse, 
                                                                       InputTokenCount, OutputTokenCount]:
        logger.debug(f"Starting chat completion with model: {self.model_name}")

        copied_messages = copy.deepcopy(messages)

        copied_messages = self.rolling_history(copied_messages)
        copied_messages = map_openai_history_to_anthropic_history(copied_messages)

        try:
            chat_completion = self.client.messages.create(
                model=self.model_name,
                messages=copied_messages,
                max_tokens=4096
            )

            response = chat_completion.content[0].text.strip()
            input_tokens = chat_completion.usage.input_tokens
            output_tokens = chat_completion.usage.output_tokens

            return copied_messages, response, input_tokens, output_tokens
        except (APITimeoutError, APIConnectionError, RateLimitError, APIStatusError) as e:
            logger.warning(f"Anthropic API error: {e}")
            sleep(3)
            return self.generate_content(messages)

    def __str__(self):
        return f"AnthropicModel(model_name={self.model_name}, max_tokens={self.max_tokens})"
