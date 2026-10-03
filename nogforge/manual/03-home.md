# Home

What's installed on this computer, as a table: **Icon · Name · Version · Tier · Option**, with what it is on the line underneath.

- **Show**: *Yours* (what you chose; the default), *All* (with everything they need), or *From the AUR*.
- **Type**: Games, Graphics, Office, Internet… from Arch's app catalogue (the one Pamac uses). Packages that aren't apps are "Other".
- **Find** (or **/**): any word from the name or the description. **Esc** leaves the field.

The icon is the category's badge. A terminal can't draw app icons; on a plain text console the badges are two letters (**GA** games, **GR** graphics, **AV** sound and video, **OF** office, **NE** internet, **SY** system, **DE** development, **UT** utilities, **ED** education, **--** other).

## Remove, and Locked

**Enter** or **Del** on a row removes it: a review first, then nog does it in the terminal, and what only that package needed goes with it (pacman lists it before asking).

Some rows say **Locked**, with the reason underneath, and can't be removed here:

- **the system needs this to start**: Tier 1, the kernel and its kind;
- **part of the base system**: Arch's minimal set;
- **needed by …**: another package depends on it. Remove that one first, and this goes with it.
