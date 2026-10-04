"""Talking to nog (v0.1.0).

nog does the thinking; nogForge shows it (Javier, 3 Oct 2026). Everything
here asks nog ≥ 1.7.0 for JSON — the installed list, search, the update plan —
and never works out a tier, a hold or a coupling itself.

Changes (install, remove, update) are *handed* to nog, which runs inside
nogForge's own window (forgekit's RunWindow, v1.1): pacman's own "Proceed?"
and the AUR's recipe review stay where nog's rulings put them (F-6 #38, #26),
and the password is asked by nogForge itself (``NOG_ASKPASS=1`` → ``sudo -A``,
whose helper asks the app; Javier, 4 Oct 2026). ``NOG_EVENTS`` names a file
where nog writes its steps, for the steps view.

``NOGFORGE_NOG`` points at another nog (the tests use a stand-in).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field



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
        raise NogError("nog isn't installed. nogForge shows what nog decides, so it needs nog 1.7.0 or newer.")
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
            raise NogError("This nog is older than 1.7.0, which nogForge needs. Update it: nog install nog")
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


def plan(keep: list[str] | None = None, promote: list[str] | None = None) -> dict:
    """nog's update plan; with what you keep back and what you promote, nog
    works out what must move or stay with them."""
    args = ["update"] + (["--keep", ",".join(keep)] if keep else []) + \
        (["--promote", ",".join(promote)] if promote else [])
    return ask(*args, timeout=600)


def change_command(action: str, names: list[str], events: str | None = None) -> tuple[list[str], dict]:
    """The nog command for a change, and the environment it runs with: every
    sudo nog runs asks through ``SUDO_ASKPASS`` (set by the app's password
    bridge), and nog's steps go to ``events``."""
    env = dict(os.environ)
    env["NOG_ASKPASS"] = "1"
    if events:
        env["NOG_EVENTS"] = events
    return [binary() or "nog", action, *names], env


def describe_password(env: dict) -> str:
    return "nogForge asks for your password itself, in its own window; it goes to sudo and nowhere else."
