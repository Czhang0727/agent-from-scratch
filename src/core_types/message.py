#!/usr/bin/env python3
"""
Message types for IO communication.
"""

from dataclasses import dataclass
from enum import Enum, auto


class IOBusMessageType(Enum):
    """Types of messages that can flow through the IO bus."""
    USER_INPUT = auto()
    AGENT_OUTPUT = auto()
    SYSTEM = auto()
    ERROR = auto()


@dataclass
class IOBusMessage:
    """A message in the IO bus."""
    content: str
    msg_type: IOBusMessageType
