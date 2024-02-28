import os

from loguru import logger
from openai import OpenAI

from src.image_gen.image_gen_model import ImageGenModel
from ..types.image_gen import ImageShape


class DALL_E_3(ImageGenModel):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=60)

    def generate_image_from_text_prompt(self, prompt: str, shape: ImageShape = "square"):
        logger.debug(f"Generating image from prompt: {prompt}")

        size = {
            "portrait": "1024x1792",
            "landscape": "1792x1024",
            "square": "1024x1024"
        }

        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size[shape],
            quality="hd",
            n=1,
            response_format="b64_json"
        )

        return response.data[0].b64_json

    def __str__(self):
        return "DALL_E_3"
