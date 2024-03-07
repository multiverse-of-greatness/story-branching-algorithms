from abc import ABC, abstractmethod

from src.types.image_gen import ImageShape


class ImageGenModel(ABC):
    @abstractmethod
    def generate_image_from_text_prompt(self, prompt: str, shape: ImageShape = "square"):
        pass
