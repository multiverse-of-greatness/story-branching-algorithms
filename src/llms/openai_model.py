import copy
import os
from time import sleep

from loguru import logger
from openai import (APIConnectionError, APIError, APITimeoutError, OpenAI,
                    RateLimitError)
from tiktoken import encoding_for_model
from typing_extensions import Optional

from src.llms.llm import LLM
from src.models.generation_context import GenerationContext
from src.types.openai import (ConversationHistory, InputTokenCount,
                              ModelResponse, OutputTokenCount)


class OpenAIModel(LLM):
    def __init__(self, model_name: str, max_tokens: int = 16385, seed: Optional[int] = None):
        super().__init__(model_name, max_tokens)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=60)
        self.seed = seed if seed is not None else 42

    @staticmethod
    def count_token(message: str) -> int:
        encoder = encoding_for_model(os.getenv("GENERATION_MODEL"))
        return len(encoder.encode(message))

    def generate_content(self, ctx: GenerationContext, messages: ConversationHistory) -> tuple[ConversationHistory, ModelResponse, 
                                                                                               InputTokenCount, OutputTokenCount]:
        logger.debug(f"Starting chat completion with model: {self.model_name}")

        copied_messages = copy.deepcopy(messages)
        copied_messages = self.rolling_history(copied_messages)

        try:
            chat_completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=copied_messages,
                response_format={"type": "json_object"},
                seed=self.seed
            )

            response = chat_completion.choices[0].message.content.strip()
            prompt_tokens = chat_completion.usage.prompt_tokens
            completion_tokens = chat_completion.usage.completion_tokens

            return copied_messages, response, prompt_tokens, completion_tokens
        except (APITimeoutError, APIConnectionError, RateLimitError, APIError) as e:
            logger.warning(f"OpenAI API error: {e}")
            sleep(3)
            return self.generate_content(ctx, messages)

    def __str__(self):
        return f"OpenAIModel(model_name={self.model_name}, max_tokens={self.max_tokens})"
