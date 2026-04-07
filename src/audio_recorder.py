#!/usr/bin/env python3
"""
Audio Recorder - Records audio from the microphone and saves as WAV.
Requires: sounddevice, numpy
"""

import io
import wave
import numpy as np
import sounddevice as sd


DEFAULT_SAMPLE_RATE = 16000
DEFAULT_DURATION = 5


def record_audio(duration: float = DEFAULT_DURATION, sample_rate: int = DEFAULT_SAMPLE_RATE) -> tuple[bytes, str]:
    """
    Record audio from the default microphone.

    Args:
        duration: Recording duration in seconds.
        sample_rate: Sample rate in Hz.

    Returns:
        Tuple of (wav_bytes, mime_type).
    """
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
    )
    sd.wait()

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    return buf.getvalue(), "audio/wav"
