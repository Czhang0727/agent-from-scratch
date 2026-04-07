#!/usr/bin/env python3
"""
Event IO Bus Module - An IOBus that publishes input events to an EventBus.
Supports multimodal input: text, image upload, audio recording.
"""

import os
import sys
import mimetypes
import threading
import termios
from event_bus import EventBus
from core_types.message import IOMessage, IOMessageType, Content


class EventIOBus:
    """
    IO Bus that publishes user input as events on an EventBus.
    Supports text, image, and audio input via slash commands.
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
        self._running = True
        if self.input_stream.isatty():
            try:
                self._original_termios = termios.tcgetattr(self.input_stream.fileno())
            except (termios.error, OSError):
                self._original_termios = None
        self._input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self._input_thread.start()

    def stop(self) -> None:
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
        self._input_enabled.clear()
        self._disable_echo()

    def resume_input(self) -> None:
        self._flush_input_buffer()
        self._restore_terminal()
        self._input_enabled.set()

    # ── Command parsing ──────────────────────────────────────────

    def _parse_input(self, line: str) -> IOMessage | None:
        """Parse input into an IOMessage. Returns None on command failure."""
        if line.startswith("/image "):
            return self._handle_image_command(line)
        elif line.startswith("/record"):
            return self._handle_record_command(line)
        else:
            return IOMessage.from_text(line)

    def _handle_image_command(self, line: str) -> IOMessage | None:
        path = line[len("/image "):].strip()
        path = os.path.expanduser(path)

        if not os.path.isfile(path):
            self.error(f"File not found: {path}")
            return None

        mime, _ = mimetypes.guess_type(path)
        if not mime or not mime.startswith("image/"):
            self.error(f"Not a recognized image type: {path}")
            return None

        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError as e:
            self.error(f"Cannot read file: {e}")
            return None

        self.system(f"Loaded image: {path} ({len(data)} bytes, {mime})")
        return IOMessage(
            parts=[Content.image(data, mime_type=mime, file_path=path)],
            msg_type=IOMessageType.USER_INPUT,
        )

    def _handle_record_command(self, line: str) -> IOMessage | None:
        parts = line.split()
        duration = 5.0
        if len(parts) > 1:
            try:
                duration = float(parts[1])
            except ValueError:
                self.error(f"Invalid duration: {parts[1]}")
                return None

        try:
            from audio_recorder import record_audio
        except ImportError:
            self.error("Audio recording requires 'sounddevice' and 'numpy'. Install with: pip install sounddevice numpy")
            return None

        self.system(f"Recording {duration}s of audio... (speak now)")
        try:
            wav_bytes, mime = record_audio(duration=duration)
        except Exception as e:
            self.error(f"Recording failed: {e}")
            return None

        self.system(f"Recorded {len(wav_bytes)} bytes of audio.")
        return IOMessage(
            parts=[Content.audio(wav_bytes, mime_type=mime)],
            msg_type=IOMessageType.USER_INPUT,
        )

    # ── Input loop ───────────────────────────────────────────────

    def _input_loop(self) -> None:
        while self._running:
            self._input_enabled.wait()

            if not self._running:
                break

            try:
                self.write_raw("> ", end="")
                raw = self.input_stream.readline()
                if not raw:
                    self.event_bus.publish("user_input", IOMessage.from_text("exit"))
                    break
                line = raw.strip()
                if line:
                    msg = self._parse_input(line)
                    if msg is not None:
                        self.event_bus.publish("user_input", msg)
            except (EOFError, KeyboardInterrupt):
                self.event_bus.publish("user_input", IOMessage.from_text("exit"))
                break

    # ── Output ───────────────────────────────────────────────────

    def write(self, message: IOMessage) -> None:
        prefix = self._get_prefix(message.msg_type)
        self.write_raw(f"{prefix}{message.summary()}")

    def write_raw(self, content: str, end: str = "\n") -> None:
        self.output_stream.write(content + end)
        self.output_stream.flush()

    def _get_prefix(self, msg_type: IOMessageType) -> str:
        prefixes = {
            IOMessageType.AGENT_OUTPUT: "\U0001f916 ",
            IOMessageType.SYSTEM: "\u2139\ufe0f  ",
            IOMessageType.ERROR: "\u274c ",
            IOMessageType.USER_INPUT: "",
        }
        return prefixes.get(msg_type, "")

    def output(self, content: str) -> None:
        self.write(IOMessage.from_text(content, IOMessageType.AGENT_OUTPUT))

    def system(self, content: str) -> None:
        self.write(IOMessage.from_text(content, IOMessageType.SYSTEM))

    def error(self, content: str) -> None:
        self.write(IOMessage.from_text(content, IOMessageType.ERROR))
