# Install

Type a name or what it does (*photo*, *paint*, *calc*): the list follows as you type — nog searches the repositories and, through its AUR helper, the AUR, half a second after your last keystroke (Enter searches at once).

Only results with your words in their name or description are shown, best first: the exact name, then names that start with it, then names that contain it, then descriptions. At the same rank the repositories come before the AUR. (pacman also matches what a package *provides*, which is how "calc" used to find perl.)

The table is the same as In-System's, with **+ Install** on the right. What you already have says **✓ Yours** (you chose it) or **✓ Installed** (it came along with something you chose).

The filter bar is In-System's: **Type**, **Tier** and **Repositories (p)** narrow the results. AUR packages are built on this computer from a recipe someone shared; the helper shows you that recipe to review before it builds.

**+ Install** (a click, or **Enter** on the row) installs it: a review first, then nog in the terminal, where pacman lists what comes with it and asks before anything happens.
