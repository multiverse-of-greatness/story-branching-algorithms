import unittest

from src.utils import format_openai_message


class FormatOpenAIMessageTest(unittest.TestCase):
    def test_format_openai_message_empty_list_default_arguments(self):
        expected = [{"role": "user", "content": ""}]
        actual = format_openai_message("")

        self.assertListEqual(expected, actual)

    def test_format_openai_message_empty_list_custom_arguments_assistant(self):
        expected = [{"role": "assistant", "content": ""}]
        actual = format_openai_message("", "assistant")

        self.assertListEqual(expected, actual)

    def test_format_openai_message_non_empty_list_default_argument_role(self):
        expected = [{"role": "user", "content": "Hello"}, {"role": "user", "content": "Hi"}]
        actual = format_openai_message("Hi", history=[{"role": "user", "content": "Hello"}])

        self.assertListEqual(expected, actual)

    def test_format_openai_message_non_empty_list_custom_arguments_system(self):
        expected = [{"role": "system", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]
        actual = format_openai_message("Hi", "assistant", [{"role": "system", "content": "Hello"}])

        self.assertListEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
