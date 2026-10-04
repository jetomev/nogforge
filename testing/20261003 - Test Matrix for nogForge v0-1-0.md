# nogForge v0.1.0 (beta) — Test Matrix

Design: `docs/design/v0.1-screens.html` (approved by Javier, 3 Oct 2026). nogForge 0.1 needs **nog 1.6.0** (`--json`, `--keep`, the password window), so nog's test version comes first. Each result is read from the run itself, not assumed.

## 1–4 · Built and checked by Claude (3 Oct 2026, 09:00–10:00)

| ID | Area | Proven by | Result |
|---|---|---|---|
| 1 | **nog 1.6.0-rc.1**: `nog list --json` (1,518 packages, 254 chosen, protections in words: linux-zen "the system needs this to start", glibc/bash "part of the base system"), `nog search --json` (repositories + AUR), `nog update --json` (10 ready, 76 held, every source checked, no question asked, nothing installed), no banner and no run-history line in JSON mode | this desktop, read-only | **PASS** |
| 2 | **Keep back**: `nog update --json --keep ldb,breezy` holds libwbclient and smbclient with ldb (same Samba build), through nog's own coupling rules | this desktop, read-only | **PASS** |
| 3 | nog's tests: 229 → 235 (6 new: the JSON readers, protection words, search, the password switch, the kept-back wording), warnings 6 → 6; inside the test package build too | `cargo test`, `scripts/make-rc-package.sh` | **PASS** |
| 4 | nogForge: 21 tests (stand-in nog, nothing installed): the three answers, a missing or too-old nog said in plain words, the password window chosen only on a desktop, catalogue (English names, cache), badges, History, the cache, Show/Type/Find, **a Locked package never reaches nog** (also checked against a deliberately broken lock: the test fails), remove and install reviewed then handed to nog, Update shows nog's plan, nothing cut off at 100 columns, every screen on a text console, the closing note | `tests/test_nogforge.py` | **PASS** |
| 4b | **KognogOS** (test VM `kognog-hypeforge`, snapshot `before-nog-1.6.0rc1` made first): nog 1.6.0rc1 installed; `list --json` 1,145 packages / 245 chosen, `search --json`, `update --json` 4 ready / 14 held with AUR, Flatpak, Snap reported "not installed" (not 0); then a **real** `nog install cowsay` and `nog remove cowsay` with `NOG_ASKPASS=1`: both done, both in nog's run log. (The ready updates went in first, as nog does before an install, #30.) Not provable there: the password window itself (the VM runs as root, so sudo asks nothing) — that's 6.6. A first try that piped all the answers at once stopped at pacman's question; the same happened without the change, so it was the test's input, not nog: run in a real terminal (`script`), both worked | VM, guest agent | **PASS** |
| 4c | **The hand-off in a real terminal** (pty, a stand-in nog that only prints): Search → Enter on Krita → review → Install: nogForge gave the terminal to nog (`install krita`), came back, "nog finished — Installed: krita". Found: the results weren't read again afterwards (Krita still said Install); fixed and tested | forgekit `console-preview.py`, test | **PASS** |
| 4d | **Update with choices and Tiers** (built after 0.1, same morning): untick → "kept back by you", and nog's coupling unticks what must stay with it ("must stay back with ldb"); ticking a forced one re-ticks its partner; Update sends only what you unticked (`nog update --keep ldb`); What changed compares versions before and after; a new kernel offers Restart Now (r) in red, Later (l) selected; Promote → review → `nog unlock … --promote`; Tiers soonest first, filter by tier, change tier (`nog pin … --tier N`) or promote. A stand-in nog that remembers what it "installed". The two coupling tests fail when nog's answer is ignored (checked). On the real nog test build: unticking ldb kept libwbclient and smbclient back | `tests/test_nogforge.py` (`Choices`, Tiers) | **PASS** |
| 5 | Text console (100×30), all six screens (and the README pictures: Update's versions and nog's notes no longer cut; headings and rows line up at any width): console font only, nothing invisible. **Found and fixed:** nogForge crashed on a console (Rich can't read the console's colour names); the shaded rows hid the selected row there | forgekit `console-preview.py`, `test_every_screen_on_a_text_console` | **PASS** |

## 6 · Javier's run (this desktop)

| ID | Do | Expect | Result |
|---|---|---|---|
| 6.1 | `nog install ~/Programs/nog/dist-rc/nog-1.6.0rc1-1-x86_64.pkg.tar.zst` | nog upgrades itself to 1.6.0rc1; `nog --version` says 1.6.0-rc.1 | |
| 6.2 | `python3 ~/Programs/nogforge/main.py` | Dashboard: Updates (after up to a minute) and Yours tables by source and tier, Recent, Space; title bar says nog 1.6.0-rc.1 | |
| 6.3 | **2** Home | your 254 by default ("Yours (254)"), badges, versions, tiers, Remove or Locked with the reason underneath; try Show (All, From the AUR), Type, Find | |
| 6.4 | On a Locked row (linux-zen), press **Del** | a note says why; nothing else happens | |
| 6.5 | **3** Search: type a word, **Enter** | results from the repositories and the AUR; the cursor moves to them; Type and Include AUR narrow them | |
| 6.6 | Install something small you want (or a harmless one, e.g. `cowsay`), **Enter** on its row | a review; **Install (i)**; the terminal shows nog and pacman's list; **the KDE password window asks**; Enter brings you back; the row now says ✓ Yours | |
| 6.7 | **2** Home, Find it, **Del** | a review; **Remove (r)**; nog and pacman remove it (and what only it needed); back in nogForge it's gone | |
| 6.8 | **4** Update | nog's plan: Ready now (ticked) and Held with Ready on dates and nog's notes | |
| 6.8b | On Update, **Space** on a ready row (e.g. ldb if it's there) | "kept back by you"; any partners untick themselves with "must stay back with …"; the button's count drops. Space again ticks it back | |
| 6.8c | **u** (only if you want to update now) | nog in the terminal with `--keep`; afterwards **What changed**: what went in, what you kept back; Restart Now (r) / Later (l) only after a kernel | |
| 6.8d | **5** Tiers: Show ▸ Tier 1; Enter on a row | the window: Tier 1/2/3 and Promote Now; Esc closes without changing anything | |
| 6.9 | **6** History | the install and removal from 6.6–6.7 at the top | |
| 6.10 | **q** | the terminal shows the banner and "2 changes made", the log line, the thank-you | |
| 6.11 *(optional)* | Ctrl+Alt+F3, log in, `python3 ~/Programs/nogforge/main.py` | everything readable; letters for badges; no password window there, so nog asks in the terminal | |

Tell Claude "done": nog's logs and nogForge's run log are read from the machine, and the results go in `testing/20261003 - Test Results for nogForge v0-1-0.md`.


## 7 · Javier's first run (3 Oct, 12:15–12:40) — what came back

Read from the machine: nog 1.6.0rc1 installed with nog (12:15); `nog unlock archiso --promote` from nogForge (12:17, archiso 90 → 91, done). Javier: *"Dashboard: looks amazing! … This is a work of art my friend."*

| Finding | Fixed in | Check |
|---|---|---|
| **F-1** closing after a promote crashed (the closing note had no words for "promote") | `cli.summary`: words for every change, never a crash | test: every kind of change |
| **F-2** Search "calc" listed perl first (pacman matches what a package *provides*), marked "Yours" though it's only a dependency | Install keeps only results with the words in the name or description, ranked (exact name, starts with, contains, description; repositories before the AUR); "✓ Installed" for dependencies | test: ranking; real "calc" |
| **F-3** the shaded rows and the selected row were the same colour | shade = a step lighter than the background; selection lighter again; the button lighter still on the selected row | pictures |
| **F-4** a ticked update couldn't be unticked | Space and a click on the box both tick and untick | test: click on the box |
| **F-5** Promote installed at once while ready updates waited | nog 1.6.0-rc.2 `--promote`: the package becomes ready (ticked, "promoted by you"), partners follow ("promoted with …"), it installs with the rest | tests; real: linux-zen brings its headers |
| **F-6** (found while fixing) opening Install put the cursor in Search and the next screen key was typed into it | while Search is empty, 1–6 switch screens | console test |
| **F-7** (found by a new test) a click on a row's name opened the install/remove review | a click on a row only selects it; only the button acts | test: row click vs button click |

**Changes asked for:** Home → **In-System**; Search → **Install**; one filter bar on both (**Search** box + **🔍 Search (Enter)** button, Show, Type, **Tier**, **Repositories (p)** with every repository in pacman.conf and the AUR); a **Repository** column; names and versions cut with "…"; the options as **buttons** (grey, blue under the mouse); **Tiers removed** ("isn't actually needed"); **History ▾ Activity / nog Logs**, with a run's full log in a window.

## 8 · Javier's second run

| ID | Do | Expect | Result |
|---|---|---|---|
| 8.1 | `nog install ~/Programs/nog/dist-rc/nog-1.6.0rc3-1-x86_64.pkg.tar.zst` | only nog installs, nothing else (nog F-8, #41); `nog --version` says 1.6.0-rc.3 | rc.2 went in 3 Oct 21:16, but nog updated 20 packages first: that was F-8 |
| 8.2 | `python3 ~/Programs/nogforge/main.py`; **2** In-System | the filter bar; Show Yours (254); Type; Tier; Repositories (p) opens a window with core, extra, multilib, chaotic-aur, AUR; the Repository column; Remove buttons grey, blue under the mouse; the selected row clearly different from the shaded ones | |
| 8.3 | **3** Install: type `calc`, click **🔍 Search** | calc near the top, no perl; Yours/Installed on what you have; Type, Tier, Repositories narrow it | |
| 8.4 | **4** Update: click a ticked box, or Space | it unticks ("kept back by you"); partners untick with the reason; again to tick | |
| 8.5 | On Held, **↑ Promote** | it moves to Ready, ticked, "promoted by you"; nothing installs yet | |
| 8.6 *(optional)* | **u** | nog in the terminal with what you kept back and promoted; What changed afterwards | |
| 8.7 | **History ▸ Activity** and **History ▸ nog Logs**; Enter on the grubforge line | the tables; the window with every package of that run | |
| 8.8 | **q** | the closing note, no crash | |
