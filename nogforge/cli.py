"""Starting nogForge from the terminal (v0.1.0).

``--version`` and ``--help`` answer and exit. Otherwise the app runs, and when
it closes the terminal gets the record of the session: the banner, what was
installed or removed, where it was logged, and a thank-you — the same start
and end as every Forge app and nog.
"""

from __future__ import annotations

import datetime as dt
import os
import sys

from . import __version__

USAGE = f"""nogForge {__version__} (beta) — packages, the KognogOS way

Usage:
  nogforge             open nogForge
  nogforge --version   print the version
  nogforge --help      print this

Inside: 1-5 change screens, u reviews updates, r searches, Enter on a row does
its option (install or remove), F1 explains, ? lists every key.
nogForge shows what nog decides; it needs nog 1.6.0 or newer.
"""

LOG_DIR = "~/.local/share/nogforge/logs"


def summary(app) -> tuple[str, list[str], str]:
    done = [c for c in app.changes if c[2] == 0]
    stopped = [c for c in app.changes if c[2] != 0]
    word = {"install": "Installed", "remove": "Removed", "update": "Updated", "clean": "Cleaned up"}
    lines = [f"{word[a]} {n}".strip() + "." for a, n, _c in done]
    lines += [f"{a.capitalize()} {n}: nog stopped (status {c}).".replace("  ", " ") for a, n, c in stopped]
    if not app.changes:
        return "nogForge · Nothing changed", ["Looked around; nothing was installed or removed."], "ok"
    return f"nogForge · {len(done)} change{'s' if len(done) != 1 else ''} made", lines, "ok" if not stopped else "warn"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] in ("--version", "-V", "version"):
        print(f"nogForge {__version__}")
        return 0
    if args and args[0] in ("--help", "-h", "help"):
        print(USAGE)
        return 0
    if args:
        print(f"nogforge: unknown option {args[0]!r}\n\n{USAGE}", file=sys.stderr)
        return 2

    from forgekit import closing_notice, runs_log_row, session_banner
    from .app import NogForgeApp

    app = NogForgeApp()
    app.run()
    ended = dt.datetime.now()
    heading, lines, level = summary(app)
    user = os.environ.get("USER") or os.environ.get("LOGNAME") or "unknown"
    logs = []
    try:
        logs.append(runs_log_row(LOG_DIR, "nogforge",
                                 [f"{app.started:%m/%d/%Y}", f"{app.started:%I:%M %p}", user, "nogforge",
                                  heading.split("·", 1)[-1].strip(), " ".join(lines)]))
    except OSError as e:
        lines = lines + [f"(This run could not be logged: {e})"]
    print(session_banner("nogForge", __version__, "nogforge", app.started, ended, user))
    print(closing_notice(heading, lines, level=level, logs=logs, thanks="Thank you for using nogForge!"))
    return 0
