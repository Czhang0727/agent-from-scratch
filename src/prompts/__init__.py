"""
Prompts Module - System prompts that give the agent intention and personality.
"""

from prompts.emotional_support import EMOTIONAL_SUPPORT_PROMPT
from prompts.productivity import PRODUCTIVITY_PROMPT

PROMPTS = {
    "emotional_support": EMOTIONAL_SUPPORT_PROMPT,
    "productivity": PRODUCTIVITY_PROMPT,
}
