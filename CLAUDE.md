# nogForge — project rules

*How this project is built, tested and shipped. Written for the AI co-developer, and public on purpose: it is part of how the human + AI method is documented.*

## What it is
A [forgekit](https://github.com/jetomev/forgekit) (Python/Textual) terminal app for packages on KognogOS: **nog's wrapper, with what Pamac does, in a terminal** (Javier, 3 Oct 2026). Screens: Dashboard, In-System (installed), Install, Update, History (Activity, nog Logs), Help; Settings next. Tiers was folded away (Javier, 3 Oct: "isn't actually needed"). Decisions in `TODO.md` ("Decided").

## Non-negotiables
- **nog does the thinking; nogForge shows it.** Tiers, holds, hold dates, coupling (which packages must move together) come from nog (`--json`, nog ≥ 1.7.0), never recomputed here. Two copies of that logic would disagree.
- **No partial upgrades.** An unticked update goes through nog's "keep these back", which says what must stay back with it; the update hands nog the ticked ones by name (`nog update a b c --promote x`, nog 1.6.1), and nog refuses a held one that wasn't promoted. nogForge never builds a package combination nog hasn't approved.
- **System packages are protected.** No uninstall on Tier 1, Arch's `base` set, or anything another package needs; the reason is shown instead. No override in the app.
- **The password is asked in nogForge's own box** (1.1, Javier 4 Oct: a desktop window "doesn't make sense" for a terminal app). sudo's helper asks the app over forgekit's private bridge; the password goes to sudo only, never to disk, a log or a command line. nog runs as the user (AUR builds refuse root).
- **nog runs inside nogForge** (1.1: forgekit's RunWindow, nog's NOG_EVENTS). Never `App.suspend()` to hand nog the terminal again.
- **Repositories are a security boundary.** Adding one requires signatures by default and shows the key's fingerprint before trusting it; `core` and `extra` can't be removed; every change to `pacman.conf` is reviewed and backed up.
- **1.0.0 is out (4 Oct 2026, Javier: "publish nogForge 1.0.0. We can do that.")**; it replaced the earlier rule "beta until Flatpak and Snap". Flatpak and Snap installs come with nog's install chain (C3). Each version is tested by Javier before the next builds on it.
- **Built on forgekit**, the grubForge 2.0 look: forms, the changes bar, the hint line, a review before every change, a manual inside the app. Colours only through `$forge-*` roles and `glyph()`; readable on a text console; nothing cut off at 100 columns.
- **The name is `nogForge`** (lowercase n). People: Javier and Claude — never the Rullynastre persona names here.
- Credit, never comparison (Pamac is the inspiration, credited, not a rival); the human + AI credit on every release artifact.

## How to run and test
- From source: `PYTHONPATH=~/Programs/forgekit python main.py`.
- Tests: `tests/`, run with `python -W default -m unittest discover tests`; report the count on every release; it never drops silently. Never run a real install, removal or update from a test: a stand-in `nog` prints nog's JSON.
- Every distribution where nog runs, in the test VMs, before a beta goes out; Javier's own run with a written test matrix in `testing/`.

## Documentation, at every step
- `TODO.md` after every step: it is the handoff between sessions.
- README accurate top to bottom; roadmap and changelog newest first.
- Findings F-n, each an issue opened with a full explanation and closed with one.
- After every push: a Vault entry in `~/Google Drive/Rullynastre/nogForge/`.
- Plain words throughout. The readers are not engineers.

## Release discipline
`~/.claude/rules/release.md`; version in every surface; signed tags; GitHub before the AUR; forgekit (and nog) on the AUR at the version nogForge needs before nogForge ships.
