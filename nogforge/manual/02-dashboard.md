# The Dashboard

**Updates**: how many updates are ready and how many nog is holding back, per source (core, extra, multilib, chaotic-aur, the AUR, Flatpak, Snap) and per tier. It comes from nog's real plan, which takes up to a minute to check every source. **Review Updates (u)** opens Update.

**Yours**: the packages you chose (not the ones they brought along), per source and tier — Flatpak apps and snaps among them, from nog's own list. **Review Packages (r)** opens Install, to see the whole picture.

**Recent**: the last three things nog did. **Open History (h)** shows them all.

**Space**: how much could go, from nog's maintenance report — old downloads, orphans, build trees, unused Flatpak runtimes, old snap revisions — and the package cache's size. **Clean Up (c)** opens **Maintenance**, where you tick what goes and nog cleans it up, each tool asking first.

## Tiers in one line

Tier 1 (kernel, bootloader, glibc, systemd) waits 30 days before an update installs, Tier 2 (desktop and key apps) 15 days, Tier 3 (everything else) 7 days. A new version proves itself on other people's computers first.
