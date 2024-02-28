from abc import ABC, abstractmethod

from PIL import Image


class BackgroundRemovalModel(ABC):
    @abstractmethod
    def remove_background(self, image: Image) -> Image:
        pass
