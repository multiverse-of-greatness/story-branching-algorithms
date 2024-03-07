import os

import requests
from loguru import logger

from src.image_gen.image_gen_model import ImageGenModel
from src.prompts.image_prompts import get_negative_image_prompt
from src.types.image_gen import ImageShape


class LocalStableDiffusionModel(ImageGenModel):
    def __init__(self):
        self.api_url = os.getenv("LOCAL_SD_BASE_URL")

    def generate_image_from_text_prompt(self, prompt: str, shape: ImageShape = "square"):
        logger.debug(f"Generating image from prompt: {prompt}")

        size = {
            "portrait": {
                'width': 768,
                'height': 1344
            },
            "landscape": {
                'width': 1344,
                'height': 768
            },
            "square": {
                'width': 1024,
                'height': 1024
            }
        }

        response = requests.post(self.api_url, json={
            "prompt": prompt,
            "negative_prompt": get_negative_image_prompt(),
            "width": size[shape]["width"],
            "height": size[shape]["height"],
            "steps": 30
        })

        return response.json().get("images")[0]

    def __str__(self):
        return "LocalStableDiffusionModel"
