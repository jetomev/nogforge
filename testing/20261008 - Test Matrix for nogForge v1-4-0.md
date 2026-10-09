# nogForge v1.4.0 — Test Matrix

*From Javier's first run of nogForge inside hypeForge Settings (8 October 2026): Ctrl+U and Ctrl+Y did nothing (F-14, #24); 5 and 6 jumped into History's pages instead of opening History's menu, and "1-6 screens" was confusing (F-15, #25); Settings needs a way to start nogForge without its own Quit (#26). The menu's keys now come from forgekit 0.10.0. **Round 2**, from Javier's second run the same day: History didn't close when its number was pressed again, and wasn't lit while open; his letter rule (first letter of the name, else the next free one; Help H, Quit Q) makes History **Ctrl+S**; License and About become pages. **Round 3**: the manual and Keys become pages too. Claude's automated checks, then Javier's run. Results in the Test Results file of the same date.*

## 1 · Automated (Claude)

| # | Check | Expected |
|---|---|---|
| 1.1 | `python -W default -m unittest discover tests` (forgekit 0.10.0 from the repo, `d7b7ba3`) | 56 pass (42 + 14), no warnings |
| 1.2 | Ctrl+U with words in Install's and In-System's search box | Update opens (1.3.0 stayed on Install: the box took Ctrl+U as "delete what I typed") |
| 1.3 | Ctrl+S, then 5 on the Dashboard, then 5 in the empty Search box | History's menu opens each time; the page doesn't change; nothing typed into the box |
| 1.4 | 6 | Help's menu opens |
| 1.5 | History ▸ nog Logs, History ▸ Activity | History lit in the menu bar for both |
| 1.6 | The bottom bar on the Dashboard | `1-6 menu` (not `1-6 screens`) |
| 1.7 | Every underlined letter in the menu bar, on the real app | D, I, N, U, S, H, Q by Javier's rule; nogForge sets none itself; no nogForge Ctrl key on any of them |
| 1.7b | 5, then 5 again; 5 then 6 | the second 5 closes History's menu; 6 swaps to Help's; History lit only while its menu is open |
| 1.7c | Help ▸ About, Help ▸ License, from Update and from nog Logs | a page in the main area (no window), Help lit; Esc goes back to Update / nog Logs, with History lit again for nog Logs |
| 1.7d | F1 on Update and on nog Logs; Help ▸ Manual; `?` | the manual as a page at Update's / History's page, Keys as a page, Help lit; Esc back to the page you were on; on these pages c, u, k, r, h, t, n, p, / do nothing |
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
| 2.6 | **Ctrl+S** (History's underlined letter is now S) | History's menu opens; **a** = Activity, **l** = nog Logs; History is lit on both | |
| 2.6b | Menu bar letters | underlined: **D**ashboard, **I**n-System, I**n**stall, **U**pdate, Hi**s**tory, **H**elp | |
| 2.7 | **Ctrl+H** | Help's menu opens | |
| 2.8 | **1**, **2**, **3**, **4** | Dashboard, In-System, Install, Update | |
| 2.9 | **5** | History's menu opens (it used to jump to Activity: F-15); the word History is lit while it's open | |
| 2.9b | **5** again | History's menu closes (round 2); History no longer lit | |
| 2.9c | Click **History** in the menu bar, then **Ctrl+S** | lit while open each time; Ctrl+S again closes it | |
| 2.10 | **6** | Help's menu opens | |
| 2.11 | On Install, with the search box empty, press **5** | History's menu opens; nothing typed into the box | |
| 2.12 | The bottom bar on the Dashboard | says **1-6 menu** | |
| 2.12b | **6**, then **a** (About); Esc. **6**, then **l** (License); Esc | each shows in the main area, not a window, with Help lit; Esc goes back to the page you were on | |
| 2.12c | On Update press **F1**; then Esc. Press **?**; then Esc | the manual opens as a page in the main area at the Update page, Help lit; Keys likewise; Esc goes back to Update each time | |
| 2.12d | In the manual press **c** | nothing happens (no clean-up starts) | |
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
