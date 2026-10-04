# nogForge v1.1.0 — Test Results (4 Oct 2026)

The full run is in `20261004 - Test Matrix for nogForge v1-1-0.md`: §1 Claude (tests, desktop
headless, the KognogOS VM on tty3), §2 Javier (desktop and tty3).

| Area | Result |
|---|---|
| §1.1–1.12 tests, VM tty3 (repo + AUR installs, update with steps, cancel, remove, grubForge) | 11 PASS, 1 FINDING (1.11 → nog F-11, fixed) |
| §2.0 install-rc.sh | PASS (finding: nog's banner width → nog F-12, fixed) |
| §2.1–2.4 update through nogForge (leancrypto, pcre2, lib32-pcre2) | PASS — *"wow! better than expected! great job!"* |
| §2.5–2.6 install (extra/cowsay, the i key) and cancel (extra/sl, Esc) | PASS — *"it went as expected!"* |
| §2.7 grubForge's own password box | PASS — *"perfect!"* |
| §2.8 tty3 on the desktop, nogForge and grubForge | PASS — *"works wonders."* The shell prompt there is a separate finding (KognogOS #12, for promptForge) |
| Tests | 37 (36 → 37) |

Findings, all with issues: nog F-11 (#45), nog F-12 (#46), KognogOS #11 (no base-devel), KognogOS #12 (console prompt); forgekit's ReviewDialog key, console "?" and bracket escaping fixed in forgekit 0.6.0 (#6).
