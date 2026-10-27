import tempfile
import os
import asyncio
from typing import Dict, Any

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

class SpeechService:
    """
    Interface for speech-to-text processing.
    """
    
    def __init__(self, provider: str = "whisper"):
        self.provider = provider
        self.model = None

    def _get_model(self):
        if self.model is None:
            if WhisperModel is None:
                raise RuntimeError(
                    "Server speech transcription is unavailable. Use browser voice input, or install faster-whisper."
                )
            # Load a fast model (e.g. tiny.en or base.en) on CPU for quick inference
            self.model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
        return self.model

    async def transcribe_audio(self, audio_bytes: bytes, content_type: str) -> Dict[str, Any]:
        """
        Transcribes the given audio payload into text.
        """
        if self.provider == "mock":
            return self._mock_transcribe(audio_bytes, content_type)
        elif self.provider == "deepgram":
            return await self._deepgram_transcribe(audio_bytes, content_type)
        elif self.provider == "whisper":
            return await self._whisper_transcribe(audio_bytes, content_type)
        else:
            raise ValueError(f"Unknown speech provider: {self.provider}")

    def _mock_transcribe(self, audio_bytes: bytes, content_type: str) -> Dict[str, Any]:
        return {
            "text": "",
            "confidence": 0.0,
            "provider": "mock"
        }

    async def _deepgram_transcribe(self, audio_bytes: bytes, content_type: str) -> Dict[str, Any]:
        raise NotImplementedError("Deepgram integration not yet implemented")

    async def _whisper_transcribe(self, audio_bytes: bytes, content_type: str) -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            model = self._get_model()
            loop = asyncio.get_event_loop()
            
            def run_transcription():
                segments, info = model.transcribe(tmp_path, beam_size=5)
                text = " ".join([segment.text for segment in segments]).strip()
                return text, info

            text, info = await loop.run_in_executor(None, run_transcription)
            
            return {
                "text": text,
                "confidence": 1.0,
                "language": info.language,
                "provider": "whisper"
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
