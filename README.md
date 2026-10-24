# CrimeVision AI

CrimeVision AI is an end-to-end multimodal forensic analysis platform that helps investigators process images, audio, and video, extract evidence, and build a chronological intelligence timeline.

The project is designed to be modular, beginner-friendly, and scalable. The codebase is structured around FastAPI backend services, ML analysis modules, a Streamlit dashboard, and PDF reporting.

## Core principles

- Preserve timestamps and evidence provenance.
- Distinguish observation from inference.
- Treat AI outputs as investigative leads, not proven facts.
- Keep database records append-only and auditable.
- Keep unverified model output visibly separate from reviewed findings.

## Project structure

```text
crimevision-ai/
├── app/
│   ├── api/
│   │   ├── audio.py
│   │   ├── cases.py
│   │   ├── chat.py
│   │   ├── images.py
│   │   ├── reports.py
│   │   ├── timeline.py
│   │   └── video.py
│   ├── core/
│   │   ├── database.py
│   │   ├── provenance.py
│   │   ├── schemas.py
│   │   └── __init__.py
│   ├── modules/
│   │   ├── audio_analysis/
│   │   │   ├── event_extractor.py
│   │   │   ├── transcriber.py
│   │   │   └── __init__.py
│   │   ├── chat/
│   │   │   ├── qa_engine.py
│   │   │   ├── retriever.py
│   │   │   └── __init__.py
│   │   ├── fusion/
│   │   │   ├── evidence_store.py
│   │   │   ├── timeline_fusion.py
│   │   │   └── __init__.py
│   │   ├── image_analysis/
│   │   │   ├── captioner.py
│   │   │   ├── detector.py
│   │   │   ├── hypotheses.py
│   │   │   └── __init__.py
│   │   ├── reports/
│   │   │   ├── pdf_generator.py
│   │   │   └── templates/
│   │   ├── video_analysis/
│   │   │   ├── action_recognizer.py
│   │   │   ├── frame_sampler.py
│   │   │   ├── timeline_builder.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── config.py
│   ├── main.py
│   └── __init__.py
├── dashboard/
│   ├── app.py
│   └── pages/
├── data/
│   ├── db/
│   ├── processed/
│   ├── reports/
│   └── uploads/
├── docs/
│   └── architecture.md
├── models/
├── notebooks/
├── scripts/
│   ├── run.sh
│   └── setup.sh
├── tests/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── create_structure.py
└── README.md
```

## Build roadmap

| Stage | Current state |
|---|---|
| Foundation | FastAPI, case/evidence storage, upload hashing, and audit log are implemented. |
| Image analysis | YOLO object detection, BLIP captioning, EXIF capture-time reading, and rule-based hypotheses are wired. Actual model inference still needs validation with real, consented test media. |
| Audio analysis | faster-whisper transcription is wired to evidence records; segment start/end times are persisted as unverified observations. |
| Video analysis | Video frames are sampled into processed files and YOLO detections retain source-relative frame timestamps. Action recognition is not implemented yet. |
| Timeline | Findings are grouped by evidence and sorted by media-relative time. Cross-file incident chronology needs verified time alignment; upload time is not treated as incident time. |
| Chat | Case-scoped lexical retrieval answers from stored findings and returns evidence citations; this is not an LLM or legal conclusion. |
| Reports | Case-specific PDF reports include hashes, findings, provenance, and the disclaimer. |
| Dashboard | Streamlit pages are connected to the API for upload, analysis, timeline, chat, and PDF download. |
| Deployment | Docker configuration, security hardening, and production deployment still need validation. |

## Local working directory

Use this folder directly as your main project root:

`c:\Projects\crimevision-ai`

If you want a Google Drive mirror, keep the same folder synced to Drive from your Windows machine. The project structure is already designed to work from that local path.

## Recommended tools and models

- FastAPI + SQLAlchemy + SQLite for the backend
- Streamlit for the dashboard
- OpenCV + Pillow for frame and image processing
- Ultralytics YOLO for object detection
- Transformers + Whisper for language tasks
- ReportLab for PDF generation

The first analysis request may download model weights. YOLO uses `yolov8n.pt` by default; BLIP and faster-whisper model assets may also require an internet connection and additional disk space. CPU inference can be slow.

## Run locally on Windows

Open two terminals in `C:\Projects\crimevision-ai`. For the existing environment at `C:\Projects\venv`, activate it in each terminal:

```powershell
..\venv\Scripts\Activate.ps1
```

Install the project dependencies into that active environment once:

```powershell
python -m pip install -r requirements.txt
```

Terminal 1 - API:

```powershell
python -m uvicorn app.main:app --reload
```

API documentation: http://127.0.0.1:8000/docs

Terminal 2 - dashboard:

```powershell
python -m streamlit run dashboard/app.py
```

Dashboard: http://localhost:8501

Run the tests:

```powershell
python -m pytest -q
```

The dashboard uses `CRIMEVISION_API_URL` if set; otherwise it connects to `http://127.0.0.1:8000`.

## Current API workflows

- Create case: `POST /cases`
- Upload evidence: `POST /cases/{case_id}/evidence`
- Analyze image: `POST /evidence/{evidence_id}/analyze-image`
- Transcribe audio: `POST /evidence/{evidence_id}/transcribe-audio`
- Analyze video frames: `POST /evidence/{evidence_id}/analyze-video`
- Review findings: `GET /cases/{case_id}/findings`
- View timeline: `GET /cases/{case_id}/timeline`
- Ask about findings: `POST /cases/{case_id}/chat`
- Generate PDF: `POST /cases/{case_id}/report`

## Important safety rule

AI outputs are investigative leads and should never be treated as verified facts. Every model prediction should retain provenance and be clearly separated into observations and inferences.

## Important limitations

- The software is a student project prototype, not a validated forensic product.
- Model outputs can be wrong or incomplete; human review is required.
- The video workflow currently detects objects in sampled frames, not actions.
- A relative timestamp such as `12.4s` is measured from that media file, not a verified wall-clock time.
- No authentication, role-based access control, chain-of-custody certification, or production security review is included yet.
