"""
Base skill interface. All skills must implement this.
"""

from abc import ABC, abstractmethod


class Skill(ABC):
    """Abstract base class for all agent skills."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique skill identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what this skill does."""
        ...

    @property
    @abstractmethod
    def parameters(self) -> dict:
        """
        Parameter schema as a dict.
        Keys are parameter names, values are dicts with:
          - "type": str (e.g. "string", "integer", "boolean")
          - "description": str
          - "required": bool (default True)
        """
        ...

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        Execute the skill with the given parameters.
        Returns a string result to feed back to the LLM.
        """
        ...

    def to_catalog_entry(self) -> str:
        """Format this skill for inclusion in the LLM system prompt."""
        params_lines = []
        for param_name, param_info in self.parameters.items():
            required = param_info.get("required", True)
            tag = "required" if required else "optional"
            params_lines.append(
                f"    - {param_name} ({param_info['type']}, {tag}): {param_info['description']}"
            )
        params_str = "\n".join(params_lines) if params_lines else "    (none)"
        return f"- **{self.name}**: {self.description}\n  Parameters:\n{params_str}"
