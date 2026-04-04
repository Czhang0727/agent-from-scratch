# Agent from Scratch

A CLI agent tool built from scratch for automating tasks through intelligent orchestration.

## Overview

This project is a command-line interface (CLI) agent tool designed to execute tasks, manage workflows, and interact with various systems through a modular architecture.

## Features

- **Async Message Loop**: Uses while True + sleep pattern for continuous operation
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

# Run the agent
python src/cli.py
```

## Architecture

### Core Components

- **Agent** (`src/agent.py`): Main orchestration loop, handles message flow
- **IOBus** (`src/io_bus.py`): Terminal I/O with input blocking during LLM inference
- **OpenRouterClient** (`src/openrouter_client.py`): LLM API client

### Message Flow

```
User Input → IOBus → Agent → LLM → Agent → IOBus → User
                ↓
         Input Blocked
         "Thinking..."
```

## TODO List

### 1. Main Orchestration
- [x] Design core agent loop (while True + sleep pattern)
- [ ] Implement task planning and decomposition
- [ ] Build execution flow controller
- [x] Add error handling and recovery mechanisms

### 2. IO (Input/Output)
- [x] Create CLI interface
- [x] Implement user input parsing
- [x] Build output formatting and display
- [x] Add input blocking during AI processing
- [ ] Add logging system

### 3. Memory
- [ ] Design memory storage architecture
- [ ] Implement short-term memory (context)
- [ ] Build long-term memory (persistence)
- [ ] Add memory retrieval and search

### 4. Executable Handler
- [ ] Create command execution engine
- [ ] Implement sandboxing for safety
- [ ] Build tool registry system
- [ ] Add support for custom executables

### 5. Guidelines
- [ ] Define agent behavior rules
- [ ] Implement safety constraints
- [ ] Build user preference system
- [ ] Add ethical guardrails
