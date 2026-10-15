# Test Matrix — nogForge v1.5.0 (every source, and Maintenance; on nog 2.0.0)

*Built the night of 2026-10-14 → 15 with nog 2.0.0. §1 is Claude's and done; §2 is Javier's, step by step, on this desktop, after nog's own bench (nog 2.0.0rc1 installed first). Package: `dist-rc/nogforge-1.5.0rc1-1-any.pkg.tar.zst` (built from the AUR recipe, 61 tests inside).*

## §1 · Claude — tests and the stand-in nog

| # | Check | Expected | Result | Notes |
|---|---|---|---|---|
| 1.1 | `python -W default -m unittest discover tests` | green, no warnings | **PASS** | 61 passed (56 at 1.4.0), 0 warnings |
| 1.2 | The rows carry nog's names | `remove_as` on an installed Flatpak (its app ID) and a package (its own name); `install_as` on a Flatpak and a snap result, empty on a package; a base snap `protected` | **PASS** | `EverySource.test_the_rows_carry_nogs_names` |
| 1.3 | The Dashboard counts Flatpaks and snaps from nog's list | Yours total 6 (4 chosen + Flatseal + hello; core20 came along), a Flatpak row; Space says "Could go" with the categories | **PASS** | from nog's rows, not this computer's counters; an older nog still uses the counters (`test_dashboard_tables`) |
| 1.4 | Install a Flatpak result, uninstall an installed Flatpak, a base snap | review → `nog install flatpak/org.gnome.Calculator`; review → `nog remove com.github.tchx84.Flatseal`; Del on core20 → no review (Locked) | **PASS** | found and fixed on the way: Install's hidden list took the keyboard after a change |
| 1.5 | Maintenance cleans up only the ticked categories | page 5: 5 rows, the empty one not tickable, Clean Up disabled with nothing ticked, `c` runs nothing; tick two → `nog clean --only <exactly those>` | **PASS** | |
| 1.6 | The menu renumbered | 1–7 in the bar, 5 Maintenance (Ctrl+M), 6 History's menu, 7 Help's; every letter its own; `c` opens Maintenance from Update and runs nothing unticked; the manual, Keys, License, About still pages; F1 on Maintenance opens its page | **PASS** | MenuKeys (11 tests), Choices, CommandLineAndNames |
| 1.7 | rc1 package | built from the AUR recipe with a terminal attached; 61 tests in `check()` | **PASS** | `dist-rc/nogforge-1.5.0rc1-1-any.pkg.tar.zst` |
| 1.8 | `man --warnings -l nogforge.1` | no warnings | **PASS** | |

## §2 · Javier, this desktop — step by step (after nog's bench; nog 2.0.0rc1 installed)

| # | Check | Expected | Result | Notes |
|---|---|---|---|---|
| 2.1 | `nog install ~/Programs/nogforge/dist-rc/nogforge-1.5.0rc1-1-any.pkg.tar.zst` | the package-file install; `nogforge --version` says **1.5.0** | | |
| 2.2 | `nogforge` → the Dashboard | the menu bar has **Maintenance** after Update; the bottom bar says **1-7 menu**; **Yours** has Flatpak 2 and Snap rows; **Space** says "Could go: ~10 GB — old downloads 4.6 GB, orphans 918 MB, …" | | the numbers are this desktop's, from nog's report |
| 2.3 | **2** In-System → Show: All → scroll to the end | `com.github.tchx84.Flatseal` and `com.termius.Termius` rows (Repository **Flatpak**), `hello` (**Snap**), `core`, `core20`, `snapd` **Locked** — "the system under the snaps" | | |
| 2.4 | **p** Repositories on In-System | the window lists Flatpak and Snap after the AUR; untick Flatpak → the Flatpak rows go; tick it back | | |
| 2.5 | **3** Install → type `calculator` → Enter | rows from the repositories, the AUR, **Flatpak** (org.gnome.Calculator and more, with their app IDs) and **Snap**; **+ Install** on each | | nog 2.0.0's search |
| 2.6 | **Enter** on org.gnome.Calculator → the review | "a Flatpak app (flatpak/org.gnome.Calculator): flatpak shows what comes with it … and asks first"; **Install (i)** → nog's window: the table (Flatpak — flathub), flatpak's question → **y**, installed; **Close** | | the password box for flatpak's system install |
| 2.7 | **2** In-System → find `calculator` → **✕ Uninstall** → the review | "flatpak shows what goes and asks first"; **Uninstall (r)** → nog's window: `nog remove org.gnome.Calculator`, flatpak's question → **y**, gone | | what nog installs, nog removes |
| 2.8 | **5** Maintenance | the report: five rows with sizes (old downloads, orphans, build trees, unused runtimes, old snap revisions); the highlighted one explained underneath; **Clean Up the Ticked Ones (0) (c)** greyed | | |
| 2.9 | **Space** on *old downloads* and on *old snap revisions* → **c** | the review-free hand-off (the page is the review): nog's window, "Clean up cache, snap? [y/N]" → **y**; the password box; "Cleaned"; **Close**; the page reloads with those two rows at "nothing" | | Javier's call which rows; orphans would ask pacman's list |
| 2.10 | **c** from the Dashboard | opens Maintenance (nothing runs) | | |
| 2.11 | **6** → **l** nog Logs → the clean run → **Enter** | the whole run as it was on screen, nog's question and your answer among it | | History is 6 now |
| 2.12 | **7** → **m** the manual → Maintenance page; **F1** on Maintenance | the Maintenance page of the manual; Esc back | | |
| 2.13 | **?** Keys | 1-7, Ctrl+M, c and k with their two meanings, Space on Maintenance | | |
| 2.14 | **4** Update → **Enter**/**Update** on a ready row (if any) | as before (1.4.0): nothing in this release changes Update | | sanity |

## Findings

*(none yet — Javier's run adds them here as F-17, F-18, …)*
