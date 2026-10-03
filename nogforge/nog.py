"""Talking to nog (v0.1.0).

nog does the thinking; nogForge shows it (Javier, 3 Oct 2026). Everything
here asks nog ≥ 1.6.0 for JSON — the installed list, search, the update plan —
and never works out a tier, a hold or a coupling itself.

Changes (install, remove, update) are *handed* to nog in the terminal: pacman's
own "Proceed?" and the AUR's recipe review stay where nog's rulings put them
(F-6 #38, #26), and the password comes through the system's own window
(``NOG_ASKPASS=1`` → ``sudo -A``), like grubForge.

``NOGFORGE_NOG`` points at another nog (the tests use a stand-in).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field

ASKPASS_HELPERS = ("/usr/bin/ksshaskpass", "/usr/lib/ssh/x11-ssh-askpass", "/usr/bin/ssh-askpass",
                   "/usr/lib/seahorse/ssh-askpass")


class NogError(Exception):
    """nog couldn't answer: missing, too old, or it failed. Plain words."""


def binary() -> str | None:
    """nog's program, or None when there's none that can run."""
    own = os.environ.get("NOGFORGE_NOG")
    if own:
        return own if os.path.isfile(own) and os.access(own, os.X_OK) else None
    return shutil.which("nog")


def ask(*args: str, timeout: float = 300) -> dict:
    """Run ``nog <args> --json`` and return its one JSON document."""
    nog = binary()
    if not nog:
        raise NogError("nog isn't installed. nogForge shows what nog decides, so it needs nog 1.6.0 or newer.")
    try:
        p = subprocess.run([nog, *args, "--json"], stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        raise NogError(f"nog took longer than {int(timeout)} seconds to answer.")
    except OSError as e:
        raise NogError(f"nog couldn't start: {e.strerror or e}.")
    out = p.stdout.strip()
    if p.returncode != 0 and not out:
        last = (p.stderr.strip().splitlines() or ["no reason given"])[-1]
        if "unexpected argument '--json'" in p.stderr or "unrecognized subcommand" in p.stderr:
            raise NogError("This nog is older than 1.6.0, which nogForge needs. Update it: nog install nog")
        raise NogError(f"nog stopped: {last}")
    try:
        return json.loads(out.splitlines()[-1])
    except (ValueError, IndexError):
        raise NogError("nog's answer couldn't be read.")


@dataclass
class Package:
    name: str
    version: str
    description: str = ""
    tier: int = 3
    source: str = ""
    explicit: bool = True
    installed: bool = True
    size: int = 0
    when: int = 0
    required_by: list[str] = field(default_factory=list)
    protected: str | None = None

    @property
    def aur(self) -> bool:
        return self.source == "aur"


def installed() -> list[Package]:
    d = ask("list")
    return [Package(p["name"], p["version"], p.get("description", ""), p.get("tier", 3), p.get("source", ""),
                    p.get("explicit", True), True, p.get("size", 0), p.get("installed", 0),
                    p.get("required_by") or [], p.get("protected")) for p in d.get("packages", [])]


def search(query: str) -> list[Package]:
    d = ask("search", query, timeout=120)
    return [Package(p["name"], p["version"], p.get("description", ""), p.get("tier", 3), p.get("source", ""),
                    installed=p.get("installed", False)) for p in d.get("results", [])]


def plan(keep: list[str] | None = None) -> dict:
    args = ["update"] + (["--keep", ",".join(keep)] if keep else [])
    return ask(*args, timeout=600)


def askpass_program() -> str | None:
    """The system's password window, if this computer has one."""
    own = os.environ.get("SUDO_ASKPASS")
    if own and os.access(own, os.X_OK):
        return own
    return next((p for p in ASKPASS_HELPERS if os.access(p, os.X_OK)), None)


def change_command(action: str, names: list[str]) -> tuple[list[str], dict]:
    """The nog command for a change, and the environment it runs with."""
    env = dict(os.environ)
    window = askpass_program()
    if window and (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        env["NOG_ASKPASS"] = "1"
        env["SUDO_ASKPASS"] = window
    return [binary() or "nog", action, *names], env


def describe_password(env: dict) -> str:
    return ("The system's password window asks for your password." if env.get("NOG_ASKPASS") == "1"
            else "nog asks for your password in the terminal (no password window here).")
