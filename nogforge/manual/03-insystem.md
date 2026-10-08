# In-System

What's on this computer, as a table: **Icon · Name · Version · Tier · Repository · buttons**, with what it is on the line underneath.

## The filter bar (the same on Install)

- **Search**: any word from a name or a description — the list follows as you type (on Install, which asks nog, after a short pause and from two characters on; Enter searches at once). **Esc** leaves the box. While the box is empty, the numbers 1–6 still go to the menu; Ctrl + a menu letter works anytime.
- **Show**: *Yours* (what you chose; the default) or *All* (with everything they brought along).
- **Type**: Games, Graphics, Office, Internet… from Arch's app catalogue (the one Pamac uses). Packages that aren't apps are *Other*.
- **Tier**: all, or one tier.
- **Repositories (p)**: a window to tick and untick the repositories to show (core, extra, multilib, chaotic-aur, any you've added, and the AUR).

The icon is the category's badge. A terminal can't draw app icons; on a plain text console the badges are two letters (**GA** games, **GR** graphics, **AV** sound and video, **OF** office, **NE** internet, **SY** system, **DE** development, **UT** utilities, **ED** education, **--** other).

## Uninstall, Update, and Locked

The **✕ Uninstall** button (a click, or **Enter** or **Del** on the row) uninstalls it: a review first, then nog does it in a window inside nogForge, and what only that package needed goes with it (pacman lists it before asking). A click elsewhere on a row only selects it.

When nog has a **newer version** of a package in its plan, the row shows **⬆ Update** beside Uninstall: a click updates that one package by itself (nog works out what has to move with it and asks first). No button appears for a downgrade yet: that waits for nog to offer one.

Some rows say **Locked**, with the reason underneath, and can't be uninstalled here:

- **the system needs this to start**: Tier 1, the kernel and its kind;
- **part of the base system**: Arch's minimal set;
- **needed by …**: another package depends on it. Uninstall that one first, and this goes with it.
