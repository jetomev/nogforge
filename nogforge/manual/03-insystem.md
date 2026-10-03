# In-System

What's on this computer, as a table: **Icon · Name · Version · Tier · Repository · Option**, with what it is on the line underneath.

## The filter bar (the same on Install)

- **Search** and **🔍 Search (Enter)**: any word from a name or a description. **Esc** leaves the box. While the box is empty, the screen keys 1–6 still work.
- **Show**: *Yours* (what you chose; the default) or *All* (with everything they brought along).
- **Type**: Games, Graphics, Office, Internet… from Arch's app catalogue (the one Pamac uses). Packages that aren't apps are *Other*.
- **Tier**: all, or one tier.
- **Repositories (p)**: a window to tick and untick the repositories to show (core, extra, multilib, chaotic-aur, any you've added, and the AUR).

The icon is the category's badge. A terminal can't draw app icons; on a plain text console the badges are two letters (**GA** games, **GR** graphics, **AV** sound and video, **OF** office, **NE** internet, **SY** system, **DE** development, **UT** utilities, **ED** education, **--** other).

## Remove, and Locked

The **✕ Remove** button (a click, or **Enter** or **Del** on the row) removes it: a review first, then nog does it in the terminal, and what only that package needed goes with it (pacman lists it before asking). A click elsewhere on a row only selects it.

Some rows say **Locked**, with the reason underneath, and can't be removed here:

- **the system needs this to start**: Tier 1, the kernel and its kind;
- **part of the base system**: Arch's minimal set;
- **needed by …**: another package depends on it. Remove that one first, and this goes with it.
