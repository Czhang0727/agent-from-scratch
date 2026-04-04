#!/usr/bin/env python3
"""
Agent Module - The main agent that processes user input and generates responses.
"""

import time
from io_bus import IOBus
from openrouter_client import OpenRouterClient


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
        self.io_bus.system("Agent started. Waiting for messages...")

        while True:
            # Check if there's a message available (non-blocking)
            msg = self.io_bus.read()

            if msg is None:
                # No message available, sleep and continue
                time.sleep(0.5)
                continue

            # Check for exit command
            if msg.content.lower() in ("exit", "quit", "q"):
                self.io_bus.system("Goodbye!")
                self.io_bus.stop()
                break

            # Send user input to LLM and get response
            try:
                response = self.llm.simple_chat(msg.content)
                self.io_bus.output(response)
            except Exception as e:
                self.io_bus.error(f"Error: {e}")
            finally:
                # Resume input after response
                self.io_bus.resume_input()
