#!/usr/bin/env python3
"""
Agent Module - The main agent that processes user input and generates responses.
"""

import time
from io_bus import IOBus
from openrouter_client import OpenRouterClient
from core_types.message import IOMessage


class Agent:
    """
    The main agent that processes user input and generates responses via LLM.
    """

    def __init__(self, io_bus: IOBus):
        self.io_bus = io_bus
        self.running = False
        self.llm = OpenRouterClient()

    def start(self) -> None:
        """Start the agent's main loop."""
        self.running = True
        self.io_bus.start()
        self.io_bus.system("Agent started. Type text, /image <path>, or /record [seconds]")

        while True:
            msg = self.io_bus.read()

            if msg is None:
                time.sleep(0.5)
                continue

            text = msg.text
            if text and text.lower() in ("exit", "quit", "q"):
                self.io_bus.system("Goodbye!")
                self.io_bus.stop()
                break

            self.io_bus.pause_input()
            self.io_bus.system("Thinking...")
            try:
                response = self._process_message(msg)
                self.io_bus.output(response)
            except Exception as e:
                self.io_bus.error(f"Error: {e}")
            finally:
                self.io_bus.resume_input()

    def _process_message(self, msg: IOMessage) -> str:
        """Process a multimodal message and return a response."""
        if msg.has_image:
            img = msg.images[0]
            return f"Received image ({img.mime_type}, {len(img.data)} bytes). Vision model integration coming soon."

        if msg.has_audio:
            audio = msg.audios[0]
            return f"Received audio ({audio.mime_type}, {len(audio.data)} bytes). Speech-to-text integration coming soon."

        return self.llm.simple_chat(msg.text)
