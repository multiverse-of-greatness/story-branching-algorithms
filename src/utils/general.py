import base64
import json
import re
from io import BytesIO

from PIL import Image


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


def get_image_from_base64(b64: str) -> Image:
    image = base64.b64decode(b64)
    return Image.open(BytesIO(image))


def get_base64_from_image(image: Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
