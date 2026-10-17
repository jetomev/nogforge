"""nog's run window, with the fold arrow (1.5.0, #23).

forgekit's ``RunWindow`` already shows a run the way Javier asked on 7 October
2026: nog's steps and a progress bar, nog's own screen folded away until nog or
pacman asks something (then the question gets a bar with Yes/No and the table
comes into view), until something fails, or until F12. What was missing was
the arrow he described: a button that says which way the fold goes. Folded,
the button points down (▾, open it); open, it points up (▴, fold it). The
words say the same, so a text console without the triangles reads it too.
"""

from __future__ import annotations

from textual.css.query import NoMatches
from textual.widgets import Button

from forgekit import RunWindow, glyph
from forgekit.console import console_mode

UP = "^" if console_mode() else "▴"       # forgekit's table has "down" (▾ / v); up is its mirror


def fold_label(open_: bool, tool: str) -> str:
    """The toggle button's words: where the fold goes next, and what it folds."""
    return f"{UP} Fold {tool}'s Screen (F12)" if open_ else f"{glyph('down')} {tool}'s Screen (F12)"


class NogRunWindow(RunWindow):
    """forgekit's run window; the toggle button carries the arrow."""

    def _show_screen(self, on: bool) -> None:
        super()._show_screen(on)
        try:
            btn = self.query_one("#run-toggle", Button)
        except NoMatches:
            return
        btn.label = fold_label(on, self._tool)
        btn.refresh(layout=True)              # the longer label needs the button re-measured, or it is cut short
