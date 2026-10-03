# Welcome to nogForge

nogForge is KognogOS's package app: your installed programs, searching and installing new ones, and updates, in plain words. It works with **nog**, KognogOS's package manager, and shows what nog decides: which tier a package is in, when an update is ready, and what must stay together. nogForge never decides those itself.

This is a **beta**. It has the Dashboard, Home, Search, Update (with your choices), Tiers and History. Settings come in the next beta, and Flatpak and Snap installs after that.

## The screens

- **1 Dashboard**: updates waiting, your packages, what nog did lately, the space old downloads take.
- **2 Home**: what's installed on this computer.
- **3 Search**: find and install something new.
- **4 Update**: nog's update plan: tick what goes in, promote what can't wait.
- **5 Tiers**: everything waiting, soonest first; change a package's tier.
- **6 History**: every install, removal and update nog ran.

## How a change happens

1. You pick it (Install or Remove on a row) and nogForge shows a review.
2. nogForge hands the terminal to nog, which runs it there: you see pacman's own list of what comes with it (or goes with it), and it asks before anything changes.
3. Your password is asked by the system's own window. nogForge never sees it.
4. Press Enter, and you're back in nogForge, with everything read again.
