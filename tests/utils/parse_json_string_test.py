import unittest

from src.utils.general import parse_json_string


class TestParseJsonString(unittest.TestCase):
    def test_parse_json_string_empty_string(self):
        with self.assertRaises(ValueError) as context:
            parse_json_string("")

        self.assertEqual(
            "JSON markdown block not found in the message. Please use the following format:\n```json\n{...}\n```",
            str(context.exception))

    def test_parse_json_string_invalid_json(self):
        with self.assertRaises(ValueError) as context:
            parse_json_string("```json\n{...}\n```")

        self.assertEqual("Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
                         str(context.exception))

    def test_parse_json_string_text_only(self):
        with self.assertRaises(ValueError) as context:
            parse_json_string("text only")

        self.assertEqual(
            "JSON markdown block not found in the message. Please use the following format:\n```json\n{...}\n```",
            str(context.exception))

    def test_parse_json_string_valid_json(self):
        expected = {"key": "value"}
        actual = parse_json_string("```json\n{\"key\": \"value\"}\n```")

        self.assertDictEqual(expected, actual)

    def test_parse_json_string_multiple_json(self):
        expected = {"key2": "value2"}
        actual = parse_json_string("```json\n{\"key1\": \"value1\"}\n```\n```json\n{\"key2\": \"value2\"}\n```")

        self.assertDictEqual(expected, actual)

    def test_parse_json_string_multiple_json_mixed_with_string(self):
        expected = {"key2": "value2"}
        actual = parse_json_string(
            "some text\n```json\n{\"key1\": \"value1\"}\n```\nmore text\n```json\n{\"key2\": \"value2\"}\n```")

        self.assertDictEqual(expected, actual)

    def test_parse_json_string_mixed_json(self):
        expected = {"key1": "value1"}
        actual = parse_json_string("some text\n```json\n{\"key1\": \"value1\"}\n```\nmore text")

        self.assertDictEqual(expected, actual)

    def test_parse_json_string_complex_json(self):
        expected = {
            "title": "game title",
            "genre": "game genre",
            "themes": ["sci-fi", "fantasy", "middle-age", "utopia", "mythical creatures", "world scale"],
            "main_scenes": [
                {"id": "id", "title": "location name", "location": "where is this place",
                 "description": "describe location"}
            ],
            "main_characters": [
                {
                    "id": "id",
                    "first_name": "first name",
                    "last_name": "last name",
                    "species": "species",
                    "age": "exact age or description",
                    "role": "role of the character",
                    "background": "background story",
                    "place_of_birth": "location",
                    "physical_appearance": ["details"]
                }
            ],
            "synopsis": "synopsis",
            "chapter_synopses": [
                {"chapter": "chapter_number", "synopsis": "synopsis"}
            ],
            "beginning": "beginning of the story",
            "endings": [
                {"id": "id", "ending": "ending"}
            ]
        }
        actual = parse_json_string(
            """```json
{
    "title": "game title",
    "genre": "game genre",
    "themes": ["sci-fi", "fantasy", "middle-age", "utopia", "mythical creatures", "world scale"],
    "main_scenes": [{"id": "id", "title": "location name", "location": "where is this place", "description": "describe location"}],
    "main_characters": [{"id": "id", "first_name": "first name", "last_name": "last name", "species": "species", "age": "exact age or description", "role": "role of the character", "background": "background story", "place_of_birth": "location", "physical_appearance": ["details"]}],
    "synopsis": "synopsis",
    "chapter_synopses": [{"chapter": "chapter_number", "synopsis": "synopsis"}],
    "beginning": "beginning of the story",
    "endings": [{"id": "id", "ending": "ending"}]
}
```"""
        )

        self.assertDictEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
