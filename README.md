# nogforge

A TUI application for managing packages on Kognog OS — searching, installing, and updating across nog, AUR, Flatpak, and Snap from a single, beautiful interface.

Part of the [KognogOS](https://github.com/jetomev/kognog) Forge suite. Will build on [forgekit](https://github.com/jetomev/forgekit) (the shared Forge TUI shell) once its API stabilizes.

## Status

Pre-development stub — nogforge activates after the forgekit → BitlaForge pilot migration proves the shared UI layer.

## Roadmap / ToDos

- [ ] **Tier editor** — visual editing of `/etc/nog/tier-pins.toml`: browse Tier 1/2/3 assignments, move packages between tiers (`nog pin` under the hood), toggle `manual_signoff` expert mode, show each package's hold-window countdown. Requested for the KognogOS Development edition workflow (Balih, 2026-07-30) — the GUI companion to the Tier Reference Guide.
- [ ] Unified search/install/update across nog + AUR (+ Flatpak/Snap later)
- [ ] Update dashboard — the `nog update` Ready/Held/Unknown report, interactive
- [ ] forgekit adoption as the UI foundation
