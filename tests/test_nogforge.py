"""nogForge 0.1, tested against a stand-in nog: a small script that answers
like nog 1.6.0 (``--json``) from recorded data, so no test ever installs,
removes or updates anything. Run: python -m unittest discover tests"""

from __future__ import annotations

import gzip
import json
import os
import re
import tempfile
import time
import unittest
from pathlib import Path

from nogforge import catalogue, nog, records
from nogforge.nog import NogError, Package
from nogforge.ui.packages import filtered, installed_row, search_row

ROOT = Path(__file__).resolve().parents[1]

LIST = {"nog": "1.6.0", "kind": "list", "packages": [
    {"name": "steam", "version": "1.0.0.87-3", "description": "Valve's digital software delivery system",
     "tier": 3, "source": "multilib", "explicit": True, "size": 20475439, "installed": 1787527681,
     "groups": [], "required_by": [], "protected": None},
    {"name": "gimp", "version": "3.2.6-2", "description": "GNU Image Manipulation Program", "tier": 3,
     "source": "extra", "explicit": True, "required_by": [], "protected": None},
    {"name": "linux-zen", "version": "7.2.7.zen1-1", "description": "The Linux ZEN kernel", "tier": 1,
     "source": "extra", "explicit": True, "required_by": [], "protected": "the system needs this to start"},
    {"name": "glibc", "version": "2.44", "description": "GNU C Library", "tier": 1, "source": "core",
     "explicit": False, "required_by": ["bash"], "protected": "part of the base system"},
    {"name": "fresh-editor-bin", "version": "0.5.1-1", "description": "A terminal text editor", "tier": 3,
     "source": "aur", "explicit": True, "required_by": [], "protected": None},
    {"name": "libfoo", "version": "1.0-1", "description": "A library", "tier": 3, "source": "extra",
     "explicit": False, "required_by": ["gimp"], "protected": "needed by gimp"},
]}
SEARCH = {"nog": "1.6.0", "kind": "search", "query": "krita", "results": [
    {"name": "krita", "version": "6.0.4-2", "description": "Edit and paint images", "source": "extra",
     "installed": False, "tier": 3},
    {"name": "gimp", "version": "3.2.6-2", "description": "GNU Image Manipulation Program", "source": "extra",
     "installed": True, "tier": 3},
    {"name": "krita-git", "version": "6.1.0-1", "description": "Krita, git version", "source": "aur",
     "installed": False, "tier": 3},
]}
PLAN = {"nog": "1.6.0", "kind": "plan",
        "sources": {"aur": "checked", "flatpak": "checked", "snap": "not installed", "chaotic_aur_off": False},
        "ready": [{"name": "tzdata", "source": "core", "tier": 3, "old": "2026d-1", "new": "2026e-1",
                   "note": "hold just expired"},
                  {"name": "breezy", "source": "extra", "tier": 3, "old": "3.3.21-2", "new": "3.3.22-1",
                   "note": "19 days past window"}],
        "held": [{"name": "linux-zen", "source": "extra", "tier": 1, "old": "7.2.7.zen1-1", "new": "7.2.8.zen1-2",
                  "note": "28 days remaining", "days_remaining": 28, "ready_on": int(time.time()) + 28 * 86400,
                  "kept_back": False, "coupled_to": None},
                 {"name": "grubforge", "source": "AUR", "tier": 2, "old": "1.1.3-1", "new": "2.0.0-1",
                  "note": "14 days remaining", "days_remaining": 14, "ready_on": int(time.time()) + 14 * 86400,
                  "kept_back": False, "coupled_to": None}],
        "unknown": [], "holds": {"tier1_days": 30, "tier2_days": 15, "tier3_days": 7}}

STAND_IN = '''#!/usr/bin/env python3
import json, sys, os
data = json.load(open(os.environ["NOGFORGE_TEST_DATA"]))
args = sys.argv[1:]
if args == ["--version"]:
    print("nog 1.6.0"); sys.exit(0)
if "--json" not in args:
    print("stand-in: only --json", file=sys.stderr); sys.exit(2)
print("nog: text that must not reach the JSON", file=sys.stderr)
print(json.dumps(data[args[0]]))
'''


class StandIn(unittest.TestCase):
    """A temporary folder with a stand-in nog, its answers, a catalogue and logs."""

    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        data = self.dir / "answers.json"
        data.write_text(json.dumps({"list": LIST, "search": SEARCH, "update": PLAN}))
        b = self.dir / "nog"
        b.write_text(STAND_IN)
        b.chmod(0o755)
        self._env = {k: os.environ.get(k) for k in ("NOGFORGE_NOG", "NOGFORGE_TEST_DATA", "DISPLAY",
                                                     "WAYLAND_DISPLAY", "SUDO_ASKPASS")}
        os.environ["NOGFORGE_NOG"] = str(b)
        os.environ["NOGFORGE_TEST_DATA"] = str(data)
        self.logs = self.dir / "logs"
        self.logs.mkdir()
        (self.logs / "20261002 nog-runs.csv").write_text(
            "date,time,user,command,status,outcome\n"
            "10/02/2026,04:52 PM,javier,install grubforge,0,done\n"
            "10/02/2026,01:00 PM,javier,update,0,done\n")
        (self.logs / "20261003 nog-runs.csv").write_text(
            "date,time,user,command,status,outcome\n"
            "10/03/2026,12:04 AM,javier,install bitlaforge,0,done\n"
            "10/03/2026,12:30 AM,javier,remove nothing-here,1,failed\n"
            "not,a,real,line\n")
        self.cache = self.dir / "pkg"
        self.cache.mkdir()
        (self.cache / "steam-1.0-1-x86_64.pkg.tar.zst").write_bytes(b"x" * 1000)
        (self.cache / "steam-1.0-1-x86_64.pkg.tar.zst.sig").write_bytes(b"x" * 99)
        self.apps = {"steam": catalogue.App("Steam", "Launcher for the Steam software distribution service",
                                            ("Game",)),
                     "gimp": catalogue.App("GNU Image Manipulation Program", "High-end image creation",
                                           ("Graphics", "2DGraphics")),
                     "krita": catalogue.App("Krita", "Digital Painting, Creative Freedom", ("Graphics",))}

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


class TalkingToNog(StandIn):
    def test_the_three_answers(self):
        pk = nog.installed()
        self.assertEqual(len(pk), 6)
        steam = next(p for p in pk if p.name == "steam")
        self.assertEqual((steam.tier, steam.source, steam.explicit, steam.protected), (3, "multilib", True, None))
        self.assertEqual(next(p for p in pk if p.name == "linux-zen").protected, "the system needs this to start")
        self.assertEqual([p.name for p in nog.search("krita")], ["krita", "gimp", "krita-git"])
        self.assertEqual(len(nog.plan()["ready"]), 2)

    def test_no_nog(self):
        os.environ["NOGFORGE_NOG"] = str(self.dir / "missing")
        with self.assertRaises(NogError):
            nog.installed()

    def test_an_older_nog_is_named(self):
        old = self.dir / "old-nog"
        old.write_text("#!/bin/sh\necho \"error: unexpected argument '--json' found\" >&2\nexit 2\n")
        old.chmod(0o755)
        os.environ["NOGFORGE_NOG"] = str(old)
        with self.assertRaises(NogError) as e:
            nog.installed()
        self.assertIn("older than 1.6.0", str(e.exception))

    def test_password_window_when_there_is_one(self):
        ask = self.dir / "askpass"
        ask.write_text("#!/bin/sh\n")
        ask.chmod(0o755)
        os.environ["SUDO_ASKPASS"] = str(ask)
        os.environ["DISPLAY"] = ":0"
        cmd, env = nog.change_command("install", ["krita"])
        self.assertEqual(cmd[1:], ["install", "krita"])
        self.assertEqual((env["NOG_ASKPASS"], env["SUDO_ASKPASS"]), ("1", str(ask)))
        os.environ.pop("DISPLAY")
        os.environ.pop("WAYLAND_DISPLAY", None)
        _cmd, env = nog.change_command("remove", ["steam"])
        self.assertNotIn("NOG_ASKPASS", env, "no desktop: the terminal asks, not a window that can't open")


class Catalogue(unittest.TestCase):
    XML = """<?xml version="1.0"?><components>
      <component type="desktop-application"><pkgname>steam</pkgname>
        <name>Steam</name><name xml:lang="ar">ستيم</name>
        <summary xml:lang="ar">مشغل</summary><summary>Launcher for Steam</summary>
        <categories><category>Game</category></categories></component>
      <component type="addon"><pkgname>krita-plugin</pkgname><name>Plugin</name></component>
    </components>"""

    def test_english_names_and_the_cache(self):
        d = Path(tempfile.mkdtemp())
        with gzip.open(d / "extra.xml.gz", "wt") as f:
            f.write(self.XML)
        cache = d / "apps.json"
        apps = catalogue.load(d, cache)
        self.assertEqual(apps["steam"].name, "Steam", "the untranslated name, not the first one in the file")
        self.assertEqual(apps["steam"].summary, "Launcher for Steam")
        self.assertNotIn("krita-plugin", apps, "add-ons aren't apps")
        self.assertTrue(cache.exists())
        (d / "extra.xml.gz").unlink()
        with gzip.open(d / "extra.xml.gz", "wt") as f:     # the stamp still matches: a different time counts
            f.write(self.XML)
        self.assertEqual(catalogue.load(d, cache)["steam"].name, "Steam")

    def test_badges(self):
        a = {"steam": catalogue.App("Steam", "", ("Game",)), "vlc": catalogue.App("VLC", "", ("AudioVideo",))}
        self.assertEqual(catalogue.kind_of("steam", a), ("🎮", "GA", "Games"))
        self.assertEqual(catalogue.kind_of("vlc", a)[2], "Sound & video")
        self.assertEqual(catalogue.kind_of("libfoo", a), catalogue.OTHER)


class Records(StandIn):
    def test_history_from_nogs_logs(self):
        runs = records.runs(self.logs)
        self.assertEqual([r.what for r in runs], ["Remove nothing-here", "Install bitlaforge", "Install grubforge",
                                                  "Update"])
        self.assertFalse(runs[0].ok)
        self.assertTrue(runs[1].ok)

    def test_cache(self):
        self.assertEqual(records.cache_size(self.cache), (1000, 1))
        self.assertEqual(records.size_words(9.6 * 1024 ** 3), "9.6 GB")


class Rows(StandIn):
    def test_locked_or_remove_or_install(self):
        pk = nog.installed()
        by = {p.name: p for p in pk}
        self.assertEqual(installed_row(by["steam"]).option_role, "danger")
        self.assertEqual(installed_row(by["linux-zen"]).option_role, "muted")
        self.assertEqual(search_row(Package("krita", "6", installed=False)).option_role, "ok")
        self.assertEqual(search_row(Package("gimp", "3", installed=True)).option_role, "muted")

    def test_search_ranks_the_name_first_and_drops_what_only_pacman_matched(self):
        from nogforge.ui.packages import relevant
        ps = [Package("abv-calc-git", "1", "ABV Calculator", source="aur"), Package("calc", "2", "Arbitrary precision",
              source="extra"), Package("perl", "5", "A programming language", source="core"),
              Package("calcurse", "4", "organizer", source="extra"), Package("kcalc", "3", "Scientific calculator",
              source="extra"), Package("bc", "1", "An arbitrary precision calculator language", source="extra")]
        self.assertEqual([p.name for p in relevant(ps, "calc", {})],
                         ["calc", "calcurse", "kcalc", "abv-calc-git", "bc"],
                         "exact, starts with, contains (repositories before the AUR), then descriptions; no perl")

    def test_show_type_find(self):
        pk = nog.installed()
        names = lambda ps: [p.name for p in ps]
        self.assertEqual(names(filtered(pk, "yours", "All types", "", self.apps)),
                         ["steam", "gimp", "linux-zen", "fresh-editor-bin"])
        self.assertEqual(names(filtered(pk, "all", "All types", "", self.apps))[-1], "libfoo")
        self.assertEqual(names(filtered(pk, "all", "All types", "", self.apps, repos={"aur"})), ["fresh-editor-bin"])
        self.assertEqual(names(filtered(pk, "all", "All types", "", self.apps, tier="1")), ["linux-zen", "glibc"])
        self.assertEqual(names(filtered(pk, "yours", "Graphics", "", self.apps)), ["gimp"])
        self.assertEqual(names(filtered(pk, "all", "All types", "manipulation", self.apps)), ["gimp"],
                         "Find matches descriptions, the catalogue's included")


def pick(pl, name):
    """Highlight a row by its package's name (never by position: rows get sorted)."""
    pl.highlighted = [r.package.name for r in pl.rows].index(name)


class Screens(StandIn, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        super().setUp()
        from unittest import mock
        # this computer's own Flatpaks and snaps stay out of the test's numbers
        for name, n in (("count_flatpaks", 2), ("count_snaps", 1)):
            patcher = mock.patch(f"nogforge.app.{name}", return_value=n)
            patcher.start()
            self.addCleanup(patcher.stop)

    def app(self):
        from nogforge.app import NogForgeApp
        a = NogForgeApp(apps=self.apps, logs=self.logs, cache_dir=self.cache)
        a.ran = []
        a.run_in_terminal = lambda cmd, env: (a.ran.append(cmd[1:]), 0)[1]
        return a

    async def until(self, pilot, cond, seconds=8.0):
        end = time.time() + seconds
        while not cond() and time.time() < end:
            await pilot.pause(0.1)
        return cond()

    async def test_dashboard_tables(self):
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            self.assertTrue(await self.until(pilot, lambda: app.plan is not None))
            await pilot.pause(0.3)
            def text(wid):          # what is drawn on screen, line by line
                w = app.query_one(wid)
                return "\n".join(w.render_line(y).text for y in range(w.size.height))
            self.assertIn("Total", text("#db-updates"))
            self.assertRegex(text("#db-updates"), r"Total\s+2\s+2\s+1\s+1\s+2")
            self.assertRegex(text("#db-yours"), r"Total\s+7\s", "4 chosen packages + 2 Flatpaks + 1 snap")
            self.assertIn("Install bitlaforge", text("#db-recent"))
            self.assertIn("1000 B", text("#db-space"))

    async def test_a_locked_package_never_reaches_nog(self):
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            await pilot.pause(0.5)
            await pilot.press("2")
            await pilot.pause(0.3)
            pl = app.query_one("#is-list")
            pick(pl, "linux-zen")
            await pilot.press("delete")
            await pilot.pause(0.4)
            self.assertNotEqual(type(app.screen).__name__, "ReviewDialog")
            self.assertEqual(app.ran, [])

    async def test_remove_is_reviewed_then_handed_to_nog(self):
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            await pilot.pause(0.5)
            await pilot.press("2")
            await pilot.pause(0.3)
            pl = app.query_one("#is-list")
            pick(pl, "steam")
            await pilot.press("delete")
            await pilot.pause(0.5)
            self.assertEqual(type(app.screen).__name__, "ReviewDialog")
            await pilot.press("escape")                        # cancel: nothing runs
            await pilot.pause(0.3)
            self.assertEqual(app.ran, [])
            await pilot.press("delete")
            await pilot.pause(0.5)
            await pilot.click("#go")
            await pilot.pause(0.5)
        self.assertEqual(app.ran, [["remove", "steam"]])
        self.assertEqual(app.changes, [("remove", "steam", 0)])

    async def test_a_click_on_the_row_selects_a_click_on_the_button_acts(self):
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            await pilot.pause(0.5)
            await pilot.press("2")
            await pilot.pause(0.4)
            pl = app.query_one("#is-list")
            await pilot.click("#is-list", offset=(10, 3))         # the second row's name
            await pilot.pause(0.4)
            self.assertEqual(pl.highlighted, 1)
            self.assertNotEqual(type(app.screen).__name__, "ReviewDialog", "a stray click never starts anything")
            await pilot.click("#is-list", offset=(pl.size.width - 8, 3))   # its button
            await pilot.pause(0.5)
            self.assertEqual(type(app.screen).__name__, "ReviewDialog")

    async def test_search_then_install(self):
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            await pilot.pause(0.5)
            await pilot.press("3")
            await pilot.pause(0.2)
            for ch in "krita":
                await pilot.press(ch)
            await pilot.click("#in-go")                       # the Search button
            pl = app.query_one("#in-list")
            self.assertTrue(await self.until(pilot, lambda: len(pl.rows) == 2))
            self.assertEqual(app.focused, pl, "after a search the results have the keys")
            self.assertEqual([r.package.name for r in pl.rows], ["krita", "krita-git"],
                             "only what has the words: gimp doesn't mention krita, though nog's search matched it")
            self.assertEqual([r.option_role for r in pl.rows], ["ok", "ok"])
            await pilot.press("enter")                         # Krita: Install
            await pilot.pause(0.5)
            self.assertEqual(type(app.screen).__name__, "ReviewDialog")
            searches = []
            real = app.run_search
            app.run_search = lambda q: (searches.append(q), real(q))
            await pilot.click("#go")
            await pilot.pause(0.5)
            self.assertEqual(app.ran, [["install", "krita"]])
            self.assertEqual(searches, ["krita"], "after a change the results are read again")
            bar = app.query_one("#in-filters")
            bar.repos = {"core", "extra", "multilib"}              # the AUR unticked in Repositories
            bar.post_message(bar.Changed())
            await pilot.pause(0.3)
            self.assertEqual([r.package.name for r in pl.rows], ["krita"], "unticking the AUR hides krita-git")

    async def test_update_shows_nogs_plan(self):
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            self.assertTrue(await self.until(pilot, lambda: app.plan is not None))
            await pilot.press("4")
            await pilot.pause(0.4)
            ready = app.query_one("#up-ready").rows
            held = {r.package.name: r for r in app.query_one("#up-held").rows}
            self.assertEqual(sorted(r.package.name for r in ready), ["breezy", "tzdata"])
            self.assertEqual(held["linux-zen"].version, "7.2.7.zen1-1 → 7.2.8.zen1-2")
            self.assertTrue(held["linux-zen"].extra, "Ready on is filled from nog's date")
            await pilot.click("#up-run")
            await pilot.pause(0.5)
            self.assertEqual(app.ran, [["update"]])

    async def test_nog_missing_is_said_not_crashed(self):
        os.environ["NOGFORGE_NOG"] = str(self.dir / "missing")
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            self.assertTrue(await self.until(pilot, lambda: bool(app.plan_error)))
            await pilot.pause(0.3)
            w = app.query_one("#db-yours")
            self.assertIn("isn't installed", "".join(w.render_line(y).text for y in range(w.size.height)))
            self.assertIsNone(app._exception)

    async def test_every_screen_fits_100_columns(self):
        from textual.widgets import Button, Input
        app = self.app()
        async with app.run_test(size=(100, 30)) as pilot:
            self.assertTrue(await self.until(pilot, lambda: app.plan is not None))
            for key in "123456":
                await pilot.press(key)
                await pilot.pause(0.5)
                for b in app.screen.query(Button):
                    if b.display and b.region.width:
                        self.assertIn(str(b.label), b.render_line(b.size.height // 2).text,   # the label sits mid-button
                                      f"screen {key}: {b.label!r} cut off")
                for w in app.screen.query("*"):
                    if isinstance(w, Input):
                        continue
                    self.assertFalse(w.display and w.show_horizontal_scrollbar, f"screen {key}: {w!r} scrolls sideways")
                for pl in app.screen.query("PackageList"):
                    for r in pl.rows:
                        from nogforge.ui.packages import colours
                        t = pl.draw(r, 1, max(pl.size.width - 2, 80), colours(app))
                        for line in t.split("\n"):
                            self.assertLessEqual(line.cell_len, max(pl.size.width - 2, 80), f"{r.package.name}")

    async def test_every_screen_on_a_text_console(self):
        """Found by the console check: Rich can't read the console's colour names."""
        from nogforge.app import NogForgeApp
        app = NogForgeApp(apps=self.apps, logs=self.logs, cache_dir=self.cache, console=True)
        app.run_in_terminal = lambda cmd, env: 0
        async with app.run_test(size=(100, 30)) as pilot:
            self.assertTrue(await self.until(pilot, lambda: app.plan is not None))
            for key in "123456":
                await pilot.press(key)
                await pilot.pause(0.5)
                self.assertIsNone(app._exception, f"screen {key} on a console")
            await pilot.press("3")
            for ch in "krita":
                await pilot.press(ch)
            await pilot.press("enter")                         # Enter searches too
            self.assertTrue(await self.until(pilot, lambda: bool(app.query_one("#in-list").rows)))
            self.assertIsNone(app._exception)
            self.assertTrue(app.query_one("#in-list").rows[0].option.startswith("Install"), "words, not marks")

    async def test_closing_note(self):
        from nogforge.cli import summary
        app = self.app()
        app.changes = [("install", "krita", 0), ("remove", "steam", 1)]
        heading, lines, level = summary(app)
        self.assertEqual(heading, "nogForge · 1 change made")
        self.assertEqual(lines, ["Installed krita.", "Remove steam: nog stopped (status 1)."])
        self.assertEqual(level, "warn")
        # every kind of change nogForge can hand to nog has its words (Javier's run: "promote" crashed it)
        app.changes = [(a, "x", 0) for a in ("install", "remove", "update", "clean", "promote", "pin", "new-kind")]
        heading, lines, _ = summary(app)
        self.assertEqual(len(lines), 7)
        self.assertIn("Promoted x.", lines)


class CommandLineAndNames(unittest.TestCase):
    def test_version_help(self):
        import contextlib
        import io
        from nogforge import __version__
        from nogforge.cli import main
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(main(["--version"]), 0)
            self.assertEqual(main(["--help"]), 0)
        self.assertIn(f"nogForge {__version__}", out.getvalue())
        self.assertIn("nog 1.6.0 or newer", out.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--nope"]), 2)

    def test_every_screen_has_its_manual_page(self):
        from forgekit import load_pages
        from nogforge.app import MANUAL_DIR, NogForgeApp
        ids = {pid for pid, _t, _m in load_pages(MANUAL_DIR)}
        for m in NogForgeApp.MENU:
            if m["kind"] == "section" or m["id"] == "history":
                self.assertIn(m["id"], ids, f"F1 on {m['title']} would open nothing")
        self.assertIn("keys", ids)

    def test_the_names(self):
        """nogForge, lowercase n; and the book persona never appears in this project."""
        for p in list((ROOT / "nogforge").rglob("*.py")) + list((ROOT / "nogforge" / "manual").glob("*.md")):
            text = p.read_text()
            self.assertEqual(re.findall(r".{0,20}NogForge(?!App).{0,20}", text), [], p.name)
            self.assertNotIn("Ba" + "lih", text, p.name)


if __name__ == "__main__":
    unittest.main()


# ── 0.2: Update with choices ─────────────────────────────────────────────────
SMART = r'''#!/usr/bin/env python3
"""A stand-in nog with a memory: --keep holds what it's told and what must
stay with it; update and promote change the versions it reports."""
import json, os, sys
d = json.load(open(os.environ["NOGFORGE_TEST_DATA"]))
state_f = os.environ["NOGFORGE_TEST_DATA"] + ".state"
state = json.load(open(state_f)) if os.path.exists(state_f) else {}
a = sys.argv[1:]
log = open(os.environ["NOGFORGE_TEST_DATA"] + ".ran", "a")
if a == ["--version"]:
    print("nog 1.6.0"); sys.exit(0)
def plan(keep, promote=()):
    ready, held = [], [r for r in d["plan"]["held"] if r["name"] not in promote]
    for r in d["plan"]["held"]:
        if r["name"] in promote:
            ready.append({**r, "note": "promoted by you"})
    stay = set(keep)
    for k in keep:
        stay |= set(d["couples"].get(k, []))
    for r in d["plan"]["ready"]:
        if r["name"] in keep:
            held.append({**r, "note": "kept back by you", "kept_back": True, "coupled_to": None, "ready_on": None})
        elif r["name"] in stay:
            partner = next(k for k in keep if r["name"] in d["couples"].get(k, []))
            held.append({**r, "note": f"blocked by {partner}", "kept_back": False, "coupled_to": partner,
                         "ready_on": None})
        else:
            ready.append(r)
    return {**d["plan"], "ready": ready, "held": held}, stay
keep = a[a.index("--keep") + 1].split(",") if "--keep" in a else []
promote = a[a.index("--promote") + 1].split(",") if "--promote" in a else []
named, i = [], 1
while i < len(a):                                   # nog 1.6.1: update a b c, only those
    if a[i].startswith("--"):
        i += 1 if a[i] == "--json" else 2
        continue
    named.append(a[i]); i += 1
if a and a[0] == "update" and named:
    keep += [r["name"] for r in d["plan"]["ready"] if r["name"] not in named]
if "--json" in a:
    if a[0] == "list":
        pk = [{**p, "version": state.get(p["name"], p["version"])} for p in d["list"]["packages"]]
        print(json.dumps({**d["list"], "packages": pk}))
    elif a[0] == "update":
        if keep or promote:
            open(os.environ["NOGFORGE_TEST_DATA"] + ".asked", "a").write(" ".join(a) + "\n")
        print(json.dumps(plan(keep, promote)[0]))
    sys.exit(0)
log.write(" ".join(a) + "\n")
if a[0] == "update":
    p, stay = plan(keep, promote)
    for r in p["ready"]:
        state[r["name"]] = r["new"]
elif a[0] == "unlock":
    r = next(r for r in d["plan"]["held"] if r["name"] == a[1])
    state[r["name"]] = r["new"]
json.dump(state, open(state_f, "w"))
'''

CHOICE_LIST = {"nog": "1.6.0", "kind": "list", "packages": [
    {"name": n, "version": v, "description": "", "tier": t, "source": "extra", "explicit": True,
     "required_by": [], "protected": None}
    for n, v, t in (("tzdata", "2026d-1", 3), ("ldb", "2:4.24.7-1", 3), ("libwbclient", "2:4.24.7-1", 3),
                    ("linux-zen", "7.2.7.zen1-1", 1))]}
CHOICE_PLAN = {"nog": "1.6.1", "kind": "plan", "sources": {}, "unknown": [],
               "ready": [{"name": "tzdata", "source": "core", "tier": 3, "old": "2026d-1", "new": "2026e-1",
                          "note": "hold just expired"},
                         {"name": "ldb", "source": "extra", "tier": 3, "old": "2:4.24.7-1", "new": "2:4.25.0-1",
                          "note": "hold just expired"},
                         {"name": "libwbclient", "source": "extra", "tier": 3, "old": "2:4.24.7-1",
                          "new": "2:4.25.0-1", "note": "hold just expired"}],
               "held": [{"name": "linux-zen", "source": "extra", "tier": 1, "old": "7.2.7.zen1-1",
                         "new": "7.2.8.zen1-2", "note": "28 days remaining", "ready_on": int(time.time()) + 86400 * 28,
                         "kept_back": False, "coupled_to": None}]}


class FullLogs(unittest.TestCase):
    """nog 1.6 keeps each run whole as a .log; nogForge finds and shows it."""

    def test_the_runs_own_log_is_found_and_read_as_the_screen_showed_it(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "20261003 nog-runs.csv").write_text(
                "date,time,user,command,status,outcome\n"
                "10/03/2026,09:16 PM,j,install /x/nog-rc2.pkg.tar.zst,0,done\n"
                "10/03/2026,09:27 PM,j,install /x/nog-rc3.pkg.tar.zst,0,done\n"
                "10/03/2026,09:37 PM,j,clean,0,done\n")
            (d / "20261003-211604 install nog-rc2.pkg.tar.zst.log").write_text(
                "Script started on 2026-10-03 21:16:04 [COMMAND=x]\nnog v1.6\r\n 10%\r 100%\r\ndone\r\n\n"
                "Script done on 2026-10-03 21:17:40 [COMMAND_EXIT_CODE=\"0\"]\n")
            (d / "20261003-212650 install nog-rc3.pkg.tar.zst.log").write_text("rc3 run\n")
            (d / "20261003-213700 clean.log").write_text("clean run\n")
            rs = {r.command.split()[-1]: r for r in records.runs(d)}
            self.assertEqual(records.full_log_for(rs["/x/nog-rc2.pkg.tar.zst"], d).name,
                             "20261003-211604 install nog-rc2.pkg.tar.zst.log")
            self.assertEqual(records.full_log_for(rs["/x/nog-rc3.pkg.tar.zst"], d).name,
                             "20261003-212650 install nog-rc3.pkg.tar.zst.log", "not the earlier install's")
            self.assertEqual(records.full_log_for(rs["clean"], d).name, "20261003-213700 clean.log",
                             "started in the same minute its line was written")
            text = records.read_full_log(d / "20261003-211604 install nog-rc2.pkg.tar.zst.log")
            self.assertEqual(text, "nog v1.6\n 100%\ndone", "script's lines dropped; a redrawn line as it ended")

    def test_a_run_from_before_nog_1_6_has_none(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "20261002 nog-runs.csv").write_text("date,time,user,command,status,outcome\n"
                                                     "10/02/2026,04:52 PM,j,install grubforge,0,done\n")
            self.assertIsNone(records.full_log_for(records.runs(d)[0], d))


class Choices(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        import subprocess
        self.dir = Path(tempfile.mkdtemp())
        self.data = self.dir / "answers.json"
        self.data.write_text(json.dumps({"list": CHOICE_LIST, "plan": CHOICE_PLAN,
                                         "couples": {"ldb": ["libwbclient"]}}))
        b = self.dir / "nog"
        b.write_text(SMART)
        b.chmod(0o755)
        self._env = {k: os.environ.get(k) for k in ("NOGFORGE_NOG", "NOGFORGE_TEST_DATA")}
        os.environ["NOGFORGE_NOG"], os.environ["NOGFORGE_TEST_DATA"] = str(b), str(self.data)
        self.subprocess = subprocess
        (self.dir / "logs").mkdir()

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def ran(self) -> list[str]:
        f = Path(str(self.data) + ".ran")
        return f.read_text().splitlines() if f.exists() else []

    def app(self):
        from nogforge.app import NogForgeApp
        a = NogForgeApp(apps={}, logs=self.dir / "logs", cache_dir=self.dir)
        a.run_in_terminal = lambda cmd, env: self.subprocess.run(cmd, env=env).returncode
        a.restarted = False
        a.restart = lambda: setattr(a, "restarted", True)
        return a

    async def until(self, pilot, cond, seconds=8.0):
        end = time.time() + seconds
        while not cond() and time.time() < end:
            await pilot.pause(0.1)
        return cond()

    async def open_update(self, app, pilot):
        self.assertTrue(await self.until(pilot, lambda: app.plan is not None))
        await pilot.press("4")
        await pilot.pause(0.4)
        return app.query_one("#up-ready")

    async def test_untick_and_nog_says_what_stays_back(self):
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            ready = await self.open_update(app, pilot)
            ready.focus()
            pick(ready, "ldb")
            await pilot.press("space")
            self.assertTrue(await self.until(pilot, lambda: app.keep_plan is not None))
            await pilot.pause(0.3)
            rows = {r.package.name: r for r in ready.rows}
            self.assertEqual((rows["ldb"].tick, rows["ldb"].note), (False, "kept back by you"))
            self.assertEqual((rows["libwbclient"].tick, rows["libwbclient"].note),
                             (False, "must stay back with ldb"), "nog's coupling, shown under the box")
            self.assertTrue(rows["tzdata"].tick)
            self.assertIn("(1)", str(app.query_one("#up-run").label))
            pick(ready, "libwbclient")                             # ticking it ticks ldb again
            await pilot.press("space")
            self.assertTrue(await self.until(pilot, lambda: not app.keep and not app.keep_busy))
            await pilot.pause(0.4)
            self.assertEqual(app.keep, set())
            self.assertTrue(all(r.tick for r in ready.rows))

    def asked(self) -> list[str]:
        f = Path(str(self.data) + ".asked")
        return f.read_text().splitlines() if f.exists() else []

    async def test_a_tick_shows_at_once_and_the_banner_says_nog_is_working(self):
        # Javier, 4 Oct: "make it look immediately while it's being executed in the back"
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            ready = await self.open_update(app, pilot)
            ready.focus()
            pick(ready, "ldb")
            await pilot.press("space")
            await pilot.pause(0.05)
            self.assertEqual(self.asked(), [], "nog not asked yet")
            rows = {r.package.name: r for r in ready.rows}
            self.assertEqual((rows["ldb"].tick, rows["ldb"].note), (False, "kept back by you"), "shown at once")
            run, busy = app.query_one("#up-run"), app.query_one("#up-busy")
            self.assertTrue(busy.has_class("-on") and busy.display, "the yellow banner")
            self.assertIn("nog is working on it", str(busy.render()))
            self.assertTrue(run.disabled and run.has_class("-waiting"), "Update waits, in pale yellow")
            await pilot.press("u")
            await pilot.pause(0.05)
            self.assertEqual(self.ran(), [], "u does nothing while nog works")
            self.assertTrue(await self.until(pilot, lambda: not app.keep_busy))
            await pilot.pause(0.3)
            self.assertFalse(busy.has_class("-on") or busy.display, "the banner goes when nog has answered")
            self.assertFalse(run.disabled or run.has_class("-waiting"))
            rows = {r.package.name: r for r in ready.rows}
            self.assertEqual(rows["libwbclient"].note, "must stay back with ldb", "then nog's answer")

    async def test_quick_clicks_go_to_nog_as_one_question(self):
        # Javier, 4 Oct: "if people go deselecting or selecting quick, batch them"
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            ready = await self.open_update(app, pilot)
            ready.focus()
            for name in ("ldb", "tzdata", "ldb"):                 # untick, untick, tick again: quickly
                pick(ready, name)
                await pilot.press("space")
                await pilot.pause(0.1)
            rows = {r.package.name: r for r in ready.rows}
            self.assertEqual((rows["ldb"].tick, rows["tzdata"].tick), (True, False), "each click shown at once")
            self.assertTrue(await self.until(pilot, lambda: not app.keep_busy))
            self.assertEqual(self.asked(), ["update --keep tzdata --json"], "one question, with the last choices")

    def test_update_hands_nog_the_ticked_list_or_for_an_older_nog_what_you_kept(self):
        from nogforge.app import update_args
        plan = {"nog": "1.6.1", "ready": [{"name": "vde2"}, {"name": "git"}], "unknown": [{"name": "x"}]}
        self.assertEqual(update_args(plan, {"freerdp"}, {"git"}), ["git", "vde2", "x", "--promote", "git"])
        self.assertEqual(update_args({**plan, "nog": "1.6.0"}, {"freerdp"}, {"git"}),
                         ["--keep", "freerdp", "--promote", "git"], "nog 1.6.0 has no named list")
        self.assertEqual(update_args({**plan, "nog": "1.7.0-rc.1"}, set(), set()), ["git", "vde2", "x"])

    async def test_a_click_on_the_box_unticks(self):
        # Javier's run: "I could not de-select a package that is ticked"
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            ready = await self.open_update(app, pilot)
            y = [r.package.name for r in ready.rows].index("ldb") * 2 + 1 - ready.scroll_offset.y
            await pilot.click("#up-ready", offset=(2, y))
            self.assertTrue(await self.until(pilot, lambda: "ldb" in app.keep))

    async def test_update_the_ticked_ones_then_what_changed(self):
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            ready = await self.open_update(app, pilot)
            ready.focus()
            pick(ready, "ldb")
            await pilot.press("space")
            self.assertTrue(await self.until(pilot, lambda: app.keep_plan is not None))
            await pilot.press("u")
            self.assertTrue(await self.until(pilot, lambda: type(app.screen).__name__ == "WhatChanged"))
            self.assertEqual(self.ran(), ["update tzdata"], "nog 1.6.1: the ticked ones by name, only those")
            text = " ".join(str(w.render()) for w in app.screen.query("Static"))
            self.assertIn("1 updated", text)
            self.assertIn("Kept back by you: ldb, libwbclient", text)
            self.assertFalse(app.screen.query("#restart"), "no kernel: no restart offered")
            await pilot.press("l")
            await pilot.pause(0.3)
            self.assertFalse(app.restarted)

    async def test_c_always_cleans_up_k_checks_for_updates(self):
        # Javier, 3 Oct: "c" said "check again" on Update and cleaned up on the Dashboard: confusing
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            await self.open_update(app, pilot)
            await pilot.press("k")
            await pilot.pause(0.1)
            self.assertTrue(await self.until(pilot, lambda: app.plan is not None), "k asked nog again")
            self.assertEqual(self.ran(), [], "checking changes nothing")
            await pilot.press("c")
            self.assertTrue(await self.until(pilot, lambda: bool(self.ran())))
            self.assertTrue(self.ran()[0].startswith("clean"), "c is clean up on Update too")

    async def test_promote_makes_it_ready_then_the_update_takes_it(self):
        # Javier, 3 Oct: "shouldn't promote just bring the package to due, so it enters the ready list?"
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            await self.open_update(app, pilot)
            held = app.query_one("#up-held")
            held.focus()
            pick(held, "linux-zen")
            await pilot.press("enter")                              # ↑ Promote
            self.assertTrue(await self.until(pilot, lambda: app.keep_plan is not None))
            await pilot.pause(0.3)
            self.assertEqual(self.ran(), [], "promoting installs nothing by itself")
            ready = {r.package.name: r for r in app.query_one("#up-ready").rows}
            self.assertEqual((ready["linux-zen"].tick, ready["linux-zen"].note), (True, "promoted by you"))
            self.assertNotIn("linux-zen", [r.package.name for r in app.query_one("#up-held").rows])
            await pilot.press("u")
            self.assertTrue(await self.until(pilot, lambda: type(app.screen).__name__ == "WhatChanged"))
            self.assertEqual(self.ran(), ["update ldb libwbclient linux-zen tzdata --promote linux-zen"],
                             "the ticked ones by name, the promoted one among them")
            self.assertTrue(app.screen.query("#restart"), "a new kernel: Restart Now (r) offered")
            self.assertEqual(app.focused.id, "later", "Enter alone never restarts")
            await pilot.press("enter")
            await pilot.pause(0.3)
            self.assertFalse(app.restarted)

    async def test_unticking_a_promoted_one_sends_it_back_to_wait(self):
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            await self.open_update(app, pilot)
            held = app.query_one("#up-held")
            held.focus()
            pick(held, "linux-zen")
            await pilot.press("enter")
            self.assertTrue(await self.until(pilot, lambda: app.keep_plan is not None))
            ready = app.query_one("#up-ready")
            ready.focus()
            pick(ready, "linux-zen")
            await pilot.press("space")
            self.assertTrue(await self.until(pilot, lambda: not app.promote and not app.keep_busy))
            await pilot.pause(0.3)
            self.assertIn("linux-zen", [r.package.name for r in app.query_one("#up-held").rows])

    async def test_restart_now(self):
        app = self.app()
        async with app.run_test(size=(100, 32)) as pilot:
            await self.open_update(app, pilot)
            held = app.query_one("#up-held")
            held.focus()
            pick(held, "linux-zen")
            await pilot.press("enter")
            self.assertTrue(await self.until(pilot, lambda: app.keep_plan is not None))
            await pilot.press("u")
            self.assertTrue(await self.until(pilot, lambda: type(app.screen).__name__ == "WhatChanged"))
            await pilot.press("r")
            await pilot.pause(0.3)
            self.assertTrue(app.restarted)
