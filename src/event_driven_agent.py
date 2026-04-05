#!/usr/bin/env python3
"""
Event-Driven Agent - Reacts to events from the event bus instead of polling.
"""

import threading
from event_io_bus import EventIOBus
from event_bus import EventBus
from openrouter_client import OpenRouterClient


class EventDrivenAgent:
    """
    An agent that subscribes to events via a pub/sub event bus.
    No polling loop — the agent only wakes when an event arrives.
    """

    def __init__(self, io_bus: EventIOBus, event_bus: EventBus):
        self.io_bus = io_bus
        self.event_bus = event_bus
        self.llm = OpenRouterClient()
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Subscribe to events and start the IO bus."""
        self.event_bus.subscribe("user_input", self._on_user_input)
        self.io_bus.start()
        self.io_bus.system("Agent started. Waiting for messages...")
        self._stop_event.wait()

    def stop(self) -> None:
        """Unsubscribe and shut down."""
        self.event_bus.unsubscribe("user_input", self._on_user_input)
        self.io_bus.stop()
        self._stop_event.set()

    def _on_user_input(self, content: str) -> None:
        """Handle a user input event."""
        if content.lower() in ("exit", "quit", "q"):
            self.io_bus.system("Goodbye!")
            self.stop()
            return

        self.io_bus.pause_input()
        self.io_bus.system("Thinking...")
        try:
            response = self.llm.simple_chat(content)
            self.io_bus.output(response)
        except Exception as e:
            self.io_bus.error(f"Error: {e}")
        finally:
            self.io_bus.resume_input()
