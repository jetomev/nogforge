# nogForge — changelog

*Newest first. The README carries the two most recent releases; older ones are here.*

### v1.1.0 — October 4, 2026 · nog works inside nogForge

Javier, an hour after 1.0.0: *"nog running outside the UI. It is not beautiful, it is disrupting"*, and the password belongs in the app, also on a text console. Five options were researched ([docs/research](docs/research/2026-10-04-nog-inside-the-ui.md)); he chose three, all in this release ([#14](https://github.com/jetomev/nogforge/issues/14)). Needs [nog 1.7.0](https://github.com/jetomev/nog/releases/tag/v1.7.0) and [forgekit 0.6.0](https://github.com/jetomev/forgekit/releases/tag/v0.6.0).

- 🪟 **No more leaving the app.** A change opens a window with nog's steps (from nog's `NOG_EVENTS`) and a progress bar. nog's own screen stays folded until nog or pacman asks something (Yes/No buttons, the table in view), until something fails, or until **F12**. yay's menus are typed in it; its viewer and editor work there too.
- 🔐 **The password in nogForge's own box**, desktop or text console; no desktop password window needed.
- 📦 **Installs name the row's source** (`aur/neofetch`, `extra/cowsay`): in the KognogOS VM, the AUR's neofetch had become chaotic-aur's unifetch ([nog F-11](https://github.com/jetomev/nog/issues/45)).
- The review window's **Install (i)** / **Remove (r)** now answer to their key (found on the text console; fixed in forgekit for every app).

Tested in the KognogOS VM on a real text console (installs from the repositories and the AUR, an update with steps, a cancelled password, a removal), then by Javier on his desktop and tty3: *"wow! better than expected!"*, *"works wonders"* ([testing/](testing/20261004%20-%20Test%20Matrix%20for%20nogForge%20v1-1-0.md)). Tests: 36 → 37.

*Earlier versions: [docs/CHANGELOG.md](docs/CHANGELOG.md).*

---

### v1.0.0 — October 4, 2026 · first stable release

Javier's Update test on the desktop (untick, promote, update), then his call: *"publish nogForge 1.0.0. We can do that."* Needs [nog 1.6.1](https://github.com/jetomev/nog/releases/tag/v1.6.1). On the [AUR](https://aur.archlinux.org/packages/nogforge) from this version.

- **A tick changes at once** ([F-10, #11](https://github.com/jetomev/nogforge/issues/11)). Before, it waited about 3 seconds for nog's answer, and every click asked nog again. Now quick clicks go to nog as one question.
- **A yellow "nog is working on it…" sign** beside the update button, which waits in cream until nog answers ([F-11, #12](https://github.com/jetomev/nogforge/issues/12)).
- **The update hands nog only the ticked ones, by name** (with nog 1.6.1, [nog#44](https://github.com/jetomev/nog/issues/44)): nog shows and installs just those, and refuses a held one that wasn't promoted.
- **A finished update no longer says "nog stopped"** ([F-12, #13](https://github.com/jetomev/nogforge/issues/13)).
- Out of beta: no "beta" in the title, a man page (`man nogforge`).

Tested by Javier on the desktop: `update vde2 wolfssl`, then git promoted with `update freerdp git --promote git`: *"exactly what was described!"* ([testing/](../testing/)). Tests: 33 → 36.

### v0.3.0 — October 3, 2026 · first beta

The design approved on 3 October, built the same morning, then reworked after Javier's two runs on the desktop the same day (*"This is a work of art my friend"*). Needs [nog 1.6.0](https://github.com/jetomev/nog/releases/tag/v1.6.0).

- Dashboard, In-System, Install, Update (with choices) and History, as above.
- From Javier's runs: Home became **In-System** and Search **Install**; one filter bar with a Search button, a Tier filter and a Repositories window; a Repository column; options drawn as buttons, blue under the mouse; **Promote makes an update ready** instead of installing it alone (nog's `--promote`); the Tiers screen folded away; History split into Activity and nog Logs, with each run's full log.
- Fixed ([F-1 to F-9](https://github.com/jetomev/nogforge/issues?q=label%3Afinding+is%3Aclosed)): a crash when quitting after a promote; "calc" finding perl first; shaded and selected rows the same colour; an update that couldn't be unticked; Promote installing at once; screen keys typed into the Search box; a click on a row's name opening the review; the two filter lines touching, boxes not lined up, short buttons, and **c** meaning two things (now always Clean Up; **k** checks for updates).
- The bottom bar showing the last screen's keys was fixed in [forgekit 0.5.2](https://github.com/jetomev/forgekit/releases/tag/v0.5.2), for every Forge app.

Tests: 33. Readable on a plain text console, every screen.
