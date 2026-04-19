"""
Workspace — manages a generated folder for each agent session.

All files created by skills go under:
    output/<timestamp>/
        scripts/     — generated scripts (.py, .sh, etc.)
        docs/        — generated documents
        data/        — other generated files
"""

from pathlib import Path
from datetime import datetime


OUTPUT_ROOT = Path(__file__).resolve().parent.parent.parent / "output"


class Workspace:
    """A session workspace rooted at output/<timestamp>/."""

    def __init__(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.root = OUTPUT_ROOT / timestamp
        self.scripts_dir = self.root / "scripts"
        self.docs_dir = self.root / "docs"
        self.data_dir = self.root / "data"

        # Create dirs upfront
        for d in (self.scripts_dir, self.docs_dir, self.data_dir):
            d.mkdir(parents=True, exist_ok=True)

    def resolve(self, path: str) -> Path:
        """
        Resolve a relative path into the workspace.

        Scripts (.py, .sh, .bash, .zsh, .bat, .ps1) → scripts/
        Docs (.md, .txt, .rst, .docx, .pdf) → docs/
        Everything else → data/
        """
        p = Path(path)
        name = p.name
        suffix = p.suffix.lower()

        script_exts = {".py", ".sh", ".bash", ".zsh", ".bat", ".ps1", ".rb", ".js", ".ts"}
        doc_exts = {".md", ".txt", ".rst", ".docx", ".pdf", ".html", ".csv"}

        if suffix in script_exts:
            return self.scripts_dir / name
        elif suffix in doc_exts:
            return self.docs_dir / name
        else:
            return self.data_dir / name
