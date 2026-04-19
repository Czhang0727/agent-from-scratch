"""
Skills Module - Tool/skill system for the agent.
"""

from skills.registry import SkillRegistry
from skills.workspace import Workspace
from skills.shell import ShellSkill
from skills.read_file import ReadFileSkill
from skills.write_file import WriteFileSkill
from skills.list_files import ListFilesSkill


def create_default_registry() -> tuple[SkillRegistry, Workspace]:
    """Create a registry with all built-in skills and a session workspace."""
    workspace = Workspace()
    registry = SkillRegistry()
    registry.register(ShellSkill(workspace))
    registry.register(ReadFileSkill(workspace))
    registry.register(WriteFileSkill(workspace))
    registry.register(ListFilesSkill(workspace))
    return registry, workspace
