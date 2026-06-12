from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import config

_processor: BlipProcessor | None = None
_model: BlipForConditionalGeneration | None = None


def _load_models() -> None:
    global _processor, _model
    if _processor is None:
        _processor = BlipProcessor.from_pretrained(config.BLIP_MODEL)
        _model = BlipForConditionalGeneration.from_pretrained(config.BLIP_MODEL)
        _model.eval()


def generate_caption(image: Image.Image) -> str:
    _load_models()
    inputs = _processor(images=image, return_tensors="pt")
    with torch.no_grad():
        output = _model.generate(**inputs, max_new_tokens=50)
    return _processor.decode(output[0], skip_special_tokens=True)
