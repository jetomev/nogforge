# nogForge 1.1.0 (with nog 1.7.0, forgekit 0.6.0, grubForge 2.1.0) — Test Matrix

**What changed (Javier, 4 Oct 2026, options 1 → 2 → 3):** nog runs *inside* nogForge (its steps, a
progress bar, its own screen when it asks something), the password is asked in the app's own
box, and grubForge's polkit password is asked in grubForge's own box (also on a text console).
Issues: forgekit#6, nog#45, nogforge#14, grubforge#36; KognogOS#11 found on the way.

## 1 · Claude — tests and the KognogOS VM (4 Oct, 11:20–12:05)

| ID | What | Result |
|---|---|---|
| 1.1 | forgekit tests | PASS — 67 (52 → 67) |
| 1.2 | nog tests / warnings | PASS — 239 (237 → 239), warnings 6 |
| 1.3 | nogForge / grubForge / alacrittyForge / bitlaForge tests on forgekit 0.6.0 | PASS — 37 / 53 / 80 / 64 |
| 1.4 | Desktop, headless: the real plan, nog's question answered No in the app | PASS — nothing installed |
| 1.5 | VM tty3 (TERM=linux): polkit spike — the app answers polkit, pkexec runs as root | PASS (the PyGObject Listener route crashed: not used) |
| 1.6 | VM tty3: grubForge Back up now → password box → wrong one → "try again" → right one | PASS — backup made as root |
| 1.7 | VM tty3: nogForge install botsay (repo) — steps, password box, pacman's question → Yes | PASS — installed |
| 1.8 | VM tty3: update with hyprland promoted — steps, password, Yes | PASS — 0.56.2-4 in |
| 1.9 | VM tty3: Esc on the password box | PASS — "no password was provided", nog stopped, nothing changed |
| 1.10 | VM tty3: AUR install through yay (pfetch-git) — yay's menus typed in nog's screen, its diff viewer, password, Yes | PASS (after `debugedit`, KognogOS#11) |
| 1.11 | VM tty3: AUR neofetch → yay swapped in chaotic-aur's unifetch | FINDING → nog F-11 (#45): `aur/x` / `repo/x` now |
| 1.12 | VM tty3, installed test packages: grubForge backup; nogForge remove botsay | PASS |

## 2 · Javier — this desktop

**Install the test packages first:** `bash ~/Programs/nogforge/scripts/install-rc.sh` (pacman shows
four packages and asks; your password once). Log: `nogforge/logs/install-rc-latest.log`.

| ID | Do | Expect | Result |
|---|---|---|---|
| 2.0 | `install-rc.sh` | **PASS** (12:16) — nog 1.7.0rc1, forgekit 0.6.0rc1, grubforge 2.1.0rc1, nogforge 1.1.0rc1 in; pyte already there. *Small finding: nog's ===== banner lines are as wide as the longest line, so four file paths made them ~330 characters (cap them at the terminal width).* | |
| 2.1 | `nogforge`, **4** Update, tick what you like, **u** | a window *inside* nogForge: steps (Checking for updates ✓ · Official packages …), a progress bar; nog's question with **Yes (y)** / **No (n)** | |
| 2.2 | answer **y** | nogForge's own password box (not KDE's window); then pacman's question with Yes/No, its table in view | |
| 2.3 | finish, **Close** | "Updated."; What changed; no "nog stopped" | |
| 2.4 | **F12** during a run | nog's own screen opens/folds | |
| 2.5 | **3** Install, search, **Enter** on a row, **i** | the review answers to **i**; same window, password, Yes; "Installed." | |
| 2.6 | an install, then **Esc** on the password box | "nog stopped (status 1)", nog's screen open, nothing changed | |
| 2.7 | `grubforge`, Backups, **Back up now (N)** | grubForge's own password box (not KDE's window); a backup appears | |
| 2.8 *(optional)* | **Ctrl+Alt+F3**, log in, `nogforge` and `grubforge` | the same boxes on the text console; **Ctrl+Alt+F1/F2** back to the desktop | |
| 2.9 | anything that looks or feels wrong | a finding | |
