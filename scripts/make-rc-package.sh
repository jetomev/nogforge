#!/usr/bin/env bash
# Build a release-candidate package of nogForge alone, from the LAST COMMIT,
# with the AUR recipe (~/Programs/aur-nogforge/PKGBUILD) changed in three
# places only: the source is a tarball of HEAD instead of the signed release
# asset (which doesn't exist yet), the version gets an "rc" suffix (1.5.0rc1
# sorts before 1.5.0, so the real release upgrades over it), and the version
# check accepts the rc. check() runs the tests exactly as on the AUR, with a
# terminal attached (util-linux script), the way yay builds.
# make-rc-packages.sh builds the whole "nog inside the app" set; this is the
# one-app version (1.5.0, 2026-10-15).
#
#   scripts/make-rc-package.sh [rc-number]      (default 1)
#
# The package lands in dist-rc/. Logs to logs/make-rc-package-<time>.log.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
log="logs/make-rc-package-$(date +%Y%m%d-%H%M%S).log"
ln -sfn "$(basename "$log")" logs/make-rc-package-latest.log
exec > >(tee "$log") 2>&1
rc="${1:-1}"
OUT="$PWD/dist-rc"
WORK="$(mktemp -d)"
trap 'rm -rf --one-file-system "$WORK"' EXIT
mkdir -p "$OUT"
ver="$(sed -n 's/^__version__ = "\([0-9.]*\).*/\1/p' nogforge/__init__.py)rc$rc"
echo "nogforge $ver from $(git log --format='%h %s' -1)"
[ -z "$(git status --porcelain --untracked-files=no)" ] || echo "  NOTE: uncommitted changes; the package is built from the last commit"
python3 - ~/Programs/aur-nogforge/PKGBUILD "$WORK/PKGBUILD" "$ver" <<'PY'
import re, sys
src, out, ver = sys.argv[1:]
s = open(src).read()
s = re.sub(r"^pkgver=.*$", f"pkgver={ver}", s, flags=re.M)
s = re.sub(r"^pkgrel=.*$", "pkgrel=1", s, flags=re.M)
s = re.sub(r"^source=\(.*?\)$", f'source=("nogforge-{ver}.tar.gz")', s, flags=re.M | re.S)
s = re.sub(r"^sha256sums=\(.*?\)$", "sha256sums=('SKIP')   # local test build: not signed", s, flags=re.M | re.S)
s = re.sub(r"^validpgpkeys=\(.*?\)$", "", s, flags=re.M | re.S)
s = s.replace("assert __version__ == '${pkgver}', __version__",
              "assert __version__.split('-')[0] == '${pkgver}'.split('rc')[0], __version__")
open(out, "w").write(s)
PY
git archive --prefix="nogforge-$ver/" -o "$WORK/nogforge-$ver.tar.gz" HEAD
(cd "$WORK" && script -qec "PKGDEST='$OUT' makepkg -f --nodeps --noconfirm" /dev/null </dev/null | grep -vE '^\s+(Compiling|Downloaded|Downloading)' )
ls -la "$OUT"/nogforge-"$ver"-*.pkg.tar.zst
echo "OK: built nogforge $ver into dist-rc/"
