#!/usr/bin/env python3
"""
CLI entry point for the event-driven agent.
"""

import sys
import argparse
import config  # Load .env file  # noqa: F401
from event_bus import EventBus
from event_driven_agent import EventDrivenAgent
from event_io_bus import EventIOBus
from prompts import PROMPTS
from skills import create_default_registry


def parse_args():
    parser = argparse.ArgumentParser(description="Agent from scratch — event-driven mode")
    parser.add_argument(
        "--persona",
        choices=list(PROMPTS.keys()),
        default=None,
        help="Agent persona (default: no system prompt)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="OpenRouter model ID (default: qwen/qwen3.5-plus-02-15)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    system_prompt = PROMPTS.get(args.persona) if args.persona else None
    registry, workspace = create_default_registry()

    event_bus = EventBus()
    io_bus = EventIOBus(event_bus)
    agent = EventDrivenAgent(io_bus, event_bus, system_prompt=system_prompt,
                             model=args.model, skill_registry=registry)

    io_bus.system(f"Workspace: {workspace.root}")

    try:
        agent.start()
    except KeyboardInterrupt:
        io_bus.system("\nInterrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
