#!/usr/bin/env bash
# The commits for the night of 2026-10-16 → 17, made in the morning.
#
# Everything was built, tested and benched while Javier slept, but every commit
# here is GPG-signed and the signing key was locked (gpg-agent had dropped the
# passphrase), so nothing could be committed overnight. This script makes the
# commits in order, one logical change each; the first one asks for the GPG
# passphrase once (the pinentry window), the rest reuse it.
#
#   bash ~/Programs/nogforge/scripts/commit-overnight.sh
#
# It stops at the first problem. It does NOT push, tag or release: that is the
# morning's review (scripts/release-150.sh afterwards). Logs to logs/.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
log="logs/commit-overnight-$(date +%Y%m%d-%H%M%S).log"
ln -sfn "$(basename "$log")" logs/commit-overnight-latest.log
exec > >(tee "$log") 2>&1
trailer="Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"

echo "== 1/5 the two features"
git add nogforge.desktop nogforge/ui/run.py nogforge/app.py tests/test_nogforge.py \
        README.md nogforge.1 nogforge/manual/01-start.md docs/PACKAGING.md CLAUDE.md
git commit -q -F - <<MSG
1.5.0: the launcher entry (#16) and the fold arrow on nog's run window (#23)

Two backlog items done the night of 2026-10-16 (Javier: "all of nogForge's
issues need to be resolved too").

- #16: nogforge.desktop at the repository root, installed by the recipe as
  /usr/share/applications/nogforge.desktop (Terminal=true; one main category,
  Settings, so a menu shows it once). desktop-file-validate runs in the tests
  and in the recipe's check(). hypeForge's own copy (a floating window)
  replaces it by name, so nothing shows twice.
- #23: forgekit's RunWindow already shows a run as nog's steps and a progress
  bar with nog's screen folded, opens it on a question (Yes/No bar, the table
  in view) or a failure, and folds it on F12. nogForge now subclasses it
  (ui/run.py) only to put Javier's arrow on the toggle button: "▾ nog's
  Screen (F12)" while folded, "▴ Fold nog's Screen (F12)" while open (v / ^ on
  a text console). hand_off goes through run_in_app → NogRunWindow;
  before_quit's check still holds.
- Tests 61 → 64 (DesktopEntry; FoldArrow: the fold and the window a change
  opens), 0 warnings. README (What's in 1.5, changelog, Installation), man
  page (FILES), manual (Starting nogForge, the arrow), PACKAGING
  (checkdepends desktop-file-utils, the files installed), CLAUDE.md.

$trailer
MSG

echo "== 2/5 the three findings"
git add nogforge/records.py nogforge/ui/screens.py tests/test_nogforge.py nogforge/manual/07-history.md
git commit -q -F - <<MSG
fix: F-17 F-18 F-19 — what the scripted bench found in the KognogOS VM (#29 #30 #31)

- F-17 (#29): the Repositories window listed Flatpak and Snap only when a
  row from them existed; a computer with flatpak installed and no app yet
  showed none. A source nog's plan checked (sources.flatpak == "checked")
  is listed, rows or no rows: nog decides.
- F-18 (#30): nog's runs line keeps minutes only, so two runs in one minute
  tied and the older came first in nog Logs. The line nog wrote last wins.
- F-19 (#31): every run's caption said "no other log for this run" while
  Enter opened the run's own log. The caption says what is there (its own
  log; N more logs; or nothing). The runs list is read once per refresh.
- Tests 64 → 67 (OvernightBenchFindings), 0 warnings. The manual's History page
  still said "5, then a" from before Maintenance took the 5: now 6.

$trailer
MSG

echo "== 3/5 the screenshots"
git add docs/screenshots/
git commit -q -F - <<MSG
docs: screenshots for 1.5.0 — Flatpak and snap rows, the Maintenance page, the fold arrow

generate.py's stand-in answers like nog 2.0.0 now (a Flatpak app and two snaps
among the rows, a Flatpak result, a sample maintenance report); a new
10-maintenance.svg with two categories ticked; 08-run.svg shows the arrow
button; the menu keys follow 1.5.0 (5 Maintenance, 6 History). The README's
Screenshots section gained Maintenance.

$trailer
MSG

echo "== 4/5 the bench"
git add scripts/bench-150.py scripts/make-rc-package.sh scripts/vm-prep-150.sh scripts/commit-overnight.sh testing/
[ -f scripts/release-150.sh ] && git add scripts/release-150.sh
git commit -q -F - <<MSG
test: the 1.5.0 bench run by a script — this desktop read-only, the KognogOS VM with real changes

Javier, 2026-10-16 23:30: "Work without needing me, everything local, use
the VM as needed." scripts/bench-150.py walks the matrix's §2 the way a
person would (the same keys and buttons) on the real app against the real
nog, headless, and keeps an SVG of every step plus a results table.

- This desktop, read-only (11 steps): all PASS (testing/bench-150/desktop/).
- The KognogOS VM (kognog-hypeforge, snapshot before-nogforge-150), with
  changes: nog install of rc2 (2.1), the Flatpak install and uninstall
  through nogForge's window (2.6, 2.7), the clean-up of two categories
  (2.9), and the #27 check — an uninstall whose leftover another app still
  uses: nog's Keep question comes up in the window and Yes keeps it. Results
  in testing/bench-150/vm/ and the Test Results file.
- make-rc-package.sh --worktree builds the package from the working tree
  (the commits were waiting for the signing key).

$trailer
MSG

echo "== 5/5 the list"
git add TODO.md
git commit -q -F - <<MSG
todo: the overnight bench of 1.5.0 (2026-10-16 → 17); the morning's review, release and AUR

$trailer
MSG

echo
git log --oneline -6
echo "OK: five commits made, nothing pushed. Next: Javier's review, then scripts/release-150.sh"
