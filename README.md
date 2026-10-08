# nogForge

> Packages, the KognogOS way: what's installed, searching and installing, and updates, in plain words, in a terminal. The decisions are **nog**'s; nogForge shows them.

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Platform: KognogOS / Arch](https://img.shields.io/badge/Platform-KognogOS%20%2F%20Arch-lightgrey.svg)
![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)
![Status: Stable](https://img.shields.io/badge/Status-Stable-brightgreen.svg)
![Version: 1.3.0](https://img.shields.io/badge/Version-1.3.0-purple.svg)
[![AUR](https://img.shields.io/aur/version/nogforge?color=1793d1&label=AUR)](https://aur.archlinux.org/packages/nogforge)

---

## Why nogForge?

[nog](https://github.com/jetomev/nog) is KognogOS's package manager: pacman with a safety net. Every package has a **tier**, and a new version waits before it installs (30 days for the kernel and its kind, 15 for the desktop, 7 for the rest) so it can prove itself on other people's computers first.

nogForge brings what [Pamac](https://github.com/manjaro/pamac), Manjaro's software centre, does so well (with thanks: it's the inspiration) to the terminal, on top of nog: your programs as a table, a search with types, and updates you can read. **nog decides; nogForge shows it.** Tiers, holds and which packages must move together are never worked out twice.

---

## What's in 1.3

Same evening, twenty minutes after 1.2.0 (Javier: *"much better… but"*): **every search follows as you type**, on In-System, Install and Update alike, and the Search button is gone (Install, which asks nog, waits half a second after your last keystroke and needs two characters). And the **filter rows are one row tall** instead of three: boxes, labels, drop-downs and buttons, so each page shows four or five more packages.

## What's in 1.2

Javier's four, from a night of using it (7 October 2026): on **Update**, a **Find** box narrows both lists as you type, every ready row has its own **⬆ Update** button (one package by itself, nog works out what moves with it), and **Tick All (t)** / **Untick All (n)** do the lot in one go; ticking a row far down the list no longer throws the list back to the top. On **In-System**, the button says **✕ Uninstall** (not Remove), and a row nog has a newer version for shows **⬆ Update** beside it. Downgrade waits for nog to offer one.

## What's in 1.1

- 🏠 **Dashboard**: updates per source and tier (nog's real plan), your packages per source and tier, the last things nog did, and the space old downloads take.
- 📦 **In-System**: what's on this computer, spreadsheet-style: badge, name, version, tier, repository, a **✕ Uninstall** button and, where nog has a newer version, **⬆ Update** beside it, with what it is underneath. System packages are **Locked**, with the reason: the system needs it to start, it's part of the base system, or another package needs it.
- 🔎 **Install**: search the repositories and the AUR (names and descriptions, best matches first) and **+ Install**.
- One **filter bar** on both: Search with a 🔍 button, Show (yours or all), Type (Games, Graphics, Office…), Tier, and **Repositories (p)**, a window to tick the repositories to show.
- ⬆ **Update**: nog's plan with your choices. Untick an update to keep it back, and **nog** says what must stay back with it, so a half-updated, broken system can't happen. A tick changes at once; while nog works out your choices, a yellow sign says so. **↑ Promote** makes a held one ready now; it goes in with the rest. **Update the Ticked Ones** hands nog exactly those, by name, and nog shows and installs only them; **⬆ Update** on a row does that one by itself, **Find** narrows the lists, **Tick All** / **Untick All** do the lot. Afterwards, **What changed** compares versions before and after, and after a new kernel offers **Restart Now (r)** or **Later (l)**.
- 🗂 **History**: **Activity** (everything nog ran, in plain words) and **nog Logs** (nog's own record; Enter opens a run whole, as it appeared on screen).
- 🪟 **nog works inside nogForge** *(1.1)*: a change opens a window over the app with nog's steps and a progress bar. nog's own screen opens by itself when nog or pacman asks something (pacman's table in view, **Yes (y) / No (n)** to answer), when something fails, or on **F12**. yay's menus for AUR builds are typed in it. Nothing leaves the app.
- 🔐 **The password is asked in nogForge's own box** *(1.1)*, on a desktop and on a text console alike. It goes to sudo and nowhere else; nothing is written to disk.
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

### nog at work, inside nogForge (1.1)
![nog's run inside nogForge](docs/screenshots/08-run.svg)
![The password, asked in nogForge](docs/screenshots/09-password.svg)

### History: Activity and nog Logs
![Activity](docs/screenshots/06-activity.svg)
![nog Logs](docs/screenshots/07-nog-logs.svg)

*Made from the running app (`python docs/screenshots/generate.py`) with a stand-in nog and a sample package list.*

---

## Requirements

- KognogOS or Arch Linux
- **nog 1.7.0 or newer** (nogForge reads its `--json` answers and its steps, and hands it the ticked updates by name)
- Python 3.11+, `python-textual`, `python-rich`, [`python-forgekit`](https://github.com/jetomev/forgekit) 0.6.0+ (with `python-pyte`)
- `archlinux-appstream-data` for app names and badges (optional; without it every package gets the plain badge)

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
| t · n | on Update: tick all · untick all |
| / | on Update: the Find box (on In-System and Install: Search) |
| r | review packages (Install) |
| k | check for updates |
| c | clean up old downloads (asks first) |
| p | Repositories (In-System, Install) |
| Space | tick or untick an update |
| Enter | the row's option: install, remove, promote · on nog Logs: open the run |
| Del | uninstall the selected package (In-System) |
| / | search |
| F1 | help on this screen |
| ? | all keys |
| q | quit |

---

## Roadmap (each version tested by Javier before the next)

- [ ] **Settings** — nog's holds and sources, pacman's safe options, repositories (signatures required, key checked first), cleaning
- [ ] **Flatpak and Snap installs**, with nog's install chain (nog C3)

---

## Changelog

### v1.3.0 — October 7, 2026 · searches follow the typing; one-row filters ([#21](https://github.com/jetomev/nogforge/issues/21), [#22](https://github.com/jetomev/nogforge/issues/22))

- **Every search filters as you type**, like Update's Find: In-System at once (it filters what is already here); Install after half a second's pause and from two characters on (it asks nog); Enter still searches at once; an emptied box clears the results. The Search button is gone.
- **One-row filters:** the search boxes, labels, drop-downs and buttons on the filter rows are one row tall (they were three), on a terminal and on a text console alike. The filter area went from seven rows to four.
- Tests: 42 (was 41); the position checks cover the drop-downs' height.

### v1.2.0 — October 7, 2026 · Javier's four ([#17](https://github.com/jetomev/nogforge/issues/17), [#18](https://github.com/jetomev/nogforge/issues/18), [#19](https://github.com/jetomev/nogforge/issues/19), [#20](https://github.com/jetomev/nogforge/issues/20))

- **Update:** a **Find** box narrows the Ready and Held lists as you type (`/` goes there); every ready row has **⬆ Update**, which hands nog that one name alone; **Tick All (t)** and **Untick All (n)**; a tick far down the list keeps the scroll and the highlight (#17).
- **In-System:** **✕ Uninstall** instead of Remove, everywhere a person reads it; **⬆ Update** beside it when nog's plan has a newer version (#19). Downgrade waits for nog to offer one (a nog feature first).
- The package list draws two buttons per row where a row has two; the mouse hovers and clicks each on its own.
- Tests: 41 (was 37). Found on the way: a plain Textual app needs forgekit's colour variables to mount a `PackageList` in a test.

## How this project is built

A human and AI collaboration: the screens were drawn and approved before any code, every change is tested (37 tests, a stand-in nog, so no test touches your packages), and the `testing/` folder holds the test matrices, published on purpose.

## Authors

**Javier ([@jetomev](https://github.com/jetomev))**: idea, direction, testing

**Claude (Anthropic)**: co-developer, architecture, implementation

## License

GPL v3. See [LICENSE](LICENSE).
