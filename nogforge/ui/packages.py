"""The package table every screen shares (v0.1.0, Javier's design of 3 Oct).

Spreadsheet style: a heading row, then two lines per package — Icon · Name ·
Version · Tier (written out) · Option at the right, and the description on
the line under it, with no heading — and every other package shaded.

Textual's own table can't put a line under a row that spans the columns, so
this is an option list whose options are drawn here, to the width it has.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rich.text import Text
from textual.binding import Binding
from textual.message import Message
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from forgekit.console import is_console

from .. import catalogue
from ..nog import Package

ICON_W, NAME_W, VER_W, TIER_W, OPTION_W, TICK_W = 3, 24, 26, 9, 17, 4


def colours(app) -> dict[str, str]:
    """forgekit's colour roles in the names Rich (which draws tables and rows)
    understands. On a text console the roles are Textual's console colours,
    ``ansi_bright_cyan``, which Rich calls ``bright_cyan``: passing them
    unchanged crashed nogForge on a console (found in the console check)."""
    out = {}
    for k, v in app.get_css_variables().items():
        v = str(v).strip()
        out[k] = v[5:] if v.startswith("ansi_") else v
    return out


def cs_warn(colours: dict) -> str:
    return colours.get("forge-warn", "")


def name_width(width: int, ver_w: int, extra: bool) -> int:
    """The name column gives up room first when a list is narrow (rows and
    headings use the same rule, so they line up)."""
    need = ICON_W + NAME_W + ver_w + TIER_W + (10 if extra else 0) + OPTION_W
    return max(12, NAME_W - max(0, need - width))


def cell(text: str, width: int) -> str:
    """Cut to fit, with an ellipsis, then pad: a column never spills."""
    if len(text) > width - 1:
        text = text[: width - 2] + "…"
    return text.ljust(width)


@dataclass
class Row:
    """One package as a screen shows it."""
    package: Package
    option: str            # the words in the Option column, "" for none
    option_role: str       # forgekit role for its colour: danger, ok, accent, muted
    version: str = ""      # overrides the package's version (e.g. "1.0 → 1.1")
    extra: str = ""        # an extra column (Ready on) after Tier
    note: str = ""         # first on the description line (nog's words)
    tick: bool | None = None   # a tick box before the icon (Update's Ready list); None = no box
    note_role: str = ""    # the note's colour role (warn for "must stay back")


class PackageHeader(Static):
    def __init__(self, extra: str = "", option: bool = True, ver_w: int = VER_W, ticks: bool = False,
                 **kw) -> None:
        super().__init__("", **kw)
        self.extra, self.option, self.ver_w, self.ticks = extra, option, ver_w, ticks

    def on_resize(self) -> None:
        self.refresh_header()

    def on_mount(self) -> None:
        self.refresh_header()

    def refresh_header(self) -> None:
        w = max(self.size.width - 2, 80)          # the list below has a border on each side
        s = (" " * TICK_W if self.ticks else "") + " " * ICON_W + \
            cell("Name", name_width(w - (TICK_W if self.ticks else 0), self.ver_w, bool(self.extra))) + \
            cell("Version", self.ver_w) + cell("Tier", TIER_W)
        if self.extra:
            s += cell(self.extra, 10)
        s = s.ljust(w - OPTION_W) + ("Option" if self.option else "")
        self.update(Text(s, style="bold"))


class PackageList(OptionList):
    """Rows of packages. Enter (or Del, for a removal) asks for the row's option."""

    BINDINGS = [Binding("delete", "act", "", show=False)]

    class Act(Message):
        def __init__(self, row: Row) -> None:
            super().__init__()
            self.row = row

    def __init__(self, apps: dict | None = None, ver_w: int = VER_W, **kw) -> None:
        super().__init__(**kw)
        self.apps = apps or {}
        self.ver_w = ver_w
        self.rows: list[Row] = []

    def show(self, rows: list[Row]) -> None:
        self.rows = rows
        self._redraw()

    def on_resize(self) -> None:
        if self.rows:
            self._redraw()

    def _redraw(self) -> None:
        keep = self.highlighted
        cs = colours(self.app)
        w = max(self.size.width - 2, 80)
        # on a console the shade and the selected row are the same blue: there
        # the selection alone marks the row
        shade = "" if is_console() else cs.get("forge-raised", "")
        self.clear_options()
        self.add_options([Option(self.draw(r, i, w, cs, shade), id=str(i)) for i, r in enumerate(self.rows)])
        if self.rows:
            self.highlighted = min(keep or 0, len(self.rows) - 1)

    def draw(self, r: Row, i: int, width: int, colours: dict, shade: str) -> Text:
        p = r.package
        app = self.apps.get(p.name)
        badge, letters, kind = catalogue.kind_of(p.name, self.apps)
        icon = letters if is_console() else badge
        name = app.name if app and app.name else p.name
        desc = (app.summary if app and app.summary else p.description) or ""
        bits = [desc, kind if kind != "Other" else "", "AUR" if p.aur else p.source]
        desc = " · ".join(b for b in bits if b)
        # the name gives up room first when the list is narrow; nothing spills
        box = TICK_W if r.tick is not None else 0
        name_w = name_width(width - box, self.ver_w, bool(r.extra))
        first = Text()
        if r.tick is not None:
            first.append("[x] " if r.tick else "[ ] ", style="" if r.tick else cs_warn(colours))
        first.append(icon)
        first.append(" " * max(ICON_W - Text(icon).cell_len, 1))        # emoji are two columns wide
        first.append(cell(name, name_w), style="bold" if r.option_role != "muted" else colours.get("forge-muted", ""))
        first.append(cell(r.version or p.version, self.ver_w))
        first.append(cell(f"Tier {p.tier}", TIER_W))
        if r.extra:
            first.append(cell(r.extra, 10))
        pad = width - OPTION_W - first.cell_len
        first.append(" " * max(pad, 1))
        first.append(r.option, style=colours.get(f"forge-{r.option_role}", ""))
        first.append(" " * max(width - first.cell_len, 0))      # the shading reaches the right edge
        second = Text(" " * (box + ICON_W))
        if r.note:
            second.append(r.note, style=colours.get(f"forge-{r.note_role}", "") if r.note_role
                          else colours.get("forge-muted", ""))
            if desc:
                second.append(" · ", style=colours.get("forge-muted", ""))
        second.append(desc, style=colours.get("forge-muted", ""))
        if second.cell_len > width:
            second.truncate(width - 1)
            second.append("…", style=colours.get("forge-muted", ""))
        second.append(" " * max(width - second.cell_len, 0))     # the shading reaches the edge here too
        first.truncate(width)
        second.truncate(width)
        t = Text("\n").join([first, second])
        if i % 2 and shade:
            t.stylize(f"on {shade}")
        return t

    def current(self) -> Row | None:
        if self.highlighted is None or not self.rows:
            return None
        return self.rows[self.highlighted]

    def on_option_list_option_selected(self, e: OptionList.OptionSelected) -> None:
        e.stop()
        row = self.rows[int(e.option.id)]
        if row.option:
            self.post_message(self.Act(row))

    def action_act(self) -> None:
        row = self.current()
        if row and row.option:
            self.post_message(self.Act(row))


def installed_row(p: Package) -> Row:
    if p.protected:
        return Row(p, ("Locked" if is_console() else "🔒 Locked"), "muted")
    return Row(p, ("Remove" if is_console() else "✕ Remove"), "danger")


def search_row(p: Package) -> Row:
    if p.installed:
        return Row(p, ("Yours" if is_console() else "✓ Yours"), "muted")
    return Row(p, ("Install" if is_console() else "+ Install"), "ok")


def filtered(pkgs: list[Package], show: str, kind: str, find: str, apps: dict,
             test: Callable[[Package], bool] | None = None) -> list[Package]:
    """Home's Show / Type / Find."""
    out = []
    f = find.strip().lower()
    for p in pkgs:
        if show == "yours" and not p.explicit:
            continue
        if show == "aur" and not p.aur:
            continue
        if kind and kind != "All types" and catalogue.kind_of(p.name, apps)[2] != kind:
            continue
        if f:
            a = apps.get(p.name)
            hay = " ".join([p.name, p.description, a.name if a else "", a.summary if a else ""]).lower()
            if f not in hay:
                continue
        if test and not test(p):
            continue
        out.append(p)
    return out
