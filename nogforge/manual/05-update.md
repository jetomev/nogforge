# Update

nog's update plan, and your choices:

- **Ready now**: updates whose wait is over, each ticked **[x]**, with nog's note (*hold just expired*, *19 days past window*).
- **Held**: still waiting, with **Ready on**, the day the wait ends, and **↑ Promote** on the right.

## Keeping one back

Move to a row and press **Space** to untick it: it says **kept back by you**. nog then works out what has to stay back with it, because some packages only work at matching versions, and those rows untick themselves with the reason (*must stay back with ldb*). Ticking one of those ticks the one it waits for again. Updating some packages but not their partners can break a system; nog never lets that happen.

**Update the Ticked Ones (u)** (or **u**) hands the run to nog in the terminal, with what you kept back: nog shows its full plan and asks before anything changes, and the password comes through the system's window. **Check for Updates (c)** asks nog again and starts your choices fresh.

## Promote

**Enter** on a held row (**↑ Promote**) installs that one now, before its wait ends, after a review. The wait exists to catch a version that turns out to be broken, so promote what you need now, not everything.

## What changed

When nog is done, a window says what really went in (nogForge compares the versions before and after), what you kept back, and what didn't go in. After a new kernel it offers **Restart Now (r)** (in red) or **Later (l)**: the new kernel only runs after a restart, and nothing forces you to stop working. **Later** is the one already selected, so a stray Enter never restarts.
