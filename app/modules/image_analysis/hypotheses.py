from app.core.schemas import Finding, FindingType

# COCO-trained YOLO only knows knife, baseball bat and scissors.
# Firearm labels are included for when you plug in a custom weapon model.
WEAPON_LIKE = {"knife", "baseball bat", "scissors", "gun", "pistol", "rifle", "firearm"}

MODEL_NAME = "rule_based_hypothesis"
MODEL_VERSION = "v1"


def _near(obj_bbox, person_bbox, margin: float = 0.25) -> bool:
    """True if the centre of obj_bbox lies inside the person box expanded by margin."""
    px1, py1, px2, py2 = person_bbox
    w, h = px2 - px1, py2 - py1
    x1, y1, x2, y2 = px1 - w * margin, py1 - h * margin, px2 + w * margin, py2 + h * margin
    cx, cy = (obj_bbox[0] + obj_bbox[2]) / 2, (obj_bbox[1] + obj_bbox[3]) / 2
    return x1 <= cx <= x2 and y1 <= cy <= y2


def _inference(case_id, evidence_id, label, description, bbox=None) -> Finding:
    return Finding(
        case_id=case_id, evidence_id=evidence_id,
        finding_type=FindingType.INFERENCE,
        label=label, description=description, bbox=bbox,
        model_name=MODEL_NAME, model_version=MODEL_VERSION,
    )


def generate_hypotheses(detections: list[Finding], case_id: str, evidence_id: str) -> list[Finding]:
    people = [d for d in detections if d.label.lower() == "person" and d.bbox]
    weapons = [d for d in detections if d.label.lower() in WEAPON_LIKE and d.bbox]
    out: list[Finding] = []

    if not detections:
        out.append(_inference(
            case_id, evidence_id, "hypothesis:no_detections",
            "No objects were detected above the confidence threshold. This does not mean "
            "nothing is present: small, dark, blurred or partly hidden items are often missed."))

    for w in weapons:
        close = [p for p in people if _near(w.bbox, p.bbox)]
        if close:
            desc = (f"Possible lead: a '{w.label}'-class object (detector confidence "
                    f"{w.confidence:.0%}) was found close to a person (detector confidence "
                    f"{close[0].confidence:.0%}). Detectors often confuse tools, utensils and "
                    f"everyday items with weapons, and proximity in a 2D image does not show "
                    f"possession or use. Human review required. Based on findings "
                    f"{w.finding_id} and {close[0].finding_id}.")
            label = "hypothesis:weapon_like_object_near_person"
        else:
            desc = (f"Possible lead: a '{w.label}'-class object (detector confidence "
                    f"{w.confidence:.0%}) appears with no person detected nearby. It may be a "
                    f"misclassification. Human review required. Based on finding {w.finding_id}.")
            label = "hypothesis:weapon_like_object_alone"
        out.append(_inference(case_id, evidence_id, label, desc, bbox=w.bbox))

    if len(people) >= 3:
        out.append(_inference(
            case_id, evidence_id, "hypothesis:group_scene",
            f"{len(people)} people were detected. This may be a group or crowd scene. "
            "Relationships, roles and intent cannot be determined from detections alone."))

    return out
