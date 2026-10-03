"""What nog has done, and what its downloads take (v0.1.0).

History reads nog's own run logs (``~/.local/share/nog/logs/<date> nog-runs.csv``:
date, time, user, command, status, outcome) — the record of every install,
removal and update nog ran, from nogForge or from a terminal. The package
cache's size comes from pacman's cache folder.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

LOGS = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "nog" / "logs"
CACHE = Path("/var/cache/pacman/pkg")


@dataclass
class Run:
    when: datetime
    command: str
    status: str
    outcome: str

    @property
    def what(self) -> str:
        words = self.command.split()
        if not words:
            return "nog"
        verb = {"install": "Install", "remove": "Remove", "update": "Update", "clean": "Clean up",
                "pin": "Change tier", "unlock": "Promote", "activate": "Turn on", "deactivate": "Turn off",
                "search": "Search", "list": "List"}.get(words[0], words[0])
        rest = " ".join(Path(w).name if "/" in w else w for w in words[1:])
        return f"{verb} {rest}".strip()

    @property
    def ok(self) -> bool:
        return self.status in ("0", "") and self.outcome not in ("failed", "stopped")


def runs(folder: Path = LOGS, limit: int = 200) -> list[Run]:
    """Newest first. Lines nog couldn't have written are skipped, not guessed at."""
    out: list[Run] = []
    for f in sorted(folder.glob("* nog-runs.csv")):
        try:
            with f.open(newline="") as fh:
                for r in csv.DictReader(fh):
                    try:
                        when = datetime.strptime(f"{r['date']} {r['time']}", "%m/%d/%Y %I:%M %p")
                    except (KeyError, ValueError, TypeError):
                        continue
                    out.append(Run(when, r.get("command") or "", r.get("status") or "", r.get("outcome") or ""))
        except OSError:
            continue
    out.sort(key=lambda r: r.when, reverse=True)
    return out[:limit]


def cache_size(folder: Path = CACHE) -> tuple[int, int]:
    """(bytes, files) of downloaded packages."""
    total = files = 0
    try:
        for e in os.scandir(folder):
            if e.is_file(follow_symlinks=False) and ".pkg.tar" in e.name and not e.name.endswith(".sig"):
                total += e.stat(follow_symlinks=False).st_size
                files += 1
    except OSError:
        pass
    return total, files


def size_words(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit in ("B", "KB") else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"
