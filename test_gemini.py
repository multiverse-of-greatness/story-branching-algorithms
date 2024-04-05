from pathlib import Path

import ujson
from dotenv import load_dotenv

from src.llms.google_model import GoogleModel
from src.models.story_data import StoryData
from src.prompts.utility_prompts import get_fix_invalid_json_prompt
from src.utils.openai_ai import append_openai_message


def main():
    gemini = GoogleModel("gemini-1.0-pro")
    story_id = "0bab26e8-f32d-11ee-acea-701ab8224821"
    story_path = Path("outputs") / "proposed" / story_id
    with open(story_path / "gemini-1.0-pro.json", 'r') as file:
        content = ujson.load(file)
    last_response = content["responses"][-1]
    error_msg = f"""main_characters.0.age
  Input should be a valid string [type=string_type, input_value=16, input_type=int]
main_characters.1.age
  Input should be a valid string [type=string_type, input_value=17, input_type=int]
main_characters.2.age
  Input should be a valid string [type=string_type, input_value=35, input_type=int]
main_characters.3.age
  Input should be a valid string [type=string_type, input_value=45, input_type=int]
main_characters.4.age
  Input should be a valid string [type=string_type, input_value=200, input_type=int]"""
    prompt = get_fix_invalid_json_prompt(last_response, error_msg)
    history = append_openai_message(prompt)
    story_data_raw, story_data_obj = gemini.generate_content(None, history)
    print(story_data_raw)
    story_data_obj["id"] = story_id
    story_data_obj["generated_by"] = "gemini-1.0-pro"
    story_data_obj["approach"] = "proposed"
    story_data = StoryData.model_validate(story_data_obj)
    print(story_data)


if __name__ == "__main__":
    load_dotenv()
    main()
