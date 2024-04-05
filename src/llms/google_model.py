import copy
import os
from time import sleep

import google.generativeai as genai
from google.ai.generativelanguage_v1beta import Content
from google.api_core.exceptions import (DeadlineExceeded, InternalServerError,
                                        ServiceUnavailable, TooManyRequests)
from google.generativeai.types import HarmBlockThreshold, HarmCategory
from loguru import logger

from src.llms.llm import LLM
from src.types.openai import ConversationHistory, ModelResponse, InputTokenCount, OutputTokenCount
from src.utils.google_ai import (map_google_history_to_openai_history,
                                 map_openai_history_to_google_history)

safety_settings={
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
}


class GoogleModel(LLM):
    def __init__(self, model_name: str, max_tokens: int = 32768):
        super().__init__(model_name, max_tokens)
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.client = genai.GenerativeModel(self.model_name)

    def count_token(self, message: str) -> int:
        count = genai.GenerativeModel(self.model_name).count_tokens(message).total_tokens
        return count

    @staticmethod
    def get_history_message(messages: list[Content]) -> str:
        history = ""
        for message in messages:
            history += f"{message.parts[0].text} "
        return history

    def generate_content(self, messages: ConversationHistory) -> tuple[ConversationHistory, ModelResponse, 
                                                                       InputTokenCount, OutputTokenCount]:
        logger.debug(f"Starting chat completion with model: {self.model_name}")

        copied_messages: ConversationHistory = copy.deepcopy(messages)
        copied_messages = self.rolling_history(copied_messages)
        last_message = copied_messages.pop()
        if last_message["role"] == "system" or last_message["role"] == "assistant":
            raise ValueError(f"Last message role is not user: {last_message['role']}")
        current_message = last_message["content"]

        copied_messages = map_openai_history_to_google_history(copied_messages)
        chat = self.client.start_chat(history=copied_messages)

        try:
            chat_completion = chat.send_message(current_message, safety_settings=safety_settings)

            response = chat_completion.text.strip()

            copied_messages = copied_messages + map_openai_history_to_google_history([last_message])
            prompt_tokens = self.count_token(self.get_history_message(copied_messages))
            response_tokens = self.count_token(response)

            return map_google_history_to_openai_history(copied_messages), response, prompt_tokens, response_tokens
        except (ServiceUnavailable, InternalServerError, TooManyRequests, DeadlineExceeded) as e:
            logger.warning(f"Google API error: {e}")
            sleep(3)
            return self.generate_content(messages)

    def __str__(self):
        return f"GoogleModel(model_name={self.model_name}, max_tokens={self.max_tokens})"
