from typing import Optional
from PIL import Image

from app.core.schemas import Finding, FindingType

EXIF_IFD = 0x8769
DATETIME_ORIGINAL = 36867
DATETIME_DIGITIZED = 36868
DATETIME_BASIC = 306


def read_capture_time(image_path: str) -> Optional[tuple[str, str]]:
    """Return (tag_name, value) for the capture time stored in EXIF, if any."""
    try:
        exif = Image.open(image_path).getexif()
        ifd = exif.get_ifd(EXIF_IFD)
        for tag, name in ((DATETIME_ORIGINAL, "DateTimeOriginal"),
                          (DATETIME_DIGITIZED, "DateTimeDigitized")):
            if tag in ifd:
                return name, str(ifd[tag])
        if DATETIME_BASIC in exif:
            return "DateTime", str(exif[DATETIME_BASIC])
    except Exception:
        return None
    return None


def exif_findings(image_path: str, case_id: str, evidence_id: str) -> list[Finding]:
    found = read_capture_time(image_path)
    if not found:
        return []
    name, value = found
    return [Finding(
        case_id=case_id, evidence_id=evidence_id,
        finding_type=FindingType.OBSERVATION,
        label="exif_capture_time",
        description=(f"EXIF {name}: {value}. Camera-reported, has no timezone, "
                     "and can be edited or set wrongly. Verify independently."),
        model_name="pillow_exif", model_version="n/a",
    )]
