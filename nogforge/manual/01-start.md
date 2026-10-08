# Welcome to nogForge

nogForge is KognogOS's package app: your installed programs, searching and installing new ones, and updates, in plain words. It works with **nog**, KognogOS's package manager, and shows what nog decides: which tier a package is in, when an update is ready, and what must stay together. nogForge never decides those itself.

It has the Dashboard, In-System, Install, Update (with your choices) and History. Settings come next, and Flatpak and Snap installs after that.

## The screens

- **1 Dashboard**: updates waiting, your packages, what nog did lately, the space old downloads take.
- **2 In-System**: what's on this computer.
- **3 Install**: find and install something new.
- **4 Update**: nog's update plan: untick what waits, promote what can't.
- **History ▸ 5 Activity / 6 nog Logs**: everything nog ran, in plain words, and nog's own logs.

## How a change happens

1. You pick it (the Install or Uninstall button on a row) and nogForge shows a review.
2. nog runs it in a window inside nogForge: its steps and a progress bar. When nog or pacman asks something, nog's own screen opens with pacman's list of what comes with it (or goes with it); answer with **Yes (y)** or **No (n)**. **F12** shows or folds nog's screen anytime.
3. Your password is asked in nogForge's own box. It goes to sudo and nowhere else.
4. When nog is done, **Close** (Enter), and everything is read again.
