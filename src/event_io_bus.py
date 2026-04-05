#!/usr/bin/env python3
"""
Event IO Bus Module - An IOBus that publishes input events to an EventBus.
Pure I/O: reads from stdin, writes to stdout, emits events.
"""

import sys
import threading
import termios
from event_bus import EventBus
from core_types.message import IOBusMessage, IOBusMessageType


class EventIOBus:
    """
    IO Bus that publishes user input as events on an EventBus.
    No internal queue — the event bus is the only delivery mechanism.
    """

    def __init__(self, event_bus: EventBus, input_stream=None, output_stream=None):
        self.event_bus = event_bus
        self.input_stream = input_stream or sys.stdin
        self.output_stream = output_stream or sys.stdout
        self._input_thread = None
        self._running = False
        self._input_enabled = threading.Event()
        self._input_enabled.set()
        self._original_termios = None

    def start(self) -> None:
        """Start the input listener in a background thread."""
        self._running = True
        if self.input_stream.isatty():
            try:
                self._original_termios = termios.tcgetattr(self.input_stream.fileno())
            except (termios.error, OSError):
                self._original_termios = None
        self._input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self._input_thread.start()

    def stop(self) -> None:
        """Stop the input listener and restore terminal settings."""
        self._running = False
        self._input_enabled.set()
        self._restore_terminal()

    def _disable_echo(self) -> None:
        if not self.input_stream.isatty() or self._original_termios is None:
            return
        try:
            fd = self.input_stream.fileno()
            attrs = termios.tcgetattr(fd)
            attrs[3] = attrs[3] & ~termios.ECHO
            termios.tcsetattr(fd, termios.TCSANOW, attrs)
        except (termios.error, OSError):
            pass

    def _restore_terminal(self) -> None:
        if self._original_termios is None or not self.input_stream.isatty():
            return
        try:
            fd = self.input_stream.fileno()
            termios.tcsetattr(fd, termios.TCSANOW, self._original_termios)
        except (termios.error, OSError):
            pass

    def _flush_input_buffer(self) -> None:
        if not self.input_stream.isatty():
            return
        try:
            fd = self.input_stream.fileno()
            termios.tcflush(fd, termios.TCIFLUSH)
        except (termios.error, OSError):
            pass

    def pause_input(self) -> None:
        """Pause input and disable echo."""
        self._input_enabled.clear()
        self._disable_echo()

    def resume_input(self) -> None:
        """Resume input and restore echo."""
        self._flush_input_buffer()
        self._restore_terminal()
        self._input_enabled.set()

    def _input_loop(self) -> None:
        """Background thread that reads input and publishes events."""
        while self._running:
            self._input_enabled.wait()

            if not self._running:
                break

            try:
                self.write_raw("> ", end="")
                raw = self.input_stream.readline()
                if not raw:  # EOF
                    self.event_bus.publish("user_input", "exit")
                    break
                line = raw.strip()
                if line:
                    self.event_bus.publish("user_input", line)
            except (EOFError, KeyboardInterrupt):
                self.event_bus.publish("user_input", "exit")
                break

    def write(self, message: IOBusMessage) -> None:
        """Write a message to the console."""
        prefix = self._get_prefix(message.msg_type)
        self.write_raw(f"{prefix}{message.content}")

    def write_raw(self, content: str, end: str = "\n") -> None:
        """Write raw content to the output stream."""
        self.output_stream.write(content + end)
        self.output_stream.flush()

    def _get_prefix(self, msg_type: IOBusMessageType) -> str:
        prefixes = {
            IOBusMessageType.AGENT_OUTPUT: "🤖 ",
            IOBusMessageType.SYSTEM: "ℹ️  ",
            IOBusMessageType.ERROR: "❌ ",
            IOBusMessageType.USER_INPUT: "",
        }
        return prefixes.get(msg_type, "")

    def output(self, content: str) -> None:
        self.write(IOBusMessage(content=content, msg_type=IOBusMessageType.AGENT_OUTPUT))

    def system(self, content: str) -> None:
        self.write(IOBusMessage(content=content, msg_type=IOBusMessageType.SYSTEM))

    def error(self, content: str) -> None:
        self.write(IOBusMessage(content=content, msg_type=IOBusMessageType.ERROR))
