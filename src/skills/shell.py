"""
Shell skill — execute shell commands within the workspace.
"""

import subprocess
from skills.base import Skill
from skills.workspace import Workspace


class ShellSkill(Skill):

    def __init__(self, workspace: Workspace):
        self.workspace = workspace

    @property
    def name(self) -> str:
        return "shell"

    @property
    def description(self) -> str:
        return "Execute a shell command. Working directory is the workspace root."

    @property
    def parameters(self) -> dict:
        return {
            "command": {
                "type": "string",
                "description": "The shell command to execute.",
                "required": True,
            },
            "timeout": {
                "type": "integer",
                "description": "Max seconds to wait (default 30).",
                "required": False,
            },
        }

    def execute(self, **kwargs) -> str:
        command = kwargs["command"]
        timeout = kwargs.get("timeout", 30)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.workspace.root),
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output.strip() or "(no output)"
        except subprocess.TimeoutExpired:
            return f"[error] Command timed out after {timeout}s."
        except Exception as e:
            return f"[error] {e}"
