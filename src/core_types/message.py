#!/usr/bin/env python3
"""
Message types for IO communication.
Supports multimodal content: text, image, audio.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class IOMessageType(Enum):
    """Types of messages that can flow through the IO bus."""
    USER_INPUT = auto()
    AGENT_OUTPUT = auto()
    SYSTEM = auto()
    ERROR = auto()


class ContentType(Enum):
    """Types of content that can be carried in a message."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"


@dataclass
class Content:
    """A single piece of content in a message."""
    type: ContentType
    data: str | bytes  # text string, or raw bytes for binary content
    mime_type: Optional[str] = None  # e.g. "image/png", "audio/wav"
    file_path: Optional[str] = None  # original file path if loaded from disk

    @staticmethod
    def text(data: str) -> "Content":
        return Content(type=ContentType.TEXT, data=data, mime_type="text/plain")

    @staticmethod
    def image(data: bytes, mime_type: str, file_path: Optional[str] = None) -> "Content":
        return Content(type=ContentType.IMAGE, data=data, mime_type=mime_type, file_path=file_path)

    @staticmethod
    def audio(data: bytes, mime_type: str = "audio/wav", file_path: Optional[str] = None) -> "Content":
        return Content(type=ContentType.AUDIO, data=data, mime_type=mime_type, file_path=file_path)


@dataclass
class IOMessage:
    """A message in the IO bus, carrying one or more content parts."""
    parts: list[Content] = field(default_factory=list)
    msg_type: IOMessageType = IOMessageType.USER_INPUT

    @property
    def text(self) -> Optional[str]:
        """Get the first text content, if any."""
        for part in self.parts:
            if part.type == ContentType.TEXT:
                return part.data
        return None

    @property
    def has_image(self) -> bool:
        return any(p.type == ContentType.IMAGE for p in self.parts)

    @property
    def has_audio(self) -> bool:
        return any(p.type == ContentType.AUDIO for p in self.parts)

    @property
    def images(self) -> list[Content]:
        return [p for p in self.parts if p.type == ContentType.IMAGE]

    @property
    def audios(self) -> list[Content]:
        return [p for p in self.parts if p.type == ContentType.AUDIO]

    @staticmethod
    def from_text(text: str, msg_type: IOMessageType = IOMessageType.USER_INPUT) -> "IOMessage":
        """Create a simple text message (backward-compatible helper)."""
        return IOMessage(parts=[Content.text(text)], msg_type=msg_type)

    def summary(self) -> str:
        """Human-readable summary of the message contents."""
        pieces = []
        for p in self.parts:
            if p.type == ContentType.TEXT:
                pieces.append(p.data)
            elif p.type == ContentType.IMAGE:
                label = p.file_path or "image"
                pieces.append(f"[Image: {label}]")
            elif p.type == ContentType.AUDIO:
                label = p.file_path or "audio"
                pieces.append(f"[Audio: {label}]")
        return " ".join(pieces) if pieces else "(empty)"
