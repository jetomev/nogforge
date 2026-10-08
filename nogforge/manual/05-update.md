# Update

nog's update plan, and your choices:

- **Ready now**: updates whose wait is over, each ticked **[x]**, with nog's note (*hold just expired*, *19 days past window*).
- **Held**: still waiting, with **Ready on**, the day the wait ends, and a **↑ Promote** button.

## One by itself, or all at once

- **Find** (or **/**): type part of a name or of what it does, and both lists narrow as you type. **Esc** goes back to the list.
- **⬆ Update** on a ready row updates **that one package by itself**: nog gets its name alone, works out what has to move with it, and asks before anything changes. The quickest way to update one thing.
- **Tick All (t)** and **Untick All (n)** tick or untick every ready row in one go. Untick all, then tick the two you want, is the quick way to a small update.

## Keeping one back

**Space** (or a click on its box) unticks a ready row: it says **kept back by you**, at once. A yellow **nog is working on it…** sign appears beside the update button, which waits in cream until nog answers; quick clicks are sent to nog together. nog then works out what has to stay back with it, because some packages only work at matching versions, and those rows untick themselves with the reason (*must stay back with ldb*). Ticking one of those ticks the one it waits for again. Updating some packages but not their partners can break a system; nog never lets that happen.

## Promote

**↑ Promote** on a held row makes it **ready now**: it moves up to Ready, ticked, saying *promoted by you*, and goes in with the others when you update. Nothing installs at that moment. If it needs a partner to go with it (a kernel and its headers), nog promotes the partner too: *promoted with linux-zen*. Untick a promoted one and it goes back to waiting.

The wait exists to catch a version that turns out to be broken, so promote what you need now, not everything.

## Updating

**Update the Ticked Ones (u)** hands nog exactly the ticked ones, by name, in a window inside nogForge: nog shows only those and asks before anything changes, and the password is asked in nogForge's own box. pacman then lists each package it skips (the held ones); nog says so first. A held package goes in only when promoted. **Check for Updates (k)** asks nog again and starts your choices fresh.

## What changed

When nog is done, a window says what really went in (nogForge compares the versions before and after), what you kept back, and what didn't go in. After a new kernel it offers **Restart Now (r)** (in red) or **Later (l)**: the new kernel only runs after a restart, and nothing forces you to stop working. **Later** is the one already selected, so a stray Enter never restarts.
