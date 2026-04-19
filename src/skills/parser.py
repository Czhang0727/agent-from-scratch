"""
Skill plan parser — extracts the structured plan from LLM responses.

The LLM wraps its plan in a ```json block:

```json
{
    "analysis": "User wants to ...",
    "plan": [
        {"skill": "shell", "params": {"command": "ls"}, "reason": "List files"}
    ]
}
```

If the response contains no JSON block, it is treated as a plain text reply
(no skills invoked).
"""

import json
import re


JSON_BLOCK_RE = re.compile(r"```json\s*\n(\{.*?\})\s*\n```", re.DOTALL)


def parse_skill_plan(text: str) -> dict | None:
    """
    Extract the skill plan JSON from the LLM response.

    Returns a dict with keys: analysis, plan.
    Returns None if no valid JSON block is found.
    """
    match = JSON_BLOCK_RE.search(text)
    if not match:
        return None

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None

    if "plan" not in data:
        return None

    return {
        "analysis": data.get("analysis", ""),
        "plan": data.get("plan", []),
    }


def extract_commentary(text: str) -> str:
    """Return the text outside the JSON block (LLM reasoning/commentary)."""
    return JSON_BLOCK_RE.sub("", text).strip()
