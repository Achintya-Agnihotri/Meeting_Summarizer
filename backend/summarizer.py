import json
import requests
from pydantic import ValidationError
from .config import Settings
from .exceptions import MeetingProcessingError
from .models import MeetingAnalysis
from .prompts import MEETING_ANALYSIS_INSTRUCTIONS

def analyze_transcript(transcript: str, settings: Settings) -> MeetingAnalysis:
    try:
        response = requests.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
            json={"model": settings.ollama_model, "system": MEETING_ANALYSIS_INSTRUCTIONS, "prompt": f"Meeting transcript:\n\n{transcript}", "format": MeetingAnalysis.model_json_schema(), "stream": False, "options": {"temperature": 0}},
            timeout=300,
        )
        response.raise_for_status()
        return MeetingAnalysis.model_validate(json.loads(response.json()["response"]))
    except MeetingProcessingError:
        raise
    except requests.ConnectionError as error:
        raise MeetingProcessingError("Local Ollama is not running. Start Ollama, then run: ollama pull llama3.2:1b", 503) from error
    except requests.HTTPError as error:
        raise MeetingProcessingError("Ollama could not use the selected model. Run: ollama pull llama3.2:1b", 503) from error
    except (KeyError, json.JSONDecodeError, ValidationError) as error:
        raise MeetingProcessingError("Local analysis returned invalid structured output. Please try again.") from error
