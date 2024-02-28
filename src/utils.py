import copy
import json
import re
from pathlib import Path

import typer
from loguru import logger

from .models.story_data import StoryData
from .types.openai import OpenAIRole, ConversationHistory


def append_openai_message(message: str,
                          role: OpenAIRole = "user",
                          history: ConversationHistory = None) -> ConversationHistory:
    if history is None:
        history = []

    history = copy.deepcopy(history)

    history.append({
        "role": role,
        "content": message
    })

    return history


def parse_json_string(json_string: str) -> dict:
    if json_string.startswith("{") and json_string.endswith("}"):
        return json.loads(json_string)

    pattern = r'```(json)?\n([\s\S]*?)(?<!`)```'
    match = re.findall(pattern, json_string, re.DOTALL)

    if match is None or len(match) == 0:
        raise ValueError(
            "JSON markdown block not found in the message. Please use the following format:\n```json\n{...}\n```")

    json_string = match[-1][-1].strip()
    return json.loads(json_string)


def validate_existing_plot(existing_plot_path: str):
    if existing_plot_path and not Path(existing_plot_path).exists():
        logger.error(f"Existing plot file not found: {existing_plot_path}")
        raise typer.Abort()

    if existing_plot_path:
        try:
            with open(existing_plot_path, "r") as file:
                content = json.load(file)
                story_data_obj = content["parsed"]
                StoryData.from_json(story_data_obj)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Existing plot file not valid: {existing_plot_path}")
            logger.error(e)
            raise typer.Abort()
