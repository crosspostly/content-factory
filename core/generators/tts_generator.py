from __future__ import annotations

import wave
from pathlib import Path
from typing import Any

from core.utils.config_loader import ProjectConfig


def _write_silence_wav(path: Path, *, duration_sec: float = 1.0, sample_rate: int = 22050) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    nframes = int(duration_sec * sample_rate)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * nframes)


def synthesize(config: ProjectConfig, script: Any, mode: str) -> dict[str, Any]:
    """Synthesize speech.

    Part 2 will implement real TTS engines. For Part 1 we generate a short
    silent WAV as a placeholder so the orchestrator can run end-to-end.
    """

    project_slug = str(config.project.get("name") or "project").replace(" ", "_")
    out_dir = Path("output") / "audio" / project_slug

    audio_path = out_dir / f"{mode}.wav"
    _write_silence_wav(audio_path)

    return {
        "blocks": {"main": str(audio_path)},
        "background_music_path": None,
        "sound_effects": {},
        "engine_used": "edge-tts",
        "total_duration_sec": 45.5,
    }
