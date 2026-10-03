# Update

nog's update plan, and your choices:

- **Ready now**: updates whose wait is over, each ticked **[x]**, with nog's note (*hold just expired*, *19 days past window*).
- **Held**: still waiting, with **Ready on**, the day the wait ends, and a **↑ Promote** button.

## Keeping one back

**Space** (or a click on its box) unticks a ready row: it says **kept back by you**. nog then works out what has to stay back with it, because some packages only work at matching versions, and those rows untick themselves with the reason (*must stay back with ldb*). Ticking one of those ticks the one it waits for again. Updating some packages but not their partners can break a system; nog never lets that happen.

## Promote

**↑ Promote** on a held row makes it **ready now**: it moves up to Ready, ticked, saying *promoted by you*, and goes in with the others when you update. Nothing installs at that moment. If it needs a partner to go with it (a kernel and its headers), nog promotes the partner too: *promoted with linux-zen*. Untick a promoted one and it goes back to waiting.

The wait exists to catch a version that turns out to be broken, so promote what you need now, not everything.

## Updating

**Update the Ticked Ones (u)** hands the run to nog in the terminal, with what you kept back and what you promoted: nog shows its full plan and asks before anything changes, and the password comes through the system's window. **Check for Updates (c)** asks nog again and starts your choices fresh.

## What changed

When nog is done, a window says what really went in (nogForge compares the versions before and after), what you kept back, and what didn't go in. After a new kernel it offers **Restart Now (r)** (in red) or **Later (l)**: the new kernel only runs after a restart, and nothing forces you to stop working. **Later** is the one already selected, so a stray Enter never restarts.
