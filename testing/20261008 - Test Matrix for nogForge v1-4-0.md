# nogForge v1.4.0 — Test Matrix

*From Javier's first run of nogForge inside hypeForge Settings (8 October 2026): Ctrl+U and Ctrl+Y did nothing (F-14, #24); 5 and 6 jumped into History's pages instead of opening History's menu, and "1-6 screens" was confusing (F-15, #25); Settings needs a way to start nogForge without its own Quit (#26). The menu's keys now come from forgekit 0.10.0. Claude's automated checks, then Javier's run. Results in the Test Results file of the same date.*

## 1 · Automated (Claude)

| # | Check | Expected |
|---|---|---|
| 1.1 | `python -W default -m unittest discover tests` (forgekit 0.10.0 from the repo) | 52 pass (42 + 10), no warnings |
| 1.2 | Ctrl+U with words in Install's and In-System's search box | Update opens (1.3.0 stayed on Install: the box took Ctrl+U as "delete what I typed") |
| 1.3 | Ctrl+Y, then 5 on the Dashboard, then 5 in the empty Search box | History's menu opens each time; the page doesn't change; nothing typed into the box |
| 1.4 | 6 | Help's menu opens |
| 1.5 | History ▸ nog Logs, History ▸ Activity | History lit in the menu bar for both |
| 1.6 | The bottom bar on the Dashboard | `1-6 menu` (not `1-6 screens`) |
| 1.7 | Every underlined letter in the menu bar | each one different; no nogForge Ctrl key on any of them |
| 1.8 | Started with `hypeforge=True` | no Quit in the bar; q, Ctrl+Q and Quit do nothing; 6 is still Help |
| 1.9 | `nogforge --hypeforge`, `nogforge --hypeForge` | the app gets the option; `--help` and the man page don't mention it; `--hype` is refused |
| 1.10 | Settings asks nogForge to close, and Ctrl+Q, while nog's run window is open | "Not yet"; nogForge stays; once nog's window is closed, Settings' request closes it |
| 1.11 | Each check above with the fix taken out | the test fails (proved once for each) |
| 1.12 | `makepkg` from the release tarball | sha256 + signature pass; `check()` runs the 52 tests |

## 2 · Inside hypeForge Settings (Javier)

| # | Do | Expected | Done |
|---|---|---|---|
| 2.1 | Install the locally built forgekit 0.10.0 and nogForge 1.4.0 (Claude gives the command) | 1.4.0 in nogForge's title bar | |
| 2.2 | Open Settings ▸ nogForge | nogForge's menu bar has **no Quit** | |
| 2.3 | Press **q**, then **Ctrl+Q** | nothing happens; nogForge stays | |
| 2.4 | **Ctrl+D**, **Ctrl+I**, **Ctrl+N**, **Ctrl+U** | Dashboard, In-System, Install, Update | |
| 2.5 | On Install, type a word in the search box, then **Ctrl+U** | Update opens (this was F-14) | |
| 2.6 | **Ctrl+Y** | History's menu opens; **a** = Activity, **l** = nog Logs; History is lit on both | |
| 2.7 | **Ctrl+H** | Help's menu opens | |
| 2.8 | **1**, **2**, **3**, **4** | Dashboard, In-System, Install, Update | |
| 2.9 | **5** | History's menu opens (it used to jump to Activity: F-15) | |
| 2.10 | **6** | Help's menu opens | |
| 2.11 | On Install, with the search box empty, press **5** | History's menu opens; nothing typed into the box | |
| 2.12 | The bottom bar on the Dashboard | says **1-6 menu** | |
| 2.13 | **?** (all keys) | lists 1-6 and Ctrl + letter; the Quit line says it isn't there inside Settings | |
| 2.14 | Close nogForge from Settings | it closes | |

## 3 · On its own, in a terminal (Javier)

| # | Do | Expected | Done |
|---|---|---|---|
| 3.1 | `nogforge` | **Quit** is in the menu bar | |
| 3.2 | Every Ctrl letter and number, as 2.4–2.11 | the same as inside Settings | |
| 3.3 | `nogforge --help` | no word about hypeForge; "1-6 or Ctrl + the underlined letter" | |
| 3.4 | Smoke: In-System and Install searches follow the typing; Update ▸ Review: untick one, Update the Ticked Ones | as 1.3.0 | |
| 3.5 | During an update (nog's window open), press **Ctrl+Q** | "Not yet": nogForge stays until nog is done | |
| 3.6 | **q** after nog is done | nogForge closes, with its closing note | |
