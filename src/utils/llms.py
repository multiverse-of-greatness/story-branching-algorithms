from src.llms.google_model import GoogleModel
from src.llms.llm import LLM
from src.llms.openai_model import OpenAIModel


def get_generation_model(model_name: str) -> LLM:
    if model_name in ["gpt-3.5-turbo-0125", "gpt-4-turbo-preview"]:
        return OpenAIModel(model_name)
    elif model_name in ["gemini-1.0-pro"]:
        return GoogleModel(model_name)
    else:
        raise ValueError(f"Unknown generation model: {model_name}")
