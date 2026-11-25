"""Gemini API text-to-speech (Interactions API — gemini-3.8-flash-tts)."""

from __future__ import annotations

import base64
import os
import time
import wave
from pathlib import Path

from config import AppConfig
from core.model_log import log_model_call
from providers.base import ProviderResult, TextToSpeechProvider

DEFAULT_TTS_MODEL = os.getenv("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts")
DEFAULT_VOICE = os.getenv("GEMINI_TTS_VOICE", "Kore")


def _write_wav_from_pcm(path: Path, pcm: bytes, rate: int = 24000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(pcm)


class GeminiTTSProvider(TextToSpeechProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY required for Gemini TTS")
        self.model = DEFAULT_TTS_MODEL
        self.voice = DEFAULT_VOICE

    def synthesize(
        self, text: str, output_path: Path, language: str, duration_hint: float
    ) -> ProviderResult:
        t0 = time.perf_counter()
        try:
            from google import genai
        except ImportError:
            return ProviderResult(
                success=False,
                message="Install google-genai>=2.25.0: pip install -U google-genai",
            )

        client = genai.Client(
            api_key=self.config.gemini_api_key,
            http_options={"api_version": "v1beta"},
        )
        style = f"Calm, clear documentary narration in language {language}."

        try:
            interaction = client.interactions.create(
                model=self.model,
                input=[
                    {
                        "type": "user_input",
                        "content": [
                            {
                                "type": "text",
                                "text": text,
                                "annotations": [
                                    {"type": "speech_metadata", "style": style},
                                ],
                            }
                        ],
                    }
                ],
                response_format={"type": "audio"},
                generation_config={
                    "speech_config": [{"voice": self.voice}],
                },
            )
        except Exception as exc:
            log_model_call(
                self.config.logs_dir,
                stage="narration",
                model=self.model,
                latency_ms=(time.perf_counter() - t0) * 1000,
                success=False,
                parameters={"language": language, "text_len": len(text)},
                message=str(exc),
            )
            return ProviderResult(
                success=False,
                message=f"Gemini TTS failed: {exc}. Use a key from https://aistudio.google.com/apikey",
            )

        audio = None
        if hasattr(interaction, "output_audio") and interaction.output_audio:
            raw = interaction.output_audio.data
            if isinstance(raw, str):
                audio = base64.b64decode(raw)
            elif isinstance(raw, (bytes, bytearray)):
                audio = bytes(raw)

        if not audio:
            log_model_call(
                self.config.logs_dir,
                stage="narration",
                model=self.model,
                latency_ms=(time.perf_counter() - t0) * 1000,
                success=False,
                parameters={"language": language},
                message="no output_audio",
            )
            return ProviderResult(success=False, message="Gemini TTS returned no audio")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        if audio[:4] == b"RIFF":
            output_path.write_bytes(audio)
        else:
            _write_wav_from_pcm(output_path, audio)

        latency = (time.perf_counter() - t0) * 1000
        log_model_call(
            self.config.logs_dir,
            stage="narration",
            model=self.model,
            latency_ms=latency,
            success=True,
            parameters={"language": language, "voice": self.voice},
            cost_usd=0.0,
        )
        return ProviderResult(success=True, path=output_path, message="gemini tts")