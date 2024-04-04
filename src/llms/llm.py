from __future__ import annotations

from abc import ABC, abstractmethod

from loguru import logger

from src.types.openai import ConversationHistory


class LLM(ABC):
    def __init__(self, model_name: str, max_tokens: int):
        self.model_name = model_name
        self.max_tokens = max_tokens

    @staticmethod
    @abstractmethod
    def count_token(message: str) -> int:
        pass

    def rolling_history(self, history: ConversationHistory) -> ConversationHistory:
        logger.debug(f"Starting rolling history with max tokens: {self.max_tokens}")
        count_tokens = 0
        first_part_history_tokens = 0
        for i, message in enumerate(history):
            if i < 4:
                first_part_history_tokens += self.count_token(message["content"])
            count_tokens += self.count_token(message["content"])

        if count_tokens > self.max_tokens * 0.8:  # Total tokens is over 80% of the limit
            n_history = len(history)

            start_idx = n_history - 1
            new_history = []
            if history[-1]["role"] == "user":  # If the last message is user message, keep it
                new_history.append(history[-1])
                count_tokens = self.count_token(history[-1]["content"])
                start_idx = n_history - 2  # Start from the latest assistant message
            elif history[-1]["role"] == "assistant":  # If the last message is assistant message, throw an error.
                # Since this is a history used to interact with LLMs, the last message must be a user message.
                raise ValueError(f"History is not in the correct conversation format: {history[-1]['role']}")

            # Do it in reverse order
            for idx in range(start_idx, 3, -2):
                if history[idx]["role"] != "assistant" or history[idx - 1]["role"] != "user":
                    raise ValueError(f"History is not in the correct conversation format: "
                                     f"{history[idx]["role"]} {history[idx - 1]["role"]}")

                assistant_message = history[idx]
                user_message = history[idx - 1]
                count_tokens += self.count_token(assistant_message["content"]) + self.count_token(
                    user_message["content"])
                if count_tokens > self.max_tokens * 0.6 - first_part_history_tokens:  # Rolling history until 60%
                    break
                new_history.append(assistant_message)
                new_history.append(user_message)

            # Keep story data and the first story chunk
            for message in history[:4][::-1]:
                new_history.append(message)

            new_history.reverse()

            logger.debug(f"History is over token limit: {count_tokens}/{self.max_tokens}. Rolling history.")
            logger.debug(
                f"New token count: {count_tokens}. New history length: {len(new_history)}. New history: {new_history}")
            return new_history
        else:
            logger.debug(f"History is within token limit: {count_tokens}/{self.max_tokens}. No need to roll.")
            return history

    @abstractmethod
    def generate_content(self, ctx: 'GenerationContext', messages: ConversationHistory) -> tuple[str, dict]:
        pass

    @abstractmethod
    def __str__(self):
        pass
