# nogForge 1.5.0 bench · 2026-10-17 00:14 · with changes (VM)

| step | result | notes |
|---|---|---|
| 2.2 Dashboard: Maintenance in the bar, 1-7 menu, Flatpak/Snap in Yours, Could go | **PASS** | Yours table: Source Yours Tier 1 Tier 2 Tier 3 / core 43 18 2 23 / extra 182 3 12 167 / multilib 5 4 0 1 / chaotic-aur 10 0 1 9 / AUR 10 0 4 ; Space: Could go: 56.0 MB — old downloads 56.0 MB, orphans 27 KB, old snap revisions 20 KB Package cache 85.7 MB, 29 files. Clean Up opens Maintenance: pick what goes; |
| 2.3 In-System · All: Flatpak + Snap rows, base snaps Locked | **PASS** | 1173 rows; Flatpak rows 0 (); Snap rows 3: core, hello-world, snapd; Locked: core, snapd; column says ['Snap'] |
| 2.4 p Repositories: Flatpak + Snap after the AUR; untick → rows go; tick back | **PASS** | listed ['core', 'extra', 'multilib', 'chaotic-aur', 'aur', 'flatpak', 'snap']; snap unticked → its rows gone; ticked back → 3 rows again |
| 2.5 Install 'calculator': repositories, AUR, Flatpak (with IDs), Snap; + Install | **PASS** | 370 rows: {'Snap': 40, 'AUR': 294, 'Flatpak': 12, 'extra': 21, 'chaotic-aur': 3}; org.gnome.Calculator is a Flatpak row with '+ Install' |
| 2.6 Enter on org.gnome.Calculator → review → Install → nog's window → flatpak asks → Yes | **PASS** | title 'Installing org.gnome.Calculator'; button at start "▾ nog's Screen (F12)"; questions answered Yes: ['Do you want to install it? [Y/n]:', 'Proceed with these changes to the system installation? [Y/n]:']; button while open "▴ Fold nog's Screen (F12)"; status 0; flatpak list has it now; password box: no |
| 2.7 In-System → ✕ Uninstall on the Flatpak → review → nog's window → flatpak asks → Yes | **FAIL** | AssertionError: the review says who asks |
| #27 Uninstall cliamp: nog's Keep question (yt-dlp, mpv uses it) in the window → Yes keeps it | **PASS** | questions, all answered Yes: ['nog: Keep yt-dlp? [Y/n]', ':: Do you want to remove these packages? [Y/n]']; cliamp gone, yt-dlp kept for mpv |
| 2.8 Maintenance: five rows with sizes, the highlighted one explained, Clean Up (0) greyed | **PASS** | rows: [('cache', 9, 58.7), ('orphans', 1, 0.0), ('aur', 0, 0.0), ('flatpak', 3, 985.4), ('snap', 1, 0.0)] MB; empty ones not tickable; button Content('Clean Up the Ticked Ones (0) (c)') greyed; summary: About 995.7 MB could go · 4 of 5 categories have something · pacman's cache holds 85.7 MB, 25 versions stay The clean-up; detail: removed by nog; root is needed |
| 2.9 Space on old downloads + old snap revisions → c → nog asks once → Yes → rows at nothing | **PASS** | ticked ['cache', 'snap'] (before {'cache': 9, 'snap': 1}); title 'Cleaning up: cache, snap'; questions: ['nog: Clean up cache, snap? [y/N]']; after: {'cache': 0, 'orphans': 1, 'aur': 0, 'flatpak': 3, 'snap': 0} |
| 2.10 c from the Dashboard opens Maintenance, runs nothing | **PASS** | c on the Dashboard opens Maintenance; no run window |
| 2.11 6 → l nog Logs → the newest run → Enter shows it whole | **PASS** | 47 runs; newest: '10/17/2026 12:14 AM clean --only cache,snap javier 0 done '; Enter opened LogDialog; the clean run shows whole, nog's question in it; caption names its own log |
| 2.12 7 → m the manual; F1 on Maintenance → its page; Esc back | **PASS** | 7 → m opens the manual at Welcome; F1 on Maintenance opens the Maintenance page; Esc back |
| 2.13 ? Keys: 1-7, Ctrl+M, c and k, Space on Maintenance | **PASS** | Keys page: 1-7, Ctrl+letter with M for Maintenance, c and k with their two meanings, Space on Maintenance |
| 2.14 4 Update: the page as before (sanity, no run) | **PASS** | plan: ready 117, held 128; summary: 117 to update · 0 kept back · 128 held The update runs here, inside nogForge: nog shows only what you ticked and asks before anything changes; nogForge asks for (nothing in 1.5.0 changes Update; no update run tonight) |

13 PASS · 1 FAIL · 0 SKIP
