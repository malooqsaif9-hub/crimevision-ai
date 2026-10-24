import hashlib
import shutil
from pathlib import Path
from fastapi import UploadFile

from app.config import UPLOAD_DIR
from app.core.schemas import EvidenceFile, MediaType

EXT_TO_TYPE = {
    ".jpg": MediaType.IMAGE, ".jpeg": MediaType.IMAGE, ".png": MediaType.IMAGE,
    ".bmp": MediaType.IMAGE, ".webp": MediaType.IMAGE,
    ".mp3": MediaType.AUDIO, ".wav": MediaType.AUDIO, ".m4a": MediaType.AUDIO,
    ".flac": MediaType.AUDIO, ".ogg": MediaType.AUDIO,
    ".mp4": MediaType.VIDEO, ".avi": MediaType.VIDEO, ".mov": MediaType.VIDEO,
    ".mkv": MediaType.VIDEO, ".webm": MediaType.VIDEO,
}


def sha256_of_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def detect_media_type(filename: str) -> MediaType:
    if not filename or not filename.strip():
        raise ValueError("Missing file name")
    ext = Path(filename).suffix.lower()
    if ext not in EXT_TO_TYPE:
        raise ValueError(f"Unsupported file type: {ext}")
    return EXT_TO_TYPE[ext]


def save_evidence(upload: UploadFile, case_id: str, uploaded_by: str = "system") -> EvidenceFile:
    """Save the original file, hash it, and return its evidence record."""
    if not case_id or not case_id.strip():
        raise ValueError("Case ID is required")

    safe_name = Path(upload.filename).name if upload.filename else ""
    if not safe_name:
        raise ValueError("Missing file name")

    media_type = detect_media_type(safe_name)
    case_dir = UPLOAD_DIR / case_id
    case_dir.mkdir(parents=True, exist_ok=True)

    tmp_path = case_dir / f"_tmp_{safe_name}"
    try:
        with open(tmp_path, "wb") as out:
            shutil.copyfileobj(upload.file, out)

        record = EvidenceFile(
            case_id=case_id,
            original_filename=safe_name,
            stored_path="",
            media_type=media_type,
            sha256=sha256_of_file(tmp_path),
            size_bytes=tmp_path.stat().st_size,
            uploaded_by=uploaded_by,
        )
        final_path = case_dir / f"{record.evidence_id}{Path(safe_name).suffix.lower()}"
        tmp_path.rename(final_path)
        try:
            final_path.chmod(0o444)  # read-only: originals are never modified
        except (PermissionError, OSError):
            pass
        record.stored_path = final_path.as_posix()
        return record
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def verify_integrity(record: EvidenceFile) -> bool:
    """Re-hash the stored file and compare to the hash taken at upload."""
    if not record.stored_path:
        return False
    p = Path(record.stored_path)
    if not p.exists() or not p.is_file():
        return False
    try:
        return sha256_of_file(p) == record.sha256
    except OSError:
        return False