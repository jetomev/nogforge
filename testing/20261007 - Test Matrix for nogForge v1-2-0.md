# nogForge v1.2.0 — Test Matrix

*Javier's four from 2026-10-07 (#17 #18 #19 #20). Claude's automated checks, then Javier's run on the desktop after the AUR update. Results in the Test Results file of the same date.*

## 1 · Automated (Claude)

| # | Check | Expected |
|---|---|---|
| 1.1 | `python -W default -m unittest discover tests` | 41 pass (37 + 4), no warnings |
| 1.2 | Untick All (n) then Tick All (t) on the stand-in plan | every ready one kept back, "(0)" on the button; then nothing kept, all ticked |
| 1.3 | `/` on Update, type `tz` | only tzdata in Ready, Held empty; Esc returns to the list; a click on the row's Update runs `nog update tzdata` |
| 1.4 | In-System with nog's plan loaded | rows nog has a newer version for show Update beside Uninstall, the others not; the second button runs `nog update <name>` |
| 1.5 | A 30-row list scrolled down, then redrawn | highlight and scroll position unchanged (#17) |
| 1.6 | `makepkg` from the release tarball | sha256 + signature pass; `check()` runs the tests |

## 2 · The desktop (Javier)

| # | Do | Expected | Done |
|---|---|---|---|
| 2.1 | Install nogForge 1.2.0 (nogForge → Update, or `nog update nogforge`) | 1.2.0 in the title bar | |
| 2.2 | Update page: scroll down the long list, untick a row near the bottom | the list stays where it was; the row says "kept back by you" | |
| 2.3 | Untick All (n), then tick two | the button says "(2)"; the rest say kept back | |
| 2.4 | Tick All (t) | all ticked again | |
| 2.5 | `/`, type part of a name (e.g. `forge`) | both lists narrow as you type; Esc back to the list | |
| 2.6 | Click ⬆ Update on one ready row | nog runs for that one package only, asks, the password box; What changed shows just it | |
| 2.7 | In-System: find a package with an update pending | ⬆ Update beside ✕ Uninstall; Update runs nog for it alone | |
| 2.8 | In-System: a row without an update | ✕ Uninstall only; Locked rows still say why | |
