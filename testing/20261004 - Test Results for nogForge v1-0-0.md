# nogForge v1.0.0 — Test Results (4 Oct 2026)

The full run is in `20261003 - Test Matrix for nogForge v0-1-0.md` (§6–§10): Javier's three runs on the desktop, 3–4 Oct.

## What 1.0.0 was released on

| Area | Result |
|---|---|
| In-System, Install, filter bar, History, quit (8.2, 8.3, 8.7, 8.8) | PASS (3 Oct) |
| Update: untick (8.4) | PASS after F-10 (#11, ticks shown at once, clicks batched) and F-11 (#12, yellow "nog is working" sign, cream button) |
| Update: update (8.6) | PASS with nog 1.6.1-rc.1/rc.2: only the ticked ones handed by name (`update vde2 wolfssl`, 10:04) after nog F-10 (nog#44); F-12 (#13, false "nog stopped" alert) fixed |
| Update: promote (8.5) | PASS (10:33): git promoted, `update freerdp git --promote git`, only those two in. Javier: *"exactly what was described!"* |
| Tests | 36 (33 → 36), all pass; screenshots regenerated at 1.0.0 |
| Text console | automated check passes on every screen; **a real virtual-console run (`Ctrl+Alt+F3`) has not been done** (issue #1) |
| Other distributions in VMs | **not run for 1.0.0**: nogForge needs nog, which today runs on Arch and KognogOS only |

## Findings
F-10 #11, F-11 #12, F-12 #13: opened and closed (confirmed by Javier). nog side: nog#43, nog#44 in nog 1.6.1.

## Still to come
Javier's install of nog 1.6.1 and nogForge 1.0.0 from the AUR.
