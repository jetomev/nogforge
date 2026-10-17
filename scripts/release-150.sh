#!/usr/bin/env bash
# nogForge 1.5.0 — the release, up to the AUR push (which is Javier's gate).
#
# Run AFTER Javier's morning review of the overnight bench and after
# scripts/commit-overnight.sh made the commits. Needs the GPG passphrase once
# (tag + asset signatures). Order, as release.md says: push main + the signed
# tag → GitHub Release with signed assets → AUR recipe (updpkgsums, .SRCINFO)
# → makepkg in ~/Programs/aur-nogforge → STOP: Javier installs the built
# package and tests; only on his pass does the AUR push happen (by hand, the
# last lines of this file say how).
#
#   bash ~/Programs/nogforge/scripts/release-150.sh
#
# Logs to logs/release-150-<time>.log (+ -latest). Stops at the first problem.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
log="logs/release-150-$(date +%Y%m%d-%H%M%S).log"
ln -sfn "$(basename "$log")" logs/release-150-latest.log
exec > >(tee "$log") 2>&1
VER=1.5.0
TAG="v$VER"
AUR=~/Programs/aur-nogforge
WORK="$(mktemp -d)"
trap 'rm -rf --one-file-system "$WORK"' EXIT

echo "== pre-flight"
[ -z "$(git status --porcelain)" ] || { echo "the working tree isn't clean: commit first (scripts/commit-overnight.sh)"; exit 1; }
grep -q "__version__ = \"$VER\"" nogforge/__init__.py || { echo "nogforge/__init__.py isn't $VER"; exit 1; }
grep -q "Version-$VER-" README.md || { echo "README badge isn't $VER"; exit 1; }
grep -q "nogForge $VER\|nogforge $VER\|\"$VER\"" nogforge.1 || echo "  note: check the man page's version line by eye"
grep -q "^pkgver=$VER$" "$AUR/PKGBUILD" || { echo "$AUR/PKGBUILD isn't pkgver=$VER"; exit 1; }
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null && { echo "tag $TAG exists already"; exit 1; }
PYTHONDONTWRITEBYTECODE=1 python -W default -m unittest discover tests 2>&1 | tail -3
desktop-file-validate nogforge.desktop
man --warnings -l nogforge.1 >/dev/null

echo; echo "== tag (signed) and push"
git tag -s "$TAG" -m "nogForge $VER — every source, Maintenance, the launcher entry and the fold arrow"
git push origin main
git push origin "$TAG"

echo; echo "== the assets: a tarball of the tag, signed, with a signed SHA256SUMS"
git archive --prefix="nogforge-$VER/" -o "$WORK/nogforge-$VER.tar.gz" "$TAG"
( cd "$WORK"
  gpg --armor --detach-sign "nogforge-$VER.tar.gz"
  sha256sum "nogforge-$VER.tar.gz" > "nogforge-$VER.SHA256SUMS"
  gpg --armor --detach-sign "nogforge-$VER.SHA256SUMS"
  gpg --verify "nogforge-$VER.tar.gz.asc" "nogforge-$VER.tar.gz" 2>&1 | grep -i 'good signature' )

echo; echo "== GitHub Release (notes = the README's 1.5.0 changelog entry, links absolute)"
python3 - README.md "$WORK/notes.md" <<'PY'
import re, sys
readme, out = sys.argv[1:]
s = open(readme).read()
m = re.search(r"^### v1\.5\.0 — .*?\n(.*?)(?=^### v|\Z)", s, flags=re.M | re.S)
body = m.group(1).strip()
body = re.sub(r"\]\((?!https?://)([^)]+)\)", r"](https://github.com/jetomev/nogforge/blob/v1.5.0/\1)", body)
head = ("**Packages, the KognogOS way, for every source.** On [nog 2.0.0](https://github.com/jetomev/nog/releases/tag/v2.0.0): "
        "Flatpak apps and snaps are rows like any package, and the new Maintenance page cleans up what each source has left behind. "
        "Plus the launcher entry (#16) and the fold arrow on nog's run window (#23). Benched on this desktop and in the KognogOS VM "
        "the night of 16 October; Javier's review the morning after.\n\n")
tail = ("\n\n**Needs:** nog ≥ 2.0.0, python-forgekit ≥ 0.10.0. **AUR:** `nog install nogforge`.\n\n"
        "*A human + AI collaboration: Javier (jetomev) and Claude (Anthropic).*\n")
open(out, "w").write(head + body + tail)
PY
gh release create "$TAG" --title "nogForge $TAG — every source, Maintenance, the launcher entry and the fold arrow" \
   --notes-file "$WORK/notes.md" --latest \
   "$WORK/nogforge-$VER.tar.gz" "$WORK/nogforge-$VER.tar.gz.asc" "$WORK/nogforge-$VER.SHA256SUMS" "$WORK/nogforge-$VER.SHA256SUMS.asc"
gh release view "$TAG" --json assets --jq '.assets[].name'

echo; echo "== the AUR recipe: checksum of the published tarball, .SRCINFO, a local build"
cd "$AUR"
updpkgsums
makepkg --printsrcinfo > .SRCINFO
grep -n 'pkgver\|pkgrel\|sha256sums\|depends' .SRCINFO | head -12
# the downloaded tarball must be byte-identical to what the tag holds
cmp "nogforge-$VER.tar.gz" "$WORK/nogforge-$VER.tar.gz" && echo "the download is byte-identical to the tag's archive"
gpg --verify "nogforge-$VER.tar.gz.asc" "nogforge-$VER.tar.gz" 2>&1 | grep -i 'good signature'
makepkg -f 2>&1 | grep -vE 'Executing <Task|^\s*$' | tail -12
ls -la "$AUR/nogforge-$VER-1-any.pkg.tar.zst"

echo
echo "OK: GitHub is live; the package is built. STOP HERE."
echo "Javier: nog install $AUR/nogforge-$VER-1-any.pkg.tar.zst  → his look at 1.5.0 on this desktop."
echo "Only on his pass:  cd $AUR && git add PKGBUILD .SRCINFO && git commit -m \"$VER — every source, Maintenance, launcher entry, fold arrow (#16 #23 #27 #28)\" && SSH_AUTH_SOCK=/tmp/aur-agent.sock git push"
