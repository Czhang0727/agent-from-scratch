# Architecture

## Polling-Based Agent (Original)

- **Agent** (`src/agent.py`): Main orchestration loop with `while True` + `sleep(0.5)` polling
- **IOBus** (`src/io_bus.py`): Terminal I/O with message queue

```
User Input → IOBus (queue) → Agent (polls) → LLM → Agent → IOBus → User
```

The agent runs a tight loop, checking the IOBus message queue every 500ms. When a message is found, the agent pauses input, sends the message to the LLM, writes the response back, and resumes input. This is simple but wastes cycles when idle.

## Event-Driven Agent

- **EventDrivenAgent** (`src/event_driven_agent.py`): Subscribes to events, no polling loop
- **EventBus** (`src/event_bus.py`): Generic pub/sub — `subscribe()`, `publish()`, `unsubscribe()`
- **EventIOBus** (`src/event_io_bus.py`): Terminal I/O that publishes `"user_input"` events

```
User Input → EventIOBus → EventBus.publish("user_input") → EventDrivenAgent → LLM → EventIOBus → User
```

Instead of polling, the EventIOBus publishes a `"user_input"` event whenever the user submits a line. The EventDrivenAgent subscribes to this event and only wakes when input arrives. The main thread blocks on a `threading.Event` until the agent is stopped.

## Shared Components

- **OpenRouterClient** (`src/openrouter_client.py`): LLM API client wrapping the OpenRouter SDK. Default model: `qwen/qwen-2.5-7b-instruct`.
- **Config** (`src/config.py`): Loads `.env` file for API keys on import. Only sets variables not already in the environment.
- **IOBusMessage** (`src/core_types/message.py`): Dataclass + enum for typed messages (user input, agent output, system, error).
