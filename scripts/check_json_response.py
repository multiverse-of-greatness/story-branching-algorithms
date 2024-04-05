import json
import re
from json.decoder import JSONDecodeError
from pathlib import Path

import typer
from dotenv import load_dotenv

app = typer.Typer()


def parse_json_string(json_string: str) -> dict:
    if not json_string.startswith("{") or not json_string.endswith("}"):
        pattern = r'```(json)?\n([\s\S]*?)(?<!`)```'
        match: list[tuple[str]] = re.findall(pattern, json_string, re.DOTALL)

        if match is None or len(match) == 0:
            raise ValueError(
                "JSON markdown block not found in the message. Please use the following format:\n```json\n{...}\n```")

        json_string = match[-1][-1].strip()
    try:
        return json.loads(json_string)
    except JSONDecodeError as e:
        raise ValueError(str(e))


@app.command()
def main(story_id: str):
    story_path = Path.cwd() / "outputs" / "proposed" / story_id
    with open(story_path / "gemini-1.0-pro.json", 'r') as file:
        content = json.load(file)
    last_response = content["responses"][-1]
    try:
        _ = parse_json_string(last_response)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    load_dotenv()
    app()
