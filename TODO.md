# nogForge — the list

*The live work list and the handoff between sessions. Newest work first. Updated after every step.*

**Status (8 Oct 2026): 1.4.0 released 2026-10-08 (GitHub + AUR; Javier on the installed package: "all perfect!")


- [ ] **#27 (2026-10-08, Javier):** Uninstall shows what goes along and starts anything another app still uses on **Keep** — after nog #49 (warning + `nog keep`)
## v1.4.0 — the menu's keys from forgekit 0.10.0; History opens its menu; --hypeforge · 2026-10-08 (#24 #25 #26)
*From Javier's first run inside hypeForge Settings. **released 2026-10-08 (GitHub + AUR; Javier on the installed package: "all perfect!")** (forgekit 0.10.0 must be on the AUR first).*
- [x] **#24 F-14** Ctrl+U and Ctrl+Y did nothing (History's key is **Ctrl+S** now, by Javier's letter rule, round 2). Cause, confirmed in a test: Ctrl+U was nogForge's own key without priority, and the search box (Textual's Input) takes Ctrl+U as "delete what I typed", so with the cursor in a search box (Install puts it there) it never reached the app; Ctrl+Y was never bound. Now forgekit 0.10.0 binds Ctrl + every underlined letter with priority; nogForge's own number and Ctrl bindings are gone
- [x] **#25 F-15** numbers in bar order: 1 Dashboard, 2 In-System, 3 Install, 4 Update, **5 History (its menu)**, **6 Help (its menu)**; the empty Search box passes a number to the same entry; Activity/nog Logs bars say `5 l` / `5 a`; the bottom bar says **1-6 menu**; `h` still opens Activity
- [x] **#26** `--hypeforge` / `--hypeForge` (forgekit's `add_hypeforge_argument`): no Quit, q / Ctrl+Q do nothing, Settings closes it; not in `--help` or the man page; documented in README, manual (Welcome, Keys), CLAUDE.md, changelog
- [x] Also: **never closed while nog is working** (`before_quit` while the run window is open): in 1.3.0 Ctrl+Q during an update closed nogForge and nog with it (checked); Settings' close request now waits too
- [x] Button labels checked ("Words (k)"): nothing to change
- [x] **Round 3** (Javier: "yes, Keys and Manual as pages too"; forgekit `d7b7ba3`): the manual opens with `show_manual` (a page, F1 at the right page, Esc back, Help lit), Keys a page via forgekit; nogForge's letter keys do nothing on these reading pages (`check_action`), so c can't start a clean-up there. Tests 54 → **56**, 0 warnings; matrix rows 1.7d, 2.12c/d
- [x] **Round 2** (Javier's second run, 10-08 evening; forgekit `d3e8e90`): Javier's letter rule (first letter, else the next free one; Help H, Quit Q; an app's `acc` ignored) → History **Ctrl+S**, Install N, all `acc` removed; History closes on its number pressed again and is lit while open; License and About are pages (Help lit, Esc back). Tests 52 → **54**, 0 warnings; docs, manual, man page, matrix rows 1.7b/1.7c, 2.6b, 2.9b/c, 2.12b
- [x] Tests 42 → 52 (round 2: **54**), warnings 0 → 0; every new test seen failing with its fix taken out; screenshots regenerated (bottom bar `1-6 menu`, title 1.4.0)
- [x] Version 1.4.0 everywhere (code, README, man page, changelog; 1.2.0 moved to docs/CHANGELOG.md); forgekit ≥ 0.10.0 in README + man page
- [ ] **Javier's run**: `testing/20261008 - Test Matrix for nogForge v1-4-0.md` §2 (inside Settings) and §3 (on its own)
- [ ] Release after his pass: push + signed tag, GitHub Release, AUR recipe (`depends` python-forgekit>=0.10.0), local makepkg, Javier installs, then AUR push; close #24 #25 #26

## Later — the run window (Javier, 2026-10-07 22:55, #23)
- [ ] **#23** a nog run as a **progress bar** with the terminal **folded behind an arrow** (▲ closed / ▼ open); nog's yes/no and AUR questions as nogForge pop-ups — shape 1 needs nog to emit its questions as events (a nog issue when we take it); shape 2 (just the fold) is cheap. Javier: "another day"

## v1.3.0 — searches follow the typing; one-row filters · 2026-10-07 night (#21 #22)
- [x] **#21** every search filters as you type: `FilterBar` posts `Searched` on `Input.Changed` — In-System at once, Install after `LIVE_WAIT` 0.5 s and from `LIVE_MIN` 2 characters (a timer reset per keystroke); the Search button removed; an emptied Install box clears the results
- [x] **#22** one-row filter rows: `SearchInput`, labels, `Select` (`SelectCurrent` without its border, also on a console) and the inline buttons at height 1; the filter area 7 → 4 rows
- [x] Tests 41 → **42** (the old search test types instead of clicking; new: In-System narrows without Enter, one nog search for five quick keystrokes, every drop-down one row, filter areas ≤ 4 rows); console preview of In-System clean
- [x] **Released 1.3.0 — 2026-10-07 22:32**: tag `v1.3.0`, GitHub Release (Latest, signed assets, download byte-identical), AUR `nogforge` 1.3.0-1 (makepkg: 42 tests in check()). Javier: `nog update nogforge --promote nogforge` → **section 2 PASSED 22:55 ("pass"); #17–#22 closed**

## v1.2.0 — Javier's four · 2026-10-07 night (#17 #18 #19 #20)
- [x] **#17** the list keeps its scroll and highlight on a redraw (`PackageList._redraw` restores `scroll_offset.y` after the rows are rebuilt)
- [x] **#18** Tick All (t) / Untick All (n) above the Update lists; `app.tick_all` / `untick_all` go through nog's plan like a tick does
- [x] **#20** a Find box on Update (`/` goes there; both lists follow as you type) and **⬆ Update** on every ready row → `app.update_one(name)`: nog gets the one name (plus `--promote` for a held one)
- [x] **#19** In-System: **✕ Uninstall** (not Remove) everywhere a person reads it; **⬆ Update** beside it when nog's plan has a newer version (`Row.option2`, two buttons per row, each with its own hover and click). **Downgrade: not yet — nog has no downgrade; a nog feature first**
- [x] Tests 37 → **41** (untick all / tick all; find + update one; In-System's Update button; the scroll survives a redraw); README, manual (03, 05, 08, 01), changelog; version 1.2.0
- [x] Released 1.2.0 — 22:10 (tag, Release, AUR 1.2.0-1); Javier's first look → #21 #22 → 1.3.0 twenty minutes later

## Backlog from Javier's use · 2026-10-07 (the sudoForge 1.0.1 update, through nogForge)
- [ ] **#17 · Update page:** unticking a package with the mouse scrolls the list back to the top — with 52 updates every tick means scrolling down again. Fix: change only the row, or restore the scroll position and the highlighted row after the redraw
- [ ] **#18 · Update page:** "Tick all" / "Untick all" buttons at the top left of the list (Javier's words: Select All / Deselect All; wording his call), acting on the filtered list; keys in the hint bar and Help
- [ ] **#19 · In-System page:** per-row buttons on the right — **Update** (only when newer), **Downgrade** (only when an older version is at hand; needs a design pass + nog's say), **Uninstall** (the word is Uninstall, not Remove; asks first with nog's removal preview)
- [ ] **#20 · Update page:** update **one** package by itself — a filter box above the list + a per-row "Update this one" button (Javier, 10-07 21:50: "too hard to get one package updated by itself"; he used `nog` in a terminal instead). **Javier: these four come before the next hypeForge steps**
- Context: the update itself went fine (sudoforge 1.0.0 → 1.0.1, built by yay, password in nogForge's own box). The wobbly box borders in Javier's screenshots were Claude Desktop's terminal font, not nogForge

## v1.1.1 — the AUR build works from a terminal · F-13 #15
- [x] Javier's AUR install of 1.1.0 failed in check(): a test's stand-in decided "in the run window" by `isatty(0)`; yay builds in a terminal. Fixed (NOG_EVENTS; stdin=DEVNULL); make-rc-packages.sh now builds under `script` (with a terminal, like yay)
- [x] Released 1.1.1: tag, GitHub Latest, AUR `7da3a19` (built under a terminal before the push: 37 tests)
- [x] Javier installed it from the AUR (15:24, nogforge 1.1.1-1) → #15 closed

## Done · v1.1.0 — nog runs inside nogForge · released 2026-10-04 (#14)
- [x] Research (`docs/research/2026-10-04-nog-inside-the-ui.md`); Javier chose 1 (terminal pane + password in the app), 2 (steps view), 3 (grubForge's polkit box)
- [x] Built on forgekit 0.6.0 (RunWindow, PasswordBridge) and nog 1.7.0 (NOG_EVENTS, `repo/name`); installs name the row's source; 37 tests
- [x] KognogOS VM, real text console: install (repo + AUR via yay), update with steps, cancelled password, remove — all PASS (matrix `testing/20261004 - Test Matrix for nogForge v1-1-0.md` §1)
- [x] **Javier's desktop test** (§2): all PASS ("wow! better than expected!", "works wonders")
- [x] Released in order: forgekit 0.6.0 → nog 1.7.0 → grubForge 2.1.0 → nogForge 1.1.0 (docs, man pages, CHANGELOGs, tags, GitHub, AUR in that order); kognogos.org; close #14, forgekit#6, nog#45, grubforge#36
- [ ] Decide: nogForge on the KognogOS disc? (it isn't in `iso/packages.x86_64`)

## Decided (Javier, 3 Oct 2026)

- **What it is:** nog's wrapper *and* Pamac's functions in a TUI. Screens: **Dashboard** ("sexy"), **Home** (installed apps: the 254 you chose by default, all 1,518 on a switch; name, version, description, tier, a category badge from `archlinux-appstream-data` since Alacritty can't draw icons; uninstall on the left), **Search** (types from AppStream: Office, Games, Internet…; same list, install on the left), **Update** (visual: Repositories, Ready with checkboxes guarded by nog's coupling — untick one, nog says what must stay back with it —, Held with Promote, Unknown, review, nog's real run, "What changed"), **Tiers** (All/1/2/3 dropdown, sorted by next update date, change tier = nog pin, Promote = nog unlock), **Settings** (nog holds/safety days/sources; pacman.conf safe options; **add/remove repositories**: signatures required by default, key fingerprint shown before trusting, core/extra never removable; clean cache), **History** (nog's log), Help, Quit.
- **System packages are protected:** no uninstall on Tier 1, the `base` set, or anything another package needs ("needed by Firefox and 3 more"); the reason shown instead. No override in the app.
- **Password like grubForge:** the system's own password window; nogForge never sees it. nog runs as the user (AUR builds refuse root) and asks through the window when nogForge calls it — needs nog 1.6.0. Text console: the terminal prompt.
- **nog 1.6.0 comes first:** `--json` output, the "keep these back" choice, the password window. Part of nog#7.
- **Flatpak and Snap** installs come later (nog#7; nog already *updates* both with holds). **nogForge stays beta (0.x) until everything is there, Flatpak and Snap included.** Beta phases, each tested by Javier: 0.1 Home/Search/install-remove · 0.2 Update · 0.3 Tiers · 0.4 Settings.

## 0.1 beta — built 3 Oct (09:00–09:45), waiting on Javier's run

- [x] nog 1.6.0-rc.1 (in nog's repo): `list/search/update --json`, `--keep`, `NOG_ASKPASS` → `sudo -A` + helper `--sudoflags -A`; test package `~/Programs/nog/dist-rc/nog-1.6.0rc1-1-x86_64.pkg.tar.zst`.
- [x] nogForge 0.1: Dashboard (Updates + Yours tables, Recent, Space), Home (Yours/All/AUR, Type, Find, Locked rows), Search (repos + AUR), Update (nog's plan, read-only; "Update the Ready Ones" hands off), History (nog's run logs). Changes: review → the terminal is handed to nog (`App.suspend`), pacman's "Proceed?" and the AUR recipe review kept (nog rulings F-6 #38, #26), password via the system window. Manual (7 pages), --version/--help, closing note + run log.
- [x] 21 tests (stand-in nog), 0 warnings; console check clean on all 5 screens. Found and fixed on the way: crash on a text console (console colour names unreadable to Rich), shading hid the selection on a console, a missing nog said in technical words, Show's count not redrawn, an unclosed file.
- [x] **0.2 and 0.3 built too (09:35–09:45)**, on top of 0.1 (Javier: "go full development"): Update with choices (Space unticks; nog's `--keep` answer unticks partners; Update sends `--keep`; What changed compares versions; Restart Now (r) red / Later (l) selected after a kernel), Promote, Tiers (soonest first, filter, change tier via `nog pin`, promote). nog's plan JSON gained `holds` (tier wait days). 27 tests; console clean on all six screens. Manual pages for Update and Tiers.
- [x] **Javier's first run (3 Oct 12:15–12:40)** — "a work of art"; findings F-1…F-7 and his changes, all done (matrix §7): In-System, Install, one filter bar (Search + 🔍 button, Show, Type, Tier, Repositories window), Repository column, button-look options with hover, Tiers removed, History ▾ Activity / nog Logs (log window), Promote = ready not install (nog 1.6.0-rc.2 `--promote`), unticking fixed, search ranked (no perl for "calc"), clicks on a row only select. 30 tests; console clean on every screen.
- [x] **Second run (3 Oct evening)** — 8.1 rc.3 pass; In-System, Install, Update "good". Fixed after: a row of space under the Search line, boxes lined up on the left, buttons as tall as the boxes; **c is always Clean Up, k checks for updates** ("c check again" was confusing). 31 tests.
- [x] **Installed 3 Oct ~22:20:** forgekit 0.5.2 (AUR, via nog; its run kept as a .log) and nog 1.6.0-rc.5 — only nog, no updates.
- [x] ~~Tomorrow (Javier): Update ticks/unticks/promote~~ → the 4 Oct item below.
- [x] **nog Logs shows each run whole (3 Oct)** — Javier's idea; nog 1.6.0-rc.4 keeps every run as a `.log` (30 days, nog #42); Enter opens it; older runs fall back to the CSV lines.
- [x] **Bottom bar kept the last screen's keys** (Javier, 3 Oct) — a forgekit bug, in all four apps; fixed in forgekit `8f14c39` (needs forgekit 0.5.2 on the AUR for installed apps). Dashboard bar now names c clean up.
- [x] **v0.3.0 RELEASED 3 Oct (first beta; Javier: "push … to final versions")** — signed tag, GitHub Release (Latest). Not on the AUR (beta until Flatpak + Snap). F-1…F-9 = issues #2–#10, opened and closed. 33 tests.
- [x] **v1.0.0 RELEASED 4 Oct — tag, GitHub Latest, AUR `nogforge` 1.0.0-1 (new package, `7481cae`), About + topics (aur-package, AUR homepage). Javier installs from the AUR (`nog install nogforge`).** (Javier, 4 Oct: "publish nogForge 1.0.0. We can do that.") — version, man page, README (stable, AUR, roadmap: nog inside the app next), CLAUDE.md beta rule replaced, screenshots, 36 tests, Test Results. Then tag, GitHub, the first AUR package (`aur-nogforge`, after nog 1.6.1 is on the AUR). Javier installs both from the AUR.
- [x] **4 Oct (Javier): Update test 8.4–8.6 PASSED at 10:33** ("exactly what was described!"); #11 #12 #13 closed. **Next: release 0.3.1** (after nog 1.6.1). Was: Update untick / promote / update (matrix §8.4–8.6); new findings → issues, fix, 0.3.x. *In progress:* 3 ready, 69 held on the desktop this morning (enough for all three).
  - [x] **F-10 (#11)** a tick changed only after nog answered (~3 s), and quick clicks each asked nog again (Javier: "make it look immediately … batch them"). **Fixed:** shown at once; nog asked once the clicking pauses (0.6 s), with every choice
  - [x] **F-11 (#12)** "asking nog…" was small grey text (Javier: "like a button, but in yellow, as a banner … the update button idle in clear yellow or cream"). **Fixed:** yellow "⏳ nog is working on it…" banner beside the update button, which waits in cream; both clear when nog answers. 35 tests. **Javier to see it on screen**, then close #11 #12 → 0.3.1
  - [x] **u hands nog the ticked ones by name** (Javier, 4 Oct: nog showed the whole pending list for a choice; nog F-10 #44): from nog 1.6.1 `nog update a b c --promote x`, so nog shows only those; nog 1.6.0 keeps `--keep`. 36 tests. Needs the nog 1.6.1 rc installed to see it
  - [x] **F-12 (#13)** a finished update said "nog stopped (status 0)" (Javier, 10:04: vde2 + wolfssl went in). Cause: the success/warning condition sent every update to the warning. **Fixed**, test fails on the old code with his exact message. 36 tests. **Seen with nog 1.6.1-rc.1: `nog update vde2 wolfssl` showed only those two and installed them (exit 0)** — nogForge side of 8.6 works
- [ ] **Javier's run**: `testing/20261003 - Test Matrix for nogForge v0-1-0.md` §6 (includes 6.8b–d for choices and Tiers).
- [ ] **0.4 Settings — not started on purpose:** it writes /etc files (nog.conf holds, pacman.conf, repositories with key trust). nog has no command for those yet; it needs either nog commands (`nog config …`, `nog repo add/remove`) or a grubForge-style privileged helper. A design question for Javier, and security-sensitive.
- [x] *(done: committed, then released 3 Oct)* **Nothing committed yet**: the GPG passphrase had expired (the pinentry window timed out at 09:05 with Javier away). Commit in steps once he unlocks it: nog (`feat` + rc script), nogForge (0.1 code, tests, manual, README, matrix).
- [x] *(done 3 Oct: nog 1.6.0 and nogForge 0.3.0 released)* After the run: Test Results; nog 1.6.0 release (docs, version surfaces, tag, GitHub, AUR) BEFORE nogForge relies on it publicly; nogForge 0.1 tag + GitHub release (beta, no AUR yet: "beta until Flatpak and Snap").

## Next
- [ ] **nog's run inside the UI** (Javier, 4 Oct: "it is not beautiful, it is disrupting"): research done (pty panel + in-app password box via askpass, then a steps view from nog events, then grubForge's own polkit agent); Javier picks the design. Also: the password on a text console, never tried (#1).
- [x] Project kit (3 Oct): `CLAUDE.md` (the decided rules), this TODO, GitHub topics completed (forge-suite, linux, aur-package, ai-collaboration, human-ai), Vault folder. Phase issues open with the design. Old stub code (`nogforge/managers/base.py`, never wired) is replaced by the build.
- [ ] **Old commit message `f16c086` (30 Jul) uses the book persona name.** Javier: "remove it" (3 Oct). The history rewrite (filter-branch + re-sign + force-push) was **blocked by Claude Code's permission system**; nothing changed. Javier decides: allow it, or run it himself. A full backup bundle was made first (session scratchpad). The name was also removed from this TODO's current text.
- [x] Research (3 Oct): nog 1.5.8 commands; 1,518 installed / 254 chosen / 24 AUR; only 29 of the 254 in Arch's app catalogue (`archlinux-appstream-data`, English names must be picked from the translations); 74 updates in nog's hold record; cache 9.7 GB; Flatpak 2, Snap 4.
- [ ] **Design page drawn (3 Oct, ~00:55), waiting on Javier's answers**: https://claude.ai/artifact/Qvj5SXyADUqjV3EpKfjn4G — 11 drawings at 100 columns from this desktop's real data (Dashboard, Home + its text-console version, Search, Update + What changed, Tiers, Settings Holds/Repositories/Add, Removing, History). Console badges are two letters (GA, GR, AV…), the lock is the word "locked" (Javier: "icon in tty version may not be visible"). Open questions: restart offer after a kernel update; Home default (Yours 254 vs apps 29); keys 1–7/U/Del//; anything missing.
  - **Version 2 (3 Oct, ~01:30), Javier's notes:** every list a spreadsheet-style table (headers, shaded alternate rows); package rows Icon · Name · Version · Tier (written out) · Option at the right, description underneath with no heading; options at the right of their row (like Promote), screen buttons at the top only; buttons "Review Updates (u)" — for every Forge app from now on (noted in each app's TODO). Dashboard: Updates table (source × ready/held/tier, from nog's last plan), Yours table (source × tier), Recent (short history), Space. Open: restart offer, Home default, keys, Review Packages → Search or Home, anything missing; and an old commit message that uses the book persona name.
  - ✅ **Design approved (3 Oct, ~01:45)**, version 3, copy in `docs/design/v0.1-screens.html`. Javier's answers: restart offered in a pop-up, Restart Now (r) in red or Later (l) ("maybe they want to keep working"); Home default Yours (254); keys 1–7, u, r, Del, / ok; Review Packages (r) opens Search ("to see the whole picture").
  - **Next: nog 1.6.0** (JSON, keep-back, password window) — then nogForge 0.1.
