from fastapi.testclient import TestClient
from backend.main import app
client = TestClient(app)

def test_health_endpoint() -> None:
    assert client.get("/health").json() == {"status": "ok"}

def test_rejects_unsupported_audio_type() -> None:
    response = client.post("/summarize", files={"audio": ("notes.txt", b"hello", "text/plain")})
    assert response.status_code == 415
    assert "Unsupported audio type" in response.json()["detail"]

def test_rejects_empty_upload() -> None:
    response = client.post("/summarize", files={"audio": ("meeting.wav", b"", "audio/wav")})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()
