#!/usr/bin/env python3
"""
IO Bus Module - Handles console input/output communication.
Acts as the communication layer between the user and the agent.
"""

import sys
import threading
import queue
import termios
from core_types.message import IOBusMessage, IOBusMessageType


class IOBus:
    """
    IO Bus for handling console input and output.
    Acts as the communication layer between the user and the agent.
    Uses a message queue to support async message processing.
    """

    def __init__(self, input_stream=None, output_stream=None):
        self.input_stream = input_stream or sys.stdin
        self.output_stream = output_stream or sys.stdout
        self._message_queue = queue.Queue()
        self._input_thread = None
        self._running = False
        self._input_enabled = threading.Event()
        self._input_enabled.set()  # Initially enabled
        self._original_termios = None

    def start(self) -> None:
        """Start the input listener in a background thread."""
        self._running = True
        # Save original terminal settings
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
        self._input_enabled.set()  # Unblock if waiting
        self._restore_terminal()

    def _disable_echo(self) -> None:
        """Disable echo on the terminal while keeping canonical mode."""
        if not self.input_stream.isatty() or self._original_termios is None:
            return
        try:
            fd = self.input_stream.fileno()
            attrs = termios.tcgetattr(fd)
            # Disable ECHO flag but keep ICANON (canonical mode)
            attrs[3] = attrs[3] & ~termios.ECHO
            termios.tcsetattr(fd, termios.TCSANOW, attrs)
        except (termios.error, OSError):
            pass

    def _restore_terminal(self) -> None:
        """Restore original terminal settings."""
        if self._original_termios is None or not self.input_stream.isatty():
            return
        try:
            fd = self.input_stream.fileno()
            termios.tcsetattr(fd, termios.TCSANOW, self._original_termios)
        except (termios.error, OSError):
            pass

    def _flush_input_buffer(self) -> None:
        """Discard any pending/buffered input."""
        if not self.input_stream.isatty():
            return
        try:
            fd = self.input_stream.fileno()
            termios.tcflush(fd, termios.TCIFLUSH)
        except (termios.error, OSError):
            pass

    def pause_input(self) -> None:
        """Pause the input thread and block terminal input (disable echo)."""
        self._input_enabled.clear()
        self._disable_echo()

    def resume_input(self) -> None:
        """Resume the input thread and unblock terminal input (restore echo)."""
        self._flush_input_buffer()
        self._restore_terminal()
        self._input_enabled.set()

    def _input_loop(self) -> None:
        """Background thread that continuously reads input."""
        while self._running:
            # Wait for input to be enabled
            self._input_enabled.wait()

            if not self._running:
                break

            try:
                self.write_raw("> ", end="")
                line = self.input_stream.readline().strip()
                if line:
                    # Block input and show thinking immediately on Enter
                    self._input_enabled.clear()
                    self._disable_echo()
                    self.system("Thinking...")
                    self._message_queue.put(
                        IOBusMessage(content=line, msg_type=IOBusMessageType.USER_INPUT)
                    )
            except (EOFError, KeyboardInterrupt):
                self._message_queue.put(
                    IOBusMessage(content="exit", msg_type=IOBusMessageType.USER_INPUT)
                )
                break

    def read(self) -> IOBusMessage | None:
        """
        Non-blocking read from the message queue.

        Returns:
            An IOBusMessage if available, None otherwise.
        """
        try:
            return self._message_queue.get_nowait()
        except queue.Empty:
            return None

    def send(self, content: str) -> None:
        """
        Send a message to the agent (for programmatic input).

        Args:
            content: The message content to send.
        """
        self._message_queue.put(
            IOBusMessage(content=content, msg_type=IOBusMessageType.USER_INPUT)
        )

    def write(self, message: IOBusMessage) -> None:
        """
        Write a message to the console.

        Args:
            message: The IOBusMessage to output.
        """
        prefix = self._get_prefix(message.msg_type)
        self.write_raw(f"{prefix}{message.content}")

    def write_raw(self, content: str, end: str = "\n") -> None:
        """
        Write raw content to the output stream.

        Args:
            content: The content to write.
            end: The ending character (default: newline).
        """
        self.output_stream.write(content + end)
        self.output_stream.flush()

    def _get_prefix(self, msg_type: IOBusMessageType) -> str:
        """Get the prefix for a message type."""
        prefixes = {
            IOBusMessageType.AGENT_OUTPUT: "🤖 ",
            IOBusMessageType.SYSTEM: "ℹ️  ",
            IOBusMessageType.ERROR: "❌ ",
            IOBusMessageType.USER_INPUT: "",
        }
        return prefixes.get(msg_type, "")

    def output(self, content: str) -> None:
        """Convenience method to output agent text."""
        self.write(IOBusMessage(content=content, msg_type=IOBusMessageType.AGENT_OUTPUT))

    def system(self, content: str) -> None:
        """Convenience method to output system messages."""
        self.write(IOBusMessage(content=content, msg_type=IOBusMessageType.SYSTEM))

    def error(self, content: str) -> None:
        """Convenience method to output error messages."""
        self.write(IOBusMessage(content=content, msg_type=IOBusMessageType.ERROR))
