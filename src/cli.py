#!/usr/bin/env python3
"""
CLI Agent - Main entry point for the agent from scratch.
Provides an IO bus for console input/output communication.
"""

import sys
import config  # Load .env file  # noqa: F401
from agent import Agent
from io_bus import IOBus


def main():
    """Main entry point for the CLI agent."""
    io_bus = IOBus()
    agent = Agent(io_bus)

    try:
        agent.start()
    except KeyboardInterrupt:
        io_bus.system("\nInterrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
