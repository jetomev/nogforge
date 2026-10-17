# nogForge 1.5.0 bench · 2026-10-17 00:16 · with changes (VM)

| step | result | notes |
|---|---|---|
| 2.2 Dashboard: Maintenance in the bar, 1-7 menu, Flatpak/Snap in Yours, Could go | **SKIP** | not in --only |
| 2.3 In-System · All: Flatpak + Snap rows, base snaps Locked | **SKIP** | not in --only |
| 2.4 p Repositories: Flatpak + Snap after the AUR; untick → rows go; tick back | **SKIP** | not in --only |
| 2.5 Install 'calculator': repositories, AUR, Flatpak (with IDs), Snap; + Install | **SKIP** | not in --only |
| 2.6 Enter on org.gnome.Calculator → review → Install → nog's window → flatpak asks → Yes | **SKIP** | not in --only |
| 2.7 In-System → ✕ Uninstall on the Flatpak → review → nog's window → flatpak asks → Yes | **PASS** | title 'Removing org.gnome.Calculator'; questions answered Yes: ['Proceed with these changes to the system installation? [Y/n]:']; status 0; flatpak list without it |
| #27 Uninstall cliamp: nog's Keep question (yt-dlp, mpv uses it) in the window → Yes keeps it | **SKIP** | not in --only |
| 2.8 Maintenance: five rows with sizes, the highlighted one explained, Clean Up (0) greyed | **SKIP** | not in --only |
| 2.9 Space on old downloads + old snap revisions → c → nog asks once → Yes → rows at nothing | **SKIP** | not in --only |
| 2.10 c from the Dashboard opens Maintenance, runs nothing | **SKIP** | not in --only |
| 2.11 6 → l nog Logs → the newest run → Enter shows it whole | **SKIP** | not in --only |
| 2.12 7 → m the manual; F1 on Maintenance → its page; Esc back | **SKIP** | not in --only |
| 2.13 ? Keys: 1-7, Ctrl+M, c and k, Space on Maintenance | **SKIP** | not in --only |
| 2.14 4 Update: the page as before (sanity, no run) | **SKIP** | not in --only |

1 PASS · 0 FAIL · 13 SKIP
