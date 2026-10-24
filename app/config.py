import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
REPORT_DIR = DATA_DIR / "reports"
DB_DIR = DATA_DIR / "db"
DB_FILE = (DB_DIR / "crimevision.db").resolve()
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DB_FILE.as_posix()}"
APP_NAME = os.getenv("APP_NAME", "CrimeVision AI")

DISCLAIMER = (
    "All outputs are AI-generated investigative leads requiring human verification. "
    "They do not establish guilt or prove that a crime occurred."
)

for d in (UPLOAD_DIR, PROCESSED_DIR, REPORT_DIR, DB_DIR):
    d.mkdir(parents=True, exist_ok=True)