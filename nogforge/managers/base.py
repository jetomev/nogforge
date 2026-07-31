"""
NogForge — Base Manager
Defines the PackageInfo dataclass and ManagerBase class that all
package manager wrappers inherit from.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional, AsyncGenerator


@dataclass
class PackageInfo:
    """A single package result, normalized across all managers."""
    name:        str
    version:     str
    description: str
    manager:     str
    installed:   bool        = False
    repo:        str         = ""
    size:        str         = ""
    url:         str         = ""
    license:     str         = ""
    depends:     list[str]   = field(default_factory=list)
    provides:    list[str]   = field(default_factory=list)

    def __hash__(self):
        return hash((self.name, self.manager))

    def __eq__(self, other):
        return (
            isinstance(other, PackageInfo)
            and self.name    == other.name
            and self.manager == other.manager
        )


class ManagerBase:
    """
    Base class for all NogForge package manager wrappers.
    Subclasses override the methods they support.
    """

    # ── Identity (override in every subclass) ────────────────────────────────
    NAME:         str = ""          # internal key  e.g. "nog"
    DISPLAY_NAME: str = ""          # shown in UI    e.g. "Nog"
    ICON:         str = "󰮯"
    COLOR:        str = "#cdd6f4"   # Catppuccin text (default)
    PRIORITY:     int = 99          # lower = runs first

    # ── Availability ──────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """Return True if this manager's binary exists on the system."""
        return False

    # ── Operations ───────────────────────────────────────────────────────────

    async def search(self, query: str) -> list[PackageInfo]:
        return []

    async def get_info(self, name: str) -> Optional[PackageInfo]:
        return None

    async def list_installed(self) -> list[PackageInfo]:
        return []

    async def install(self, name: str) -> AsyncGenerator[str, None]:
        yield "[error] Not implemented"
        yield "\x00EXIT:1"

    async def remove(self, name: str) -> AsyncGenerator[str, None]:
        yield "[error] Not implemented"
        yield "\x00EXIT:1"

    async def update_all(self) -> AsyncGenerator[str, None]:
        yield "[error] Not implemented"
        yield "\x00EXIT:1"

    # ── Shared subprocess helper ──────────────────────────────────────────────

    async def stream_command(
        self, cmd: list[str]
    ) -> AsyncGenerator[str, None]:
        """
        Run a shell command and yield its output line by line.
        The final yielded line is always '\x00EXIT:<code>' so callers
        know when the process finished and whether it succeeded.
        """
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            assert proc.stdout is not None
            async for raw in proc.stdout:
                line = raw.decode(errors="replace").rstrip("\n")
                if line:
                    yield line
            await proc.wait()
            yield f"\x00EXIT:{proc.returncode}"
        except FileNotFoundError:
            yield f"[error] Command not found: {cmd[0]}"
            yield "\x00EXIT:127"
        except Exception as exc:
            yield f"[error] {exc}"
            yield "\x00EXIT:1"