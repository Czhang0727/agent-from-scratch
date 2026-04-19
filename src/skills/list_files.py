"""
List files skill — list directory contents within the workspace.
"""

from pathlib import Path
from skills.base import Skill
from skills.workspace import Workspace


class ListFilesSkill(Skill):

    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return "List files and directories. Defaults to workspace root. Relative paths resolve to workspace."

    @property
    def parameters(self) -> dict:
        return {
            "path": {
                "type": "string",
                "description": "Directory path to list (default: workspace root).",
                "required": False,
            },
            "recursive": {
                "type": "boolean",
                "description": "List recursively (default: false).",
                "required": False,
            },
        }

    def execute(self, **kwargs) -> str:
        raw = kwargs.get("path", ".")
        path = Path(raw).expanduser()

        # Relative paths resolve against workspace root
        if not path.is_absolute():
            path = self.workspace.root / path

        if not path.exists():
            return f"[error] Path not found: {path}"
        if not path.is_dir():
            return f"[error] Not a directory: {path}"

        try:
            recursive = kwargs.get("recursive", False)
            entries = []
            if recursive:
                for item in sorted(path.rglob("*")):
                    rel = item.relative_to(path)
                    tag = "d" if item.is_dir() else "f"
                    entries.append(f"[{tag}] {rel}")
            else:
                for item in sorted(path.iterdir()):
                    tag = "d" if item.is_dir() else "f"
                    entries.append(f"[{tag}] {item.name}")

            if not entries:
                return "(empty directory)"
            return "\n".join(entries)
        except Exception as e:
            return f"[error] {e}"
