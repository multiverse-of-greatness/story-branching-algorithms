import unittest

from src.llms.llm import LLM
from src.types.openai import ConversationHistory


class TestLLM(LLM):
    def __init__(self, max_tokens: int):
        super().__init__(max_tokens=max_tokens)

    def count_token(self, message: str) -> int:
        return len(message.split())

    def generate_content(self, ctx: 'GenerationContext', messages: ConversationHistory) -> tuple[str, dict]:
        return "generated content", {}

    def __str__(self):
        return "TestLLM"


class RollingHistoryTest(unittest.TestCase):
    def test_empty_history(self):
        expected = []
        llm = TestLLM(10)
        actual = llm.rolling_history(expected)
        self.assertListEqual(expected, actual)

    def test_no_need_to_roll(self):
        expected = [{
            "role": "user",
            "content": "1 2 3"
        }, {
            "role": "assistant",
            "content": "4 5"
        }]
        llm = TestLLM(10)
        actual = llm.rolling_history(expected)
        self.assertListEqual(expected, actual)

    def test_roll_with_valid_history(self):
        history: ConversationHistory = []
        for i in range(1, 106, 5):
            role = "user" if i % 2 == 1 else "assistant"
            history.append({"role": role, "content": f"{i} {i + 1} {i + 2} {i + 3} {i + 4}"})

        expected = history[:4] + history[-1:]
        llm = TestLLM(50)
        actual = llm.rolling_history(history)
        self.assertListEqual(expected, actual)

    def test_roll_with_invalid_history_last_message_is_assistant(self):
        history: ConversationHistory = []
        for i in range(1, 91, 5):
            role = "user" if i % 2 == 1 else "assistant"
            history.append({"role": role, "content": f"{i} {i + 1} {i + 2} {i + 3} {i + 4}"})

        llm = TestLLM(50)
        with self.assertRaises(ValueError) as context:
            llm.rolling_history(history)

        self.assertTrue("History is not in the correct conversation format: assistant" in str(context.exception))


if __name__ == "__main__":
    unittest.main()
