from src.image_gen.dall_e_three import DallEThree
from src.image_gen.image_gen_model import ImageGenModel
from src.image_gen.local_sd import LocalStableDiffusionModel
from src.llms.anthropic_model import AnthropicModel
from src.llms.google_model import GoogleModel
from src.llms.llm import LLM
from src.llms.openai_model import OpenAIModel


def get_generation_model(model_name: str) -> LLM:
    if model_name in ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview"]:
        return OpenAIModel(model_name)
    elif model_name in ["gemini-1.0-pro"]:
        return GoogleModel(model_name)
    elif model_name in ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-2.1"]:
        return AnthropicModel(model_name)
    else:
        raise ValueError(f"Unknown generation model: {model_name}")


def get_image_generation_model(model_name: str) -> ImageGenModel:
    if model_name in ["dall-e-3"]:
        return DallEThree()
    elif model_name in ['local-sd']:
        return LocalStableDiffusionModel()
    else:
        raise ValueError(f"Unknown image generation model: {model_name}")
