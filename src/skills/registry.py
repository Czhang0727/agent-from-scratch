"""
Skill registry — stores, looks up, and lists available skills.
"""

from skills.base import Skill


class SkillRegistry:
    """Registry that holds all available skills."""

    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def list_names(self) -> list[str]:
        return list(self._skills.keys())

    def catalog(self) -> str:
        """Generate the full skill catalog string for the LLM system prompt."""
        if not self._skills:
            return "No skills available."
        entries = [skill.to_catalog_entry() for skill in self._skills.values()]
        return "\n\n".join(entries)
