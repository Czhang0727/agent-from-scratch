"""
Write file skill — create or overwrite a file within the workspace.
"""

from skills.base import Skill
from skills.workspace import Workspace


class WriteFileSkill(Skill):

    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return (
            "Write content to a file. Files are automatically placed in the "
            "workspace: scripts go to scripts/, docs go to docs/, others to data/."
        )

    @property
    def parameters(self) -> dict:
        return {
            "path": {
                "type": "string",
                "description": "Filename (e.g. 'report.md', 'fetch_data.py'). Auto-routed by extension.",
                "required": True,
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file.",
                "required": True,
            },
        }

    def execute(self, **kwargs) -> str:
        resolved = self.workspace.resolve(kwargs["path"])
        content = kwargs["content"]

        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(content, encoding="utf-8")
            return f"Written {len(content)} chars to {resolved}"
        except Exception as e:
            return f"[error] {e}"
