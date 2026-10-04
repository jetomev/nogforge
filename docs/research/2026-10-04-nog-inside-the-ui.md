# Keeping nog's work inside the UI — research report (2026-10-04)

Question: nogForge leaves the UI (`App.suspend()`) to show nog's raw terminal run, and asks
for passwords through a desktop window. Javier wants the work and the password to stay inside
the TUI, on the desktop *and* on a plain text console (TTY). grubForge has the same password
question. What is feasible, complete, and not half-baked?

## 1. What is there today (read from the code)

| Piece | How it works now | Source |
|---|---|---|
| nogForge change | `with self.suspend(): subprocess.run(nog …)`, then `input("Press Enter to go back")` | `~/Programs/nogforge/nogforge/app.py:563` (`hand_off`), `:639` (`run_in_terminal`) |
| nogForge password | if `DISPLAY`/`WAYLAND_DISPLAY` and a graphical askpass exists (`/usr/bin/ksshaskpass` here), sets `NOG_ASKPASS=1` + `SUDO_ASKPASS=<window>`; otherwise sudo asks in the raw terminal | `nogforge/nog.py:103-123` |
| nog privilege | nog stays unprivileged and calls `sudo` many times per run: pacman, AUR helper (`--sudoflags -A`), `sudo snap`, `sudo tee`, `sudo rm` | `src/machine.rs:112-128`, `src/snap.rs`, `src/sources.rs`, `src/cache.rs` |
| nog terminal handling | pacman's stderr goes straight to the terminal for steps that ask questions (relaying raced pacman's table, F-8); runs are recorded by re-running inside util-linux `script` | `src/handoff.rs` header + `run_on_screen`, `src/record.rs` |
| nog and libalpm | nog does **not** link libalpm; it reads the databases itself (`local_db.rs`, `sync_db.rs`) and hands the transaction to pacman. README: "nog is a wrapper around pacman, not a replacement." | `Cargo.toml`, `README.md:35` |
| grubForge privilege | polkit. Root helper `/usr/lib/grubforge/grubforge-helper` (fixed verbs, stdlib only), policy `org.kognogos.grubforge.manage` with `allow_active=auth_admin_keep`, `allow_any=no`. Called as `pkexec --disable-internal-agent <helper> <verb>` | `grubforge/privilege.py`, `polkit/org.kognogos.grubforge.policy` |
| grubForge on a TTY | `--disable-internal-agent` stops pkexec printing a prompt under Textual. With no desktop agent, pkexec exits 127 and grubForge says "this session has no authentication agent … run grubForge with sudo instead". **So today grubForge cannot save on a TTY without being started with sudo.** Over SSH it is worse: `allow_any=no` refuses even with an agent. | `privilege.py:144-149, 190-212` |

So the password window Javier dislikes is a choice in both apps, not a requirement: grubForge
gets it from the desktop polkit agent, nogForge from ksshaskpass.

## 2. Embedded terminal inside Textual

Commands run and results:
- `python -c "import textual; print(textual.__version__)"` → **8.2.8**. Textual has no terminal widget of its own (no pty/pyte code in `site-packages/textual/`).
- `pacman -Si python-pyte` → **extra, 0.8.2-5**, already installed. PyPI: 0.8.2, released 2023-11-12; before that 0.8.1 (2022). Small, stable, slow-moving.
- `pacman -Ss python-ptyprocess python-pexpect` → both in extra (not needed; stdlib `pty` is enough).
- `textual-terminal` (PyPI) → 0.3.0, last release **2023-01-29**, built for Textual 0.x; "simple key handling". Not packaged on Arch. **Treat as a reference, not a dependency.**
- Toad (Will McGugan, the author of Textual; 2025) embeds "a fully working shell with full-color output, interactive commands" inside a Textual app. **AGPL-3.0**. Proof that the approach works on Textual at production quality; code could be studied (AGPL can be combined with GPL-3 under GPLv3 §13, but writing our own ~600-line widget is cleaner).

Prototype I ran (`ptytest.py` in this folder): stdlib `pty.fork()` + `TIOCSWINSZ` + `pyte.ByteStream`,
child prints a coloured `\r` progress line, then asks `:: Proceed with installation? [Y/n]` on stderr and reads.
Result: progress collapsed correctly to `downloading 100%`, colour/bold kept (`fg=blue, bold=True`),
the question was detected on the virtual screen and answered by writing `y\r` to the pty, child saw
`answer=y`, and `tput cols` reported **60** (the size we set). The mechanics are sound.

pyte probe (grep of `pyte/screens.py` + feed test): **no alternate-screen (`?1049h`) support, no bracketed
paste, no mouse modes.** Feeding `\e[?1049h\e[2J` simply cleared the main screen. Consequence: a full-screen
program inside the pane (vim/nano for yay's PKGBUILD edit menu, `less` for the diff menu) draws fine, but
when it exits the previous output is gone instead of restored. Fix: subclass `pyte.Screen` to keep a
second buffer on `?1049h/l` (~50 lines) — known, small, testable.

What the widget must do (all verified possible, none exotic):
- render pyte's buffer to Textual `Strip`s (colour, bold, reverse, cursor);
- forward keys as bytes (Textual key → VT sequence table: arrows, Enter, Backspace, Tab, F-keys, Ctrl-letters). Ctrl+C must go to the child; the app needs one reserved key to leave the pane;
- resize: `TIOCSWINSZ` + `screen.resize()` on `on_resize`;
- cap scrollback (AUR builds can be megabytes) — `pyte.HistoryScreen` or keep a byte tail like `handoff.rs` does;
- read the pty in a worker thread / `loop.add_reader`, so the UI stays live.

What breaks or changes:
- **sudo's cached password.** sudo's default `timestamp_type=tty` keys the cache to the terminal. Each run in a fresh pty is a new terminal, so the user is asked once per change instead of once per 5 minutes. Within one nog run (several sudo calls) the cache works, because they share the pty. Acceptable, arguably safer.
- nog's `script` recording still works (it only needs stdin to be a terminal; the pty is one).
- pyte is unmaintained-ish (last release 2023) but in Arch `extra` and tiny. Risk is low; worst case vendor it.

## 3. Structured progress without a raw terminal

libalpm offers everything a native UI needs:
- Rust `alpm` crate **5.0.2 (2026-01-08)**: `set_log_cb`, `set_dl_cb`, `set_event_cb`, `set_progress_cb`, `set_question_cb`, `set_fetch_cb` ([docs.rs](https://docs.rs/alpm/latest/alpm/struct.Alpm.html)).
- Python `pyalpm` **0.12.0** in extra: the same callbacks (`dlcb`, `eventcb`, `questioncb`, `progresscb`, `logcb`) (from pyalpm's API; not exercised here — pyalpm is not installed).
- Questions arrive as typed events: replace package, conflict, remove corrupted package, import PGP key, choose provider. Hooks (mkinitcpio etc.) and `.pacnew` handling are inside libalpm, so they still happen; scriptlet output arrives through the log/event callbacks.

How others do it:
- **Pamac**: libalpm in Vala; privileged work in a D-Bus system service checked by **polkit**; AUR builds run as the user ([Pamac README](https://gitlab.manjaro.org/applications/pamac/blob/b8153ea47435633a8eb825f30c0976245b417a7e/README); Manjaro forum: needs polkitd *and* an authentication agent, [thread](https://forum.manjaro.org/t/pamac-auth-fails/44276)).
- **PackageKit**: same shape (packagekitd + polkit, alpm backend).
- **Octopi**: wraps pacman in a pty with its own sudo helper (from memory, not re-verified).

What nog would have to become: a privileged transaction service (root, polkit-started, like pamac-daemon) linking libalpm, plus an event stream (`nog update --events` as JSON lines) for the UI, and its own answers to every pacman question. Lost or to rebuild: pacman's exact behaviour and wording (nog's core promise), yay's AUR flow (clean/diff/edit menus, dependency solving, building as the user then installing), flatpak/snap stay external anyway. **Effort: months (3–6), and it turns nog from a wrapper into a replacement.**

Parsing pacman's text: pacman disables progress bars when stdout is not a terminal; text is translated (`LANG`) and unversioned. Fragile as the *only* source of truth. Safe as a *decoration* on top of a real terminal (if the parser misses a line, the raw text is still there).

A cheap middle ground that is not fragile: nog already orchestrates the steps itself (sync, pacman, AUR, flatpak, snap, holds, reboot check). It can announce those on a side channel, e.g. `NOG_EVENTS_FD=3` → JSON lines `{"step":"pacman","state":"start"}`, `{"step":"aur","pkg":"foo","state":"done","status":0,"reason":"…"}`. That is nog's own vocabulary (it already has `--json` in `machine.rs` and `reason` in `handoff.rs`), so it does not break when pacman's wording changes.

## 4. Password inside the TUI

| Method | How | Security | TTY | Verdict |
|---|---|---|---|---|
| `sudo -S` from a TUI field | password on sudo's stdin | stdin is also pacman's answer channel → conflicts | yes | **No** |
| **SUDO_ASKPASS bridge** | tiny `forgekit-askpass` program; sudo runs it; it connects to the running app over a unix socket in `$XDG_RUNTIME_DIR` (mode 0600, random token in env); app shows a masked password modal; askpass prints it to sudo | password passes through the app's memory and a user-only socket — same exposure as ksshaskpass today; never on disk or in argv | **yes** (needs no display) | **Yes, for nog/nogForge.** nog already supports it (`NOG_ASKPASS=1` → `sudo -A`, AUR `--sudoflags -A`); only the askpass program changes. |
| Detect "Password:" in the pty and pop a modal | lazygit's approach for git credentials | works, but pattern-matching prompts | yes | Fallback only |
| **In-process polkit agent** | PyGObject + `PolkitAgent-1.0` typelib (present: `/usr/lib/girepository-1.0/PolkitAgent-1.0.typelib`, `gi` 3.56.3); subclass `PolkitAgent.Listener`, register for grubForge's own PID; polkit's setuid `polkit-agent-helper-1` (socket-activated here: `polkit-agent-helper.socket`) checks the password | password typed in our modal, verified by polkit's helper; grubForge still never runs as root | yes on a local console (session is active); SSH still refused by `allow_any=no` unless the policy changes | **Yes, for grubForge.** Precedent: `pkttyagent --process PID` does exactly this as text, and systemctl uses it. Needs a GLib main loop in a thread. |
| `pkttyagent --process <pid>` in a small pty pane | reuse the terminal widget for polkit's own text prompt | polkit's own code | yes | Quick fallback for grubForge |
| Long-running privileged helper | start once via pkexec, talk over a pipe | one password per session, but a root process lives as long as the app | yes | Not needed; more risk |

Precedents: yay uses sudo (+ `--sudoloop`); archinstall simply requires root; Cockpit takes the password in its own UI and relays it to sudo for its privileged bridge (from memory). A plain TTY needs nothing graphical: an in-app modal works identically there and over SSH (for sudo).

Unverified: that pkexec uses its *parent* process as the polkit subject (from my knowledge of pkexec's source; if true, an agent registered for grubForge's PID answers grubForge's pkexec calls). Must be proven with a 30-line spike before committing.

## 5. Language

- Rust has more mature parts: `vt100` 0.16.2 (2025-07, alternate screen supported), `tui-term` 0.3.4 (2026-04), `portable-pty` 0.9.0, `ratatui` 0.30.2 (2026-06), `alpm` 5.0.2 — all from crates.io API today. Linking nog's code directly would remove the JSON hop.
- But nothing in options 1–2 is blocked by Python: pty is stdlib, pyte works (prototype), the alt-screen gap is ~50 lines, the askpass bridge and polkit agent are both available from Python.
- Cost of switching: forgekit is shared by grubForge, alacrittyForge, bitlaForge, nogForge (forgekit ~2,000 lines, nogForge ~1,150). Rewriting nogForge alone splits the suite's look and keys; rewriting all four is months.
- **Honest verdict: the language is not the limit.** Rust is a defensible long-term choice for a libalpm-native engine (option 4), not for these fixes.

## 6. Options

1. **forgekit terminal pane + in-app password (recommended first).** nog unchanged; nogForge opens a framed pane inside the UI running nog in a pty (pyte + alt-screen subclass); `SUDO_ASKPASS` bridge → masked modal. Effort ~3–4 weeks. TTY: yes, and over SSH. grubForge: shares the modal; its polkit side is option 3.
2. **Steps view on top of option 1.** nog adds `NOG_EVENTS_FD` JSON-lines step events (~1 week in nog, one phase); nogForge shows a checklist + progress bar, the pane collapsed; it opens by itself when a question appears (`[Y/n]`, `[y/N]`, `Enter a number`) or on failure. Effort +2 weeks. TTY: yes.
3. **grubForge in-process polkit agent.** PyGObject `PolkitAgent.Listener` registered for the app's PID; password modal in the TUI; polkit's helper checks it. Effort ~1–1.5 weeks incl. spike. TTY: yes (local console); SSH needs a policy decision.
4. **libalpm-native engine** (root service + polkit + event stream, Pamac-style). 3–6 months; nog stops being a wrapper; AUR flow rebuilt. Not now.
5. **Rust rewrite** (ratatui + tui-term + vt100 + nog as a library). Months, splits or rewrites the Forge Suite. Only together with 4, if ever.

## Sources
- [textual-terminal on PyPI](https://pypi.org/project/textual-terminal) · [repo](https://github.com/mitosch/textual-terminal)
- [pyte on PyPI](https://pypi.org/project/pyte/)
- [Toad](https://github.com/batrachianai/toad) · [Simon Willison on Toad](https://simonwillison.net/2025/Jul/23/announcing-toad/)
- [alpm crate callbacks](https://docs.rs/alpm/latest/alpm/struct.Alpm.html)
- [Pamac README](https://gitlab.manjaro.org/applications/pamac/blob/b8153ea47435633a8eb825f30c0976245b417a7e/README) · [Pamac auth / polkit agent thread](https://forum.manjaro.org/t/pamac-auth-fails/44276)
- crates.io API for vt100, tui-term, portable-pty, alpm, ratatui (queried 2026-10-04)
- Local: `pacman -Si python-pyte pyalpm polkit sudo`, `pkttyagent --help`, `ls /usr/lib/girepository-1.0`, `yay --help`, code paths cited above.
