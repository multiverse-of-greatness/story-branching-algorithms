import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from huggingface_hub import hf_hub_download
from torchvision.transforms.functional import normalize

from src.bg_remover.bg_removal_model import BackgroundRemovalModel
from src.bg_remover.bria_rmbg_utils import BriaRMBG, resize_image


class Bria(BackgroundRemovalModel):
    def __init__(self, ):
        self.model = BriaRMBG()
        model_path = hf_hub_download("briaai/RMBG-1.4", 'model.pth')

        if torch.cuda.is_available():
            self.model.load_state_dict(torch.load(model_path)).cuda()
        elif torch.backends.mps.is_available():
            self.model.load_state_dict(torch.load(model_path, map_location="mps"))
        else:
            self.model.load_state_dict(torch.load(model_path, map_location="cpu"))
        self.model.eval()

    def remove_background(self, image: Image) -> Image:
        w, h = image.size

        image = resize_image(image)
        im_np = np.array(image)

        im_tensor = torch.tensor(im_np, dtype=torch.float32).permute(2, 0, 1)
        im_tensor = torch.unsqueeze(im_tensor, 0)
        im_tensor = torch.divide(im_tensor, 255.0)
        im_tensor = normalize(im_tensor, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])

        if torch.cuda.is_available():
            im_tensor = im_tensor.cuda()

        result = self.model(im_tensor)

        result = torch.squeeze(F.interpolate(result[0][0], size=(h, w), mode='bilinear'), 0)
        ma = torch.max(result)
        mi = torch.min(result)
        result = (result - mi) / (ma - mi)

        im_array = (result * 255).cpu().data.numpy().astype(np.uint8)
        pil_im = Image.fromarray(np.squeeze(im_array))

        new_image = Image.new("RGBA", pil_im.size, (0, 0, 0, 0))
        new_image.paste(image, mask=pil_im)

        return new_image

    def __str__(self):
        return "Bria"
