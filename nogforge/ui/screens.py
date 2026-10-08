"""nogForge's screens: Dashboard, In-System, Install, Update, History ▸
Activity and nog Logs (after Javier's first run, 3 Oct).

Drawn from the approved design (docs/design/v0.1-screens.html) and his notes:
In-System and Install share one filter bar — Search with its button, Type,
Tier, Repositories — with the same names and the same behaviour; tables in
the spreadsheet style; options at the right as buttons; screen buttons at the
top; buttons that say "Words (k)". Tiers was folded away ("isn't needed").
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from rich.markup import escape
from rich.table import Table
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, ScrollableContainer, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Input, OptionList, Select, Static
from textual.widgets.option_list import Option

from forgekit import CheckList, ForgeModal, glyph
from forgekit.console import is_console

from .. import catalogue, records
from .packages import (
    TIERS, PackageHeader, PackageList, Row, cell, colours, filtered, installed_row, relevant, search_row,
)

SOURCES = ["core", "extra", "multilib", "chaotic-aur", "aur", "Flatpak", "Snap"]
PACMAN_CONF = Path("/etc/pacman.conf")


def label(src: str) -> str:
    return "AUR" if src == "aur" else src


def repositories(conf: Path = PACMAN_CONF) -> list[str]:
    """This computer's repositories, in pacman.conf's order, and the AUR."""
    try:
        names = re.findall(r"^\s*\[([^\]]+)\]", conf.read_text(), re.M)
    except OSError:
        names = ["core", "extra", "multilib"]
    return [n for n in names if n != "options"] + ["aur"]


def table(app, columns: list[str], rows: list[list[str]], foot: list[str] | None = None) -> Table:
    """A spreadsheet-style table for the Dashboard: headings, every other row shaded."""
    c = colours(app)
    shade = c.get("forge-surface") if not is_console() else None
    t = Table(box=None, padding=(0, 1, 0, 0), pad_edge=False, show_edge=False, expand=False,
              header_style=f"bold {c.get('forge-accent', '')}", row_styles=["", f"on {shade}"] if shade else None)
    for col in columns:
        t.add_column(col, no_wrap=True)
    for r in rows:
        t.add_row(*r)
    if foot:
        t.add_row(*[Text(x, style="bold") for x in foot], style="")
    return t


def search_label() -> str:
    return "Search (Enter)" if is_console() else "🔍 Search (Enter)"


# ── the filter bar In-System and Install share ───────────────────────────────
SCREEN_KEYS = {"1": "dashboard", "2": "insystem", "3": "install", "4": "update", "5": "activity", "6": "noglogs"}


class SearchInput(Input):
    """The Search box. While it's empty, the screen keys 1–6 still switch
    screens (found in testing: opening Install put the cursor here, and the
    next screen key was typed in as text). Once you type, digits are text."""

    async def _on_key(self, event) -> None:
        if not self.value and event.character and event.character in "123456":
            event.prevent_default()                 # the box doesn't type it...
            self.app.action_go(SCREEN_KEYS[event.character])   # ...the screen key works
            event.stop()
            return
        await super()._on_key(event)

class RepositoriesDialog(ForgeModal[set | None]):
    """Which repositories to show: tick and untick (Javier: "a button leading to
    a pop-up with the repositories available to select and de-select")."""

    def __init__(self, names: list[str], chosen: set[str]) -> None:
        super().__init__()
        self.names, self.chosen = names, chosen

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel"):
            yield Static("Repositories", classes="forge-panel-title")
            yield Static("[$forge-muted]Show packages from the ticked ones. Space ticks; Enter or Done (d) closes.[/]")
            yield CheckList(*[(label(n), n, n in self.chosen) for n in self.names], id="rp-list")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("All (a)", id="rp-all")
                yield Button("Done (d)", id="rp-done", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#rp-list").focus()

    def on_key(self, e) -> None:
        if e.key in ("enter", "d"):
            e.stop()
            self.dismiss(set(self.query_one("#rp-list", CheckList).selected))
        elif e.key == "a":
            e.stop()
            self.query_one("#rp-list", CheckList).select_all()
        elif e.key == "escape":
            e.stop()
            self.dismiss(None)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        if e.button.id == "rp-all":
            self.query_one("#rp-list", CheckList).select_all()
        else:
            self.dismiss(set(self.query_one("#rp-list", CheckList).selected))


class FilterBar(Vertical):
    """Search ▸ 🔍 · Show · Type · Tier · Repositories — the same on both screens."""

    class Changed(Message):
        """The filters changed (not the search words: those wait for the button or Enter)."""

    class Searched(Message):
        def __init__(self, words: str, final: bool = False) -> None:
            super().__init__()
            self.words = words
            self.final = final      # True on Enter: the keyboard may move to the list; False while typing

    def __init__(self, prefix: str, show: bool, **kw) -> None:
        super().__init__(classes="nf-filters", **kw)
        self.prefix, self.with_show = prefix, show
        self.repos: set[str] | None = None            # None: all of them

    LIVE_WAIT = 0.5          # Install asks nog: wait this long after the last keystroke (#21)
    LIVE_MIN = 2             # ...and only from two characters on

    def compose(self) -> ComposeResult:
        p = self.prefix
        with Horizontal(classes="nf-bar"):
            yield Static("Search", classes="nf-label -lead")
            yield SearchInput(placeholder="a name or what it does — the list follows as you type", id=f"{p}-find")
        with Horizontal(classes="nf-bar -last"):
            # Javier, 3 Oct: the boxes line up on the left: the first label of each line is one width
            if self.with_show:
                yield Static("Show", classes="nf-label -lead")
                yield Select([("Yours", "yours"), ("All", "all")], value="yours", allow_blank=False, id=f"{p}-show")
            yield Static("Type", classes="nf-label" if self.with_show else "nf-label -lead")
            yield Select([(t, t) for t in catalogue.TYPES], value="All types", allow_blank=False, id=f"{p}-type")
            yield Static("Tier", classes="nf-label")
            yield Select(TIERS, value="0", allow_blank=False, id=f"{p}-tier")
            with Horizontal(classes="forge-buttons nf-inline"):
                yield Button("Repositories (p)", id=f"{p}-repos")

    def values(self) -> dict:
        p = self.prefix
        return {"show": self.query_one(f"#{p}-show", Select).value if self.with_show else "all",
                "kind": self.query_one(f"#{p}-type", Select).value,
                "tier": self.query_one(f"#{p}-tier", Select).value,
                "repos": self.repos, "words": self.query_one(f"#{p}-find", Input).value.strip()}

    @on(Select.Changed)
    def _select(self, e: Select.Changed) -> None:
        e.stop()
        self.post_message(self.Changed())

    @on(Input.Submitted)
    def _enter(self, e: Input.Submitted) -> None:
        e.stop()
        self._cancel_pending()
        self.post_message(self.Searched(e.value.strip(), final=True))

    _pending = None

    def _cancel_pending(self) -> None:
        if self._pending is not None:
            self._pending.stop()
            self._pending = None

    @on(Input.Changed)
    def _typed(self, e: Input.Changed) -> None:
        """Javier (2026-10-07): every search follows as you type, no button. In-System
        filters what is already here, at once. Install asks nog, so it waits LIVE_WAIT after the
        last keystroke and needs LIVE_MIN characters (an emptied box clears the results at once)."""
        e.stop()
        words = e.value.strip()
        self._cancel_pending()
        if self.prefix == "in" and words and len(words) < self.LIVE_MIN:
            return
        if self.prefix == "in" and words:
            self._pending = self.set_timer(self.LIVE_WAIT, lambda: self.post_message(self.Searched(words)))
            return
        self.post_message(self.Searched(words))

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == f"{self.prefix}-repos":
            e.stop()
            self.choose_repositories()

    def choose_repositories(self) -> None:
        names = repositories(getattr(self.app, "pacman_conf", PACMAN_CONF))
        chosen = self.repos if self.repos is not None else set(names)

        def done(picked) -> None:
            if picked is None:
                return
            self.repos = None if picked >= set(names) else picked
            n = len(names) if self.repos is None else len(self.repos)
            self.query_one(f"#{self.prefix}-repos", Button).label = (
                "Repositories (p)" if self.repos is None else f"Repositories: {n} of {len(names)} (p)")
            self.post_message(self.Changed())
        self.app.push_screen(RepositoriesDialog(names, chosen), done)


# ── Dashboard ────────────────────────────────────────────────────────────────
class DashboardScreen(VerticalScroll, can_focus=False):
    FORGE_HINTS = [("u", "updates"), ("r", "packages"), ("c", "clean up"), ("1-6", "screens"), ("F1", "help"), ("?", "all keys")]

    def compose(self) -> ComposeResult:
        with Grid(id="nf-dash"):
            with Vertical(classes="nf-box", id="box-updates"):
                yield Static("", id="db-updates")
                with Horizontal(classes="forge-buttons nf-box-buttons"):
                    yield Button("Review Updates (u)", id="db-review-updates", variant="primary")
            with Vertical(classes="nf-box", id="box-yours"):
                yield Static("", id="db-yours")
                with Horizontal(classes="forge-buttons nf-box-buttons"):
                    yield Button("Review Packages (r)", id="db-review-packages", variant="primary")
            with Vertical(classes="nf-box", id="box-recent"):
                yield Static("", id="db-recent")
                with Horizontal(classes="forge-buttons nf-box-buttons"):
                    yield Button("Open History (h)", id="db-history")
            with Vertical(classes="nf-box", id="box-space"):
                yield Static("", id="db-space")
                with Horizontal(classes="forge-buttons nf-box-buttons"):
                    yield Button("Clean Up (c)", id="db-clean")

    def on_mount(self) -> None:
        for box, title in (("box-updates", "Updates"), ("box-yours", "Yours"), ("box-recent", "Recent"),
                           ("box-space", "Space")):
            self.query_one(f"#{box}").border_title = title
        self.refresh_view()

    def refresh_view(self) -> None:
        app = self.app
        m = "$forge-muted"
        plan = app.plan
        if app.plan_error:
            self.query_one("#db-updates", Static).update(f"[$forge-warn]{glyph('warn')} {app.plan_error}[/]")
        elif plan is None:
            self.query_one("#db-updates", Static).update(
                f"[{m}]Asking nog what's waiting{glyph('ellipsis')} (it checks every source; up to a minute)[/]")
        else:
            rows, tot = [], Counter()
            for src in SOURCES:
                ready = [r for r in plan["ready"] if source_of(r) == src]
                held = [r for r in plan["held"] + plan.get("unknown", []) if source_of(r) == src]
                tiers = Counter(r["tier"] for r in ready + held)
                if src in ("Flatpak", "Snap") and not (ready or held):
                    state = plan.get("sources", {}).get(src.lower(), "")
                    rows.append([src, "0", "0", "0", "0", "0"] if state == "checked" else
                                [src, Text(state or "—", style=colours(app).get("forge-muted", "")), "", "", "", ""])
                    continue
                if not (ready or held) and src not in ("core", "extra"):
                    continue
                rows.append([label(src), str(len(ready)), str(len(held)), str(tiers[1]), str(tiers[2]), str(tiers[3])])
                tot.update({"r": len(ready), "h": len(held), 1: tiers[1], 2: tiers[2], 3: tiers[3]})
            self.query_one("#db-updates", Static).update(table(app, ["Source", "Ready", "Held", "Tier 1", "Tier 2",
                                                                     "Tier 3"], rows,
                                                               ["Total", str(tot["r"]), str(tot["h"]), str(tot[1]),
                                                                str(tot[2]), str(tot[3])]))
        if app.packages_error:
            self.query_one("#db-yours", Static).update(f"[$forge-warn]{glyph('warn')} {app.packages_error}[/]")
        else:
            mine = [p for p in app.packages if p.explicit]
            rows, tot = [], Counter()
            for src in sorted({p.source for p in mine}, key=lambda s: (SOURCES + [s]).index(s)):
                ps = [p for p in mine if p.source == src]
                t = Counter(p.tier for p in ps)
                rows.append([label(src), str(len(ps)), str(t[1]), str(t[2]), str(t[3])])
                tot.update({"n": len(ps), 1: t[1], 2: t[2], 3: t[3]})
            for src, n in (("Flatpak", app.flatpaks), ("Snap", app.snaps)):
                if n is not None:
                    rows.append([src, str(n), "0", "0", str(n)])
                    tot.update({"n": n, 3: n})
            self.query_one("#db-yours", Static).update(table(app, ["Source", "Yours", "Tier 1", "Tier 2", "Tier 3"],
                                                             rows, ["Total", str(tot["n"]), str(tot[1]), str(tot[2]),
                                                                    str(tot[3])]))
        runs = app.runs[:3]
        if runs:
            rows = [[r.when.strftime("%b %-d %H:%M"), r.what[:24],
                     Text(glyph("ok"), style="green") if r.ok else Text(glyph("error"), style="red")] for r in runs]
            self.query_one("#db-recent", Static).update(table(app, ["When", "What", ""], rows))
        else:
            self.query_one("#db-recent", Static).update(f"[{m}]Nothing yet: nog's runs show here.[/]")
        size, files = app.cache
        self.query_one("#db-space", Static).update(
            f"[{m}]Package cache[/] [b]{records.size_words(size)}[/] [{m}]{glyph('dash')} {files:,} files[/]\n"
            f"[{m}]Clean Up asks nog to let old downloads go, keeping what a held package may still need. "
            f"It shows the list and asks first.[/]")


def source_of(r: dict) -> str:
    s = (r.get("source") or "").lower()
    if s.startswith("flatpak"):
        return "Flatpak"
    if s.startswith("snap"):
        return "Snap"
    return "aur" if s in ("aur", "") else s


# ── In-System (was Home) ─────────────────────────────────────────────────────
class InSystemScreen(Vertical):
    FORGE_HINTS = [("↑↓", "pick"), ("Del", "uninstall"), ("/", "search"), ("p", "repositories"), ("F1", "help")]

    def compose(self) -> ComposeResult:
        yield FilterBar("is", show=True, id="is-filters")
        yield PackageHeader(id="is-head")
        yield PackageList(id="is-list")
        yield Static("", id="is-count", classes="nf-count")

    def on_mount(self) -> None:
        self.query_one(PackageList).apps = self.app.apps
        self.refresh_view()

    def refresh_view(self) -> None:
        pk = self.app.packages
        show = self.query_one("#is-show", Select)
        opts = [(f"Yours ({sum(p.explicit for p in pk):,})", "yours"), (f"All ({len(pk):,})", "all")]
        cur = show.value if show.value in ("yours", "all") else "yours"
        with show.prevent(Select.Changed):
            show.set_options(opts)
            # Select only redraws its label when the value changes: change it twice
            show.value = "all" if cur != "all" else "yours"
            show.value = cur
        self._fill()

    def _fill(self) -> None:
        v = self.query_one(FilterBar).values()
        pkgs = filtered(self.app.packages, v["show"], v["kind"], v["words"], self.app.apps, v["tier"], v["repos"])
        newer = self.app.updatable_names()
        self.query_one(PackageList).show([installed_row(p, updatable=p.name in newer) for p in pkgs])
        msg = self.app.packages_error or f"{len(pkgs):,} shown"
        self.query_one("#is-count", Static).update(f"[$forge-muted]{msg}[/]")

    @on(FilterBar.Changed)
    @on(FilterBar.Searched)
    def _changed(self, e) -> None:
        e.stop()
        self._fill()
        if isinstance(e, FilterBar.Searched) and e.final:
            self.query_one(PackageList).focus()          # Enter: the keyboard moves to the list; typing keeps it

    def on_key(self, e) -> None:
        if e.key == "escape" and isinstance(self.app.focused, Input):
            e.stop()
            self.query_one(PackageList).focus()


# ── Install (was Search) ─────────────────────────────────────────────────────
class InstallScreen(Vertical):
    FORGE_HINTS = [("type", "the list follows"), ("Enter", "install"), ("p", "repositories"), ("F1", "help")]

    def compose(self) -> ComposeResult:
        yield FilterBar("in", show=False, id="in-filters")
        yield PackageHeader(id="in-head")
        yield PackageList(id="in-list")
        yield Static("[$forge-muted]Type a name or what it does: the list follows as you type. Type, Tier and "
                     "Repositories narrow the results.[/]", id="in-count", classes="nf-count")

    def on_mount(self) -> None:
        self.query_one(PackageList).apps = self.app.apps
        self.results = []

    _final = False

    @on(FilterBar.Searched)
    def _search(self, e: FilterBar.Searched) -> None:
        e.stop()
        self._final = e.final
        if e.words:
            self.query_one("#in-count", Static).update(f"[$forge-muted]Searching{glyph('ellipsis')}[/]")
            self.app.run_search(e.words)
        else:
            self.show_results([])
            self.query_one("#in-count", Static).update("[$forge-muted]Type a name or what it does: the list follows as you type.[/]")

    def show_results(self, results, error: str = "") -> None:
        self.results = results
        self._fill(error)
        if self._final and self.query_one(PackageList).rows:
            self.query_one(PackageList).focus()          # after Enter: keys act again, Enter on a row; typing keeps the box

    @on(FilterBar.Changed)
    def _filter(self, e) -> None:
        e.stop()
        self._fill()

    def _fill(self, error: str = "") -> None:
        v = self.query_one(FilterBar).values()
        words = self.query_one("#in-find", Input).value.strip()
        pkgs = relevant(self.results, words, self.app.apps)
        pkgs = filtered(pkgs, "all", v["kind"], "", self.app.apps, v["tier"], v["repos"])
        explicit = {p.name for p in self.app.packages if p.explicit}
        self.query_one(PackageList).show([search_row(p, p.name in explicit) for p in pkgs])
        self.query_one("#in-count", Static).update(
            f"[$forge-warn]{error}[/]" if error else f"[$forge-muted]{len(pkgs):,} found[/]")

    def on_key(self, e) -> None:
        if e.key == "escape" and isinstance(self.app.focused, Input):
            e.stop()
            self.query_one(PackageList).focus()


# ── Update: choose what goes in; nog says what must stay together ────────────
class UpdateScreen(VerticalScroll, can_focus=False):
    FORGE_HINTS = [("Space", "tick / untick"), ("Enter", "update this one / promote"), ("t", "tick all"),
                   ("n", "untick all"), ("/", "find"), ("k", "check"), ("u", "update"), ("F1", "help")]

    def compose(self) -> ComposeResult:
        with Horizontal(classes="forge-buttons nf-top"):
            yield Button("Check for Updates (k)", id="up-check")
            yield Button("Update the Ticked Ones (u)", id="up-run", variant="primary")
            yield Static("", id="up-busy")
        yield Static("", id="up-summary")
        # nogforge#18 + #20 (Javier, 2026-10-07): tick / untick everything in one go, and find one
        # package to update by itself — "too hard to get one package updated by itself"
        with Horizontal(classes="nf-bar -last nf-upbar"):
            yield Static("Find", classes="nf-label -lead")
            yield SearchInput(placeholder="a name or what it does — the lists below follow as you type",
                              id="up-find")
            with Horizontal(classes="forge-buttons nf-inline"):
                yield Button("Tick All (t)", id="up-tick-all")
                yield Button("Untick All (n)", id="up-untick-all")
        yield Static("[b]Ready now[/]  [$forge-muted]untick to keep one back: nog says what must stay back with it; "
                     "Update on a row updates that one by itself[/]",
                     classes="nf-section")
        yield PackageHeader(option=False, ver_w=32, ticks=True, id="up-ready-head")
        yield PackageList(ver_w=32, id="up-ready")
        yield Static("[b]Held[/]  [$forge-muted]Promote makes one ready now: it goes in with the ticked ones[/]",
                     classes="nf-section")
        yield PackageHeader("Ready on", ver_w=32, id="up-held-head")
        yield PackageList(ver_w=32, id="up-held")

    def on_mount(self) -> None:
        for pl in self.query(PackageList):
            pl.apps = self.app.apps
        self.refresh_view()

    def refresh_view(self) -> None:
        from datetime import datetime
        from ..nog import Package
        app, m = self.app, "$forge-muted"
        plan = app.choice_plan()
        waiting = app.keep_busy or (plan is None and not app.plan_error)
        busy = self.query_one("#up-busy", Static)
        busy.set_class(waiting, "-on")
        run = self.query_one("#up-run", Button)
        run.set_class(waiting, "-waiting")
        if waiting:
            busy.update(f"{glyph('busy')} nog is working on it{glyph('ellipsis')}"
                        if plan is not None else f"{glyph('busy')} nog is checking{glyph('ellipsis')}")
            run.disabled = True
        if app.plan_error:
            self.query_one("#up-summary", Static).update(f"[$forge-warn]{glyph('warn')} {app.plan_error}[/]")
            return
        if plan is None:
            self.query_one("#up-summary", Static).update("")
            return

        def pkg(r):
            return Package(r["name"], r["new"], "", r["tier"], source_of(r), installed=True)
        one = "Update" if is_console() else "⬆ Update"
        # nog's plan with your choices: what's ready (promoted too), and what stays back
        ready = []
        for r in plan["ready"]:
            ready.append(Row(pkg(r), one, "ok", version=f"{r['old']} → {r['new']}", tick=True,
                             note=r.get("note", ""), note_role="accent" if "promoted" in r.get("note", "") else ""))
        for r in plan["held"]:
            if r.get("kept_back") or r["name"] in app.kept_partners():
                why = "kept back by you" if r.get("kept_back") else f"must stay back with {r.get('coupled_to')}"
                ready.append(Row(pkg(r), "", "muted", version=f"{r['old']} → {r['new']}", tick=False,
                                 note=why, note_role="warn"))
        base_ready = {r["name"] for r in (app.plan or {}).get("ready", [])}
        ready.sort(key=lambda row: (row.package.name not in base_ready, row.package.name))
        promote = "Promote" if is_console() else "↑ Promote"
        held = [Row(pkg(r), promote, "accent", version=f"{r['old']} → {r['new']}",
                    extra=datetime.fromtimestamp(r["ready_on"]).strftime("%b %-d") if r.get("ready_on") else "—",
                    note=r.get("note", ""))
                for r in plan["held"] if not (r.get("kept_back") or r["name"] in app.kept_partners())]
        self.all_ready, self.all_held = ready, held
        self._show_filtered()
        ticked = sum(1 for r in ready if r.tick)
        self.query_one("#up-run", Button).label = f"Update the Ticked Ones ({ticked}) (u)"
        run.disabled = waiting or (ticked == 0 and not plan.get("unknown"))
        unk = len(plan.get("unknown", []))
        promoted = len(app.promote)
        self.query_one("#up-summary", Static).update(
            f"[b]{ticked} to update[/]" + (f" ({promoted} promoted)" if promoted else "") +
            f" · {len(ready) - ticked} kept back · {len(held)} held" +
            (f" · {unk} nog will ask you about" if unk else "") +
            f"\n[{m}]The update runs here, inside nogForge: nog shows only what you ticked and asks before "
            f"anything changes; nogForge asks for your password itself.[/]")

    all_ready: list = []
    all_held: list = []

    def _show_filtered(self) -> None:
        """Both lists, narrowed by the Find box (name or description, any case)."""
        words = self.query_one("#up-find", Input).value.strip().lower().split()

        def match(row: Row) -> bool:
            p = row.package
            app = self.app.apps.get(p.name)
            hay = " ".join((p.name, (app.name if app and app.name else ""), (app.summary if app and app.summary else ""),
                            p.description or "", row.note or "")).lower()
            return all(w in hay for w in words)
        self.query_one("#up-ready", PackageList).show([r for r in self.all_ready if match(r)])
        self.query_one("#up-held", PackageList).show([r for r in self.all_held if match(r)])

    @on(Input.Changed, "#up-find")
    def _find(self, e: Input.Changed) -> None:
        e.stop()
        self._show_filtered()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "up-tick-all":
            e.stop()
            self.app.tick_all()
        elif e.button.id == "up-untick-all":
            e.stop()
            self.app.untick_all()

    def on_key(self, e) -> None:
        if e.key == "escape" and isinstance(self.app.focused, Input):
            e.stop()
            self.query_one("#up-ready", PackageList).focus()

    @on(PackageList.Tick)
    def _tick(self, e: PackageList.Tick) -> None:
        e.stop()
        self.app.toggle_keep(e.row.package.name)


# ── History ▸ Activity and nog Logs ─────────────────────────────────────────
class RecordList(OptionList):
    """A full-width table like the package ones: cells, a line underneath, shaded rows."""

    class Open(Message):
        def __init__(self, index: int) -> None:
            super().__init__()
            self.index = index

    def __init__(self, columns: list[tuple[str, int]], **kw) -> None:
        super().__init__(**kw)
        self.columns, self.rows = columns, []

    def show(self, rows: list[tuple[list[Text | str], str]]) -> None:
        self.rows = rows
        self._redraw()

    def on_resize(self) -> None:
        if self.rows:
            self._redraw()

    def _redraw(self) -> None:
        cs = colours(self.app)
        w = max(self.size.width - 2, 80)
        opts = []
        for i, (cells, under) in enumerate(self.rows):
            first = Text()
            for (_h, width), c in zip(self.columns, cells):
                if isinstance(c, Text):
                    first.append(c.plain[: width - 1].ljust(width), style=c.style)
                else:
                    first.append(cell(str(c), width))
            first.append(" " * max(w - first.cell_len, 0))
            first.truncate(w)
            second = Text("  " + under, style=cs.get("forge-muted", ""))
            second.truncate(w)
            second.append(" " * max(w - second.cell_len, 0))
            t = Text("\n").join([first, second])
            if i % 2 and not is_console() and cs.get("forge-surface"):
                t.stylize_before(f"on {cs['forge-surface']}")
            opts.append(Option(t, id=str(i)))
        keep = self.highlighted
        self.clear_options()
        self.add_options(opts)
        if opts:
            self.highlighted = min(keep or 0, len(opts) - 1)

    def heading(self) -> Text:
        return Text("".join(cell(h, w) for h, w in self.columns), style="bold")

    def on_option_list_option_selected(self, e: OptionList.OptionSelected) -> None:
        e.stop()
        self.post_message(self.Open(int(e.option.id)))


class ActivityScreen(Vertical):
    FORGE_HINTS = [("↑↓", "move"), ("6", "nog Logs"), ("F1", "help"), ("?", "all keys")]
    COLUMNS = [("When", 16), ("What", 42), ("By", 12), ("Result", 22)]

    def compose(self) -> ComposeResult:
        yield Static("[b $forge-title-accent]Activity[/]   [$forge-muted]every install, removal and update nog ran, "
                     "from nogForge or a terminal, in plain words[/]", classes="nf-section")
        yield Static("", id="ac-head", classes="nf-head")
        yield RecordList(self.COLUMNS, id="ac-list")

    def on_mount(self) -> None:
        self.query_one("#ac-head", Static).update(self.query_one(RecordList).heading())
        self.refresh_view()

    def refresh_view(self) -> None:
        cs = colours(self.app)
        rows = []
        for r in self.app.runs:
            res = Text(f"{glyph('ok')} done", style=cs.get("forge-ok", "")) if r.ok else \
                Text(f"{glyph('error')} {r.outcome or 'stopped'}", style=cs.get("forge-danger", ""))
            rows.append(([r.when.strftime("%b %-d  %H:%M"), r.what, r.user or "—", res],
                         f"nog {r.command}" + (f" · status {r.status}" if r.status not in ("", "0") else "")))
        self.query_one(RecordList).show(rows)


class NogLogsScreen(Vertical):
    FORGE_HINTS = [("↑↓", "move"), ("Enter", "open the log"), ("5", "Activity"), ("F1", "help")]
    COLUMNS = [("Date", 12), ("Time", 10), ("Command", 40), ("User", 12), ("Status", 8), ("Outcome", 12)]

    def compose(self) -> ComposeResult:
        yield Static("[b $forge-title-accent]nog Logs[/]   [$forge-muted]nog's own record, as nog wrote it; "
                     "Enter opens a run's full log[/]", classes="nf-section")
        yield Static("", id="nl-head", classes="nf-head")
        yield RecordList(self.COLUMNS, id="nl-list")

    def on_mount(self) -> None:
        self.query_one("#nl-head", Static).update(self.query_one(RecordList).heading())
        self.refresh_view()

    def refresh_view(self) -> None:
        rows = []
        for r in self.app.runs:
            files = records.details_for(r, self.app.logs)
            under = (f"{len(files)} more log{'s' if len(files) != 1 else ''} for this run: " +
                     ", ".join(f.kind for f in files)) if files else "no other log for this run"
            rows.append(([r.when.strftime("%m/%d/%Y"), r.when.strftime("%I:%M %p"), r.command, r.user or "—",
                          r.status or "—", r.outcome or "—"], under))
        self.query_one(RecordList).show(rows)

    @on(RecordList.Open)
    def _open(self, e: RecordList.Open) -> None:
        e.stop()
        run = self.app.runs[e.index]
        self.app.push_screen(LogDialog(run, records.details_for(run, self.app.logs),
                                       records.full_log_for(run, self.app.logs)))


class LogDialog(ForgeModal[None]):
    """One run's full log: what nog wrote for it, line by line."""

    def __init__(self, run: records.Run, details: list, full: Path | None = None) -> None:
        super().__init__()
        self.run, self.details, self.full = run, details, full

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel nf-log-panel"):
            yield Static(f"nog {self.run.command}", classes="forge-panel-title")
            yield Static(f"[$forge-muted]{self.run.when:%b %-d, %Y %H:%M} · {self.run.user} · status "
                         f"{self.run.status or '—'} · {self.run.outcome or '—'}[/]")
            with ScrollableContainer(id="nl-body"):
                if self.full is not None:
                    # nog 1.6: the whole run, as it was on screen (colours too)
                    yield Static(f"[$forge-muted]{escape(str(self.full).replace(str(Path.home()), '~'))}[/]")
                    yield Static(Text.from_ansi(records.read_full_log(self.full), no_wrap=True),
                                 classes="nf-full-log")
                elif not self.details:
                    yield Static("[$forge-muted]nog kept no other log for this run: the line above is all of it. "
                                 "(nog 1.6 keeps every run whole.)[/]")
                else:
                    for d in self.details:
                        yield Static(f"[b]{d.kind}[/]  [$forge-muted]{d.path}[/]")
                        yield Static(d.table(colours(self.app)))
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Close (c)", id="nl-close", variant="primary")

    def on_key(self, e) -> None:
        if e.key in ("escape", "c"):
            e.stop()
            self.dismiss(None)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss(None)
