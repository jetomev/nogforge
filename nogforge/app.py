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
    FORGE_CSS, GPL3_NOTICE, ChangeGroup, ForgeApp, ForgeModal, ManualScreen, Notice, ReviewDialog, load_pages,
)

from . import __version__, catalogue, nog, records
from .nog import NogError, Package
from .ui.packages import PackageList
from .ui.screens import DashboardScreen, HistoryScreen, HomeScreen, SearchScreen, TiersScreen, UpdateScreen

MANUAL_DIR = os.path.join(os.path.dirname(__file__), "manual")

NF_CSS = FORGE_CSS + """
/* nogForge's own sections, coloured only through forgekit's roles */
#nf-dash { grid-size: 2 2; grid-columns: 1fr 1fr; grid-rows: auto auto; grid-gutter: 1 1; height: auto; padding: 0 1 0 0; }
.nf-box { height: auto; border: round $forge-border; border-title-color: $forge-accent; border-title-style: bold; padding: 0 1; }
.nf-box-buttons { height: auto; padding: 1 0 0 0; align-horizontal: left; }
.nf-box-buttons Button { margin: 0; width: auto; min-width: 0; padding: 0 2; }
.nf-bar { height: 3; margin: 0 0 1 0; }
.nf-label { width: auto; height: 3; content-align: left middle; color: $forge-muted; padding: 0 1 0 1; }
#hm-show { width: 26; } #hm-type { width: 20; } #hm-find { width: 1fr; }
#tr-show { width: 18; } #tr-find { width: 1fr; }
#sr-find { width: 1fr; } #sr-type { width: 20; } #sr-aur { width: auto; height: 3; content-align: left middle; margin: 0 0 0 1; }
PackageHeader { height: 1; padding: 0 1; color: $forge-accent; }
PackageList { height: 1fr; border: solid $forge-field-border; background: $forge-bg; padding: 0; }
PackageList:focus { border: solid $forge-accent; }
.nf-count { height: 1; padding: 0 1; }
#sec-home, #sec-search { padding: 0 2 0 0; }
#sec-update { padding: 0 2 0 0; }
#sec-update PackageList { height: auto; max-height: 14; }
.nf-top { height: auto; padding: 0 0 1 0; align-horizontal: left; }
.nf-top Button { margin: 0 2 0 0; }
.nf-section { height: auto; margin: 1 0 0 0; }
#up-summary { height: auto; }
#sec-history { padding: 0 2 0 0; }
#nf-changed-msg { height: auto; padding: 0 0 1 0; }
"""

class TierDialog(ForgeModal[str | None]):
    """A package's tier, or promote it now. Returns "1"/"2"/"3", "promote" or None."""

    def __init__(self, p: Package, holds: dict) -> None:
        super().__init__()
        self.p, self.holds = p, holds

    def compose(self):
        from forgekit import Choices
        d = lambda t: self.holds.get(f"tier{t}_days", {1: 30, 2: 15, 3: 7}[t])
        with Vertical(classes="forge-panel"):
            yield Static(f"{self.p.name}: tier, or promote", classes="forge-panel-title")
            yield Static(f"[$forge-muted]Its tier decides how long a new version waits before it installs. "
                         f"Now: Tier {self.p.tier}.[/]")
            yield Choices([("1", f"Tier 1 · {d(1)} days"), ("2", f"Tier 2 · {d(2)} days"),
                           ("3", f"Tier 3 · {d(3)} days")], str(self.p.tier), id="td-tier")
            yield Static("[$forge-muted]Tier 1 is for what the system needs to start (kernel, bootloader). "
                         "The change is saved by nog in /etc/nog/tier-pins.toml (it asks for your password).[/]")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Change Tier (t)", id="td-pin", variant="primary")
                yield Button("Promote Now (p)", id="td-promote")
                yield Button("Cancel", id="td-cancel")

    def on_mount(self) -> None:
        self.query_one("#td-tier").focus()

    def on_key(self, e) -> None:
        if e.key == "escape":
            e.stop()
            self.dismiss(None)
        elif e.key == "t":
            e.stop()
            self.dismiss(self.query_one("#td-tier").value)
        elif e.key == "p":
            e.stop()
            self.dismiss("promote")

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss({"td-pin": self.query_one("#td-tier").value, "td-promote": "promote"}.get(e.button.id))


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


class NogForgeApp(ForgeApp):
    APP_NAME = f"nogForge {__version__} · packages, the KognogOS way · beta"
    SHOW_HINT_BAR = True
    SHOW_CHANGES_BAR = True
    CSS = NF_CSS
    LICENSE_NOTICE = GPL3_NOTICE
    MENU = [
        {"id": "dashboard", "title": "Dashboard", "kind": "section"},
        {"id": "home", "title": "Home", "kind": "section", "acc": "o"},
        {"id": "search", "title": "Search", "kind": "section", "acc": "a"},
        {"id": "update", "title": "Update", "kind": "section"},
        {"id": "tiers", "title": "Tiers", "kind": "section"},
        {"id": "history", "title": "History", "kind": "section", "acc": "y"},
        {"id": "help", "title": "Help", "kind": "menu", "items": [
            ("Manual", "m", "manual"), ("Keys", "k", "shortcuts"),
            ("License", "l", "license"), ("About", "a", "about")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    SHORTCUTS = [
        ("1-6, Ctrl+letter", "Dashboard, Home, Search, Update, Tiers, History"),
        ("u", "review updates"),
        ("r", "review packages (Search)"),
        ("h", "open History"),
        ("Enter", "the row's option: install or remove"),
        ("Del", "remove the selected package (Home)"),
        ("/", "find"),
        ("Esc", "leave a field, close a window"),
        ("F1", "help on this screen"),
        ("?", "this list"),
        ("q or Ctrl+Q", "quit"),
    ]
    HINTS = [("u", "updates"), ("r", "packages"), ("1-6", "screens"), ("F1", "help"), ("?", "all keys")]
    BINDINGS = [
        Binding("1", "go('dashboard')", show=False), Binding("2", "go('home')", show=False),
        Binding("3", "go('search')", show=False), Binding("4", "go('update')", show=False),
        Binding("5", "go('tiers')", show=False), Binding("6", "go('history')", show=False),
        Binding("ctrl+t", "go('tiers')", show=False),
        Binding("ctrl+d", "go('dashboard')", show=False), Binding("ctrl+o", "go('home')", show=False),
        Binding("ctrl+a", "go('search')", show=False), Binding("ctrl+u", "go('update')", show=False),
        Binding("ctrl+y", "go('history')", show=False),
        Binding("u", "updates", show=False), Binding("r", "go('search')", show=False),
        Binding("h", "go('history')", show=False), Binding("c", "check_or_clean", show=False),
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
        self.keep_plan: dict | None = None   # nog's plan with those kept back: what must stay with them
        self.keep_busy = False
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
        yield HomeScreen(id="sec-home")
        yield SearchScreen(id="sec-search")
        yield UpdateScreen(id="sec-update")
        yield TiersScreen(id="sec-tiers")
        yield HistoryScreen(id="sec-history")

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
        self.call_from_thread(self.query_one(SearchScreen).show_results, res, err)

    # ── Update's choices: nog decides what must stay together ───────────────
    def toggle_keep(self, name: str) -> None:
        """Untick (keep back) or tick again. Ticking one that only stays back
        because of another ticks that other one again."""
        forced = self.forced_partner(name)
        if name in self.keep:
            self.keep.discard(name)
        elif forced:
            self.keep.discard(forced)
        else:
            self.keep.add(name)
        self.keep_plan = None
        self.keep_busy = bool(self.keep)
        self.refresh_screens()
        if self.keep:
            self.load_keep_plan(sorted(self.keep))

    @work(thread=True, exclusive=True, group="nf-keep")
    def load_keep_plan(self, keep: list[str]) -> None:
        try:
            p, err = nog.plan(keep), ""
        except NogError as e:
            p, err = None, str(e)
        self.call_from_thread(self._keep_done, keep, p, err)

    def _keep_done(self, keep: list[str], plan, err: str) -> None:
        if sorted(self.keep) != keep:
            return                              # the ticks changed meanwhile; a newer answer is coming
        self.keep_plan, self.keep_busy = plan, False
        if err:
            self.notify(err, title="nog couldn't answer", severity="warning", timeout=8)
        self.refresh_screens()

    def must_stay_back(self) -> dict[str, str]:
        """Packages nog holds because of what you unticked: name → nog's reason."""
        out = {}
        for r in (self.keep_plan or {}).get("held", []):
            partner = r.get("coupled_to")
            if partner and (partner in self.keep or partner in out):
                out[r["name"]] = f"must stay back with {partner}"
        return out

    def forced_partner(self, name: str) -> str | None:
        for r in (self.keep_plan or {}).get("held", []):
            if r["name"] == name and r.get("coupled_to"):
                p = r["coupled_to"]
                while self.forced_partner_of(p):          # a chain ends at what you unticked
                    p = self.forced_partner_of(p)
                return p
        return None

    def forced_partner_of(self, name: str) -> str | None:
        if name in self.keep:
            return None
        for r in (self.keep_plan or {}).get("held", []):
            if r["name"] == name and r.get("coupled_to"):
                return r["coupled_to"]
        return None

    def refresh_screens(self) -> None:
        for cls in (DashboardScreen, HomeScreen, UpdateScreen, TiersScreen, HistoryScreen):
            try:
                self.query_one(cls).refresh_view()
            except NoMatches:
                pass

    # ── moving around ────────────────────────────────────────────────────────
    def action_go(self, section: str) -> None:
        self._switch_section(section)

    def on_section_shown(self, section_id: str) -> None:
        focus = {"home": "#hm-list", "search": "#sr-find", "update": "#up-ready", "tiers": "#tr-list"}.get(section_id)
        if focus:
            self.query_one(focus).focus()

    def action_find(self) -> None:
        cur = self.query_one("#forge-work").current
        if cur == "sec-home":
            self.query_one("#hm-find").focus()
        else:
            self._switch_section("search")
            self.query_one("#sr-find").focus()

    def action_check_or_clean(self) -> None:
        if self.query_one("#forge-work").current == "sec-update":
            self.check_updates()
        elif self.query_one("#forge-work").current == "sec-dashboard":
            self.hand_off("clean", [])

    def action_updates(self) -> None:
        """u: open Update; on Update, update the ticked ones."""
        if self.query_one("#forge-work").current == "sec-update":
            if self.plan and not self.keep_busy:
                self.update_ticked()
        else:
            self._switch_section("update")

    def check_updates(self) -> None:
        self.keep, self.keep_plan, self.keep_busy = set(), None, False      # a fresh plan, fresh choices
        self.plan, self.plan_error = None, ""
        self.refresh_screens()
        self.load_plan()

    def on_action(self, action_id: str) -> None:
        if action_id == "manual":
            self.open_manual()

    def open_manual(self, page: str | None = None) -> None:
        pages = load_pages(MANUAL_DIR) if os.path.isdir(MANUAL_DIR) else []
        if pages:
            self.push_screen(ManualScreen("nogForge manual", pages, start=page))

    def action_help_here(self) -> None:
        cur = self.query_one("#forge-work").current.removeprefix("sec-")
        self.open_manual(cur)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        bid = e.button.id or ""
        if bid == "db-review-updates":
            self._switch_section("update")
        elif bid == "db-review-packages":
            self._switch_section("search")
        elif bid == "db-history":
            self._switch_section("history")
        elif bid == "db-clean":
            self.hand_off("clean", [])
        elif bid == "up-check":
            self.check_updates()
        elif bid == "up-run":
            self.update_ticked()

    # ── changes: reviewed here, then nog runs them in the terminal ───────────
    def on_package_list_act(self, e: PackageList.Act) -> None:
        p = e.row.package
        if "Tier" in e.row.option:
            self.choose_tier(p)
            return
        if e.row.option.endswith("Promote"):
            self.review_promote(p)
            return
        if e.row.option_role == "muted":
            if p.protected:
                self.notify(f"{p.name} can't be removed here: {p.protected}.", title="Locked", timeout=8)
            return
        self.review(p, removing=e.row.option_role == "danger")

    @work(exclusive=True, group="nf-change")
    async def review(self, p: Package, removing: bool) -> None:
        cmd, env = nog.change_command("remove" if removing else "install", [p.name])
        if removing:
            change = ChangeGroup("Remove", "", [(p.name, p.version, "removed")])
            steps = ["nog runs in this terminal and shows pacman's own list: what goes with it "
                     "(what only it needed) — and asks before anything changes",
                     nog.describe_password(env), "Then you come back here"]
        else:
            where = "built on this computer from the AUR: its helper shows the build recipe to review" if p.aur \
                else f"from {p.source}"
            change = ChangeGroup("Install", "", [(p.name, "not installed", p.version)])
            steps = [f"nog runs in this terminal: {where}; pacman shows what comes with it and asks first",
                     nog.describe_password(env), "Then you come back here"]
        choice = await self.push_screen_wait(ReviewDialog(
            "Review before " + ("removing" if removing else "installing"), [change], steps=steps,
            buttons=[("Remove (r)" if removing else "Install (i)", "go", True)]))
        if choice is None:
            return
        self.hand_off("remove" if removing else "install", [p.name])

    @work(exclusive=True, group="nf-change")
    async def review_promote(self, p: Package) -> None:
        _cmd, env = nog.change_command("unlock", [p.name, "--promote"])
        choice = await self.push_screen_wait(ReviewDialog(
            "Review before promoting", [ChangeGroup("Promote", "", [(p.name, "held", f"{p.version} now")])],
            steps=[f"nog installs {p.name} now, before its wait ends: the one thing the wait protects you from "
                   "is a version that turns out to be broken",
                   "nog runs in this terminal and pacman asks first", nog.describe_password(env),
                   "Then you come back here"],
            buttons=[("Promote (p)", "go", True)]))
        if choice is not None:
            self.hand_off("promote", [p.name])

    @work(exclusive=True, group="nf-change")
    async def choose_tier(self, p: Package) -> None:
        holds = (self.plan or {}).get("holds", {})
        choice = await self.push_screen_wait(TierDialog(p, holds))
        if choice is None:
            return
        if choice == "promote":
            self.review_promote(p)
        elif choice != str(p.tier):
            self.hand_off("pin", [p.name, "--tier", choice])

    def update_ticked(self) -> None:
        names = sorted(self.keep)
        self.hand_off("update", ["--keep", ",".join(names)] if names else [])

    def hand_off(self, action: str, names: list[str]) -> None:
        """Give the terminal to nog for a change, then come back and read everything again."""
        verb = "unlock" if action == "promote" else action
        args = [names[0], "--promote"] if action == "promote" else names
        cmd, env = nog.change_command(verb, args)
        before = {p.name: p.version for p in self.packages}
        expected = self._expected(action, names)
        kept = sorted(set(self.keep) | set(self.must_stay_back())) if action == "update" else []
        code = self.run_in_terminal(cmd, env)
        shown = "" if action == "update" else " ".join(names)
        self.changes.append((action, shown, code))
        word = {"install": "Installed", "remove": "Removed", "update": "Update finished",
                "clean": "Clean-up finished", "promote": "Promoted", "pin": "Tier changed"}
        if code == 0 and action not in ("update", "promote"):
            self.notify(f"{word[action]}: {shown or 'done'}.", title="nog finished", timeout=8)
        else:
            self.notify(f"nog stopped (status {code}): declined, or something went wrong — nog's own words are "
                        f"in the terminal above, and in History.", title="Not done", severity="warning", timeout=12)
        self.load_local()
        if action in ("update", "promote"):
            self.keep, self.keep_plan = set(), None
            self.show_what_changed(code, before, expected, kept)
        query = self.query_one("#sr-find").value.strip()
        if query and action in ("install", "remove"):
            self.run_search(query)               # the row turns into "Yours" (or back)
        if action in ("update", "install", "remove", "pin", "promote"):
            self.check_updates()

    def _expected(self, action: str, names: list[str]) -> dict[str, str]:
        """What should change: name → new version, from nog's plan."""
        plan = self.plan or {}
        if action == "promote":
            return {r["name"]: r["new"] for r in plan.get("held", []) if r["name"] == names[0]}
        if action == "update":
            stay = set(self.keep) | set(self.must_stay_back())
            return {r["name"]: r["new"] for r in plan.get("ready", []) if r["name"] not in stay}
        return {}

    def show_what_changed(self, code: int, before: dict[str, str], expected: dict[str, str],
                          kept: list[str]) -> None:
        """Compare versions before and after: what really went in, not what was hoped."""
        now = {p.name: p.version for p in self.packages}
        went_in = sorted(n for n, v in now.items() if before.get(n) not in (None, v))
        missing = sorted(n for n in expected if n not in went_in)
        kernel = [n for n in went_in if n in KERNELS]
        if code != 0 and not went_in:
            self.notify("nog stopped before anything changed (declined, or an error: its words are in the "
                        "terminal above, and in History).", title="Nothing changed", severity="warning",
                        timeout=12)
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

    def run_in_terminal(self, cmd: list[str], env: dict) -> int:
        """The terminal belongs to nog until it's done (tests replace this)."""
        with self.suspend():
            print(f"\n── nogForge hands this to nog: {' '.join(cmd[1:])} ──\n", flush=True)
            try:
                code = subprocess.run(cmd, env=env).returncode
            except OSError as e:
                print(f"nog couldn't start: {e}")
                code = 127
            try:
                input("\n── Press Enter to go back to nogForge ──")
            except EOFError:
                pass
        return code
