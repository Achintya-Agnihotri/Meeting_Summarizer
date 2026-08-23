

## Problem

Meeting recordings contain valuable context, but replaying them to find decisions and responsibilities is slow. This application makes those outcomes easier to review while keeping the transcript as the source of truth.

## Solution

```text
Audio → ASR → Transcript → LLM → Summary + Decisions + Action Items
```

## Features

- Upload MP3, WAV, M4A, MP4, MPEG, or WebM recordings.
- Local faster-whisper transcription with temporary file handling.
- Pydantic-validated structured analysis.
- Transcript-grounded decisions and action-item extraction.
- Owners and deadlines are left unspecified unless in the transcript.
- FastAPI service and Streamlit review interface.

## Architecture

```text
Audio upload
    │
    ▼
FastAPI validation + temporary storage
    │
    ▼
OpenAI transcription API ──► transcript
    │                         │
    └─────────────────────────▼
                  OpenAI structured analysis
                            │
                            ▼
             validated result returned to Streamlit
```

## Tech stack

Python, FastAPI, Uvicorn, faster-whisper, Ollama, Pydantic, Streamlit, and Pytest.

## Setup

```bash
git clone <your-repository-url>
cd Meeting_Summarizer
python -m venv .venv
```

Activate the environment (`.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on macOS/Linux), then install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. No API key is required:

```env
WHISPER_MODEL=base
WHISPER_MODEL_DIR=local_models/whisper
OLLAMA_MODEL=llama3.2:1b
```

The models are stored in `local_models/` on the D: drive. The free Whisper model downloads on the first transcription.

## Run the backend

```bash
uvicorn backend.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`; health check: `GET /health`.

## Run the frontend

In a second terminal:

```bash
streamlit run frontend/app.py
```

Open the local Streamlit URL (normally `http://localhost:8501`). Set `MEETING_API_URL` to use a different API host.

## Example output

```json
{
  "transcript": "Maya approved the launch plan. Jordan will send the final brief by Friday.",
  "summary": "The team approved the launch plan and agreed to finalize the brief.",
  "key_decisions": ["The launch plan was approved."],
  "action_items": [{"task": "Send the final brief", "owner": "Jordan", "deadline": "Friday"}]
}
```

## Testing

```bash
pytest
```

Tests cover structured-output validation and basic API input behavior without network calls.

## Limitations

Transcription quality depends on audio clarity, overlap, language support, and background noise. Local processing speed depends on your computer; the first request may be slower while Whisper downloads. Implicit responsibilities may be omitted intentionally because the application reports only transcript-supported facts.

# Meeting_Summarizer
AI meeting summarizer that converts audio into transcripts, key decisions, summaries, and actionable tasks.
