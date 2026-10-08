# nogForge v1.3.0 — Test Matrix

*Twenty minutes after 1.2.0, from Javier's first look at it (#21 #22): every search follows the typing, no Search button; one-row filter rows. Claude's automated checks, then Javier's run. Results in the Test Results file of the same date.*

## 1 · Automated (Claude)

| # | Check | Expected |
|---|---|---|
| 1.1 | `python -W default -m unittest discover tests` | 42 pass (41 + 1), no warnings |
| 1.2 | Install: type `krita` quickly | one nog search, not five; the keyboard stays in the box; Enter searches at once and moves the keys to the list |
| 1.3 | In-System: `/`, type three letters | the list narrows without Enter; no Search button exists |
| 1.4 | Positions at 100 columns | filter areas ≤ 4 rows (were 7); every drop-down 1 row; Update's bar at one row, nothing past column 100 |
| 1.5 | Console preview, In-System at 100×30 (`TERM=linux`) | one-row filters readable; every character in the console font; exit 0 |
| 1.6 | `makepkg` from the release tarball | sha256 + signature pass; `check()` runs the 42 tests |

## 2 · The desktop (Javier)

| # | Do | Expected | Done |
|---|---|---|---|
| 2.1 | `nog update nogforge --promote nogforge` | 1.3.0 in the title bar | |
| 2.2 | In-System: `/`, type part of a name | the list narrows as you type; filters take two short rows | |
| 2.3 | Install: type a word | nothing happens on the first letter; from the second, half a second after you stop, results appear; Enter searches at once | |
| 2.4 | Update: `/`, type; Tick All / Untick All; scroll and tick far down | as 1.2.0, on a one-row bar | |
| 2.5 | All three pages | the search boxes are one row tall ("cannot be thinner?" — answered) | |
