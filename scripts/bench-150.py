#!/usr/bin/env python3
"""The 1.5.0 bench, driven by a script (the night of 2026-10-16: Javier asleep,
"work without needing me"). It walks `testing/20261015 - Test Matrix for
nogForge v1-5-0.md` §2 the way a person would — the same keys, the same
buttons — on the real app against the real nog, headless (Textual's Pilot),
and keeps a screenshot (SVG) of every step plus a results table.

    scripts/bench-150.py --out DIR [--changes] [--size 110x34] [--password P]

Without --changes only the read-only steps run (safe on this desktop: nothing
installed, removed or cleaned). With --changes the steps that change the
computer run too (2.6 install a Flatpak, 2.7 uninstall it, 2.9 clean up, and
the #27 check: an uninstall whose leftover another app still uses) — for the
test VM only. --password answers nogForge's own password box if it appears
(the VM's sudo doesn't ask; the box is reported either way).

Every step is PASS / FAIL / SKIP with a note; a failing step never stops the
rest. Exit 1 when any step failed.
"""

from __future__ import annotations

import argparse
import asyncio
import html
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

# run from the repository (python scripts/bench-150.py) or against the installed
# package (PYTHONPATH=/usr/lib/nogforge): the repository's own code comes first when it is here
_repo = Path(__file__).resolve().parents[1]
if (_repo / "nogforge" / "__init__.py").is_file() and str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--changes", action="store_true")
ap.add_argument("--size", default="110x34")
ap.add_argument("--password", default=None)
ap.add_argument("--only", default=None, help="comma-separated step prefixes to run (e.g. 2.7,#27); the rest are skipped")
A = ap.parse_args()
OUT = Path(A.out)
OUT.mkdir(parents=True, exist_ok=True)
W, H = (int(x) for x in A.size.lower().split("x"))

RESULTS: list[tuple[str, str, str]] = []
_n = 0
PILOT = APP = None
# Textual takes over sys.stdout while the app runs: write to the real one, and to a log of our own
REAL_OUT = sys.__stdout__
LOG = open(OUT / "bench.log", "a", buffering=1)
import faulthandler
faulthandler.register(__import__("signal").SIGUSR1, file=LOG, all_threads=True)   # kill -USR1 <pid>: where is it?
STEP_SECONDS = {"read": 420.0, "change": 2100.0}


def out(line: str) -> None:
    for f in (REAL_OUT, LOG):
        try:
            f.write(line + "\n")
            f.flush()
        except Exception:
            pass


def say(step: str, verdict: str, note: str) -> None:
    note = " ".join(note.split())
    RESULTS.append((step, verdict, note))
    out(f"| {step} | **{verdict}** | {note} |")


def shot(app, name: str) -> Path:
    global _n
    _n += 1
    p = OUT / f"{_n:02d}-{name}.svg"
    try:
        p.write_text(app.export_screenshot(title=f"nogForge bench · {name}"))
    except Exception as e:                       # a shot that fails must not fail the step
        p.write_text(f"<!-- no screenshot: {e} -->")
    return p


def svg_text(app) -> str:
    """Every word on the screen, from the SVG (spacing is approximate)."""
    try:
        s = app.export_screenshot()
    except Exception:
        return ""
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return " ".join(html.unescape(s).split())


def text(app, wid: str) -> str:
    w = app.query_one(wid)
    return "\n".join(w.render_line(y).text for y in range(w.size.height))


async def until(pilot, cond, seconds=30.0):
    end = time.time() + seconds
    while time.time() < end:
        try:
            if cond():
                return True
        except Exception:
            pass
        await pilot.pause(0.2)
    try:
        return bool(cond())
    except Exception:
        return False


def pick(pl, name: str) -> None:
    names = [r.package.name for r in pl.rows]
    if name not in names:
        raise AssertionError(f"no row {name!r}; first rows: {names[:8]} ({len(names)} rows)")
    pl.highlighted = names.index(name)


def sh(*cmd: str) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


async def drive_run(pilot, app, name: str, timeout: float = 1500.0) -> dict:
    """Wait for nog's run window, answer every yes/no with Yes, keep what it asked
    and how the window looked, close it when nog is done."""
    from forgekit import RunWindow
    from forgekit.terminal import TerminalPane
    if not await until(pilot, lambda: isinstance(app.screen, RunWindow), 30):
        raise AssertionError(f"no run window; screen is {type(app.screen).__name__}")
    win = app.screen
    await pilot.pause(0.6)
    r = {"title": win._title, "label_at_start": str(win.query_one("#run-toggle").label),
         "folded_at_start": not win.query_one(TerminalPane).display, "questions": [], "screen_open_at_question": [],
         "password_box": False, "label_when_open": None}
    end = time.time() + timeout
    while win.status is None and time.time() < end:
        top = app.screen
        if type(top).__name__ == "PasswordDialog":
            r["password_box"] = True
            if A.password:
                for ch in A.password:
                    await pilot.press(ch)
                await pilot.press("enter")
                await pilot.pause(1.0)
                continue
            raise AssertionError("nogForge's password box came up and no --password was given")
        q = win.query_one("#run-question")
        if q.display and win.query_one("#run-yes").display and win._question:
            r["questions"].append(win._question)
            r["screen_open_at_question"].append(win.query_one(TerminalPane).display)
            if win.query_one(TerminalPane).display and r["label_when_open"] is None:
                r["label_when_open"] = str(win.query_one("#run-toggle").label)
            shot(app, f"{name}-question-{len(r['questions'])}")
            await pilot.click("#run-yes")
            await pilot.pause(0.8)
            continue
        await pilot.pause(0.4)
    r["status"] = win.status
    r["screen_tail"] = "\n".join(win.query_one(TerminalPane).lines_plain()[-12:])
    r["label_at_end"] = str(win.query_one("#run-toggle").label)
    shot(app, f"{name}-done")
    if win.status is None:
        raise AssertionError(f"nog still running after {int(timeout)} s; questions so far: {r['questions']}")
    await pilot.click("#run-close")
    await until(pilot, lambda: not isinstance(app.screen, RunWindow), 20)
    await pilot.pause(0.8)
    return r


async def settle(pilot, app) -> None:
    """Back to the app's own screen: a step that failed may have left a window open."""
    for _ in range(6):
        if app.screen is app.screen_stack[0]:
            return
        top = app.screen
        if type(top).__name__ == "PasswordDialog":
            await pilot.press("escape")
        elif hasattr(top, "status") and getattr(top, "status", None) is None and hasattr(top, "_cmd"):
            await pilot.pause(2.0)                       # nog still running: wait, never close it
            continue
        else:
            await pilot.press("escape")
        await pilot.pause(0.5)


ONLY = [x.strip() for x in A.only.split(",")] if A.only else None


async def step(name: str, fn, *args, kind: str = "read"):
    if ONLY is not None and not any(name.startswith(o) for o in ONLY):
        say(name, "SKIP", "not in --only")
        return
    out(f"-- {time.strftime('%H:%M:%S')} {name}")
    try:
        await settle(PILOT, APP)
        note = await asyncio.wait_for(fn(*args), STEP_SECONDS[kind])
        say(name, "PASS", note or "")
    except asyncio.TimeoutError:
        say(name, "FAIL", f"hung: no answer after {int(STEP_SECONDS[kind])} s (the app was left as it was)")
    except SkipStep as e:
        say(name, "SKIP", str(e))
    except Exception as e:
        tb = traceback.format_exc().strip().splitlines()[-1]
        say(name, "FAIL", f"{e} ({tb})" if str(e) not in tb else tb)


class SkipStep(Exception):
    pass


async def main() -> int:
    from forgekit import RunWindow
    from nogforge import __version__
    from nogforge.app import NogForgeApp

    changes = A.changes
    app = NogForgeApp()
    out(f"nogForge {__version__} · size {W}x{H} · changes={'yes' if changes else 'no (read-only)'} · "
        f"nog: {sh('nog', '--version')[1]} · {time.strftime('%Y-%m-%d %H:%M')}\n")
    out("| step | result | notes |\n|---|---|---|")
    async with app.run_test(size=(W, H)) as pilot:
        global PILOT, APP
        PILOT, APP = pilot, app
        # nog's first answers (the list, the plan, the report) before any step: a list that is still being
        # rebuilt loses the highlighted row under the keys (seen with --only 2.7: Del reached no review)
        t0 = time.time()
        loaded = await until(pilot, lambda: app.packages and app.plan is not None and app.maint is not None, 240)
        out(f"-- loaded in {time.time() - t0:.0f} s: packages {len(app.packages)}, plan {app.plan is not None}, "
            f"report {app.maint is not None}{'' if loaded else ' (NOT all loaded)'}")

        # ── 2.2 the Dashboard ────────────────────────────────────────────────
        async def s22():
            ok = await until(pilot, lambda: app.packages and app.plan is not None and app.maint is not None, 240)
            await pilot.pause(0.8)
            shot(app, "2.2-dashboard")
            if not ok:
                raise AssertionError(f"nog didn't answer in time: packages={bool(app.packages)} plan={app.plan is not None} "
                                     f"maint={app.maint is not None} err={app.maint_error!r}")
            words = svg_text(app)
            assert "Maintenance" in words, "Maintenance in the menu bar"
            assert "1-7 menu" in words, f"the bottom bar says 1-7 menu: {words[-300:]}"
            yours = text(app, "#db-yours")
            space = text(app, "#db-space")
            srcs = {p.source for p in app.packages}
            notes = [f"Yours table: {' / '.join(l.strip() for l in yours.splitlines() if l.strip())[:220]}"]
            for s_, word in (("flatpak", "Flatpak"), ("snap", "Snap")):
                if s_ in srcs:
                    assert word in yours, f"{word} row in Yours"
            assert "Could go" in space, f"Space says what could go: {space!r}"
            notes.append(f"Space: {' '.join(space.split())[:160]}")
            return "; ".join(notes)
        await step("2.2 Dashboard: Maintenance in the bar, 1-7 menu, Flatpak/Snap in Yours, Could go", s22)

        # ── 2.3 In-System, Show: All ─────────────────────────────────────────
        async def s23():
            await pilot.press("2")
            await pilot.pause(0.5)
            app.query_one("#is-show").value = "all"
            pl = app.query_one("#is-list")
            # All is applied a moment after the drop-down changes: wait for a row that Yours never shows
            ok = await until(pilot, lambda: any(not r.package.explicit for r in pl.rows), 60)
            assert ok, f"Show: All applied ({len(pl.rows)} rows, all explicit)"
            rows = pl.rows
            fl = [r for r in rows if r.package.flatpak]
            sn = [r for r in rows if r.package.snap]
            locked = [r for r in sn if r.package.protected]
            assert sn, "snap rows under All"
            assert locked, "a base snap is Locked"
            for r in locked:
                assert r.option_role == "muted", f"{r.package.name}: Locked, no Uninstall button"
                assert r.package.protected == "the system under the snaps", r.package.protected
            where = {r.package.where for r in fl + sn}
            # scroll to the snaps and keep the picture
            pick(pl, locked[0].package.name)
            await pilot.pause(0.5)
            shot(app, "2.3-insystem-all-snaps")
            words = svg_text(app)
            assert "Locked" in words, "the word Locked is drawn"
            return (f"{len(rows)} rows; Flatpak rows {len(fl)} ({', '.join(r.package.name for r in fl[:3])}"
                    f"{'…' if len(fl) > 3 else ''}); Snap rows {len(sn)}: {', '.join(r.package.name for r in sn)}; "
                    f"Locked: {', '.join(r.package.name for r in locked)}; column says {sorted(where)}")
        await step("2.3 In-System · All: Flatpak + Snap rows, base snaps Locked", s23)

        # ── 2.4 Repositories window ──────────────────────────────────────────
        async def s24():
            await pilot.press("2")
            await pilot.pause(0.3)
            pl = app.query_one("#is-list")
            app.query_one("#is-show").value = "all"
            await pilot.pause(0.4)
            pl.focus()
            await pilot.press("p")
            ok = await until(pilot, lambda: type(app.screen).__name__ == "RepositoriesDialog", 10)
            assert ok, f"p opens Repositories; screen is {type(app.screen).__name__}"
            dlg = app.screen
            names = list(dlg.names)
            shot(app, "2.4-repositories")
            low = [n.lower() for n in names]
            checked = {k for k, v in ((app.plan or {}).get("sources") or {}).items() if v == "checked"}
            for src in ("flatpak", "snap"):
                if src in checked:
                    assert src in low, f"{src}: nog checked it, so it is listed (F-17): {names}"
            assert low.index("flatpak") > low.index("aur") if "aur" in low else True, f"after the AUR: {names}"
            # untick the source that has rows here, see them go, tick it back
            have = {r.package.source for r in pl.rows}
            target = next((n for n in names if n.lower() in ("flatpak", "snap") and n.lower() in have), None)
            if target is None:
                await pilot.press("escape")
                return f"listed {names}; nothing installed from Flatpak or Snap here, so untick not tried"
            lst = dlg.query_one("#rp-list")
            lst.deselect(target)
            await pilot.pause(0.2)
            await pilot.press("enter")
            await until(pilot, lambda: type(app.screen).__name__ != "RepositoriesDialog", 10)
            await pilot.pause(0.8)
            left = [r for r in pl.rows if r.package.source == target.lower()]
            shot(app, f"2.4-without-{target.lower()}")
            assert not left, f"{target} unticked: {len(left)} of its rows still shown"
            pl.focus()
            await pilot.press("p")
            await until(pilot, lambda: type(app.screen).__name__ == "RepositoriesDialog", 10)
            app.screen.query_one("#rp-list").select(target)
            await pilot.pause(0.2)
            await pilot.press("enter")
            await until(pilot, lambda: type(app.screen).__name__ != "RepositoriesDialog", 10)
            await pilot.pause(0.8)
            back = [r for r in pl.rows if r.package.source == target.lower()]
            assert back, f"{target} ticked back: its rows return"
            return f"listed {names}; {target} unticked → its rows gone; ticked back → {len(back)} rows again"
        await step("2.4 p Repositories: Flatpak + Snap after the AUR; untick → rows go; tick back", s24)

        # ── 2.5 Install: calculator ──────────────────────────────────────────
        async def s25():
            await pilot.press("3")
            await pilot.pause(0.4)
            box = app.query_one("#in-find")
            box.focus()
            box.value = ""
            for ch in "calculator":
                await pilot.press(ch)
            await pilot.press("enter")
            pl = app.query_one("#in-list")
            ok = await until(pilot, lambda: bool(pl.rows), 240)
            assert ok, "nog's search answered"
            await pilot.pause(0.5)
            rows = pl.rows
            srcs = {}
            for r in rows:
                srcs[r.package.where] = srcs.get(r.package.where, 0) + 1
            fl = [r for r in rows if r.package.flatpak]
            sn = [r for r in rows if r.package.snap]
            assert fl, f"Flatpak results: {srcs}"
            assert sn, f"Snap results: {srcs}"
            calc = next((r for r in fl if r.package.name == "org.gnome.Calculator"), None)
            assert calc is not None, f"org.gnome.Calculator among the Flatpak rows: {[r.package.name for r in fl][:8]}"
            assert calc.package.install_as == "flatpak/org.gnome.Calculator", calc.package.install_as
            assert "Install" in calc.option, calc.option
            pick(pl, "org.gnome.Calculator")
            await pilot.pause(0.4)
            shot(app, "2.5-install-calculator")
            return f"{len(rows)} rows: {srcs}; org.gnome.Calculator is a Flatpak row with '{calc.option.strip()}'"
        await step("2.5 Install 'calculator': repositories, AUR, Flatpak (with IDs), Snap; + Install", s25)

        # ── 2.6 install the Flatpak (changes) ────────────────────────────────
        async def s26():
            if not changes:
                raise SkipStep("a real install: VM only (--changes)")
            code, before = sh("flatpak", "list", "--app", "--columns=application")
            assert "org.gnome.Calculator" not in before, "not installed before"
            pl = app.query_one("#in-list")
            pick(pl, "org.gnome.Calculator")
            pl.focus()
            await pilot.press("enter")
            ok = await until(pilot, lambda: type(app.screen).__name__ == "ReviewDialog", 10)
            assert ok, f"the review: {type(app.screen).__name__}"
            await pilot.pause(0.4)
            words = svg_text(app)
            shot(app, "2.6-review-flatpak")
            assert "flatpak/org.gnome.Calculator" in words or "flatpak/org.gnome.Calculator" in words.replace(" ", ""), \
                "the review names nog's install_as"
            assert "asks first" in words, "the review says flatpak asks first"
            await pilot.click("#go")
            r = await drive_run(pilot, app, "2.6-install")
            code, after = sh("flatpak", "list", "--app", "--columns=application")
            assert r["status"] == 0, f"nog's status {r['status']}; its screen: {r['screen_tail']}"
            assert "org.gnome.Calculator" in after, f"installed: {after}"
            assert r["folded_at_start"], "the run starts as a progress bar, screen folded (#23)"
            assert r["label_at_start"].startswith(("▾", "v")), r["label_at_start"]
            assert any("roceed" in q for q in r["questions"]), f"flatpak's question caught: {r['questions']}"
            assert all(r["screen_open_at_question"]), "the screen opened for the question (the table in view)"
            return (f"title {r['title']!r}; button at start {r['label_at_start']!r}; questions answered Yes: {r['questions']}; "
                    f"button while open {r['label_when_open']!r}; status 0; flatpak list has it now; password box: "
                    f"{'yes' if r['password_box'] else 'no'}")
        await step("2.6 Enter on org.gnome.Calculator → review → Install → nog's window → flatpak asks → Yes", s26, kind="change")

        # ── 2.7 uninstall it (changes) ───────────────────────────────────────
        async def s27():
            if not changes:
                raise SkipStep("a real uninstall: VM only (--changes)")
            await pilot.press("2")
            await pilot.pause(0.4)
            pl = app.query_one("#is-list")
            app.query_one("#is-show").value = "all"
            ok = await until(pilot, lambda: "org.gnome.Calculator" in [r.package.name for r in pl.rows], 90)
            assert ok, "the new Flatpak is an In-System row after the install"
            pick(pl, "org.gnome.Calculator")
            row = pl.rows[pl.highlighted]
            assert "Uninstall" in row.option, row.option
            assert row.package.remove_as == "org.gnome.Calculator", row.package.remove_as
            await pilot.pause(0.3)
            shot(app, "2.7-insystem-calculator")
            pl.focus()
            pick(pl, "org.gnome.Calculator")
            assert pl.rows[pl.highlighted].package.name == "org.gnome.Calculator", "the highlighted row is the one picked"
            await pilot.press("delete")
            ok = await until(pilot, lambda: type(app.screen).__name__ == "ReviewDialog", 10)
            assert ok, f"the review: {type(app.screen).__name__}"
            await pilot.pause(0.4)
            words = svg_text(app)
            shot(app, "2.7-review-uninstall")
            for piece in ("flatpak shows what goes", "asks first"):          # wrapped across two lines on screen
                assert piece in words, f"the review says who asks: {piece!r}"
            await pilot.click("#go")
            r = await drive_run(pilot, app, "2.7-uninstall")
            code, after = sh("flatpak", "list", "--app", "--columns=application")
            assert r["status"] == 0, f"nog's status {r['status']}; its screen: {r['screen_tail']}"
            assert "org.gnome.Calculator" not in after, f"gone: {after}"
            return f"title {r['title']!r}; questions answered Yes: {r['questions']}; status 0; flatpak list without it"
        await step("2.7 In-System → ✕ Uninstall on the Flatpak → review → nog's window → flatpak asks → Yes", s27, kind="change")

        # ── #27 an uninstall whose leftover another app still uses (changes) ─
        async def s27b():
            if not changes:
                raise SkipStep("a real uninstall: VM only (--changes)")
            victim, leftover, user = "cliamp", "yt-dlp", "mpv"
            for p_ in (victim, leftover, user):
                code, _ = sh("pacman", "-Q", p_)
                if code:
                    raise SkipStep(f"{p_} isn't installed here; the pair {victim} → {leftover} (optional for {user}) is needed")
            await pilot.press("2")
            await pilot.pause(0.4)
            pl = app.query_one("#is-list")
            app.query_one("#is-show").value = "all"
            await until(pilot, lambda: victim in [r.package.name for r in pl.rows], 60)
            pick(pl, victim)
            pl.focus()
            pick(pl, victim)
            assert pl.rows[pl.highlighted].package.name == victim, "the highlighted row is the one picked"
            await pilot.press("delete")
            ok = await until(pilot, lambda: type(app.screen).__name__ == "ReviewDialog", 10)
            assert ok, "the review"
            await pilot.pause(0.4)
            words = svg_text(app)
            shot(app, "27-review-keep")
            assert "Keep" in words, "the review says nog offers a Keep for what another app still uses"
            await pilot.click("#go")
            r = await drive_run(pilot, app, "27-uninstall-keep")
            gone = sh("pacman", "-Q", victim)[0] != 0
            kept = sh("pacman", "-Q", leftover)[0] == 0
            keepq = [q for q in r["questions"] if leftover in q]
            assert r["status"] == 0, f"nog's status {r['status']}; its screen: {r['screen_tail']}"
            assert keepq, f"nog's Keep question about {leftover} came up as a Yes/No bar: {r['questions']}"
            assert gone, f"{victim} removed"
            assert kept, f"{leftover} kept (Yes to Keep): still installed"
            return f"questions, all answered Yes: {r['questions']}; {victim} gone, {leftover} kept for {user}"
        await step("#27 Uninstall cliamp: nog's Keep question (yt-dlp, mpv uses it) in the window → Yes keeps it", s27b, kind="change")

        # ── 2.8 Maintenance ──────────────────────────────────────────────────
        async def s28():
            await pilot.press("5")
            await pilot.pause(0.6)
            assert app.query_one("#forge-work").current == "sec-maintain"
            ok = await until(pilot, lambda: app.maint is not None and app.query_one("#mt-list").option_count == 5, 120)
            assert ok, f"the report: maint={app.maint is not None} rows={app.query_one('#mt-list').option_count} err={app.maint_error!r}"
            lst = app.query_one("#mt-list")
            cats = app.maint["categories"]
            dis = [lst.get_option_at_index(i).disabled for i in range(5)]
            for i, c in enumerate(cats):
                assert dis[i] == (not c.get("items")), f"{c['id']}: tickable iff it has something"
            btn = app.query_one("#mt-run")
            assert btn.disabled and "(0)" in str(btn.label), f"{btn.label!r} disabled={btn.disabled}"
            lst.focus()
            lst.highlighted = 0
            await pilot.pause(0.4)
            shot(app, "2.8-maintenance")
            summary = text(app, "#mt-summary")
            detail = text(app, "#mt-detail")
            assert "could go" in summary.lower(), summary
            return (f"rows: {[(c['id'], c['items'], round(c['bytes'] / 1e6, 1)) for c in cats]} MB; empty ones not tickable; "
                    f"button {btn.label!r} greyed; summary: {' '.join(summary.split())[:120]}; detail: {' '.join(detail.split())[:100]}")
        await step("2.8 Maintenance: five rows with sizes, the highlighted one explained, Clean Up (0) greyed", s28)

        # ── 2.9 clean up two categories (changes) ────────────────────────────
        async def s29():
            if not changes:
                raise SkipStep("a real clean-up: VM only (--changes)")
            await pilot.press("5")
            await pilot.pause(0.5)
            lst = app.query_one("#mt-list")
            cats = {c["id"]: c for c in app.maint["categories"]}
            want = [cid for cid in ("cache", "snap") if cats.get(cid, {}).get("items")]
            if not want:
                raise SkipStep(f"nothing in cache or snap to clean: {[(c, cats[c]['items']) for c in cats]}")
            before = {cid: cats[cid]["items"] for cid in want}
            for cid in want:
                lst.select(cid)
            await pilot.pause(0.4)
            btn = app.query_one("#mt-run")
            assert f"({len(want)})" in str(btn.label) and not btn.disabled, btn.label
            shot(app, "2.9-ticked")
            lst.focus()
            await pilot.press("c")
            r = await drive_run(pilot, app, "2.9-clean")
            assert r["status"] == 0, f"nog's status {r['status']}; its screen: {r['screen_tail']}"
            assert r["title"].startswith("Cleaning up"), r["title"]
            assert any("lean up" in q for q in r["questions"]), f"nog asked once: {r['questions']}"
            ok = await until(pilot, lambda: app.maint is not None and all(
                not next(c for c in app.maint["categories"] if c["id"] == cid)["items"] for cid in want), 120)
            after = {c["id"]: c["items"] for c in app.maint["categories"]}
            await pilot.pause(0.5)
            shot(app, "2.9-after")
            assert ok, f"those rows at nothing after the reload: {after}"
            return f"ticked {want} (before {before}); title {r['title']!r}; questions: {r['questions']}; after: {after}"
        await step("2.9 Space on old downloads + old snap revisions → c → nog asks once → Yes → rows at nothing", s29, kind="change")

        # ── 2.10 c from the Dashboard ────────────────────────────────────────
        async def s210():
            await pilot.press("1")
            await pilot.pause(0.4)
            app.query_one("#db-review-updates").focus()
            await pilot.press("c")
            await pilot.pause(0.6)
            cur = app.query_one("#forge-work").current
            assert cur == "sec-maintain", cur
            assert not isinstance(app.screen, RunWindow), "nothing runs"
            shot(app, "2.10-c-opens-maintenance")
            return "c on the Dashboard opens Maintenance; no run window"
        await step("2.10 c from the Dashboard opens Maintenance, runs nothing", s210)

        # ── 2.11 History → nog Logs → a run whole ────────────────────────────
        async def s211():
            await pilot.press("6")
            await pilot.pause(0.4)
            await pilot.press("l")
            ok = await until(pilot, lambda: app.query_one("#forge-work").current == "sec-noglogs", 10)
            assert ok, app.query_one("#forge-work").current
            lst = app.query_one("#nl-list")
            ok = await until(pilot, lambda: lst.option_count > 0, 30)
            assert ok, "nog Logs lists runs"
            first = lst.get_option_at_index(0).prompt
            first = first.plain if hasattr(first, "plain") else str(first)
            lst.focus()
            lst.highlighted = 0
            await pilot.pause(0.4)
            shot(app, "2.11-nog-logs")
            await pilot.press("enter")
            ok = await until(pilot, lambda: type(app.screen).__name__ not in ("Screen",) and app.screen is not app.screen_stack[0], 10)
            await pilot.pause(0.6)
            words = svg_text(app)
            shot(app, "2.11-a-run-whole")
            note = f"{lst.option_count} runs; newest: {first[:90]!r}; Enter opened {type(app.screen).__name__}"
            await pilot.press("escape")
            await pilot.pause(0.4)
            if changes:
                assert "clean" in first.lower(), f"the newest run is the clean-up (F-18: two runs in one minute): {first!r}"
                assert "Clean up" in words or "clean" in words.lower(), "the whole run on screen, nog's question among it"
                assert "its own log" in first, f"the caption says the run's own log is there (F-19): {first!r}"
                note += "; the clean run shows whole, nog's question in it; caption names its own log"
            return note
        await step("2.11 6 → l nog Logs → the newest run → Enter shows it whole", s211)

        # ── 2.12 the manual, and F1 on Maintenance ───────────────────────────
        async def s212():
            await pilot.press("7")
            await pilot.pause(0.4)
            await pilot.press("m")
            await pilot.pause(0.8)
            words = svg_text(app)
            shot(app, "2.12-manual")
            assert "Welcome to nogForge" in words, "the manual opens on Welcome"
            await pilot.press("escape")
            await pilot.pause(0.4)
            await pilot.press("5")
            await pilot.pause(0.4)
            await pilot.press("f1")
            await pilot.pause(0.8)
            words = svg_text(app)
            shot(app, "2.12-f1-on-maintenance")
            assert "left behind" in words and "Maintenance" in words, "F1 on Maintenance opens its manual page"
            await pilot.press("escape")
            await pilot.pause(0.4)
            assert app.query_one("#forge-work").current == "sec-maintain", "Esc goes back to the page"
            return "7 → m opens the manual at Welcome; F1 on Maintenance opens the Maintenance page; Esc back"
        await step("2.12 7 → m the manual; F1 on Maintenance → its page; Esc back", s212)

        # ── 2.13 Keys ────────────────────────────────────────────────────────
        async def s213():
            await pilot.press("1")
            await pilot.pause(0.3)
            await pilot.press("question_mark")
            await pilot.pause(0.8)
            words = svg_text(app)
            shot(app, "2.13-keys")
            # the page says "Ctrl+letter … D, I, N, U, M, S (History), H (Help)": M is Maintenance's letter
            for w_ in ("1-7", "Ctrl+letter", ", M,", "Maintenance", "on Maintenance: clean up", "on Maintenance: look again",
                       "on Maintenance: a category"):
                assert w_ in words, f"{w_!r} on the Keys page: {words[-900:]}"
            await pilot.press("escape")
            await pilot.pause(0.3)
            return "Keys page: 1-7, Ctrl+letter with M for Maintenance, c and k with their two meanings, Space on Maintenance"
        await step("2.13 ? Keys: 1-7, Ctrl+M, c and k, Space on Maintenance", s213)

        # ── 2.14 Update, a look ──────────────────────────────────────────────
        async def s214():
            await pilot.press("4")
            await pilot.pause(0.5)
            assert app.query_one("#forge-work").current == "sec-update"
            ok = await until(pilot, lambda: app.plan is not None, 120)
            await pilot.pause(0.5)
            summary = text(app, "#up-summary")
            shot(app, "2.14-update")
            plan = app.plan or {}
            return (f"plan: ready {len(plan.get('ready', []))}, held {len(plan.get('held', []))}; summary: "
                    f"{' '.join(summary.split())[:160]} (nothing in 1.5.0 changes Update; no update run tonight)")
        await step("2.14 4 Update: the page as before (sanity, no run)", s214)

    failed = [r for r in RESULTS if r[1] == "FAIL"]
    (OUT / "results.md").write_text(
        f"# nogForge {__version__} bench · {time.strftime('%Y-%m-%d %H:%M')} · {'with changes (VM)' if changes else 'read-only'}\n\n"
        "| step | result | notes |\n|---|---|---|\n" + "\n".join(f"| {s} | **{v}** | {n} |" for s, v, n in RESULTS)
        + f"\n\n{len([r for r in RESULTS if r[1] == 'PASS'])} PASS · {len(failed)} FAIL · "
          f"{len([r for r in RESULTS if r[1] == 'SKIP'])} SKIP\n")
    out(f"\n{len(RESULTS) - len(failed)} of {len(RESULTS)} steps did not fail; results in {OUT / 'results.md'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
