# nogForge — what the package needs

*Measured from the code on 2026-10-11 (Javier: "check all Forge Suite apps for all dependencies needed to build and
run them"), with the Forge Suite's audit, `forge-suite/scripts/needs-audit.py`, and proven by building the
AUR recipe in a clean Arch system (devtools' `makechrootpkg`, tests included). `tests/test_needs.py` reads every import and fails when one isn't listed here, so this page can't fall behind the code.
Arch's `base` packages (bash, coreutils, glibc, sed, grep, util-linux, systemd…) are on every Arch install and
aren't listed.*

## Needs (the recipe's `depends`)

| Package | What uses it | Module / program |
|---|---|---|
| python | everything | — |
| python-textual | the app's screens | textual |
| python-rich | tables and text | rich |
| python-forgekit (>= 0.10.0) | the Forge look, the terminal pane, the password bridge | forgekit |
| nog (>= 2.0.0) | every install, update, search and clean-up goes through nog; 1.5.0 reads its every-source rows and its maintenance report | (program nog) |

## Optional (`optdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| archlinux-appstream-data | app descriptions and icons | — |
| flatpak | the Flatpak pages (only when it's installed) | (program flatpak) |
| snapd | the Snap pages (only when it's installed) | (program snap) |

## The AUR recipe

AUR 1.4.0-1 lacked the optional **flatpak** and **snapd**; 1.4.0-2 added them. 1.5.0 raises `nog` to `>= 2.0.0` (nog 2.0.0 must be on the AUR first: the dependency goes first).
