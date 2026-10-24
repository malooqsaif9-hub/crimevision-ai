"""Quick check without the server:  python scripts/try_image.py path/to/photo.jpg"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.provenance import sha256_of_file
from app.core.schemas import EvidenceFile, MediaType
from app.modules.image_analysis.analyzer import analyze_image

p = Path(sys.argv[1]).resolve()
ev = EvidenceFile(case_id="demo", original_filename=p.name, stored_path=str(p),
                  media_type=MediaType.IMAGE, sha256=sha256_of_file(p),
                  size_bytes=p.stat().st_size)
for f in analyze_image(ev):
    print(f"[{f.finding_type.value:11}] {f.label:42} conf={f.confidence} | {f.description[:100]}")
print("\nAnnotated copy saved under data/processed/demo/")
