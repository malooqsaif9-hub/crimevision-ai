import os
from functools import lru_cache

from app.core.schemas import Finding, FindingType
from app.modules.image_analysis.hypotheses import WEAPON_LIKE

# Set YOLO_WEIGHTS in .env to use your own trained weights (e.g. a weapon model).
WEIGHTS = os.getenv("YOLO_WEIGHTS", "yolov8n.pt")
CONF_THRESHOLD = float(os.getenv("YOLO_CONF", "0.35"))


@lru_cache(maxsize=1)
def _load_model():
    from ultralytics import YOLO   # imported lazily so the API starts fast
    return YOLO(WEIGHTS)


def _version() -> str:
    try:
        import ultralytics
        return f"ultralytics {ultralytics.__version__}"
    except Exception:
        return "unknown"


def detect_objects(image_path: str, case_id: str, evidence_id: str) -> list[Finding]:
    model = _load_model()
    result = model.predict(image_path, conf=CONF_THRESHOLD, verbose=False)[0]
    version = _version()
    findings = []
    for box in result.boxes:
        name = result.names[int(box.cls[0])]
        conf = float(box.conf[0])
        bbox = [round(float(v), 1) for v in box.xyxy[0].tolist()]
        desc = f"Detector output: '{name}' class at {conf:.0%} confidence."
        if name.lower() in WEAPON_LIKE:
            desc += " This class is on the weapon-like watchlist; detectors often confuse similar objects."
        findings.append(Finding(
            case_id=case_id, evidence_id=evidence_id,
            finding_type=FindingType.OBSERVATION,
            label=name, description=desc, confidence=round(conf, 4), bbox=bbox,
            model_name=f"yolo:{WEIGHTS}", model_version=version,
        ))
    return findings
