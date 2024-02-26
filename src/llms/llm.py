from abc import ABC, abstractmethod

from loguru import logger

from src.types import ConversationHistory


class LLM(ABC):

    @property
    @abstractmethod
    def encoder(self):
        pass

    @property
    @abstractmethod
    def max_tokens(self):
        pass

    def rolling_history(self, history: ConversationHistory) -> ConversationHistory:
        logger.debug(f"Starting rolling history with max tokens: {self.max_tokens}")
        count_tokens = 0
        new_history = []
        for message in history:
            count_tokens += len(self.encoder.encode(message["content"]))

        if count_tokens > self.max_tokens * 0.8:  # Total tokens is over 80% of the limit
            count_tokens = 0
            for message in history[-1:3:-1]:
                count_tokens += len(self.encoder.encode(message["content"]))
                if count_tokens > self.max_tokens * 0.5:  # Rolling history until 50% of the limit
                    break
                new_history.append(message)

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
    def generate_content(self, messages: ConversationHistory) -> tuple[str, dict]:
        pass

    @abstractmethod
    def __str__(self):
        pass
