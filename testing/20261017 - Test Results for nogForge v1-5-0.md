# Test Results — nogForge v1.5.0 (the overnight bench, 2026-10-16 23:30 → 2026-10-17 00:30)

*The matrix is `20261015 - Test Matrix for nogForge v1-5-0.md`. Its §2 was written for Javier's hands; on 16 October at 23:30 he went to bed with "work without needing me, everything local, use the VM as needed", so a script walked it instead — `scripts/bench-150.py`: the real app, headless (Textual's Pilot), against the real nog 2.0.0, the same keys and buttons a person would press, an SVG of every step and a results table. Two places: this desktop, read-only (nothing installed, removed or cleaned), and the KognogOS VM `kognog-hypeforge` with real changes (reset by `scripts/vm-prep-150.sh` from snapshot `before-nogforge-150`). Javier reviews this file in the morning; the release waits for his look at the built package.*

## Roll-up

| Where | Steps | PASS | FAIL | SKIP | Evidence |
|---|---|---|---|---|---|
| §1 Claude — tests and the stand-in | 11 | 11 | 0 | 0 | the matrix's §1 table (rows 1.9–1.11 added tonight) |
| §2 this desktop, read-only (`python scripts/bench-150.py --out …`) | 14 | 11 | 0 | 3 (the three change steps) | `testing/bench-150/desktop/` (12 SVGs + results.md) |
| §2 the VM, run 1 (rc2, 23:54) | 14 | 6 | 8 | 0 | `testing/bench-150/vm-run1/` — 3 real findings (F-17, F-18, F-19), 5 cascades from the driver |
| §2 the VM, run 2 (rc3, 00:12) | 14 | 13 | 1 | 0 | `testing/bench-150/vm/` (27 SVGs) — the FAIL was the driver's own check |
| §2 the VM, 2.7 alone (rc3, 00:25) | 1 | 1 | 0 | 0 | `testing/bench-150/vm-2.7/` |

**Every step of §2 has passed where it can run: the 11 read-only ones on this desktop and all 14 in the VM.** Tests 61 → 67, 0 warnings. Three findings, all fixed the same night and in rc3.

## §2, step by step (the VM, run 2 unless said; the desktop's notes in the matrix are from the same script)

| # | Check | Result | What the script saw |
|---|---|---|---|
| 2.1 | `nog install …nogforge-1.5.0rc3-1-any.pkg.tar.zst` (as javier; `vm-prep-150.sh`) | **PASS** | pacman's "Proceed with installation? [Y/n]" answered y; `nogforge --version` → **nogForge 1.5.0**; the launcher entry installed and valid (pacman's MIME-cache hook ran) |
| 2.2 | the Dashboard | **PASS** | Maintenance in the menu bar; the bottom bar says **1-7 menu**; Yours has the Snap row (the VM has no Flatpak app; this desktop: Flatpak 23 and Snap 4 both there); Space: *Could go: 56.0 MB — old downloads 56.0 MB, orphans 27 KB, old snap revisions 20 KB* |
| 2.3 | In-System · Show: All | **PASS** | 1,173 rows; Snap rows core, hello-world, snapd; **core and snapd Locked** — *the system under the snaps*; the column says Snap. Desktop: 1,608 rows, 23 Flatpak rows (Flatseal, Termius, the eXoDOS set…), 4 snaps, core/core20/snapd Locked |
| 2.4 | p Repositories | **PASS** (run 1: **FAIL → F-17**) | listed core, extra, multilib, chaotic-aur, AUR, **Flatpak, Snap**; Snap unticked → its 3 rows gone; ticked back → 3 rows again. Desktop: Flatpak unticked → 23 rows gone and back. Run 1 had no Flatpak entry (no Flatpak app installed) → F-17 |
| 2.5 | Install "calculator" | **PASS** | 370 rows: extra 21, chaotic-aur 3, AUR 294, **Flatpak 12**, **Snap 40**; org.gnome.Calculator is a Flatpak row with **+ Install**, `install_as flatpak/org.gnome.Calculator` (5–10 s for nog's search in the VM) |
| 2.6 | Enter on org.gnome.Calculator → review → Install → nog's window | **PASS** | the review names `flatpak/org.gnome.Calculator` and says flatpak asks first; the window **starts folded with ▾ nog's Screen (F12)** (#23); flatpak's two questions — *Do you want to install it? [Y/n]* and *Proceed with these changes to the system installation? [Y/n]* — each came up as the **Yes (y) / No (n)** bar with the screen opened for the table; Yes to both; status 0; `flatpak list` has it; no password box (the VM's sudo doesn't ask) |
| 2.7 | In-System → ✕ Uninstall on the Flatpak → review → nog's window | **PASS** (2.7 alone; run 2's FAIL was the check reading a sentence that wraps on screen) | the row says ✕ Uninstall, `remove_as org.gnome.Calculator`; the review: *flatpak shows what goes and asks first*; title *Removing org.gnome.Calculator*; flatpak's question → Yes; status 0; `flatpak list` without it |
| #27 | Uninstall cliamp (yt-dlp is optional for the installed mpv) | **PASS** (both runs) | the review says nog first says what another app still uses, with a Keep; nog's window: *yt-dlp goes too, but mpv uses it (optional: for video-sharing websites playback)* and **`nog: Keep yt-dlp? [Y/n]`** as the Yes/No bar → Yes; nog marked yt-dlp installed on purpose; pacman's *Do you want to remove these packages? [Y/n]* → Yes; **cliamp gone, yt-dlp kept**, status 0 |
| 2.8 | Maintenance | **PASS** | five rows with sizes (cache 9 items 58.7 MB, orphans 1, build trees 0, unused runtimes 3 after the Flatpak install, old snap revisions 1); empty ones not tickable; **Clean Up the Ticked Ones (0) (c)** greyed; the summary says what could go; the highlighted row explained (*removed by nog; root is needed*). Desktop: 13 / 27 / 0 / 3 / 0, 1.3 GB |
| 2.9 | Space on old downloads + old snap revisions → c | **PASS** (both runs) | button *(2)*; title **Cleaning up: cache, snap**; nog's one question *Clean up cache, snap? [y/N]* → Yes; status 0; the page reloaded with cache 0 and snap 0, orphans and the runtimes untouched |
| 2.10 | c from the Dashboard | **PASS** | opens Maintenance; no run window |
| 2.11 | 6 → l nog Logs → Enter | **PASS** (run 1: **FAIL → F-18, F-19**) | 47 runs; the newest is *clean --only cache,snap* (F-18: it tied on the minute with *remove cliamp* and lost in run 1); its caption says *its own log, as it was on screen: Enter opens it* (F-19); Enter shows the run whole, nog's question in it. Desktop: 200 runs, Enter opens the log window |
| 2.12 | 7 → m the manual; F1 on Maintenance | **PASS** | the manual opens on Welcome; F1 on Maintenance opens the Maintenance page; Esc back to the page |
| 2.13 | ? Keys | **PASS** | 1-7; *Ctrl+letter … D, I, N, U, M, S (History), H (Help)*; c and k with their two meanings; Space on Maintenance |
| 2.14 | 4 Update | **PASS** | the page as before: 117 to update · 0 kept back · 128 held in the VM (14 / 246 here); no update run tonight |

## Findings

| # | Issue | What | Fixed |
|---|---|---|---|
| F-17 | [#29](https://github.com/jetomev/nogforge/issues/29) | the Repositories window listed Flatpak only once a Flatpak row existed (installed, or in Install's results); a computer with flatpak installed and no app yet had no Flatpak entry | a source nog's plan `checked` is listed, rows or no rows (`FilterBar.choose_repositories`); test `test_f17…` |
| F-18 | [#30](https://github.com/jetomev/nogforge/issues/30) | two runs in the same minute showed oldest first in nog Logs (minutes-only stamps; a stable sort kept nog's append order) | the line nog wrote last wins the tie (`records.runs`); test `test_f18…` |
| F-19 | [#31](https://github.com/jetomev/nogforge/issues/31) | every run's caption said *no other log for this run* while Enter opened the run's own log | the caption says what is there (its own log; N more logs; or nothing), the runs list read once per refresh; test `test_f19…` |

Also fixed on the way, no finding number: the fold-arrow label was cut short on the button until the button was re-measured (`refresh(layout=True)`), seen in the regenerated `08-run.svg`; the manual's History page still said "5, then a" (now 6).

**Driver faults, not the app's** (run 1): a step that failed left its window open and the next five failed on it (`settle()` before every step now); the pilot hung for six minutes at 2.5 with nothing running until a SIGINT woke it (a per-step `asyncio.wait_for` watchdog, the bench's own log file, `kill -USR1` dumps every thread's stack); Textual takes `sys.stdout` while the app runs, so a bench must write its own log; and in a run that starts at a later step the list was still being rebuilt under the keys (the bench waits for nog's first answers first and re-checks the picked row before Del).

**A note for nog** (not an issue tonight; nog has none open): `nog clean` run as the user printed *Leftover download folders 5 — size not readable* in its cache table (the download folders are root's). True, but the row could say why.

## What this does not prove

- Javier's own eyes on 1.5.0 on this desktop: the password box in a real run here (the VM's sudo doesn't ask; the box was proven in 1.1.0 and 1.4.0 and its code didn't change), the launcher entry in his menu, the arrow in a real terminal. That is the morning's install of the built package, before the AUR push.
- Snap install/uninstall through nogForge (no snap was installed in the bench; the review and `install_as snap/<name>` are covered by the tests).
- A text console run (tty) of 1.5.0 — no change to the console code; the matrix has no tty row for 1.5.0.
