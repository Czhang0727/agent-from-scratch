"""
Skill invocation schema — defines the JSON structure the LLM must output
when it wants to use skills.

Flow: Plan → Execute → Summarize

1. LLM receives user request and outputs a full plan (JSON).
2. Agent executes every step in order.
3. Agent sends all results back to LLM for a final summary.

Schema:
{
    "analysis": "Restate what the user wants.",
    "plan": [
        {
            "skill": "<skill_name>",
            "params": { ... },
            "reason": "Why this step is needed."
        }
    ]
}

- analysis:  Brief restatement of the user's intent.
- plan:      Ordered list of skill calls to execute. The agent runs them
             all in sequence, then asks the LLM to summarize.
             Empty list = no skills needed (e.g. just a question).
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "analysis": {
            "type": "string",
            "description": "Restate the user's intent in your own words.",
        },
        "plan": {
            "type": "array",
            "description": "Ordered list of skill calls to execute.",
            "items": {
                "type": "object",
                "properties": {
                    "skill": {
                        "type": "string",
                        "description": "Name of the skill to invoke.",
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameters to pass to the skill.",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Why this step is needed.",
                    },
                },
                "required": ["skill", "params", "reason"],
            },
        },
    },
    "required": ["analysis", "plan"],
}
