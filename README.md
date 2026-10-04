# nogForge

> Packages, the KognogOS way: what's installed, searching and installing, and updates, in plain words, in a terminal. The decisions are **nog**'s; nogForge shows them.

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Platform: KognogOS / Arch](https://img.shields.io/badge/Platform-KognogOS%20%2F%20Arch-lightgrey.svg)
![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)
![Status: Stable](https://img.shields.io/badge/Status-Stable-brightgreen.svg)
![Version: 1.0.0](https://img.shields.io/badge/Version-1.0.0-purple.svg)
[![AUR](https://img.shields.io/aur/version/nogforge?color=1793d1&label=AUR)](https://aur.archlinux.org/packages/nogforge)

---

## Why nogForge?

[nog](https://github.com/jetomev/nog) is KognogOS's package manager: pacman with a safety net. Every package has a **tier**, and a new version waits before it installs (30 days for the kernel and its kind, 15 for the desktop, 7 for the rest) so it can prove itself on other people's computers first.

nogForge brings what [Pamac](https://github.com/manjaro/pamac), Manjaro's software centre, does so well (with thanks: it's the inspiration) to the terminal, on top of nog: your programs as a table, a search with types, and updates you can read. **nog decides; nogForge shows it.** Tiers, holds and which packages must move together are never worked out twice.

---

## What's in 1.0

- 🏠 **Dashboard**: updates per source and tier (nog's real plan), your packages per source and tier, the last things nog did, and the space old downloads take.
- 📦 **In-System**: what's on this computer, spreadsheet-style: badge, name, version, tier, repository, and a **✕ Remove** button, with what it is underneath. System packages are **Locked**, with the reason: the system needs it to start, it's part of the base system, or another package needs it.
- 🔎 **Install**: search the repositories and the AUR (names and descriptions, best matches first) and **+ Install**.
- One **filter bar** on both: Search with a 🔍 button, Show (yours or all), Type (Games, Graphics, Office…), Tier, and **Repositories (p)**, a window to tick the repositories to show.
- ⬆ **Update**: nog's plan with your choices. Untick an update to keep it back, and **nog** says what must stay back with it, so a half-updated, broken system can't happen. A tick changes at once; while nog works out your choices, a yellow sign says so. **↑ Promote** makes a held one ready now; it goes in with the rest. **Update the Ticked Ones** hands nog exactly those, by name, and nog shows and installs only them. Afterwards, **What changed** compares versions before and after, and after a new kernel offers **Restart Now (r)** or **Later (l)**.
- 🗂 **History**: **Activity** (everything nog ran, in plain words) and **nog Logs** (nog's own record; Enter opens a run whole, as it appeared on screen).
- 🔐 **Your password goes to the system's own window**, never to nogForge (like grubForge). The change itself runs in the terminal, where pacman shows what comes with it and asks first.
- 📖 A manual inside the app (**F1**), readable on a plain text console, nothing cut off at 100 columns.

Arch's app catalogue (the one Pamac uses) gives apps their proper names and a category badge (🎮 🎨 🎵 📝 🌐 ⚙); a terminal can't draw app icons, and on a text console the badges become two letters.

The design, drawn and approved before any code: [`docs/design/v0.1-screens.html`](docs/design/v0.1-screens.html).

---

## Screenshots

### Dashboard
![Dashboard](docs/screenshots/01-dashboard.svg)

### In-System
![In-System](docs/screenshots/02-in-system.svg)

### Install, and the review before installing
![Install](docs/screenshots/03-install.svg)
![Review](docs/screenshots/04-review.svg)

### Update: one kept back, one promoted
![Update](docs/screenshots/05-update.svg)

### History: Activity and nog Logs
![Activity](docs/screenshots/06-activity.svg)
![nog Logs](docs/screenshots/07-nog-logs.svg)

*Made from the running app (`python docs/screenshots/generate.py`) with a stand-in nog and a sample package list.*

---

## Requirements

- KognogOS or Arch Linux
- **nog 1.6.1 or newer** (nogForge reads its `--json` answers and hands it the ticked updates by name)
- Python 3.11+, `python-textual`, `python-rich`, [`python-forgekit`](https://github.com/jetomev/forgekit) 0.5.2+
- `archlinux-appstream-data` for app names and badges (optional; without it every package gets the plain badge)
- A password window for `sudo -A` (KDE's `ksshaskpass`, or `x11-ssh-askpass`); without one, nog asks in the terminal

## Installation

From the [AUR](https://aur.archlinux.org/packages/nogforge), with nog:

```bash
nog install nogforge
nogforge
```

Or from source:

```bash
git clone https://github.com/jetomev/nogforge.git
python3 nogforge/main.py
```

`man nogforge` has the reference; **F1** inside the app has the manual.

---

## Keys

| Key | Does |
|---|---|
| 1 – 6 | Dashboard, In-System, Install, Update, Activity, nog Logs |
| u | open Update · on Update: update the ticked ones |
| r | review packages (Install) |
| k | check for updates |
| c | clean up old downloads (asks first) |
| p | Repositories (In-System, Install) |
| Space | tick or untick an update |
| Enter | the row's option: install, remove, promote · on nog Logs: open the run |
| Del | remove the selected package (In-System) |
| / | search |
| F1 | help on this screen |
| ? | all keys |
| q | quit |

---

## Roadmap (each version tested by Javier before the next)

- [ ] **Next: nog's work inside the app.** Today a change leaves the screen for the terminal and comes back. Javier: *"it is not beautiful, it is disrupting."* Options researched on 4 Oct; the design is his call.
- [ ] **Settings** — nog's holds and sources, pacman's safe options, repositories (signatures required, key checked first), cleaning
- [ ] **Flatpak and Snap installs**, with nog's install chain (nog C3)

---

## Changelog

### v1.0.0 — October 4, 2026 · first stable release

Javier's Update test on the desktop (untick, promote, update), then his call: *"publish nogForge 1.0.0. We can do that."* Needs [nog 1.6.1](https://github.com/jetomev/nog/releases/tag/v1.6.1). On the [AUR](https://aur.archlinux.org/packages/nogforge) from this version.

- **A tick changes at once** ([F-10, #11](https://github.com/jetomev/nogforge/issues/11)). Before, it waited about 3 seconds for nog's answer, and every click asked nog again. Now quick clicks go to nog as one question.
- **A yellow "nog is working on it…" sign** beside the update button, which waits in cream until nog answers ([F-11, #12](https://github.com/jetomev/nogforge/issues/12)).
- **The update hands nog only the ticked ones, by name** (with nog 1.6.1, [nog#44](https://github.com/jetomev/nog/issues/44)): nog shows and installs just those, and refuses a held one that wasn't promoted.
- **A finished update no longer says "nog stopped"** ([F-12, #13](https://github.com/jetomev/nogforge/issues/13)).
- Out of beta: no "beta" in the title, a man page (`man nogforge`).

Tested by Javier on the desktop: `update vde2 wolfssl`, then git promoted with `update freerdp git --promote git`: *"exactly what was described!"* ([testing/](testing/)). Tests: 33 → 36.

### v0.3.0 — October 3, 2026 · first beta

The design approved on 3 October, built the same morning, then reworked after Javier's two runs on the desktop the same day (*"This is a work of art my friend"*). Needs [nog 1.6.0](https://github.com/jetomev/nog/releases/tag/v1.6.0).

- Dashboard, In-System, Install, Update (with choices) and History, as above.
- From Javier's runs: Home became **In-System** and Search **Install**; one filter bar with a Search button, a Tier filter and a Repositories window; a Repository column; options drawn as buttons, blue under the mouse; **Promote makes an update ready** instead of installing it alone (nog's `--promote`); the Tiers screen folded away; History split into Activity and nog Logs, with each run's full log.
- Fixed ([F-1 to F-9](https://github.com/jetomev/nogforge/issues?q=label%3Afinding+is%3Aclosed)): a crash when quitting after a promote; "calc" finding perl first; shaded and selected rows the same colour; an update that couldn't be unticked; Promote installing at once; screen keys typed into the Search box; a click on a row's name opening the review; the two filter lines touching, boxes not lined up, short buttons, and **c** meaning two things (now always Clean Up; **k** checks for updates).
- The bottom bar showing the last screen's keys was fixed in [forgekit 0.5.2](https://github.com/jetomev/forgekit/releases/tag/v0.5.2), for every Forge app.

Tests: 33. Readable on a plain text console, every screen.

---

## How this project is built

A human and AI collaboration: the screens were drawn and approved before any code, every change is tested (36 tests, a stand-in nog, so no test touches your packages), and the `testing/` folder holds the test matrices, published on purpose.

## Authors

**Javier ([@jetomev](https://github.com/jetomev))**: idea, direction, testing

**Claude (Anthropic)**: co-developer, architecture, implementation

## License

GPL v3. See [LICENSE](LICENSE).
