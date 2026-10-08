# nogForge v1.3.0 — Test Results (7 Oct 2026)

Matrix: `20261007 - Test Matrix for nogForge v1-3-0.md`.

| Area | Result |
|---|---|
| 1.1 suite | **42 PASS** (41 + 1), `-W default`: no warnings printed |
| 1.2 | PASS — `Screens.test_search_then_install`: five keystrokes, one search (`searches_seen == ["krita"]`), keyboard in the box, Enter → the list |
| 1.3–1.4 | PASS — `Choices.test_in_system_filters_as_you_type_and_the_filter_rows_are_short`: no `#is-go`, the list narrowed on three letters, filter areas ≤ 4 rows, drop-downs 1 row; `test_untick_all_and_tick_all` asserts Update's bar positions |
| 1.5 console | PASS — `20261007 - console preview 1-3-0 In-System one-row filters.png`: two one-row filter rows, 8 packages visible where 6 were; every character drawable and visible |
| 1.6 makepkg | *(filled in at release)* |
| 2 · The desktop | *(Javier's run)* |

Found on the way: the first live-filter version moved the keyboard to the list after every keystroke (so "tzd" typed "t" and then two list keys). Typing now keeps the box; Enter moves to the list. The screenshot generator still clicked the removed Search button; it presses Enter now.
