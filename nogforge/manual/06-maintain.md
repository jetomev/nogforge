# Maintenance

What each source has left behind, from nog's own report (nog 2.0.0): a row per category with its size, and what would remove it.

- **Old downloads**: pacman keeps every version it ever downloaded. nog keeps the last few of each package by tier (3 for Tier 1, 2 for Tier 2, 1 for Tier 3) and never the installed one; the rest can go.
- **Orphans**: packages that came along as dependencies and nothing needs any more. pacman shows the list and asks before removing them.
- **Build trees**: what the AUR helper (yay or paru) left behind after building packages. Yours, under your home folder, so no password.
- **Unused runtimes**: Flatpak runtimes no installed app uses any more (an app removed leaves its runtime behind). nog estimates; flatpak decides the exact list, shows it and asks.
- **Old snap revisions**: snapd keeps the previous revision of each snap after an update. Each old one is removed on its own.

## Picking what goes

**Space** (or a click) ticks a category; a category with nothing in it can't be ticked. The line underneath says what the highlighted category holds and who removes it. **Clean Up the Ticked Ones (c)** hands nog exactly those categories (`nog clean --only …`): nog asks once in its window, then pacman and flatpak ask with their own lists; nothing is removed without your yes. **Look Again (k)** asks nog for a fresh report.

The clean-up runs inside nogForge, like every change: a window with nog's steps, nog's own screen when something asks, and your password in nogForge's box.

## From the Dashboard

**Space** on the Dashboard says how much could go, in a line, and **Clean Up (c)** opens this page.
