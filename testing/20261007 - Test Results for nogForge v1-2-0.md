# nogForge v1.2.0 — Test Results (7 Oct 2026)

Matrix: `20261007 - Test Matrix for nogForge v1-2-0.md`.

| Area | Result |
|---|---|
| 1.1 suite | **41 PASS** (37 + 4), `-W default`: no warnings printed |
| 1.2–1.5 | PASS — `tests/test_nogforge.py`: `Choices.test_untick_all_and_tick_all`, `test_find_one_and_update_it_by_itself` (the stand-in logged `update tzdata`), `test_in_system_offers_update_beside_uninstall_when_nog_has_a_newer_version`, `ScrollSurvives` |
| 1.6 makepkg | PASS 22:10 — checksum + signature pass; `check()` ran the 41 tests; `nogforge 1.2.0-1` built |
| 2 · The desktop | Javier tried the Find box at 22:20 ("Much better") and asked for #21 #22 → 1.3.0 the same night; the rest of section 2 runs on 1.3.0 |

Found on the way: a plain Textual app cannot mount a `PackageList` without forgekit's colour variables (`$forge-bg` undefined) — the test gives them through `get_css_variables`, as sudoForge's box does.
