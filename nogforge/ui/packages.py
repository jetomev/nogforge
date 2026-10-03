"""The tables every screen shares (Javier's design of 3 Oct, and his notes of
his first run).

Spreadsheet style: a heading row, then two lines per entry — the cells, and the
description underneath with no heading — every other entry shaded, and the
selected one clearly different from both (they were the same colour). Package
tables: Icon · Name · Version · Tier · Repository · Option. Long names and
versions are cut with "…" so the columns stay put.

The Option cell is drawn as a button: grey, blue under the mouse, and a click
on it acts. A click anywhere else on the row only selects the row, so a stray
click never starts an install. Enter acts too; Space ticks a box (Update).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rich.text import Text
from textual import events
from textual.binding import Binding
from textual.message import Message
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from forgekit.console import is_console

from .. import catalogue
from ..nog import Package

ICON_W, NAME_W, VER_W, TIER_W, REPO_W, OPTION_W, TICK_W = 3, 22, 22, 8, 13, 16, 4


def colours(app) -> dict[str, str]:
    """forgekit's colour roles in the names Rich (which draws these rows)
    understands. On a text console the roles are Textual's console colours,
    ``ansi_bright_cyan``, which Rich calls ``bright_cyan``: passing them
    unchanged crashed nogForge on a console (found in the console check)."""
    out = {}
    for k, v in app.get_css_variables().items():
        v = str(v).strip()
        out[k] = v[5:] if v.startswith("ansi_") else v
    return out


def cell(text: str, width: int) -> str:
    """Cut to fit, with an ellipsis, then pad: a column never spills."""
    if len(text) > width - 1:
        text = text[: width - 2] + "…"
    return text.ljust(width)


def name_width(width: int, ver_w: int, extra: bool, tick: bool) -> int:
    """The name column gives up room first when a list is narrow (rows and
    headings use the same rule, so they line up)."""
    need = (TICK_W if tick else 0) + ICON_W + NAME_W + ver_w + TIER_W + REPO_W + (10 if extra else 0) + OPTION_W
    return max(12, NAME_W - max(0, need - width))


@dataclass
class Row:
    """One package as a screen shows it."""
    package: Package
    option: str            # the Option button's words ("✕ Remove"); "" for none
    option_role: str       # danger / ok / accent: what it does; muted = not a button (Locked, Yours)
    version: str = ""      # overrides the package's version (e.g. "1.0 → 1.1")
    extra: str = ""        # an extra column (Ready on) after Tier
    note: str = ""         # first on the description line (nog's words)
    tick: bool | None = None   # a tick box before the icon (Update's Ready list); None = no box
    note_role: str = ""    # the note's colour role (warn for "must stay back")


def repository(p: Package) -> str:
    return "AUR" if p.aur else (p.source or "—")


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
            cell("Name", name_width(w, self.ver_w, bool(self.extra), self.ticks)) + \
            cell("Version", self.ver_w) + cell("Tier", TIER_W) + (cell(self.extra, 10) if self.extra else "") + \
            cell("Repository", REPO_W)
        s = s.ljust(w - OPTION_W) + ("Option" if self.option else "")
        self.update(Text(s, style="bold"))


class PackageList(OptionList):
    """Rows of packages, with an Option button on each."""

    BINDINGS = [Binding("delete", "act", "", show=False), Binding("space", "tick", "", show=False)]

    class Act(Message):
        def __init__(self, row: Row) -> None:
            super().__init__()
            self.row = row

    class Tick(Message):
        def __init__(self, row: Row) -> None:
            super().__init__()
            self.row = row

    def __init__(self, apps: dict | None = None, ver_w: int = VER_W, **kw) -> None:
        super().__init__(**kw)
        self.apps = apps or {}
        self.ver_w = ver_w
        self.rows: list[Row] = []
        self.hover: int | None = None             # the row whose button is under the mouse

    def show(self, rows: list[Row]) -> None:
        self.rows = rows
        self.hover = None
        self._redraw()

    def on_resize(self) -> None:
        if self.rows:
            self._redraw()

    @property
    def row_width(self) -> int:
        return max(self.size.width - 2, 80)

    def _redraw(self) -> None:
        keep = self.highlighted
        cs = colours(self.app)
        self.clear_options()
        self.add_options([Option(self.draw(r, i, self.row_width, cs), id=str(i)) for i, r in enumerate(self.rows)])
        if self.rows:
            self.highlighted = min(keep or 0, len(self.rows) - 1)

    def _redraw_row(self, i: int) -> None:
        if 0 <= i < len(self.rows):
            self.replace_option_prompt_at_index(i, self.draw(self.rows[i], i, self.row_width, colours(self.app)))

    def option_start(self) -> int:
        """Where the Option button starts, in columns from the row's left edge."""
        return self.row_width - OPTION_W

    def draw(self, r: Row, i: int, width: int, cs: dict) -> Text:
        p = r.package
        app = self.apps.get(p.name)
        badge, letters, kind = catalogue.kind_of(p.name, self.apps)
        icon = letters if is_console() else badge
        name = app.name if app and app.name else p.name
        desc = (app.summary if app and app.summary else p.description) or ""
        desc = " · ".join(b for b in (desc, kind if kind != "Other" else "") if b)
        muted = cs.get("forge-muted", "")
        tick = r.tick is not None
        name_w = name_width(width, self.ver_w, bool(r.extra), tick)
        first = Text()
        if tick:
            first.append("[x] " if r.tick else "[ ] ", style="" if r.tick else cs.get("forge-warn", ""))
        first.append(icon)
        first.append(" " * max(ICON_W - Text(icon).cell_len, 1))        # emoji are two columns wide
        first.append(cell(name, name_w), style="bold" if r.option_role != "muted" or not r.option else muted)
        first.append(cell(r.version or p.version, self.ver_w))
        first.append(cell(f"Tier {p.tier}", TIER_W))
        if r.extra:
            first.append(cell(r.extra, 10))
        first.append(cell(repository(p), REPO_W))
        first.append(" " * max(width - OPTION_W - first.cell_len, 1))
        first.append(self.button(r, i, cs))
        first.append(" " * max(width - first.cell_len, 0))      # the shading reaches the right edge
        first.truncate(width)
        lead = TICK_W if tick else 0
        second = Text(" " * (lead + ICON_W))
        if r.note:
            second.append(r.note, style=cs.get(f"forge-{r.note_role}", "") if r.note_role else muted)
            if desc:
                second.append(" · ", style=muted)
        second.append(desc, style=muted)
        if second.cell_len > width:
            second.truncate(width - 1)
            second.append("…", style=muted)
        second.append(" " * max(width - second.cell_len, 0))
        t = Text("\n").join([first, second])
        # every other row shaded; never on a console, where the shade is the selection's blue
        if i % 2 and not is_console() and cs.get("forge-surface"):
            t.stylize_before(f"on {cs['forge-surface']}")     # under the cells: the button keeps its grey
        return t

    def button(self, r: Row, i: int, cs: dict) -> Text:
        """The Option cell: a button (grey; blue under the mouse), or plain words when it isn't one."""
        if not r.option:
            return Text("")
        if r.option_role == "muted":
            return Text(r.option, style=cs.get("forge-muted", ""))
        words = f" {r.option} ".ljust(OPTION_W - 1)
        if i == self.hover:
            return Text(words, style=f"bold {cs.get('forge-primary', '')} on {cs.get('forge-primary-bg', '')}")
        if i == self.highlighted:          # the selected row is button-grey itself: a lighter grey shows the button
            return Text(words, style=f"{cs.get('forge-button', '')} on {cs.get('forge-button-hover', '')}")
        return Text(words, style=f"{cs.get('forge-button', '')} on {cs.get('forge-button-bg', '')}")

    def watch_highlighted(self, before: int | None, after: int | None) -> None:
        """Redraw the rows the selection left and reached (their buttons change grey)."""
        super().watch_highlighted(after)            # Textual's own: scrolls the row into view
        for j in (before, after):
            if j is not None and self.rows and j < len(self.rows) and self.option_count == len(self.rows):
                self._redraw_row(j)

    def current(self) -> Row | None:
        if self.highlighted is None or not self.rows:
            return None
        return self.rows[self.highlighted]

    # ── keys ────────────────────────────────────────────────────────────────
    def on_option_list_option_selected(self, e: OptionList.OptionSelected) -> None:
        e.stop()
        row = self.rows[int(e.option.id)]
        if row.option:
            self.post_message(self.Act(row))

    def action_act(self) -> None:
        row = self.current()
        if row and row.option:
            self.post_message(self.Act(row))

    def action_tick(self) -> None:
        row = self.current()
        if row and row.tick is not None:
            self.post_message(self.Tick(row))

    # ── the mouse: the button hovers and clicks; the rest of the row selects ─
    def _on_button_area(self, x: int) -> bool:
        return x - 1 >= self.option_start()          # 1: the border

    def _on_mouse_move(self, event: events.MouseMove) -> None:
        super()._on_mouse_move(event)
        i = event.style.meta.get("option")
        over = i if (i is not None and self._on_button_area(event.x)) else None
        if over != self.hover:
            before, self.hover = self.hover, over
            for j in (before, over):
                if j is not None:
                    self._redraw_row(j)

    def on_leave(self, _event) -> None:
        if self.hover is not None:
            before, self.hover = self.hover, None
            self._redraw_row(before)

    async def _on_click(self, event: events.Click) -> None:
        i = event.style.meta.get("option")
        if i is None:
            return
        event.stop()
        event.prevent_default()        # Textual's own click would "select" the row: that acts (found by a test)
        self.highlighted = i
        row = self.rows[i]
        if row.tick is not None and event.x - 1 < TICK_W:
            self.post_message(self.Tick(row))          # the box itself
        elif self._on_button_area(event.x) and row.option:
            self.post_message(self.Act(row))           # the button
        self.focus()


def installed_row(p: Package) -> Row:
    if p.protected:
        return Row(p, ("Locked" if is_console() else "🔒 Locked"), "muted")
    return Row(p, ("Remove" if is_console() else "✕ Remove"), "danger")


def search_row(p: Package, explicit: bool | None = None) -> Row:
    """In Install: what you chose says Yours, what came along says Installed
    (Javier's run: perl said "Yours" — it only came as a dependency)."""
    if p.installed:
        word = "Yours" if explicit else "Installed"
        return Row(p, (word if is_console() else f"✓ {word}"), "muted")
    return Row(p, ("Install" if is_console() else "+ Install"), "ok")


TIERS = [("All tiers", "0"), ("Tier 1", "1"), ("Tier 2", "2"), ("Tier 3", "3")]


def repo_key(p: Package) -> str:
    return "aur" if p.aur else p.source


def filtered(pkgs: list[Package], show: str, kind: str, find: str, apps: dict, tier: str = "0",
             repos: set[str] | None = None, test: Callable[[Package], bool] | None = None) -> list[Package]:
    """The filter bar: Show / Type / Tier / Repositories / Search."""
    out = []
    f = find.strip().lower()
    for p in pkgs:
        if show == "yours" and not p.explicit:
            continue
        if kind and kind != "All types" and catalogue.kind_of(p.name, apps)[2] != kind:
            continue
        if tier and tier != "0" and str(p.tier) != tier:
            continue
        if repos is not None and repo_key(p) not in repos:
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


def relevant(pkgs: list[Package], query: str, apps: dict) -> list[Package]:
    """Install's results: only those with the words in the name or the
    description (pacman also matches what a package provides: "calc" found
    perl), names first."""
    q = query.strip().lower()
    if not q:
        return pkgs

    def where(p: Package) -> int:
        """0 the exact name · 1 a name starting with it · 2 a name with it · 3 the description · 4 no."""
        a = apps.get(p.name)
        names = [p.name.lower()] + ([a.name.lower()] if a and a.name else [])
        if q in names:
            return 0
        if any(n.startswith(q) for n in names):
            return 1
        if any(q in n for n in names):
            return 2
        if q in p.description.lower() or (a and q in a.summary.lower()):
            return 3
        return 4
    # the repositories before the AUR at the same rank: they're built and signed by the distribution
    return sorted((p for p in pkgs if where(p) < 4), key=lambda p: (where(p), p.aur, p.name))
