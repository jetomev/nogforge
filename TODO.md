# nogForge — the list

*The live work list and the handoff between sessions. Newest work first. Updated after every step.*

**Status: not started (README only).** Starts after alacrittyForge and bitlaForge match grubForge 2.0 (Javier, 2 Oct 2026: "after that, we are ready to start working on nogForge!!!").

## Decided (Javier, 3 Oct 2026)

- **What it is:** nog's wrapper *and* Pamac's functions in a TUI. Screens: **Dashboard** ("sexy"), **Home** (installed apps: the 254 you chose by default, all 1,518 on a switch; name, version, description, tier, a category badge from `archlinux-appstream-data` since Alacritty can't draw icons; uninstall on the left), **Search** (types from AppStream: Office, Games, Internet…; same list, install on the left), **Update** (visual: Repositories, Ready with checkboxes guarded by nog's coupling — untick one, nog says what must stay back with it —, Held with Promote, Unknown, review, nog's real run, "What changed"), **Tiers** (All/1/2/3 dropdown, sorted by next update date, change tier = nog pin, Promote = nog unlock), **Settings** (nog holds/safety days/sources; pacman.conf safe options; **add/remove repositories**: signatures required by default, key fingerprint shown before trusting, core/extra never removable; clean cache), **History** (nog's log), Help, Quit.
- **System packages are protected:** no uninstall on Tier 1, the `base` set, or anything another package needs ("needed by Firefox and 3 more"); the reason shown instead. No override in the app.
- **Password like grubForge:** the system's own password window; nogForge never sees it. nog runs as the user (AUR builds refuse root) and asks through the window when nogForge calls it — needs nog 1.6.0. Text console: the terminal prompt.
- **nog 1.6.0 comes first:** `--json` output, the "keep these back" choice, the password window. Part of nog#7.
- **Flatpak and Snap** installs come later (nog#7; nog already *updates* both with holds). **nogForge stays beta (0.x) until everything is there, Flatpak and Snap included.** Beta phases, each tested by Javier: 0.1 Home/Search/install-remove · 0.2 Update · 0.3 Tiers · 0.4 Settings.

## Next
- [x] Project kit (3 Oct): `CLAUDE.md` (the decided rules), this TODO, GitHub topics completed (forge-suite, linux, aur-package, ai-collaboration, human-ai), Vault folder. Phase issues open with the design. Old stub code (`nogforge/managers/base.py`, never wired) is replaced by the build.
- [ ] **Ask Javier:** old commit message `f16c086` (30 Jul) says "Balih" in this public repo; removing it means rewriting history (force-push). His call.
- [ ] Research: what nog does today (tiers, holds, queue, updates, logs) and what a screen for it should show; forgekit 0.5.0 as the base
- [ ] Design: screen-by-screen plan for Javier's approval before any code, the grubForge 2.0 method
