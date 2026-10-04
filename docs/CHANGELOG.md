# nogForge — changelog

*Newest first. The README carries the two most recent releases; older ones are here.*

### v0.3.0 — October 3, 2026 · first beta

The design approved on 3 October, built the same morning, then reworked after Javier's two runs on the desktop the same day (*"This is a work of art my friend"*). Needs [nog 1.6.0](https://github.com/jetomev/nog/releases/tag/v1.6.0).

- Dashboard, In-System, Install, Update (with choices) and History, as above.
- From Javier's runs: Home became **In-System** and Search **Install**; one filter bar with a Search button, a Tier filter and a Repositories window; a Repository column; options drawn as buttons, blue under the mouse; **Promote makes an update ready** instead of installing it alone (nog's `--promote`); the Tiers screen folded away; History split into Activity and nog Logs, with each run's full log.
- Fixed ([F-1 to F-9](https://github.com/jetomev/nogforge/issues?q=label%3Afinding+is%3Aclosed)): a crash when quitting after a promote; "calc" finding perl first; shaded and selected rows the same colour; an update that couldn't be unticked; Promote installing at once; screen keys typed into the Search box; a click on a row's name opening the review; the two filter lines touching, boxes not lined up, short buttons, and **c** meaning two things (now always Clean Up; **k** checks for updates).
- The bottom bar showing the last screen's keys was fixed in [forgekit 0.5.2](https://github.com/jetomev/forgekit/releases/tag/v0.5.2), for every Forge app.

Tests: 33. Readable on a plain text console, every screen.
