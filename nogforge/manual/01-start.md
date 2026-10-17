# Welcome to nogForge

nogForge is KognogOS's package app: your installed programs, searching and installing new ones, and updates, in plain words. It works with **nog**, KognogOS's package manager, and shows what nog decides: which tier a package is in, when an update is ready, and what must stay together. nogForge never decides those itself.

It has the Dashboard, In-System, Install, Update (with your choices), Maintenance and History, for every source: the repositories, the AUR, Flatpak and Snap. Settings come next.

## The screens

- **1 Dashboard**: updates waiting, your packages, what nog did lately, the space old downloads take.
- **2 In-System**: what's on this computer.
- **3 Install**: find and install something new.
- **4 Update**: nog's update plan: untick what waits, promote what can't.
- **5 Maintenance**: what each source has left behind; tick what goes, and nog cleans it up.
- **6 History**: opens its menu: **Activity** (everything nog ran, in plain words) or **nog Logs** (nog's own logs).
- **7 Help**: opens its menu: this manual, the list of keys, the license, About. Each shows as a page here, Help lit; Esc goes back. **F1** opens the manual at the page for where you are.

Every name in the menu bar has a number (1 to 7, left to right) and an underlined letter: **Ctrl** + that letter goes there too, even while you're typing in a search box (Ctrl+U for Update, Ctrl+M for Maintenance, Ctrl+S for History). The letter is the first letter of its name, or the next free letter of the name when that one is taken; Help is always H and Quit Q. History and Help open their menus, and their name is lit while the menu is open; pick from it with the underlined letter or Enter, and press the number again to close it.

## Starting nogForge

Type `nogforge` in a terminal, or pick **nogForge** in your app menu (the package puts it there; it opens in your terminal). Inside hypeForge, it's a page of Settings too.

## Closing nogForge

**q**, **Ctrl+Q** or **Quit** in the menu bar. Inside **hypeForge Settings**, nogForge is one of Settings' pages: there's no Quit, and q and Ctrl+Q do nothing. You close it from Settings, which asks nogForge first. Either way, nogForge never closes while nog is working: stopping nog halfway through an update could break the system, so it says *Not yet* until nog is done.

## How a change happens

1. You pick it (the Install or Uninstall button on a row) and nogForge shows a review.
2. nog runs it in a window inside nogForge: its steps and a progress bar. When nog or pacman asks something, nog's own screen opens with pacman's list of what comes with it (or goes with it); answer with **Yes (y)** or **No (n)**. **F12** shows or folds nog's screen anytime, and so does the window's arrow button: **▾ nog's Screen** opens it, **▴ Fold nog's Screen** folds it.
3. Your password is asked in nogForge's own box. It goes to sudo and nowhere else.
4. When nog is done, **Close** (Enter), and everything is read again.
