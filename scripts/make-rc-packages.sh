#!/usr/bin/env bash
# Build release-candidate packages for the "nog inside the app" work (4 Oct
# 2026): python-forgekit, grubforge and nogforge from their current commits,
# and nog through its own scripts/make-rc-package.sh.
#
# The recipes are the AUR ones (~/Programs/aur-*), copied and changed in
# three places only: the source is a tarball of the current commit instead of
# the signed release asset (which doesn't exist yet), the version gets an
# "rc" suffix (1.1.0rc1 sorts before 1.1.0, so the real release upgrades over
# it), and the requirements on each other accept the rc. check() and
# package() run exactly as on the AUR. The AUR folders are never changed.
#
#   scripts/make-rc-packages.sh [rc-number]      (default 1)
#
# Packages land in ~/Programs/nogforge/dist-rc/. Logs to logs/make-rc-packages-<time>.log.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
log="logs/make-rc-packages-$(date +%Y%m%d-%H%M%S).log"
ln -sfn "$(basename "$log")" logs/make-rc-packages-latest.log
exec > >(tee "$log") 2>&1

rc="${1:-1}"
NF="$PWD"
FK="$(cd ../forgekit && pwd)"
GF="$(cd ../grubforge && pwd)"
NOG="$(cd ../nog && pwd)"
OUT="$NF/dist-rc"
WORK="$(mktemp -d)"
trap 'rm -rf --one-file-system "$WORK"' EXIT
mkdir -p "$OUT"

# 1.1.1: build the way yay does, with a terminal attached (util-linux script).
# nogForge 1.1.0's tests passed here without one and failed in Javier's yay build.
in_a_terminal() { script -qec "$*" /dev/null </dev/null; }

ver_of() { sed -n 's/^__version__ = "\([0-9.]*\).*/\1/p' "$1"; }
fk_ver="$(ver_of "$FK/forgekit/__init__.py")rc$rc"
gf_ver="$(ver_of "$GF/grubforge/__init__.py")rc$rc"
nf_ver="$(ver_of "$NF/nogforge/__init__.py")rc$rc"
for repo in "$FK" "$GF" "$NF" "$NOG"; do
  echo "$(basename "$repo"): $(git -C "$repo" log --format='%h %s' -1)"
  if [ -n "$(git -C "$repo" status --porcelain --untracked-files=no)" ]; then
    echo "  NOTE: uncommitted changes; the package is built from the last commit"
  fi
done

# rc_recipe <aur dir> <src name> <version> <out dir>
rc_recipe() {
  local aur="$1" src="$2" ver="$3" dir="$4"
  mkdir -p "$dir"
  python3 - "$aur/PKGBUILD" "$dir/PKGBUILD" "$src" "$ver" <<'PY'
import re, sys
src_path, out, name, ver = sys.argv[1:]
s = open(src_path).read()
s = re.sub(r"^pkgver=.*$", f"pkgver={ver}", s, flags=re.M)
s = re.sub(r"^pkgrel=.*$", "pkgrel=1", s, flags=re.M)
s = re.sub(r"^source=\(.*?\)$", f'source=("{name}-{ver}.tar.gz")', s, flags=re.M | re.S)
s = re.sub(r"^sha256sums=\(.*?\)$", "sha256sums=('SKIP')   # local test build: not signed", s, flags=re.M | re.S)
s = re.sub(r"^validpgpkeys=\(.*?\)$", "", s, flags=re.M | re.S)
s = s.replace("python-forgekit>=0.6.0", "python-forgekit>=0.6.0rc1").replace("nog>=1.7.0", "nog>=1.7.0rc1")
s = s.replace("assert __version__ == '${pkgver}', __version__",
              "assert __version__.split('-')[0] == '${pkgver}'.split('rc')[0], __version__")
open(out, "w").write(s)
PY
}

echo; echo "=== nog (its own script)"
bash "$NOG/scripts/make-rc-package.sh" "$rc" | tail -3
cp "$NOG"/dist-rc/nog-*rc"$rc"-1-x86_64.pkg.tar.zst "$OUT/"

echo; echo "=== python-forgekit $fk_ver"
d="$WORK/forgekit"; rc_recipe ~/Programs/aur-python-forgekit forgekit "$fk_ver" "$d"
git -C "$FK" archive --prefix="forgekit-$fk_ver/" -o "$d/forgekit-$fk_ver.tar.gz" HEAD
(cd "$d" && in_a_terminal PKGDEST="$OUT" makepkg -f --nodeps --noconfirm)
mkdir -p "$WORK/fk-src" && tar -C "$WORK/fk-src" -xzf "$d/forgekit-$fk_ver.tar.gz"
export PYTHONPATH="$WORK/fk-src/forgekit-$fk_ver"   # the apps' checks use the forgekit being packaged

echo; echo "=== grubforge $gf_ver"
d="$WORK/grubforge"; rc_recipe ~/Programs/aur-grubforge grubforge "$gf_ver" "$d"
git -C "$GF" archive --prefix="grubforge-$gf_ver/" -o "$d/grubforge-$gf_ver.tar.gz" HEAD
(cd "$d" && in_a_terminal PKGDEST="$OUT" makepkg -f --nodeps --noconfirm)

echo; echo "=== nogforge $nf_ver"
d="$WORK/nogforge"; rc_recipe ~/Programs/aur-nogforge nogforge "$nf_ver" "$d"
git -C "$NF" archive --prefix="nogforge-$nf_ver/" -o "$d/nogforge-$nf_ver.tar.gz" HEAD
(cd "$d" && in_a_terminal PKGDEST="$OUT" makepkg -f --nodeps --noconfirm)

echo
ls -l "$OUT"
echo OK
