"""Arch's app catalogue: proper names, descriptions and a category badge (v0.1.0).

A terminal can't draw app icons, so each package gets a badge from its
category in Arch's AppStream catalogue (``archlinux-appstream-data``, the same
one Pamac uses). On a text console the badges are two letters (Javier,
3 Oct: "icon in tty version may not be visible").

Most packages aren't apps (libraries, tools): they get the plain package
badge and pacman's own description. Read once, then kept in
``~/.cache/nogforge/apps.json`` until the catalogue changes.
"""

from __future__ import annotations

import gzip
import json
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

CATALOGUE = Path("/usr/share/swcatalog/xml")
CACHE = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "nogforge" / "apps.json"
LANG = "{http://www.w3.org/XML/1998/namespace}lang"

# category → (badge, console letters, what it is in words); first match wins
KINDS = (
    ("Game", ("🎮", "GA", "Games")),
    ("Graphics", ("🎨", "GR", "Graphics")),
    ("AudioVideo", ("🎵", "AV", "Sound & video")),
    ("Audio", ("🎵", "AV", "Sound & video")),
    ("Video", ("🎵", "AV", "Sound & video")),
    ("Office", ("📝", "OF", "Office")),
    ("Network", ("🌐", "NE", "Internet")),
    ("Email", ("🌐", "NE", "Internet")),
    ("Development", ("🛠", "DE", "Development")),
    ("Education", ("🎓", "ED", "Education")),
    ("Science", ("🎓", "ED", "Education")),
    ("System", ("⚙", "SY", "System")),
    ("Settings", ("⚙", "SY", "System")),
    ("Utility", ("🔧", "UT", "Utilities")),
)
OTHER = ("📦", "--", "Other")
TYPES = ["All types"] + sorted({k[2] for _c, k in KINDS}) + ["Other"]


@dataclass(frozen=True)
class App:
    name: str
    summary: str
    categories: tuple[str, ...]

    @property
    def kind(self) -> tuple[str, str, str]:
        for cat, k in KINDS:
            if cat in self.categories:
                return k
        return OTHER


def _plain(c, tag: str) -> str:
    for e in c.findall(tag):
        if e.get(LANG) in (None, "en", "en_US"):
            return (e.text or "").strip()
    return ""


def _read(folder: Path) -> dict[str, dict]:
    apps: dict[str, dict] = {}
    for f in sorted(folder.glob("*.xml.gz")):
        try:
            for _ev, c in ET.iterparse(gzip.open(f), events=("end",)):
                if c.tag != "component":
                    continue
                pk = c.findtext("pkgname")
                if pk and c.get("type") in ("desktop-application", "desktop", "console-application"):
                    apps.setdefault(pk, {"name": _plain(c, "name"), "summary": _plain(c, "summary"),
                                         "categories": [x.text for x in c.iter("category") if x.text]})
                c.clear()
        except (OSError, ET.ParseError, EOFError):
            continue
    return apps


def _stamp(folder: Path) -> str:
    try:
        return ",".join(f"{p.name}:{p.stat().st_mtime_ns}" for p in sorted(folder.glob("*.xml.gz")))
    except OSError:
        return ""


def load(folder: Path = CATALOGUE, cache: Path = CACHE) -> dict[str, App]:
    stamp = _stamp(folder)
    raw = None
    try:
        c = json.loads(cache.read_text())
        if c.get("stamp") == stamp:
            raw = c["apps"]
    except (OSError, ValueError, KeyError):
        pass
    if raw is None:
        raw = _read(folder)
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps({"stamp": stamp, "apps": raw}))
        except OSError:
            pass
    return {k: App(v["name"], v["summary"], tuple(v["categories"])) for k, v in raw.items()}


def kind_of(name: str, apps: dict[str, App]) -> tuple[str, str, str]:
    a = apps.get(name)
    return a.kind if a else OTHER
