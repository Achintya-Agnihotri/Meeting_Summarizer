from backend.transcription import _get_whisper_model


def test_whisper_model_loader_is_cached(monkeypatch) -> None:
    created = []

    class FakeWhisperModel:
        def __init__(self, *args, **kwargs) -> None:
            created.append((args, kwargs))

    monkeypatch.setattr("faster_whisper.WhisperModel", FakeWhisperModel)
    _get_whisper_model.cache_clear()
    first = _get_whisper_model("base", "local_models/whisper", 4, 2)
    second = _get_whisper_model("base", "local_models/whisper", 4, 2)
    assert first is second
    assert len(created) == 1
    _get_whisper_model.cache_clear()
