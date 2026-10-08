"""nogForge v0.1.0 — the app frame, on forgekit.

nog's wrapper, with what Pamac does, in a terminal (Javier, 3 Oct 2026). The
frame is forgekit's; the screens are nogForge's; every decision is nog's.
Beta 0.1: Dashboard, Home, Search, install and remove, History, and Update
showing nog's real plan. Choosing updates (0.2), Tiers (0.3) and Settings
(0.4) come next, each tested by Javier first.
"""

from __future__ import annotations

import os
import shutil
import subprocess

from textual import work
from textual.binding import Binding
from textual.app import ComposeResult
from textual.css.query import NoMatches
from textual.widgets import Button

from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from forgekit import (
    FORGE_CSS, GPL3_NOTICE, MENU_HINT, ChangeGroup, ForgeApp, ForgeModal, ManualScreen, Notice, ReviewDialog,
    load_pages,
)

from . import __version__, catalogue, nog, records
from .nog import NogError, Package
from .ui.packages import PackageList
from .ui.screens import (
    ActivityScreen, DashboardScreen, FilterBar, InstallScreen, InSystemScreen, NogLogsScreen, UpdateScreen,
)

MANUAL_DIR = os.path.join(os.path.dirname(__file__), "manual")

NF_CSS = FORGE_CSS + """
/* nogForge's own sections, coloured only through forgekit's roles */
#nf-dash { grid-size: 2 2; grid-columns: 1fr 1fr; grid-rows: auto auto; grid-gutter: 1 1; height: auto; padding: 0 1 0 0; }
.nf-box { height: auto; border: round $forge-border; border-title-color: $forge-accent; border-title-style: bold; padding: 0 1; }
.nf-box-buttons { height: auto; padding: 1 0 0 0; align-horizontal: left; }
.nf-box-buttons Button { margin: 0; width: auto; min-width: 0; padding: 0 2; }
/* #22 (Javier, 2026-10-07: "the search boxes are extremely tall"): one row each — the box, the labels,
   the drop-downs and the buttons — so a page spends two rows on its filters, not seven */
.nf-filters { height: auto; }
.nf-bar { height: 1; margin: 0 0 1 0; }
.nf-bar.-last { margin: 0 0 1 0; }
.nf-label.-lead { width: 9; padding: 0 1 0 1; }
.nf-label { width: auto; height: 1; content-align: left middle; color: $forge-muted; padding: 0 1 0 1; }
.nf-inline { width: auto; height: 1; padding: 0 0 0 1; }
.nf-inline Button { margin: 0 0 0 1; min-width: 0; width: auto; height: 1; padding: 0 2; content-align: center middle; }
.nf-bar SearchInput { height: 1; border: none; padding: 0 1; background: $forge-surface; color: $forge-text; }
.nf-bar SearchInput:focus { background: $forge-selected-bg; color: $forge-selected; }
.nf-bar SearchInput:ansi { background: $forge-bg; }
.nf-bar SearchInput:focus:ansi { background: $forge-selected-bg; }
.nf-bar Select { height: 1; margin: 0 1 0 0; }
.nf-bar Select > SelectCurrent { border: none; height: 1; padding: 0 1; }
.nf-bar Select > SelectCurrent:ansi { border: none; }
.nf-bar Select:focus > SelectCurrent { background: $forge-selected-bg; color: $forge-selected; }
#is-find, #in-find, #up-find { width: 1fr; }
#is-show { width: 19; } #is-type, #in-type { width: 18; } #is-tier, #in-tier { width: 17; }
PackageHeader, .nf-head { height: 1; padding: 0 1; color: $forge-accent; margin: 1 0 0 0; }
PackageList, RecordList { height: 1fr; border: solid $forge-field-border; background: $forge-bg; padding: 0; }
PackageList:focus, RecordList:focus { border: solid $forge-accent; }
PackageList > .option-list--option-highlighted, RecordList > .option-list--option-highlighted {
    background: $forge-selected-bg; }
PackageList:focus > .option-list--option-highlighted, RecordList:focus > .option-list--option-highlighted {
    background: $forge-selected-bg; text-style: bold; }
.nf-count { height: 1; padding: 0 1; }
#sec-insystem, #sec-install, #sec-update, #sec-activity, #sec-noglogs { padding: 0 2 0 0; }
#sec-update PackageList { height: auto; max-height: 14; }
.nf-top { height: auto; padding: 0 0 1 0; align-horizontal: left; }
.nf-upbar { margin: 0 0 1 0; }
.nf-top Button { margin: 0 2 0 0; }
.nf-section { height: auto; margin: 1 0 0 0; }
#up-summary { height: auto; }
/* While nog works out your choices (Javier, 4 Oct): a yellow banner shaped like a button, and the
   update button waits in a pale yellow beside it, so the two read as one message. */
#up-busy { display: none; width: auto; height: 1; padding: 0 2; margin: 0 2 0 0;
           background: $forge-warn; color: $forge-on-accent; text-style: $forge-strong; }
#up-busy.-on { display: block; }
.nf-top Button#up-run.-waiting, .nf-top Button#up-run.-waiting:hover, .nf-top Button#up-run.-waiting:disabled {
    background: $nf-cream; color: $forge-on-accent; text-style: none; text-opacity: 100%; opacity: 100%; }
.nf-log-panel { width: 96; height: auto; max-height: 90%; }
#nl-body { height: auto; max-height: 55vh; overflow-x: auto; overflow-y: auto; }
.nf-full-log { width: auto; }
#nf-changed-msg { height: auto; padding: 0 0 1 0; }
"""

KERNELS = ("linux", "linux-zen", "linux-lts", "linux-hardened", "linux-rt", "linux-rt-lts")


class WhatChanged(ForgeModal[str | None]):
    """After an update: what went in, what stayed back, and whether to restart.
    Javier, 3 Oct: a pop-up, Restart Now (r) in red, or Later (l) — "maybe they
    want to keep working"."""

    def __init__(self, heading: str, lines: list[str], restart: bool) -> None:
        super().__init__()
        self._heading, self._lines, self._restart = heading, lines, restart

    def compose(self):
        with Vertical(classes="forge-panel"):
            yield Static("What changed", classes="forge-panel-title")
            yield Notice(self._heading, self._lines, level="warn" if self._restart else "ok", id="nf-changed-msg")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                if self._restart:
                    yield Button("Restart Now (r)", id="restart", variant="error")
                    yield Button("Later (l)", id="later")
                else:
                    yield Button("Close (c)", id="later", variant="primary")

    def on_mount(self) -> None:
        self.query_one("#later", Button).focus()          # never restart by a stray Enter

    def on_key(self, e) -> None:
        if self._restart and e.key == "r":
            e.stop()
            self.dismiss("restart")
        elif e.key in ("l", "c", "escape"):
            e.stop()
            self.dismiss(None)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss("restart" if e.button.id == "restart" else None)


def count_flatpaks() -> int | None:
    if not shutil.which("flatpak"):
        return None
    try:
        out = subprocess.run(["flatpak", "list", "--app", "--columns=application"], capture_output=True, text=True,
                             timeout=20).stdout
        return len([l for l in out.splitlines() if l.strip()])
    except (OSError, subprocess.SubprocessError):
        return None


def count_snaps() -> int | None:
    """Apps only: the base snaps (core*, snapd, bare) are the system under them."""
    if not shutil.which("snap"):
        return None
    try:
        out = subprocess.run(["snap", "list"], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    names = [l.split()[0] for l in out.splitlines()[1:] if l.strip()]
    return len([n for n in names if not (n.startswith("core") or n in ("snapd", "bare"))])


def update_args(plan: dict, keep: set[str], promote: set[str]) -> list[str]:
    """What Update hands nog. nog 1.6.1 takes the ticked ones by name and shows
    only those (Javier, 4 Oct: "a specific list, it's intentional"); a held one
    must be promoted, which these are. An older nog gets what you kept back."""
    promoted = ["--promote", ",".join(sorted(promote))] if promote else []
    try:
        named = tuple(int(x) for x in plan.get("nog", "").split("-")[0].split(".")[:3]) >= (1, 6, 1)
    except ValueError:
        named = False
    if not named:
        return (["--keep", ",".join(sorted(keep))] if keep else []) + promoted
    ticked = {r["name"] for r in plan.get("ready", [])} | {r["name"] for r in plan.get("unknown", [])}
    return sorted(ticked) + promoted


def _events_file() -> str:
    """A private, empty file for nog's steps (NOG_EVENTS), in the user's runtime folder."""
    import tempfile
    base = os.environ.get("XDG_RUNTIME_DIR")
    fd, path = tempfile.mkstemp(prefix="nogforge-events-", dir=base if base and os.access(base, os.W_OK) else None)
    os.close(fd)
    return path


class NogForgeApp(ForgeApp):
    APP_NAME = f"nogForge {__version__} · packages, the KognogOS way"
    SHOW_HINT_BAR = True
    SHOW_CHANGES_BAR = True
    CSS = NF_CSS
    LICENSE_NOTICE = GPL3_NOTICE
    PASSWORD_TITLE = "nog needs your password"

    def get_css_variables(self) -> dict[str, str]:
        """forgekit's roles, plus one of nogForge's own: cream, forgekit's yellow
        made paler, for the update button while nog works (a plain yellow on a
        text console, which has no in-between shades)."""
        v = super().get_css_variables()
        warn = v.get("forge-warn", "")
        if warn.startswith("ansi_") or not warn:
            v["nf-cream"] = "ansi_yellow"
        else:
            from textual.color import Color
            v["nf-cream"] = Color.parse(warn).blend(Color(255, 255, 255), 0.55).hex
        return v
    MENU = [
        {"id": "dashboard", "title": "Dashboard", "kind": "section"},
        {"id": "insystem", "title": "In-System", "kind": "section"},
        {"id": "install", "title": "Install", "kind": "section"},
        {"id": "update", "title": "Update", "kind": "section"},
        {"id": "history", "title": "History", "kind": "menu", "items": [
            ("Activity", "a", "show-activity"), ("nog Logs", "l", "show-noglogs")]},
        {"id": "help", "title": "Help", "kind": "menu", "items": [
            ("Manual", "m", "manual"), ("Keys", "k", "shortcuts"),
            ("License", "l", "license"), ("About", "a", "about")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    # 1.4.0 (Javier, 2026-10-08, #24 #25): the menu's keys come from forgekit 0.10.0. Every entry has a
    # number in bar order (1 Dashboard … 5 History, 6 Help; Quit has none) and Ctrl + its underlined
    # letter, which works from inside a search box too. History and Help open their menus. The letters
    # follow Javier's rule (forgekit's assign_accels: the title's first letter, else its next free one;
    # Help H, Quit Q): D, I, N (Install: I is taken), U, S (History: H and I are taken)
    SHORTCUTS = [
        ("1-6", "Dashboard, In-System, Install, Update, History (its menu), Help (its menu)"),
        ("Ctrl+letter", "the underlined letter in the menu bar: D, I, N, U, S (History), H (Help)"),
        ("u", "open Update · on Update: update the ticked ones"),
        ("r", "review packages (Install)"),
        ("h", "open History (Activity)"),
        ("Enter", "the row's option: install, remove, promote; on nog Logs: open the log"),
        ("Space", "tick or untick an update"),
        ("Del", "uninstall the selected package (In-System)"),
        ("/", "search"),
        ("p", "repositories (In-System, Install)"),
        ("Esc", "leave a field, close a window"),
        ("F1", "help on this screen"),
        ("?", "this list"),
        ("q or Ctrl+Q", "quit (not there inside hypeForge Settings: Settings closes nogForge)"),
    ]
    HINTS = [("u", "updates"), ("r", "packages"), MENU_HINT, ("F1", "help"), ("?", "all keys")]
    BINDINGS = [
        Binding("u", "updates", show=False), Binding("r", "go('install')", show=False),
        Binding("h", "go('activity')", show=False), Binding("c", "clean", show=False),
        Binding("k", "check", show=False),
        Binding("t", "tick_all", show=False), Binding("n", "untick_all", show=False),
        Binding("p", "repositories", show=False),
        Binding("slash", "find", show=False),
        Binding("f1", "help_here", show=False, priority=True),
        Binding("question_mark", "act('shortcuts')", show=False),
        Binding("q", "act('quit')", show=False),
    ]

    def __init__(self, *, apps: dict | None = None, logs=None, cache_dir=None, **kw) -> None:
        self.apps = catalogue.load() if apps is None else apps
        self.logs = logs or records.LOGS
        self.cache_dir = cache_dir or records.CACHE
        self.packages: list[Package] = []
        self.packages_error = ""
        self.plan: dict | None = None
        self.plan_error = ""
        self.runs: list[records.Run] = []
        self.cache = (0, 0)
        self.flatpaks: int | None = None
        self.snaps: int | None = None
        self.changes: list[tuple[str, str, int]] = []      # (action, names, exit code), for the closing note
        self.keep: set[str] = set()          # what you unticked on Update
        self.promote: set[str] = set()       # what you promoted: ready now, with the ticked ones
        self.keep_plan: dict | None = None   # nog's plan with your choices: what must move or stay with them
        self.keep_busy = False
        self._ask_timer = None               # the pause before nog is asked about your choices
        self.started = __import__("datetime").datetime.now()
        self.ABOUT = {
            "name": "nogForge", "version": __version__,
            "tagline": "Packages, the KognogOS way",
            "description": "Part of the Forge Suite for KognogOS. Shows what nog decides; with thanks to "
                           "Pamac, whose ideas it brings to the terminal.",
            "authors": "jetomev (Javier) · Claude (Anthropic), co-developer",
            "license": "GPL-3.0-or-later",
            "links": [("Code", "https://github.com/jetomev/nogforge")],
        }
        super().__init__(**kw)

    def compose_sections(self) -> ComposeResult:
        yield DashboardScreen(id="sec-dashboard")
        yield InSystemScreen(id="sec-insystem")
        yield InstallScreen(id="sec-install")
        yield UpdateScreen(id="sec-update")
        yield ActivityScreen(id="sec-activity")
        yield NogLogsScreen(id="sec-noglogs")

    def on_mount(self) -> None:
        super().on_mount()
        self.set_title_status(f"{os.uname().nodename} · {self.nog_version()}")
        self.load_local()
        self.load_plan()

    def nog_version(self) -> str:
        b = nog.binary()
        if not b:
            return "nog is not installed"
        try:
            out = subprocess.run([b, "--version"], capture_output=True, text=True, timeout=5).stdout.strip()
            return out or "nog"
        except (OSError, subprocess.SubprocessError):
            return "nog"

    # ── data ─────────────────────────────────────────────────────────────────
    def load_local(self) -> None:
        """Installed packages, History and the cache: quick, so straight away."""
        try:
            self.packages = nog.installed()
            self.packages_error = ""
        except NogError as e:
            self.packages, self.packages_error = [], str(e)
        self.runs = records.runs(self.logs)
        self.cache = records.cache_size(self.cache_dir)
        self.flatpaks, self.snaps = count_flatpaks(), count_snaps()
        self.refresh_screens()

    @work(thread=True, exclusive=True, group="nf-plan")
    def load_plan(self) -> None:
        """nog's update plan checks every source: up to a minute, in the background."""
        try:
            p, err = nog.plan(), ""
        except NogError as e:
            p, err = None, str(e)
        self.call_from_thread(self._plan_done, p, err)

    def _plan_done(self, plan, err: str) -> None:
        self.plan, self.plan_error = plan, err
        self.refresh_screens()

    @work(thread=True, exclusive=True, group="nf-search")
    def run_search(self, query: str) -> None:
        if not query:
            return
        try:
            res, err = nog.search(query), ""
        except NogError as e:
            res, err = [], str(e)
        self.call_from_thread(self.query_one(InstallScreen).show_results, res, err)

    # ── Update's choices: nog decides what must move or stay together ───────
    def choice_plan(self) -> dict | None:
        """The plan as it is with your choices: nog's answer, or, while nog is
        still working them out, your choices shown at once over the last answer."""
        if self.keep_busy and self.plan is not None:
            return self.shown_at_once()
        if (self.keep or self.promote) and self.keep_plan is not None:
            return self.keep_plan
        return self.plan

    def shown_at_once(self) -> dict:
        """Javier, 4 Oct: a tick changes on screen the moment you press it; nog's
        answer follows. What you kept back or promoted moves now; what must stay
        with it is still the last answer's, until nog says again."""
        base, last = self.plan, self.keep_plan or self.plan
        base_ready = {r["name"] for r in base["ready"]}
        last_by = {r["name"]: r for r in last["ready"] + last["held"]}
        last_ready = {r["name"] for r in last["ready"]}
        partners = self.kept_partners()
        ready, held = [], []
        for r in base["ready"] + base["held"]:
            n = r["name"]
            if n in self.promote:
                ready.append({**r, "note": "promoted by you"})
            elif n in self.keep:
                held.append({**r, "note": "kept back by you", "kept_back": True})
            elif n in partners:
                held.append(last_by[n])
            elif n in base_ready:
                ready.append({**r, "kept_back": False})
            elif n in last_ready and last_by[n].get("note", "").removeprefix("promoted with ") in self.promote:
                ready.append(last_by[n])
            else:
                held.append(r)
        return {**base, "ready": ready, "held": held}

    def kept_partners(self) -> set[str]:
        """What nog holds because of what you kept back (not their own wait)."""
        held = (self.keep_plan or {}).get("held", []) if (self.keep or self.promote) else []
        by = {r["name"]: r.get("coupled_to") for r in held}

        def root(n, seen=()):
            p = by.get(n)
            if not p or n in seen:
                return None
            return p if p in self.keep else root(p, seen + (n,))
        return {n for n in by if root(n)}

    def root_of(self, name: str) -> str | None:
        held = {r["name"]: r.get("coupled_to") for r in (self.keep_plan or {}).get("held", [])}
        n, seen = name, set()
        while held.get(n) and n not in seen:
            seen.add(n)
            n = held[n]
            if n in self.keep:
                return n
        return None

    def toggle_keep(self, name: str) -> None:
        """Space on a ready row: keep it back, or tick it again. A promoted one
        unticked goes back to waiting; one that only stays back because of
        another ticks that other one again."""
        if name in self.promote:
            self.promote.discard(name)
        elif name in self.keep:
            self.keep.discard(name)
        elif (root := self.root_of(name)):
            self.keep.discard(root)
        elif any(r["name"] == name for r in (self.choice_plan() or {}).get("ready", [])):
            ready_note = next(r.get("note", "") for r in self.choice_plan()["ready"] if r["name"] == name)
            if ready_note.startswith("promoted with "):
                self.promote.discard(ready_note.removeprefix("promoted with "))
            else:
                self.keep.add(name)
        self.reload_choices()

    def promote_package(self, name: str) -> None:
        """Promote: ready now, it goes in with the ticked ones (Javier: "shouldn't
        promote just bring the package to due, so it enters the ready list?")."""
        self.promote.add(name)
        self.keep.discard(name)
        self.reload_choices()
        self.notify(f"{name} is ready now; it goes in with the ticked ones. Space unticks it again.",
                    title="Promoted", timeout=6)

    ASK_AFTER = 0.6   # seconds of quiet before nog is asked: quick clicks go as one question

    def reload_choices(self) -> None:
        """Shown at once; nog is asked once the clicking pauses, with every choice
        made so far (Javier, 4 Oct: "if people go selecting quick, batch them")."""
        if self._ask_timer is not None:
            self._ask_timer.stop()
            self._ask_timer = None
        self.keep_busy = bool(self.keep or self.promote)
        if not self.keep_busy:
            self.keep_plan = None
        self.refresh_screens()
        if self.keep_busy:
            self._ask_timer = self.set_timer(self.ASK_AFTER, self._ask_nog)

    def _ask_nog(self) -> None:
        self._ask_timer = None
        self.load_keep_plan(sorted(self.keep), sorted(self.promote))

    @work(thread=True, exclusive=True, group="nf-keep")
    def load_keep_plan(self, keep: list[str], promote: list[str]) -> None:
        try:
            p, err = nog.plan(keep, promote), ""
        except NogError as e:
            p, err = None, str(e)
        self.call_from_thread(self._keep_done, keep, promote, p, err)

    def _keep_done(self, keep: list[str], promote: list[str], plan, err: str) -> None:
        if (sorted(self.keep), sorted(self.promote)) != (keep, promote):
            return                              # the choices changed meanwhile; a newer answer is coming
        self.keep_plan, self.keep_busy = plan, False
        if err:
            self.notify(err, title="nog couldn't answer", severity="warning", timeout=8)
        self.refresh_screens()

    def refresh_screens(self) -> None:
        for cls in (DashboardScreen, InSystemScreen, UpdateScreen, ActivityScreen, NogLogsScreen):
            try:
                self.query_one(cls).refresh_view()
            except NoMatches:
                pass

    # ── moving around ────────────────────────────────────────────────────────
    def action_go(self, section: str) -> None:
        self._switch_section(section)

    def on_section_shown(self, section_id: str) -> None:
        focus = {"insystem": "#is-list", "install": "#in-find", "update": "#up-ready", "activity": "#ac-list",
                 "noglogs": "#nl-list"}.get(section_id)
        if focus:
            self.query_one(focus).focus()

    def action_find(self) -> None:
        cur = self.query_one("#forge-work").current
        if cur == "sec-insystem":
            self.query_one("#is-find").focus()
        elif cur == "sec-update":
            self.query_one("#up-find").focus()       # #20: find the one to update by itself
        else:
            self._switch_section("install")
            self.query_one("#in-find").focus()

    # Javier, 3 Oct: one letter, one meaning: "c" said "check again" on Update and
    # cleaned up on the Dashboard. c is always Clean Up; k checks for updates.
    def action_clean(self) -> None:
        self.hand_off("clean", [])

    def action_check(self) -> None:
        if self.query_one("#forge-work").current != "sec-update":
            self._switch_section("update")
        self.check_updates()

    def action_updates(self) -> None:
        """u: open Update; on Update, update the ticked ones."""
        if self.query_one("#forge-work").current == "sec-update":
            if self.plan and not self.keep_busy:
                self.update_ticked()
        else:
            self._switch_section("update")

    def check_updates(self) -> None:
        if self._ask_timer is not None:
            self._ask_timer.stop()
            self._ask_timer = None
        self.keep, self.promote, self.keep_plan, self.keep_busy = set(), set(), None, False   # fresh choices
        self.plan, self.plan_error = None, ""
        self.refresh_screens()
        self.load_plan()

    def on_action(self, action_id: str) -> None:
        if action_id == "manual":
            self.open_manual()
        elif action_id == "show-activity":
            self._switch_section("activity")
        elif action_id == "show-noglogs":
            self._switch_section("noglogs")

    def before_quit(self) -> bool:
        """1.4.0 (#26): never close while nog is working. q, Ctrl+Q, Quit and hypeForge Settings'
        request to close all ask here; stopping nog halfway through an update could break the system."""
        from forgekit import RunWindow
        if any(isinstance(s, RunWindow) for s in self.screen_stack):
            self.notify("nog is still working. Close nogForge once nog is done.", title="Not yet", timeout=8)
            return False
        return True

    def _mark_active(self, section_id: str) -> None:
        """History is a menu of two screens: it's lit for both."""
        for m in self.MENU:
            on = m["id"] == section_id or (m["id"] == "history" and section_id in ("activity", "noglogs"))
            self.query_one(f"#menu-{m['id']}").set_class(on, "active")

    def action_repositories(self) -> None:
        cur = self.query_one("#forge-work").current
        if cur in ("sec-insystem", "sec-install"):
            self.query_one(f"#{cur} FilterBar", FilterBar).choose_repositories()

    def open_manual(self, page: str | None = None) -> None:
        pages = load_pages(MANUAL_DIR) if os.path.isdir(MANUAL_DIR) else []
        if pages:
            self.push_screen(ManualScreen("nogForge manual", pages, start=page))

    def action_help_here(self) -> None:
        cur = self.query_one("#forge-work").current.removeprefix("sec-")
        self.open_manual({"activity": "history", "noglogs": "history"}.get(cur, cur))

    def on_button_pressed(self, e: Button.Pressed) -> None:
        bid = e.button.id or ""
        if bid == "db-review-updates":
            self._switch_section("update")
        elif bid == "db-review-packages":
            self._switch_section("install")
        elif bid == "db-history":
            self._switch_section("activity")
        elif bid == "db-clean":
            self.hand_off("clean", [])
        elif bid == "up-check":
            self.check_updates()
        elif bid == "up-run":
            self.update_ticked()

    # ── changes: reviewed here, then nog runs them in the terminal ───────────
    def on_package_list_act(self, e: PackageList.Act) -> None:
        p = e.row.package
        label = e.row.option2 if e.which == 2 else e.row.option
        if label.endswith("Update"):             # Update's Ready rows, and In-System's second button (#19, #20)
            self.update_one(p.name)
            return
        if e.row.option.endswith("Promote"):
            self.promote_package(p.name)
            return
        if e.row.option_role == "muted":
            if p.protected:
                self.notify(f"{p.name} can't be uninstalled here: {p.protected}.", title="Locked", timeout=8)
            return
        self.review(p, removing=e.row.option_role == "danger")

    # ── one package by itself, every package at once (nogforge#18, #20; Javier, 2026-10-07) ──
    def updatable_names(self) -> set[str]:
        """Every package nog's plan knows a newer version of (ready or held)."""
        plan = self.plan or {}
        return {r["name"] for r in plan.get("ready", [])} | {r["name"] for r in plan.get("held", [])}

    def update_one(self, name: str) -> None:
        """Update this one package by itself: nog gets its name alone (and a promote if it is
        held), and works out itself what has to move with it."""
        if self.keep_busy:
            return
        held = {r["name"] for r in (self.plan or {}).get("held", [])}
        self.hand_off("update", [name] + (["--promote", name] if name in held else []))

    def tick_all(self) -> None:
        if self.keep:
            self.keep = set()
            self.reload_choices()

    def untick_all(self) -> None:
        names = {r["name"] for r in (self.choice_plan() or self.plan or {}).get("ready", [])}
        if names - self.keep:
            self.keep |= names
            self.reload_choices()

    def action_tick_all(self) -> None:
        if self.query_one("#forge-work").current == "sec-update":
            self.tick_all()

    def action_untick_all(self) -> None:
        if self.query_one("#forge-work").current == "sec-update":
            self.untick_all()

    @work(exclusive=True, group="nf-change")
    async def review(self, p: Package, removing: bool) -> None:
        cmd, env = nog.change_command("remove" if removing else "install", [p.name])
        if removing:
            change = ChangeGroup("Uninstall", "", [(p.name, p.version, "uninstalled")])
            steps = ["nog runs here, in a window inside nogForge, and pacman shows its own list: what goes "
                     "with it (what only it needed), and asks before anything changes",
                     nog.describe_password(env), "Each step shows as it happens; nog's own screen opens when it asks"]
        else:
            where = "built on this computer from the AUR: its helper shows the build recipe to review" if p.aur \
                else f"from {p.source}"
            change = ChangeGroup("Install", "", [(p.name, "not installed", p.version)])
            steps = [f"nog runs here, in a window inside nogForge: {where}; pacman shows what comes with it "
                     f"and asks first", nog.describe_password(env),
                     "Each step shows as it happens; nog's own screen opens when it asks"]
        choice = await self.push_screen_wait(ReviewDialog(
            "Review before " + ("uninstalling" if removing else "installing"), [change], steps=steps,
            buttons=[("Uninstall (r)" if removing else "Install (i)", "go", True)]))
        if choice is None:
            return
        # nog 1.7 (F-11): install from the source of the row picked, so the AUR's
        # neofetch is never swapped for a repository package providing "neofetch"
        name = p.name if removing else (f"aur/{p.name}" if p.aur else f"{p.source}/{p.name}" if p.source else p.name)
        self.hand_off("remove" if removing else "install", [name])

    def update_ticked(self) -> None:
        if self.keep_busy:
            return                              # nog is still working out your choices: the banner says so
        self.hand_off("update", update_args(self.choice_plan() or {}, self.keep, self.promote))

    # tests set this to run nog without a window: (cmd, env) -> status
    run_in_terminal = None

    def hand_off(self, action: str, names: list[str]) -> None:
        """nog runs the change inside nogForge (v1.1: Javier, 4 Oct, "it stays
        inside the UI"); when its window closes, everything is read again."""
        events = None if self.run_in_terminal else _events_file()
        cmd, env = nog.change_command(action, names, events)
        before = {p.name: p.version for p in self.packages}
        expected = self._expected(action, names)
        kept = sorted(set(self.keep) | self.kept_partners()) if action == "update" else []

        def after(code: int | None) -> None:
            if events:
                try:
                    os.unlink(events)
                except OSError:
                    pass
            self._after_hand_off(action, names, 1 if code is None else code, before, expected, kept)

        if self.run_in_terminal:
            after(self.run_in_terminal(cmd, env))
            return
        targets = [n.split("/", 1)[-1] for n in names if not n.startswith("-")]
        if "--promote" in names:
            targets = [n.split("/", 1)[-1] for n in names[:names.index("--promote")] if not n.startswith("-")]
        title = {"install": f"Installing {' '.join(targets)}", "remove": f"Removing {' '.join(targets)}",
                 "update": f"Updating {len(targets)} package{'s' if len(targets) != 1 else ''}"
                 + (f": {', '.join(targets[:5])}" + (" …" if len(targets) > 5 else "") if targets else ""),
                 "clean": "Cleaning up old downloads"}.get(action, f"nog {action}")
        done = {"install": "Installed.", "remove": "Removed.", "update": "Updated.",
                "clean": "Cleaned up."}.get(action, "Done.")
        self.run_worker(self.run_in_app(title, cmd, env, callback=after, events_path=events, tool="nog",
                                        done_words=done), group="nf-run")

    def _after_hand_off(self, action: str, names: list[str], code: int, before: dict, expected: dict,
                        kept: list[str]) -> None:
        shown = "" if action == "update" else " ".join(n.split("/", 1)[-1] for n in names)
        self.changes.append((action, shown, code))
        word = {"install": "Installed", "remove": "Removed", "update": "Update finished",
                "clean": "Clean-up finished", "promote": "Promoted", "pin": "Tier changed"}
        # Javier, 4 Oct: a finished update said "nog stopped". Success on an update
        # is told by What changed; the warning is only for a run that didn't finish.
        if code == 0:
            if action not in ("update", "promote"):
                self.notify(f"{word[action]}: {shown or 'done'}.", title="nog finished", timeout=8)
        else:
            self.notify(f"nog stopped (status {code}): declined, or something went wrong — nog's own words are "
                        f"on its screen in the run window, and in History.", title="Not done", severity="warning",
                        timeout=12)
        self.load_local()
        if action == "update":
            self.keep, self.promote, self.keep_plan = set(), set(), None
            self.show_what_changed(code, before, expected, kept)
        query = self.query_one("#in-find").value.strip()
        if query and action in ("install", "remove"):
            self.run_search(query)               # the row turns into "Yours" (or back)
        if action in ("update", "install", "remove"):
            self.check_updates()

    def _expected(self, action: str, names: list[str]) -> dict[str, str]:
        """What should change: name → new version, from nog's plan."""
        if action == "update":
            return {r["name"]: r["new"] for r in (self.choice_plan() or {}).get("ready", [])}
        return {}

    def show_what_changed(self, code: int, before: dict[str, str], expected: dict[str, str],
                          kept: list[str]) -> None:
        """Compare versions before and after: what really went in, not what was hoped."""
        now = {p.name: p.version for p in self.packages}
        went_in = sorted(n for n, v in now.items() if before.get(n) not in (None, v))
        missing = sorted(n for n in expected if n not in went_in)
        kernel = [n for n in went_in if n in KERNELS]
        if code != 0 and not went_in:
            self.notify("nog stopped before anything changed (declined, or an error: its words were on its "
                        "screen in the run window, and are in History).", title="Nothing changed",
                        severity="warning", timeout=12)
            return
        lines = []
        if missing:
            lines.append(f"Didn't go in: {', '.join(missing[:6])}" + (f" and {len(missing) - 6} more" if len(missing) > 6
                                                                     else "") + ".")
        if kept:
            lines.append(f"Kept back by you: {', '.join(kept[:6])}" + (f" and {len(kept) - 6} more" if len(kept) > 6
                                                                       else "") + ".")
        if kernel:
            lines.append(f"Restart needed: {', '.join(kernel)} is new; the running kernel stays the old one "
                         f"until you restart.")
        heading = f"{len(went_in)} updated" if went_in else "Nothing went in"
        self.push_screen(WhatChanged(heading, lines or ["Everything nog planned went in."], bool(kernel)),
                         self._after_what_changed)

    def _after_what_changed(self, choice: str | None) -> None:
        if choice == "restart":
            self.restart()

    def restart(self) -> None:
        """Restart the computer (tests replace this). The restart is asked for
        first; nogForge closes as it begins."""
        try:
            subprocess.Popen(["systemctl", "reboot"])
        except OSError as e:
            self.notify(f"The restart couldn't start: {e.strerror or e}. Restart from the desktop's menu.",
                        title="Not restarted", severity="error", timeout=12)
            return
        self.exit()

