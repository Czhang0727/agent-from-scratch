#!/usr/bin/env python3
"""
Event-Driven Agent - Reacts to events from the event bus instead of polling.

Flow: User → LLM (plan) → Execute all steps → LLM (summarize) → User
Maintains conversation history across turns.
"""

import json
import threading
from event_io_bus import EventIOBus
from event_bus import EventBus
from openrouter_client import OpenRouterClient
from core_types.message import IOMessage
from skills.registry import SkillRegistry
from skills.parser import parse_skill_plan
from skills.schema import SCHEMA


class EventDrivenAgent:
    """
    An agent that subscribes to events via a pub/sub event bus.
    No polling loop — the agent only wakes when an event arrives.
    """

    def __init__(self, io_bus: EventIOBus, event_bus: EventBus,
                 system_prompt: str = None, model: str = None,
                 skill_registry: SkillRegistry = None):
        self.io_bus = io_bus
        self.event_bus = event_bus
        self.system_prompt = system_prompt
        self.skill_registry = skill_registry
        self.llm = OpenRouterClient(model=model)
        self.history: list[dict] = []
        self._stop_event = threading.Event()

    def _build_system_prompt(self) -> str | None:
        """Combine persona prompt with skill catalog and schema."""
        parts = []
        if self.system_prompt:
            parts.append(self.system_prompt)
        if self.skill_registry:
            catalog = self.skill_registry.catalog()
            schema_str = json.dumps(SCHEMA, indent=2)
            parts.append(SKILL_INSTRUCTIONS.format(catalog=catalog, schema=schema_str))
        return "\n\n".join(parts) if parts else None

    def _build_messages(self, user_content: str) -> list[dict]:
        """Build the full message list: system + history + new user message."""
        messages = []
        system_prompt = self._build_system_prompt()
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_content})
        return messages

    def start(self) -> None:
        self.event_bus.subscribe("user_input", self._on_user_input)
        self.io_bus.start()
        self.io_bus.system("Agent started. Type text, /image <path>, or /record [seconds]")
        self._stop_event.wait()

    def stop(self) -> None:
        self.event_bus.unsubscribe("user_input", self._on_user_input)
        self.io_bus.stop()
        self._stop_event.set()

    def _on_user_input(self, msg: IOMessage) -> None:
        """Handle a user input event."""
        text = msg.text
        if text and text.lower() in ("exit", "quit", "q"):
            self.io_bus.system("Goodbye!")
            self.stop()
            return

        self.io_bus.pause_input()
        self.io_bus.system("Thinking...")
        try:
            response = self._process_message(msg)
            self.io_bus.output(response)
        except Exception as e:
            self.io_bus.error(f"Error: {e}")
        finally:
            self.io_bus.resume_input()

    def _process_message(self, msg: IOMessage) -> str:
        """Process a multimodal message and return a response."""
        if msg.has_image:
            img = msg.images[0]
            return f"Received image ({img.mime_type}, {len(img.data)} bytes). Vision model integration coming soon."

        if msg.has_audio:
            audio = msg.audios[0]
            return f"Received audio ({audio.mime_type}, {len(audio.data)} bytes). Speech-to-text integration coming soon."

        messages = self._build_messages(msg.text)

        # Step 1: Plan
        response = self.llm.chat_completion(messages)
        plan = parse_skill_plan(response) if self.skill_registry else None

        if plan is None:
            self.history.append({"role": "user", "content": msg.text})
            self.history.append({"role": "assistant", "content": response})
            return response

        if plan["analysis"]:
            self.io_bus.system(f"Analysis: {plan['analysis']}")

        if not plan["plan"]:
            self.history.append({"role": "user", "content": msg.text})
            self.history.append({"role": "assistant", "content": plan["analysis"]})
            return plan["analysis"]

        self.io_bus.system(f"Plan: {len(plan['plan'])} step(s)")
        for i, step in enumerate(plan["plan"], 1):
            self.io_bus.system(f"  {i}. [{step['skill']}] {step['reason']}")

        # Step 2: Execute all steps
        step_results = []
        for i, step in enumerate(plan["plan"], 1):
            skill = self.skill_registry.get(step["skill"])
            if skill is None:
                step_results.append({
                    "step": i,
                    "skill": step["skill"],
                    "error": f"Unknown skill: {step['skill']}",
                })
                self.io_bus.error(f"  Step {i}: unknown skill '{step['skill']}'")
                continue

            self.io_bus.system(f"  Executing step {i}: {skill.name}...")
            result = skill.execute(**step["params"])
            step_results.append({
                "step": i,
                "skill": skill.name,
                "reason": step["reason"],
                "result": result,
            })

        # Step 3: Summarize
        messages.append({"role": "assistant", "content": response})
        messages.append({
            "role": "user",
            "content": (
                "All steps have been executed. Here are the results:\n\n"
                + json.dumps(step_results, indent=2)
                + "\n\nSummarize what was done and present the final result to the user."
            ),
        })

        self.io_bus.system("Summarizing...")
        summary = self.llm.chat_completion(messages)

        self.history.append({"role": "user", "content": msg.text})
        self.history.append({"role": "assistant", "content": summary})

        return summary


SKILL_INSTRUCTIONS = """\
## Skills

You have access to skills (tools) you can invoke to accomplish tasks. \
When you want to use skills, respond ONLY with a JSON block in this format:

```json
{{
    "analysis": "Restate what the user wants.",
    "plan": [
        {{"skill": "<name>", "params": {{...}}, "reason": "Why this step."}}
    ]
}}
```

### Rules

1. **Plan everything upfront.** List ALL steps needed to complete the task.
2. **plan** is an ordered list — the agent executes them top to bottom.
3. After execution, you will receive all results and produce a final summary.
4. If the request is ambiguous, return an empty plan and put your question in analysis.
5. If no skills are needed (e.g. the user asks a knowledge question), respond \
with plain text — no JSON block.

### JSON Schema

{schema}

### Available Skills

{catalog}
"""
