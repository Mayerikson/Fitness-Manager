import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from fitness_manager.audio import MAX_AUDIO_BYTES, _load_model, transcribe_audio_local


class FakeSegment:
    def __init__(self, text, end=2.0):
        self.text = text
        self.end = end


class FakeInfo:
    language = "pt"
    duration = 2.0


class FakeModel:
    def transcribe(self, path, **kwargs):
        self.path = path
        self.kwargs = kwargs
        return [FakeSegment("peso atual 72,4 kg")], FakeInfo()


class AudioTests(unittest.TestCase):
    def tearDown(self):
        _load_model.cache_clear()

    def test_local_transcription_uses_optional_model_and_returns_text(self):
        fake_model = FakeModel()
        fake_module = types.ModuleType("faster_whisper")
        fake_module.WhisperModel = lambda *args, **kwargs: fake_model
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "sample.ogg"
            audio_path.write_bytes(b"fake audio")
            with patch.dict(sys.modules, {"faster_whisper": fake_module}):
                result = transcribe_audio_local(audio_path)
        self.assertEqual(result["text"], "peso atual 72,4 kg")
        self.assertEqual(result["engine"], "faster-whisper-local")
        self.assertEqual(fake_model.kwargs["language"], "pt")

    def test_audio_size_limit_is_enforced_before_model_load(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "large.ogg"
            with audio_path.open("wb") as stream:
                stream.truncate(MAX_AUDIO_BYTES + 1)
            with self.assertRaisesRegex(RuntimeError, "15 MB"):
                transcribe_audio_local(audio_path)

    def test_missing_optional_dependency_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "sample.ogg"
            audio_path.write_bytes(b"audio")
            with patch.dict(sys.modules, {"faster_whisper": None}):
                with self.assertRaisesRegex(RuntimeError, "requirements-audio"):
                    transcribe_audio_local(audio_path)


if __name__ == "__main__":
    unittest.main()
