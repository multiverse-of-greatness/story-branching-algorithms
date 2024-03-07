import os

import requests
from loguru import logger

from src.image_gen.image_gen_model import ImageGenModel
from ..types.image_gen import ImageShape


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
            "negative_prompt": "multiple people, poorly Rendered face, poorly drawn face, poor facial details, poorly drawn hands, poorly rendered hands, low resolution, blurry image, oversaturated, bad anatomy, signature, watermark, username, error, missing limbs, error, out of frame, extra fingers, mutated hands, poorly drawn hands, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck, username, bad face",
            "width": size[shape]["width"],
            "height": size[shape]["height"],
            "steps": 30
        })

        return response.json().get("images")[0]

    def __str__(self):
        return "LocalStableDiffusionModel"
