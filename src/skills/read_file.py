"""
Read file skill — read contents of a file within the workspace.
"""

from pathlib import Path
from skills.base import Skill
from skills.workspace import Workspace


class ReadFileSkill(Skill):

    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file. Relative paths resolve to the workspace."

    @property
    def parameters(self) -> dict:
        return {
            "path": {
                "type": "string",
                "description": "Path to the file to read (relative to workspace or absolute).",
                "required": True,
            },
        }

    def execute(self, **kwargs) -> str:
        raw = kwargs["path"]
        path = Path(raw).expanduser()

        # Relative paths resolve against workspace root
        if not path.is_absolute():
            path = self.workspace.root / path

        if not path.exists():
            return f"[error] File not found: {path}"
        if not path.is_file():
            return f"[error] Not a file: {path}"

        try:
            content = path.read_text(encoding="utf-8")
            if not content:
                return "(file is empty)"
            return content
        except Exception as e:
            return f"[error] {e}"
