# CrimeVision AI: build plan and working structure

This is the implementation map for the existing project at `C:\Projects\crimevision-ai`. Work from that folder; do not run `create_structure.py` because it creates a second nested `crimevision-ai` directory.

## How to access the project

- **On this computer:** open `C:\Projects\crimevision-ai` in VS Code, PyCharm, or File Explorer. Keep the source folders in place and launch the API/dashboard from this root.
- **Google Drive:** optionally mirror the project folder with Drive for Desktop. For privacy, keep `data/uploads`, `data/db`, `.env`, and any real case media out of shared or cloud-synced folders unless you have explicit authorization and appropriate access controls. The database and evidence files are local application data, not source code.

## Folder responsibilities

| Folder | Responsibility | Current state |
|---|---|---|
| `app/api` | HTTP endpoints for cases, evidence, modality analysis, timeline, chat, and reports | API routers; `/api/cases` is available for compatibility |
| `app/core` | Configuration-facing schemas, SQLite persistence, hashing, and provenance | Foundation implemented |
| `app/modules/image_analysis` | Image metadata, object detections, captions, and cautious hypotheses | Model-backed prototype; downloads/weights required |
| `app/modules/audio_analysis` | Timestamped transcription and event conversion | faster-whisper prototype |
| `app/modules/video_analysis` | Frame sampling and source-relative timestamps | Object detection per sampled frame; action recognition is future work |
| `app/modules/fusion` | Cross-media evidence/timeline helpers | Extend after each modality is stable |
| `app/modules/chat` | Case-scoped retrieval and evidence citations | Lexical retrieval prototype |
| `app/modules/reports` | PDF report generation | Implemented prototype |
| `dashboard` | Streamlit user interface | Upload, analysis, timeline, chat, and report pages |
| `data/uploads` | Immutable original uploads | Runtime data; preserve |
| `data/processed` | Derived frames and annotations | Runtime data; regenerable but may be useful |
| `data/db` | SQLite cases, evidence metadata, findings, and audit entries | Runtime data; preserve |
| `data/reports` | Generated PDF reports | Runtime output; preserve unless deliberately archived |
| `models` | Optional local model weights | Keep model files out of source control |
| `tests` | Automated tests and mocked model workflows | Existing coverage |
| `docs` | Architecture, setup, and implementation notes | Project documentation |

## Development sequence

1. **Make the foundation reproducible:** create a virtual environment, install dependencies, initialize the database, and start the API and dashboard.
2. **Stabilize case/evidence handling:** verify upload, SHA-256 integrity, append-only audit events, and evidence retrieval.
3. **Harden image analysis:** validate actual image files, keep annotations separate from originals, and record model/version provenance.
4. **Harden audio analysis:** transcribe supported formats and preserve segment start/end times.
5. **Harden video analysis:** sample frames with media-relative times, then add action recognition only as a separate, clearly labeled inference.
6. **Unify findings:** add reviewer-confirmed time offsets only when supported by source metadata or documented review; never infer incident time from upload time.
7. **Finish the dashboard, chat, and reports:** ensure each view stays case-scoped and shows source evidence, timestamps, review status, and limitations.
8. **Deploy only after review:** add authentication, authorization, secure storage, retention rules, audit protection, and model validation before handling real investigations.

## Safe interpretation and evidence rules

- Original media is immutable; derived artifacts belong in `data/processed`.
- Every output must retain its `case_id`, `evidence_id`, model identity, and source-relative timestamp when available.
- Model outputs begin as `unverified_lead`. Keep direct observations separate from inferences and reviewer-confirmed findings.
- A generated description or hypothesis is an investigative lead. AI output alone does not establish guilt or prove that a crime occurred.
- The prototype is not a validated forensic product and should use synthetic or explicitly authorized media during development.

## Windows launch commands

Run these from `C:\Projects\crimevision-ai` in two PowerShell terminals. If the existing environment at `C:\Projects\venv` is present, activate it with `..\venv\Scripts\Activate.ps1`; otherwise create a local environment with `python -m venv .venv` and activate `.\.venv\Scripts\Activate.ps1`.

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

In the second terminal:

```powershell
python -m streamlit run dashboard/app.py
```

The API is at `http://127.0.0.1:8000` and its interactive docs are at `/docs`. The dashboard is at `http://localhost:8501`. Large vision and speech model packages/weights may take substantial time and disk space; first inference can require internet access to fetch model files.

## Triage when startup fails

1. Confirm the terminal is in `C:\Projects\crimevision-ai`, not the `.pytest_cache` subfolder.
2. Check that the selected Python environment is activated and has the project dependencies installed.
3. Start the API first and open `/health`; then start the dashboard.
4. Set `CRIMEVISION_API_URL` only when the API is hosted somewhere other than `http://127.0.0.1:8000`.
5. Read the full traceback. Missing optional model packages/weights affect analysis endpoints; they should not prevent basic case management and health checks from starting.

