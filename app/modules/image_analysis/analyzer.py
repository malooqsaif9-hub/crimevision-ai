from pathlib import Path

from app.config import PROCESSED_DIR
from app.core.schemas import EvidenceFile, Finding
from app.modules.image_analysis.captioner import caption_image
from app.modules.image_analysis.detector import detect_objects
from app.modules.image_analysis.exif_reader import exif_findings
from app.modules.image_analysis.hypotheses import WEAPON_LIKE, generate_hypotheses


def annotated_path(case_id: str, evidence_id: str) -> Path:
    return PROCESSED_DIR / case_id / f"{evidence_id}_annotated.jpg"


def save_annotated(src: str, detections: list[Finding], case_id: str, evidence_id: str) -> Path:
    """Draw boxes on a COPY. The original evidence file is never touched."""
    from PIL import Image, ImageDraw
    img = Image.open(src).convert("RGB")
    draw = ImageDraw.Draw(img)
    for f in detections:
        if not f.bbox:
            continue
        color = "red" if f.label.lower() in WEAPON_LIKE else "lime"
        draw.rectangle(f.bbox, outline=color, width=3)
        draw.text((f.bbox[0] + 3, f.bbox[1] + 3), f"{f.label} {f.confidence:.0%}", fill=color)
    out = annotated_path(case_id, evidence_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def analyze_image(evidence: EvidenceFile) -> list[Finding]:
    path, cid, eid = evidence.stored_path, evidence.case_id, evidence.evidence_id
    findings: list[Finding] = []
    findings += exif_findings(path, cid, eid)
    detections = detect_objects(path, cid, eid)
    findings += detections
    findings += caption_image(path, cid, eid)
    findings += generate_hypotheses(detections, cid, eid)
    save_annotated(path, detections, cid, eid)
    return findings
