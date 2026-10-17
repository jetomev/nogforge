# nogForge 1.5.0 bench · 2026-10-16 23:54 · read-only

| step | result | notes |
|---|---|---|
| 2.2 Dashboard: Maintenance in the bar, 1-7 menu, Flatpak/Snap in Yours, Could go | **PASS** | Yours table: Source Yours Tier 1 Tier 2 Tier 3 / core 16 4 0 12 / extra 214 2 14 198 / multilib 3 0 0 3 / chaotic-aur 18 0 0 18 / AUR 20 0 2 ; Space: Could go: 1.3 GB — old downloads 6.2 MB, orphans 918.2 MB, unused runtimes 444.7 MB Package cache 11.8 GB, 1,611 files. Clean Up opens Maintenance: pick what go |
| 2.3 In-System · All: Flatpak + Snap rows, base snaps Locked | **PASS** | 1608 rows; Flatpak rows 23 (com.github.tchx84.Flatseal, com.retro_exo.abiword, com.retro_exo.aria2c…); Snap rows 4: core, core20, hello, snapd; Locked: core, core20, snapd; column says ['Flatpak', 'Snap'] |
| 2.4 p Repositories: Flatpak + Snap after the AUR; untick → rows go; tick back | **PASS** | listed ['core', 'extra', 'multilib', 'chaotic-aur', 'aur', 'flatpak', 'snap']; flatpak unticked → its rows gone; ticked back → 23 rows again |
| 2.5 Install 'calculator': repositories, AUR, Flatpak (with IDs), Snap; + Install | **PASS** | 370 rows: {'extra': 21, 'Snap': 40, 'AUR': 294, 'Flatpak': 12, 'chaotic-aur': 3}; org.gnome.Calculator is a Flatpak row with '+ Install' |
| 2.6 Enter on org.gnome.Calculator → review → Install → nog's window → flatpak asks → Yes | **SKIP** | a real install: VM only (--changes) |
| 2.7 In-System → ✕ Uninstall on the Flatpak → review → nog's window → flatpak asks → Yes | **SKIP** | a real uninstall: VM only (--changes) |
| #27 Uninstall cliamp: nog's Keep question (yt-dlp, mpv uses it) in the window → Yes keeps it | **SKIP** | a real uninstall: VM only (--changes) |
| 2.8 Maintenance: five rows with sizes, the highlighted one explained, Clean Up (0) greyed | **PASS** | rows: [('cache', 13, 6.5), ('orphans', 27, 962.8), ('aur', 0, 0.0), ('flatpak', 3, 466.3), ('snap', 0, 0.0)] MB; empty ones not tickable; button Content('Clean Up the Ticked Ones (0) (c)') greyed; summary: About 1.3 GB could go · 3 of 5 categories have something · pacman's cache holds 11.8 GB, 1,604 versions stay The clean-u; detail: removed by nog; root is needed |
| 2.9 Space on old downloads + old snap revisions → c → nog asks once → Yes → rows at nothing | **SKIP** | a real clean-up: VM only (--changes) |
| 2.10 c from the Dashboard opens Maintenance, runs nothing | **PASS** | c on the Dashboard opens Maintenance; no run window |
| 2.11 6 → l nog Logs → the newest run → Enter shows it whole | **PASS** | 200 runs; newest: '10/16/2026 04:51 PM tier nvidia-utils jetomev 0 done '; Enter opened LogDialog |
| 2.12 7 → m the manual; F1 on Maintenance → its page; Esc back | **PASS** | 7 → m opens the manual at Welcome; F1 on Maintenance opens the Maintenance page; Esc back |
| 2.13 ? Keys: 1-7, Ctrl+M, c and k, Space on Maintenance | **PASS** | Keys page: 1-7, Ctrl+letter with M for Maintenance, c and k with their two meanings, Space on Maintenance |
| 2.14 4 Update: the page as before (sanity, no run) | **PASS** | plan: ready 14, held 246; summary: 14 to update · 0 kept back · 246 held The update runs here, inside nogForge: nog shows only what you ticked and asks before anything changes; nogForge asks for (nothing in 1.5.0 changes Update; no update run tonight) |

10 PASS · 0 FAIL · 4 SKIP
