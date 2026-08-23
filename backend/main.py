import logging
import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .exceptions import MeetingProcessingError
from .models import HealthResponse, MeetingResult
from .summarizer import analyze_transcript
from .transcription import transcribe_audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".mpeg", ".webm"}
app = FastAPI(title="Meeting Summarizer API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8501"], allow_methods=["GET", "POST"], allow_headers=["*"])

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")

def _validate_upload(audio: UploadFile) -> str:
    filename = audio.filename or ""
    extension = Path(filename).suffix.lower()
    if not filename:
        raise HTTPException(400, "Please choose an audio file.")
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, "Unsupported audio type. Upload MP3, WAV, M4A, MP4, MPEG, or WebM.")
    return extension

@app.post("/summarize", response_model=MeetingResult)
def summarize(audio: UploadFile = File(...)) -> MeetingResult:
    """Validate, transcribe, analyze, and discard a meeting recording."""
    extension = _validate_upload(audio)
    settings = get_settings()
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            temp_path = Path(temp_file.name)
            shutil.copyfileobj(audio.file, temp_file)
        size = temp_path.stat().st_size
        if size == 0:
            raise HTTPException(400, "The uploaded file is empty.")
        if size > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(413, f"Audio exceeds the {settings.max_upload_size_mb} MB upload limit.")
        transcript = transcribe_audio(temp_path, settings)
        analysis = analyze_transcript(transcript, settings)
        return MeetingResult(transcript=transcript, **analysis.model_dump())
    except MeetingProcessingError as error:
        logger.warning("Meeting processing failed: %s", error.message)
        raise HTTPException(error.status_code, error.message) from error
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Unexpected processing failure")
        raise HTTPException(500, "We could not process this meeting. Please try again.") from error
    finally:
        audio.file.close()
        if temp_path:
            temp_path.unlink(missing_ok=True)
