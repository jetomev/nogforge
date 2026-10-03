"""nogForge's screens (v0.1.0): Dashboard, Home, Search, Update, History.

Drawn from the approved design (docs/design/v0.1-screens.html): tables in the
spreadsheet style, options at the right of their row, screen buttons at the
top only, buttons that say "Words (k)". Update in 0.1 shows nog's real plan
(read-only); ticking, keeping back and promoting come with 0.2.
"""

from __future__ import annotations

from collections import Counter

from rich.table import Table
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Select, Static

from forgekit import Toggle, glyph
from forgekit.console import is_console

from .. import catalogue, records
from .packages import PackageHeader, PackageList, Row, colours, filtered, installed_row, search_row

SOURCES = ["core", "extra", "multilib", "chaotic-aur", "aur", "Flatpak", "Snap"]


def label(src: str) -> str:
    return "AUR" if src == "aur" else src


def table(app, columns: list[str], rows: list[list[str]], foot: list[str] | None = None) -> Table:
    """A spreadsheet-style table: headings, and every other row shaded."""
    c = colours(app)
    t = Table(box=None, padding=(0, 1, 0, 0), pad_edge=False, show_edge=False, expand=False,
              header_style=f"bold {c.get('forge-accent', '')}",
              row_styles=["", f"on {c.get('forge-raised', '')}"] if c.get("forge-raised") else None)
    for col in columns:
        t.add_column(col, no_wrap=True)
    for r in rows:
        t.add_row(*r)
    if foot:
        t.add_row(*[Text(x, style="bold") for x in foot], style="")
    return t


# ── Dashboard ────────────────────────────────────────────────────────────────
class DashboardScreen(VerticalScroll, can_focus=False):
    FORGE_HINTS = [("u", "updates"), ("r", "packages"), ("1-5", "screens"), ("F1", "help"), ("?", "all keys")]

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
        # Updates: nog's plan, per source and tier
        plan = app.plan
        if app.plan_error:
            self.query_one("#db-updates", Static).update(f"[$forge-warn]{glyph('warn')} {app.plan_error}[/]")
        elif plan is None:
            self.query_one("#db-updates", Static).update(
                f"[{m}]Asking nog what's waiting{glyph('ellipsis')} (it checks every source; up to a minute)[/]")
        else:
            rows, tot = [], Counter()
            for src in SOURCES:
                ready = [r for r in plan["ready"] if self._src(r) == src]
                held = [r for r in plan["held"] + plan.get("unknown", []) if self._src(r) == src]
                tiers = Counter(r["tier"] for r in ready + held)
                if src in ("Flatpak", "Snap") and not (ready or held):
                    state = plan.get("sources", {}).get(src.lower(), "")
                    rows.append([src, "0", "0", "0", "0", "0"] if state == "checked" else
                                [src, Text(state or "—", style=m.strip('$')), "", "", "", ""])
                    continue
                if not (ready or held) and src not in ("core", "extra"):
                    continue
                rows.append([label(src), str(len(ready)), str(len(held)), str(tiers[1]), str(tiers[2]), str(tiers[3])])
                tot.update({"r": len(ready), "h": len(held), 1: tiers[1], 2: tiers[2], 3: tiers[3]})
            self.query_one("#db-updates", Static).update(table(app, ["Source", "Ready", "Held", "Tier 1", "Tier 2",
                                                                     "Tier 3"], rows,
                                                               ["Total", str(tot["r"]), str(tot["h"]), str(tot[1]),
                                                                str(tot[2]), str(tot[3])]))
        # Yours: the packages you chose, per source and tier
        if app.packages_error:
            self.query_one("#db-yours", Static).update(f"[$forge-warn]{glyph('warn')} {app.packages_error}[/]")
        else:
            mine = [p for p in app.packages if p.explicit]
            rows, tot = [], Counter()
            for src in ["core", "extra", "multilib", "chaotic-aur", "aur"]:
                ps = [p for p in mine if p.source == src]
                if not ps:
                    continue
                t = Counter(p.tier for p in ps)
                rows.append([label(src), str(len(ps)), str(t[1]), str(t[2]), str(t[3])])
                tot.update({"n": len(ps), 1: t[1], 2: t[2], 3: t[3]})
            other = [p for p in mine if p.source not in ("core", "extra", "multilib", "chaotic-aur", "aur")]
            if other:
                rows.append(["other", str(len(other)), "", "", ""])
                tot["n"] += len(other)
            for src, n in (("Flatpak", app.flatpaks), ("Snap", app.snaps)):
                if n is not None:
                    rows.append([src, str(n), "0", "0", str(n)])
                    tot.update({"n": n, 3: n})
            self.query_one("#db-yours", Static).update(table(app, ["Source", "Yours", "Tier 1", "Tier 2", "Tier 3"],
                                                             rows, ["Total", str(tot["n"]), str(tot[1]), str(tot[2]),
                                                                    str(tot[3])]))
        # Recent
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

    @staticmethod
    def _src(r: dict) -> str:
        s = (r.get("source") or "").lower()
        if s.startswith("flatpak"):
            return "Flatpak"
        if s.startswith("snap"):
            return "Snap"
        return "aur" if s in ("aur", "") else s


# ── Home ─────────────────────────────────────────────────────────────────────
class HomeScreen(Vertical):
    FORGE_HINTS = [("↑↓", "pick"), ("Del", "remove"), ("/", "find"), ("F1", "help"), ("?", "all keys")]

    def compose(self) -> ComposeResult:
        with Horizontal(classes="nf-bar"):
            yield Static("Show", classes="nf-label")
            yield Select([("Yours", "yours")], value="yours", allow_blank=False, id="hm-show")
            yield Static("Type", classes="nf-label")
            yield Select([(t, t) for t in catalogue.TYPES], value="All types", allow_blank=False, id="hm-type")
            yield Static("Find", classes="nf-label")
            yield Input(placeholder="name or words", id="hm-find")
        yield PackageHeader(id="hm-head")
        yield PackageList(id="hm-list")
        yield Static("", id="hm-count", classes="nf-count")

    def on_mount(self) -> None:
        self.query_one(PackageList).apps = self.app.apps
        self.refresh_view()

    def refresh_view(self) -> None:
        app = self.app
        pk = app.packages
        show = self.query_one("#hm-show", Select)
        counts = (sum(p.explicit for p in pk), len(pk), sum(p.aur for p in pk))
        opts = [(f"Yours ({counts[0]:,})", "yours"), (f"All ({counts[1]:,})", "all"),
                (f"From the AUR ({counts[2]:,})", "aur")]
        cur = show.value if show.value in ("yours", "all", "aur") else "yours"
        with show.prevent(Select.Changed):
            show.set_options(opts)
            # Select only redraws its label when the value changes: change it twice
            show.value = "all" if cur != "all" else "yours"
            show.value = cur
        self._fill()

    def _fill(self) -> None:
        pkgs = filtered(self.app.packages, self.query_one("#hm-show", Select).value,
                        self.query_one("#hm-type", Select).value, self.query_one("#hm-find", Input).value,
                        self.app.apps)
        self.query_one(PackageList).show([installed_row(p) for p in pkgs])
        msg = self.app.packages_error or f"{len(pkgs):,} shown"
        self.query_one("#hm-count", Static).update(f"[$forge-muted]{msg}[/]")

    @on(Select.Changed)
    @on(Input.Changed, "#hm-find")
    def _changed(self, e) -> None:
        e.stop()
        self._fill()

    def on_key(self, e) -> None:
        if e.key == "escape" and isinstance(self.app.focused, Input):
            e.stop()
            self.query_one(PackageList).focus()


# ── Search ───────────────────────────────────────────────────────────────────
class SearchScreen(Vertical):
    FORGE_HINTS = [("type", "then Enter to search"), ("Enter", "install"), ("Tab", "next"), ("F1", "help")]

    def compose(self) -> ComposeResult:
        with Horizontal(classes="nf-bar"):
            yield Static("Find", classes="nf-label")
            yield Input(placeholder="a name or what it does, then Enter", id="sr-find")
            yield Static("Type", classes="nf-label")
            yield Select([(t, t) for t in catalogue.TYPES], value="All types", allow_blank=False, id="sr-type")
            yield Toggle(True, on_label="Include AUR", off_label="No AUR", id="sr-aur")
        yield PackageHeader(id="sr-head")
        yield PackageList(id="sr-list")
        yield Static("[$forge-muted]Type what you're looking for and press Enter; Type narrows the results.[/]",
                     id="sr-count", classes="nf-count")

    def on_mount(self) -> None:
        self.query_one(PackageList).apps = self.app.apps
        self.results = []

    @on(Input.Submitted, "#sr-find")
    def _search(self, e: Input.Submitted) -> None:
        e.stop()
        self.app.run_search(e.value.strip())

    def show_results(self, results, error: str = "") -> None:
        self.results = results
        self._fill(error)
        if results:
            self.query_one(PackageList).focus()          # keys act again: 1-5, Enter on a row

    @on(Select.Changed, "#sr-type")
    @on(Toggle.Changed, "#sr-aur")
    def _filter(self, e) -> None:
        e.stop()
        if not self.results and not self.query_one("#sr-find", Input).value.strip():
            self.query_one("#sr-count", Static).update(
                "[$forge-muted]Type a word too (a name or what it does), then Enter: nog searches by words.[/]")
            return
        self._fill()

    def _fill(self, error: str = "") -> None:
        aur = bool(self.query_one("#sr-aur", Toggle).value)
        pkgs = filtered(self.results, "all", self.query_one("#sr-type", Select).value, "", self.app.apps,
                        test=lambda p: aur or not p.aur)
        self.query_one(PackageList).show([search_row(p) for p in pkgs])
        self.query_one("#sr-count", Static).update(
            f"[$forge-warn]{error}[/]" if error else f"[$forge-muted]{len(pkgs):,} found[/]")

    def on_key(self, e) -> None:
        if e.key == "escape" and isinstance(self.app.focused, Input):
            e.stop()
            self.query_one(PackageList).focus()


# ── Update (0.2: choose what goes in; nog says what must stay together) ────
class UpdateScreen(VerticalScroll, can_focus=False):
    FORGE_HINTS = [("Space", "tick / untick"), ("Enter", "promote (Held)"), ("c", "check again"),
                   ("u", "update"), ("F1", "help")]

    def compose(self) -> ComposeResult:
        with Horizontal(classes="forge-buttons nf-top"):
            yield Button("Check for Updates (c)", id="up-check")
            yield Button("Update the Ticked Ones (u)", id="up-run", variant="primary")
        yield Static("", id="up-summary")
        yield Static("[b]Ready now[/]  [$forge-muted]untick to keep one back: nog says what must stay back with it[/]",
                     classes="nf-section")
        yield PackageHeader(option=False, ver_w=36, ticks=True, id="up-ready-head")
        yield PackageList(ver_w=36, id="up-ready")
        yield Static("[b]Held[/]", classes="nf-section")
        yield PackageHeader("Ready on", ver_w=36, id="up-held-head")
        yield PackageList(ver_w=36, id="up-held")

    def on_mount(self) -> None:
        for pl in self.query(PackageList):
            pl.apps = self.app.apps
        self.refresh_view()

    def refresh_view(self) -> None:
        from datetime import datetime
        from ..nog import Package
        app, m = self.app, "$forge-muted"
        plan = app.plan
        if app.plan_error:
            self.query_one("#up-summary", Static).update(f"[$forge-warn]{glyph('warn')} {app.plan_error}[/]")
            return
        if plan is None:
            self.query_one("#up-summary", Static).update(f"[{m}]Asking nog{glyph('ellipsis')}[/]")
            return

        def pkg(r):
            return Package(r["name"], r["new"], "", r["tier"], self._src(r), installed=True)
        held_by_keep = app.must_stay_back()            # name → why, from nog's answer to the unticked ones
        ready = []
        for r in plan["ready"]:
            name = r["name"]
            if name in app.keep:
                ready.append(Row(pkg(r), "", "muted", version=f"{r['old']} → {r['new']}", tick=False,
                                 note="kept back by you", note_role="warn"))
            elif name in held_by_keep:
                ready.append(Row(pkg(r), "", "muted", version=f"{r['old']} → {r['new']}", tick=False,
                                 note=held_by_keep[name], note_role="warn"))
            else:
                ready.append(Row(pkg(r), "", "ok", version=f"{r['old']} → {r['new']}", tick=True,
                                 note=r.get("note", "")))
        promote = "Promote" if is_console() else "↑ Promote"
        held = [Row(pkg(r), promote, "accent", version=f"{r['old']} → {r['new']}",
                    extra=datetime.fromtimestamp(r["ready_on"]).strftime("%b %-d") if r.get("ready_on") else "—",
                    note=r.get("note", "")) for r in plan["held"]]
        self.query_one("#up-ready", PackageList).show(ready)
        self.query_one("#up-held", PackageList).show(held)
        ticked = sum(1 for r in ready if r.tick)
        self.query_one("#up-run", Button).label = f"Update the Ticked Ones ({ticked}) (u)"
        self.query_one("#up-run", Button).disabled = ticked == 0 and not plan.get("unknown")
        unk = len(plan.get("unknown", []))
        busy = f"   [{m}]asking nog what must stay back{glyph('ellipsis')}[/]" if app.keep_busy else ""
        self.query_one("#up-summary", Static).update(
            f"[b]{ticked} to update[/] · {len(ready) - ticked} kept back · {len(held)} held"
            + (f" · {unk} nog will ask you about" if unk else "") + busy +
            f"\n[{m}]The update itself runs in the terminal: nog shows its plan and asks before anything "
            f"changes, and the password comes through the system's window.[/]")

    def on_key(self, e) -> None:
        if e.key == "space" and self.app.focused is self.query_one("#up-ready", PackageList):
            e.stop()
            row = self.query_one("#up-ready", PackageList).current()
            if row:
                self.app.toggle_keep(row.package.name)

    @staticmethod
    def _src(r: dict) -> str:
        return DashboardScreen._src(r)


# ── Tiers (0.3) ──────────────────────────────────────────────────────────────
class TiersScreen(Vertical):
    FORGE_HINTS = [("↑↓", "pick"), ("Enter", "tier or promote"), ("/", "find"), ("F1", "help")]

    def compose(self) -> ComposeResult:
        with Horizontal(classes="nf-bar"):
            yield Static("Show", classes="nf-label")
            yield Select([("All tiers", "0"), ("Tier 1", "1"), ("Tier 2", "2"), ("Tier 3", "3")], value="0",
                         allow_blank=False, id="tr-show")
            yield Static("Find", classes="nf-label")
            yield Input(placeholder="a package", id="tr-find")
        yield Static("", id="tr-summary", classes="nf-count")
        yield PackageHeader("Ready on", ver_w=30, id="tr-head")
        yield PackageList(ver_w=30, id="tr-list")

    def on_mount(self) -> None:
        self.query_one(PackageList).apps = self.app.apps
        self.refresh_view()

    def refresh_view(self) -> None:
        from datetime import datetime
        from ..nog import Package
        app, m = self.app, "$forge-muted"
        plan = app.plan
        if app.plan_error or plan is None:
            self.query_one("#tr-summary", Static).update(
                f"[$forge-warn]{glyph('warn')} {app.plan_error}[/]" if app.plan_error else
                f"[{m}]Asking nog{glyph('ellipsis')}[/]")
            return
        h = plan.get("holds") or {}
        days = " · ".join(f"Tier {t} waits {h[f'tier{t}_days']} days" for t in (1, 2, 3)
                          if f"tier{t}_days" in h)
        show = self.query_one("#tr-show", Select).value
        find = self.query_one("#tr-find", Input).value.strip().lower()
        waiting = sorted(plan["held"], key=lambda r: (r.get("ready_on") or 10 ** 12, r["name"]))
        option = "Tier  Promote" if is_console() else "⇅ Tier ↑ Promote"
        rows = []
        for r in waiting:
            if show != "0" and str(r["tier"]) != show:
                continue
            if find and find not in r["name"].lower():
                continue
            rows.append(Row(Package(r["name"], r["new"], "", r["tier"], UpdateScreen._src(r)), option, "accent",
                            version=f"{r['old']} → {r['new']}",
                            extra=datetime.fromtimestamp(r["ready_on"]).strftime("%b %-d") if r.get("ready_on")
                            else "—", note=r.get("note", "")))
        self.query_one(PackageList).show(rows)
        self.query_one("#tr-summary", Static).update(
            f"[{m}]{len(rows)} waiting, soonest first" + (f" · {days}" if days else "") + "[/]")

    @on(Select.Changed, "#tr-show")
    @on(Input.Changed, "#tr-find")
    def _changed(self, e) -> None:
        e.stop()
        self.refresh_view()

    def on_key(self, e) -> None:
        if e.key == "escape" and isinstance(self.app.focused, Input):
            e.stop()
            self.query_one(PackageList).focus()


# ── History ──────────────────────────────────────────────────────────────────
class HistoryScreen(VerticalScroll, can_focus=False):
    FORGE_HINTS = [("1-5", "screens"), ("F1", "help"), ("?", "all keys")]

    def compose(self) -> ComposeResult:
        yield Static("[b $forge-title-accent]History[/]   [$forge-muted]from nog's own logs: every install, "
                     "removal and update, from nogForge or a terminal[/]", classes="nf-section")
        yield Static("", id="hs-table")

    def on_mount(self) -> None:
        self.refresh_view()

    def refresh_view(self) -> None:
        runs = self.app.runs
        if not runs:
            self.query_one("#hs-table", Static).update("[$forge-muted]Nothing yet.[/]")
            return
        rows = [[r.when.strftime("%b %-d  %H:%M"), r.what[:46],
                 Text(f"{glyph('ok')} done", style="green") if r.ok else Text(f"{glyph('error')} {r.outcome}",
                                                                               style="red")]
                for r in runs[:60]]
        self.query_one("#hs-table", Static).update(table(self.app, ["When", "What", "Result"], rows))
