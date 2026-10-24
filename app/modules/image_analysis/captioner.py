from functools import lru_cache
from PIL import Image

from app.core.schemas import Finding, FindingType

MODEL_ID = "Salesforce/blip-image-captioning-base"


@lru_cache(maxsize=1)
def _load():
    from transformers import BlipProcessor, BlipForConditionalGeneration
    processor = BlipProcessor.from_pretrained(MODEL_ID)
    model = BlipForConditionalGeneration.from_pretrained(MODEL_ID)
    model.eval()
    return processor, model


def caption_image(image_path: str, case_id: str, evidence_id: str) -> list[Finding]:
    import torch
    processor, model = _load()
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=40)
    text = processor.decode(out[0], skip_special_tokens=True).strip()
    return [Finding(
        case_id=case_id, evidence_id=evidence_id,
        finding_type=FindingType.OBSERVATION,
        label="scene_caption",
        description=f"{text} (Automatic caption; may be inaccurate or miss details.)",
        model_name=MODEL_ID, model_version="transformers",
    )]
