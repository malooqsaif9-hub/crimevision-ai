# Architecture overview

## System flow

1. The user creates a case in the Streamlit dashboard or FastAPI.
2. Evidence uploads are saved under a case-specific directory; the server records a SHA-256 hash and metadata.
3. A modality-specific endpoint validates evidence type and verifies the stored hash before processing.
4. Analysis findings retain case/evidence identifiers, model metadata, finding type, and source time where available.
5. Findings are persisted in SQLite and logged in the append-only audit table.
6. The case timeline groups findings by source file and sorts each file's events by media-relative time.
7. Chat uses lexical retrieval over saved findings and returns citations.
8. The PDF report includes case metadata, evidence hashes, findings, model provenance, and the review disclaimer.

## Main components

- `app/core`: Pydantic schemas, SQLAlchemy persistence, upload hashing, and integrity verification.
- `app/api`: FastAPI endpoints for cases, evidence, analysis, findings, timelines, chat, and reports.
- `app/modules/image_analysis`: YOLO detections, BLIP captions, EXIF capture-time metadata, and rule-based hypotheses.
- `app/modules/audio_analysis`: faster-whisper transcript segments and timestamp-preserving finding conversion.
- `app/modules/video_analysis`: OpenCV frame sampling to processed files and YOLO detections per sampled frame.
- `app/modules/fusion`: timeline utilities and evidence storage primitives.
- `app/modules/chat`: lexical retrieval and citation-based answers, scoped to the selected case.
- `app/modules/reports`: PDF generation.
- `dashboard`: Streamlit pages using the HTTP API.

## Time semantics

Audio and video timestamps are relative to the source media. The API does not infer real-world incident time from file upload time. The timeline groups items by evidence and sorts within each file; cross-file chronology needs reliable capture-time data or reviewer-confirmed offsets. EXIF times are camera-reported, timezone-naive, and editable.

## Provenance and interpretation rules

- Original evidence is not used as a processing output; sampled and annotated artifacts go under `data/processed`.
- The integrity endpoint hashes the stored file and compares it with the upload hash.
- Every analysis finding links to its source evidence.
- Direct model outputs are labeled observations; rule-based hypotheses are labeled inferences.
- Findings default to `unverified_lead`.
- AI output is not proof of guilt or proof that a crime occurred.

## Current limitations and next work

- Video action recognition is not implemented; sampled frames currently receive object detection only.
- Chat uses simple lexical search, not a vector database or generative language model.
- The automated model tests mock inference; model weights and real media still require local validation.
- Authentication, access controls, formal chain-of-custody procedures, model validation, and deployment hardening are still required before any operational use.
