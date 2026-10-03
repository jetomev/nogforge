# Tiers

Everything nog is holding, **soonest first**, with **Ready on**, the day each wait ends, and the waits themselves at the top (Tier 1 waits 30 days, Tier 2 15, Tier 3 7, or whatever you've set).

- **Show**: All tiers, or one tier.
- **Find** (or **/**): a package's name.

**Enter** on a row opens its window:

- **Change Tier (t)**: pick Tier 1, 2 or 3. nog saves it in `/etc/nog/tier-pins.toml`, so it asks for your password. Tier 1 is for what the system needs to start (the kernel, the bootloader); Tier 3 for everyday programs.
- **Promote Now (p)**: install this one now, before its wait ends (a review first, see *Update*).
