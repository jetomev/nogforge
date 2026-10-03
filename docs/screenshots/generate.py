#!/usr/bin/env python3
"""Regenerate the README screenshots (v0.1.0) — Textual SVGs at 100 columns.

Run from the repo root (forgekit on PYTHONPATH if not installed):
    python docs/screenshots/generate.py
A stand-in nog answers from the sample below — never your own package list,
which is nobody else's business — and nothing is installed or removed. The
app catalogue is this computer's (names and badges).
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp())

now = int(time.time())


def p(name, version, desc, tier, source, explicit=True, protected=None):
    return {"name": name, "version": version, "description": desc, "tier": tier, "source": source,
            "explicit": explicit, "required_by": [], "protected": protected}


SAMPLE = {
    "list": {"nog": "1.6.0", "kind": "list", "packages": [
        p("alacritty", "0.17.0-1", "A cross-platform, OpenGL terminal emulator", 2, "extra"),
        p("dolphin", "26.08.1-1", "KDE File Manager", 2, "extra"),
        p("firefox", "143.0.2-1", "Fast, Private & Safe Web Browser", 2, "extra"),
        p("gimp", "3.2.6-2", "GNU Image Manipulation Program", 3, "extra"),
        p("keepassxc", "2.7.12-5", "Cross-platform community-driven port of KeePass", 3, "extra"),
        p("linux-zen", "7.2.7.zen1-1", "The Linux ZEN kernel and modules", 1, "extra",
          protected="the system needs this to start"),
        p("nog", "1.6.0-1", "A tier-aware package manager for Arch Linux", 2, "aur"),
        p("steam", "1.0.0.87-3", "Valve's digital software delivery system", 3, "multilib"),
        p("thunderbird", "156.0-1", "Standalone mail and news reader from mozilla.org", 3, "extra"),
        p("vlc", "3.0.23_2-16", "Multi-platform MPEG, VCD/DVD, and DivX player", 3, "extra"),
        p("glibc", "2.44", "GNU C Library", 1, "core", explicit=False, protected="part of the base system"),
    ]},
    "search": {"nog": "1.6.0", "kind": "search", "query": "paint", "results": [
        {"name": "krita", "version": "6.0.4-2", "description": "Edit and paint images", "source": "extra",
         "installed": False, "tier": 3},
        {"name": "pinta", "version": "3.0.3-1", "description": "Drawing/editing program modeled after Paint.NET",
         "source": "extra", "installed": False, "tier": 3},
        {"name": "gimp", "version": "3.2.6-2", "description": "GNU Image Manipulation Program", "source": "extra",
         "installed": True, "tier": 3},
        {"name": "mypaint", "version": "2.0.1-15", "description": "A fast and easy painting application",
         "source": "extra", "installed": False, "tier": 3},
        {"name": "krita-ai-diffusion", "version": "1.53.0-1", "description": "Generative AI plugin for Krita",
         "source": "aur", "installed": False, "tier": 3},
    ]},
    "update": {"nog": "1.6.0", "kind": "plan",
               "sources": {"aur": "checked", "flatpak": "checked", "snap": "checked", "chaotic_aur_off": False},
               "ready": [{"name": "tzdata", "source": "core", "tier": 3, "old": "2026d-1", "new": "2026e-1",
                          "note": "hold just expired"},
                         {"name": "thunderbird", "source": "extra", "tier": 3, "old": "156.0-1", "new": "156.0.1-1",
                          "note": "2 days past window"},
                         {"name": "vlc", "source": "extra", "tier": 3, "old": "3.0.23_2-16", "new": "3.0.23_2-17",
                          "note": "hold just expired"}],
               "held": [{"name": "linux-zen", "source": "extra", "tier": 1, "old": "7.2.7.zen1-1",
                         "new": "7.2.8.zen1-2", "note": "28 days remaining", "ready_on": now + 28 * 86400},
                        {"name": "firefox", "source": "extra", "tier": 2, "old": "143.0.2-1", "new": "144.0-1",
                         "note": "11 days remaining", "ready_on": now + 11 * 86400},
                        {"name": "gimp", "source": "extra", "tier": 3, "old": "3.2.6-2", "new": "3.2.8-1",
                         "note": "4 days remaining", "ready_on": now + 4 * 86400}],
               "unknown": [], "holds": {"tier1_days": 30, "tier2_days": 15, "tier3_days": 7}},
}
STAND_IN = '''#!/usr/bin/env python3
import json, os, sys
d = json.load(open(os.environ["NOGFORGE_TEST_DATA"]))
if sys.argv[1:] == ["--version"]:
    print("nog 1.6.0"); sys.exit(0)
print(json.dumps(d[sys.argv[1]]))
'''


def shot(app, name: str) -> None:
    app.save_screenshot(filename=f"{name}.svg", path=str(OUT))
    print(f"  {name}.svg")


async def main() -> None:
    (TMP / "data.json").write_text(json.dumps(SAMPLE))
    nog = TMP / "nog"
    nog.write_text(STAND_IN)
    nog.chmod(0o755)
    os.environ["NOGFORGE_NOG"] = str(nog)
    os.environ["NOGFORGE_TEST_DATA"] = str(TMP / "data.json")
    logs = TMP / "logs"
    logs.mkdir()
    (logs / "20261003 nog-runs.csv").write_text(
        "date,time,user,command,status,outcome\n"
        "10/03/2026,09:12 AM,you,install krita,0,done\n"
        "10/02/2026,04:52 PM,you,update,0,done\n"
        "10/01/2026,08:30 PM,you,remove cowsay,0,done\n")
    cache = TMP / "pkg"
    cache.mkdir()
    (cache / "example-1-1-x86_64.pkg.tar.zst").write_bytes(b"x" * 4096)
    from unittest import mock
    from nogforge.app import NogForgeApp
    with mock.patch("nogforge.app.count_flatpaks", return_value=2), \
            mock.patch("nogforge.app.count_snaps", return_value=1):
        app = NogForgeApp(logs=logs, cache_dir=cache)
        app.set_title_status = lambda text: NogForgeApp.set_title_status(app, "your-computer · nog 1.6.0")
        async with app.run_test(size=(100, 32)) as pilot:
            await pilot.pause(2.0)
            shot(app, "01-dashboard")
            await pilot.press("2")
            await pilot.pause(0.6)
            shot(app, "02-home")
            await pilot.press("3")
            for ch in "paint":
                await pilot.press(ch)
            await pilot.press("enter")
            await pilot.pause(1.5)
            shot(app, "03-search")
            await pilot.press("enter")
            await pilot.pause(0.8)
            shot(app, "04-review")
            await pilot.press("escape")
            await pilot.press("4")
            await pilot.pause(0.6)
            ready = app.query_one("#up-ready")
            ready.focus()
            ready.highlighted = 1
            await pilot.press("space")                 # keep one back
            await pilot.pause(1.0)
            shot(app, "05-update")
            await pilot.press("5")
            await pilot.pause(0.6)
            shot(app, "06-tiers")
            await pilot.press("6")
            await pilot.pause(0.5)
            shot(app, "07-history")
    print("nogForge screenshots done.")


asyncio.run(main())
