import torch.backends.mps
from diffusers import StableCascadePriorPipeline, StableCascadeDecoderPipeline
from diffusers.pipelines.wuerstchen import DEFAULT_STAGE_C_TIMESTEPS
from loguru import logger

from src.image_gen.image_gen_model import ImageGenModel
from src.prompts.image_prompts import get_negative_image_prompt
from src.types.image_gen import ImageShape
from src.utils.general import get_base64_from_image


class StableCascade(ImageGenModel):
    def __init__(self):
        device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.prior_pipeline = StableCascadePriorPipeline.from_pretrained(
            "stabilityai/stable-cascade-prior"
        ).to(device)
        self.decoder_pipeline = StableCascadeDecoderPipeline.from_pretrained(
            "stabilityai/stable-cascade"
        ).to(device)
        self.generator = torch.Generator(device=device)

    def _generate_image(self, prompt: str, negative_prompt: str, width: int, height: int, prior_steps: int = 20,
                        decoder_steps: int = 10, prior_guidance_scale: float = 4.0,
                        decoder_guidance_scale: float = 0.0):
        prior_output = self.prior_pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            height=width,
            width=height,
            num_inference_steps=prior_steps,
            timesteps=DEFAULT_STAGE_C_TIMESTEPS,
            guidance_scale=prior_guidance_scale,
            num_images_per_prompt=1,
            generator=self.generator,
        )
        decoder_output = self.decoder_pipeline(
            image_embeddings=prior_output.image_embeddings,
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=decoder_steps,
            guidance_scale=decoder_guidance_scale,
            generator=self.generator,
            output_type="pil",
        )

        return decoder_output.images[0]

    def generate_image_from_text_prompt(self, prompt: str, shape: ImageShape = "square"):
        logger.debug(f"Generating image from prompt: {prompt}")

        size = {
            "portrait": {
                'width': 1024,
                'height': 1536
            },
            "landscape": {
                'width': 1536,
                'height': 1024
            },
            "square": {
                'width': 1024,
                'height': 1024
            }
        }

        response = self._generate_image(prompt, get_negative_image_prompt(), size[shape]['width'],
                                        size[shape]['height'])
        converted_response = get_base64_from_image(response)

        return converted_response

    def __str__(self):
        return "StableCascade"
