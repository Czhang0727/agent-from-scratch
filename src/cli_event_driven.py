#!/usr/bin/env python3
"""
CLI entry point for the event-driven agent.
"""

import sys
import config  # Load .env file  # noqa: F401
from event_bus import EventBus
from event_driven_agent import EventDrivenAgent
from event_io_bus import EventIOBus


def main():
    event_bus = EventBus()
    io_bus = EventIOBus(event_bus)
    agent = EventDrivenAgent(io_bus, event_bus)

    try:
        agent.start()
    except KeyboardInterrupt:
        io_bus.system("\nInterrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
