import base64
import json
import re
from io import BytesIO
from json.decoder import JSONDecodeError

import ujson
from PIL import Image
from pydantic import BaseModel


def json_dumps_list(data_obj: list[BaseModel]) -> str:
    return ujson.dumps([d.model_dump() for d in data_obj])


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


def get_image_from_base64(b64: str) -> Image:
    image = base64.b64decode(b64)
    return Image.open(BytesIO(image))


def get_base64_from_image(image: Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
