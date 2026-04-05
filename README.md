# Agent from Scratch

A CLI agent tool built from scratch for automating tasks through intelligent orchestration.

## Overview

This project is a command-line interface (CLI) agent tool designed to execute tasks, manage workflows, and interact with various systems through a modular architecture.

## Features

- **Two Agent Modes**: Polling-based and event-driven architectures
- **Pub/Sub Event Bus**: Decoupled communication between IO and agent via publish/subscribe
- **LLM Integration**: Direct raw input to LLM via OpenRouter API
- **Input Blocking**: Terminal input is blocked during AI processing with "Thinking..." status
- **Two-Role Interaction**: One message per user input + AI response cycle

## Quick Start

```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenRouter API key
export OPENROUTER_API_KEY="your-api-key"

# Run the polling-based agent
python src/cli.py

# Or run the event-driven agent
python src/cli_event_driven.py
```

## Docs

- [Agent Flow Implementation](docs/agent-flow-implementation.md) — polling-based vs event-driven agents, component breakdown
- [TODO](docs/todo.md) — roadmap and progress
