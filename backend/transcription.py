from functools import lru_cache
from pathlib import Path

from .config import Settings
from .exceptions import MeetingProcessingError


@lru_cache(maxsize=1)
def _get_whisper_model(
    model_name: str,
    model_dir: str,
    cpu_threads: int,
    num_workers: int,
):
    """Load the model once per server process and reuse it for every upload."""
    from faster_whisper import WhisperModel

    return WhisperModel(
        model_name,
        device="cpu",
        compute_type="int8",
        download_root=model_dir,
        cpu_threads=cpu_threads,
        num_workers=num_workers,
    )


def transcribe_audio(audio_path: Path, settings: Settings) -> str:
    try:
        settings.whisper_model_dir.mkdir(parents=True, exist_ok=True)
        model = _get_whisper_model(
            settings.whisper_model,
            str(settings.whisper_model_dir),
            settings.whisper_cpu_threads,
            settings.whisper_num_workers,
        )
        segments, _ = model.transcribe(str(audio_path), vad_filter=True, beam_size=1)
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
    except ImportError as error:
        raise MeetingProcessingError("Local transcription is not installed. Run pip install -r requirements.txt.", 503) from error
    except Exception as error:
        raise MeetingProcessingError("Local transcription failed. Ensure FFmpeg is installed and the audio file is playable.", 422) from error
    if not transcript:
        raise MeetingProcessingError("No speech was detected in this recording.", 422)
    return transcript
