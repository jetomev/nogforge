#!/usr/bin/env bash
# Install the test packages of the "nog inside the app" work (4 Oct 2026) on
# this computer, with nog: nog 1.7.0rc1, python-forgekit 0.6.0rc1, grubforge
# 2.1.0rc1 and nogforge 1.1.0rc1, from dist-rc/ (built by make-rc-packages.sh).
# pacman shows the four packages and asks; your password is asked once.
# The real releases later upgrade over these (rc sorts before the release).
#
#   bash ~/Programs/nogforge/scripts/install-rc.sh
#
# Logs to ~/Programs/nogforge/logs/install-rc-<time>.log (+ install-rc-latest.log).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
log="logs/install-rc-$(date +%Y%m%d-%H%M%S).log"
ln -sfn "$(basename "$log")" logs/install-rc-latest.log
exec > >(tee "$log") 2>&1

echo "== before"; pacman -Q nog python-forgekit grubforge nogforge 2>&1 || true
files=(dist-rc/nog-1.7.0rc1-1-x86_64.pkg.tar.zst dist-rc/python-forgekit-0.6.0rc1-1-any.pkg.tar.zst
       dist-rc/grubforge-2.1.0rc1-1-any.pkg.tar.zst dist-rc/nogforge-1.1.0rc1-1-any.pkg.tar.zst)
for f in "${files[@]}"; do [ -f "$f" ] || { echo "missing: $f"; exit 1; }; done
echo; echo "== installing with nog"
nog install "${files[@]/#/$PWD/}"
echo; echo "== after"; pacman -Q nog python-forgekit grubforge nogforge python-pyte
nog --version
echo OK
