#!/usr/bin/env bash
# Reset the KognogOS test VM (kognog-hypeforge) for a nogForge 1.5.0 bench run:
# back to the `before-nogforge-150` snapshot (nog 1.9.0, flatpak + snapd + yay,
# javier with NOPASSWD sudo, the test-only polkit rule for Flatpak), then nog
# 2.0.0, python-forgekit 0.10.0 (+ python-pyte) from the packages built here,
# some garbage for Maintenance to find (an orphan, an old snap revision), and
# the nogforge rc package installed the way step 2.1 says (`nog install <file>`
# as javier, pacman's question answered). Then scripts/bench-150.py is copied in.
#
#   scripts/vm-prep-150.sh dist-rc/nogforge-1.5.0rcN-1-any.pkg.tar.zst
#
# Logs to logs/vm-prep-150-<time>.log (+ -latest); the last line says OK.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs
log="logs/vm-prep-150-$(date +%Y%m%d-%H%M%S).log"
ln -sfn "$(basename "$log")" logs/vm-prep-150-latest.log
exec > >(tee "$log") 2>&1
PKG="${1:?the nogforge rc package (dist-rc/…pkg.tar.zst)}"
[ -f "$PKG" ] || { echo "no such package: $PKG"; exit 1; }
VM=kognog-hypeforge
NOG=~/Programs/nog/scripts
X() { "$NOG/vm-exec.py" --timeout "${T:-900}" -- "$@"; }

echo "== VM: back to before-nogforge-150, start"
virsh -c qemu:///system destroy "$VM" >/dev/null 2>&1 || true
virsh -c qemu:///system snapshot-revert "$VM" before-nogforge-150
virsh -c qemu:///system start "$VM" >/dev/null 2>&1 || true
for i in $(seq 1 60); do
  virsh -c qemu:///system qemu-agent-command "$VM" '{"execute":"guest-ping"}' >/dev/null 2>&1 && break
  sleep 5
done
sleep 8

echo "== nog 2.0.0, forgekit 0.10.0, pyte; the driver"
"$NOG/vm-put.py" /var/cache/pacman/pkg/python-pyte-0.8.2-5-any.pkg.tar.zst /tmp/python-pyte.pkg.tar.zst
"$NOG/vm-put.py" ~/Programs/aur-python-forgekit/python-forgekit-0.10.0-1-any.pkg.tar.zst /tmp/python-forgekit.pkg.tar.zst
"$NOG/vm-put.py" ~/Programs/aur-nog/nog-2.0.0-1-x86_64.pkg.tar.zst /tmp/nog-2.0.0.pkg.tar.zst
"$NOG/vm-put.py" --mode 755 "$NOG/vm-drive.py" /usr/local/bin/vm-drive
"$NOG/vm-put.py" --mode 755 scripts/bench-150.py /home/javier/bench-150.py
"$NOG/vm-put.py" "$PKG" "/home/javier/$(basename "$PKG")"
X 'pacman -U --noconfirm /tmp/python-pyte.pkg.tar.zst /tmp/python-forgekit.pkg.tar.zst /tmp/nog-2.0.0.pkg.tar.zst 2>&1 | grep -E "^(upgrading|installing|error)" ; pacman -Q nog python-forgekit python-pyte; chown javier:javier /home/javier/bench-150.py /home/javier/*.pkg.tar.zst'

echo "== garbage for Maintenance: an orphan (sl), an old snap revision (hello-world 27 → 29)"
X 'pacman -S --asdeps --noconfirm sl >/dev/null 2>&1; snap refresh hello-world --revision=27 >/dev/null 2>&1; snap refresh hello-world >/dev/null 2>&1; echo "orphans: $(pacman -Qtdq | tr "\n" " ")"; snap list --all | grep hello'

echo "== 2.1: nog install of the rc, as javier"
X "runuser -u javier -- env HOME=/home/javier vm-drive --timeout 500 --log /home/javier/bench-2.1.log 'cd ~ && nog install ~/$(basename "$PKG")' 'Proceed with installation' 'y' | tail -6; runuser -u javier -- nogforge --version; pacman -Q nogforge; desktop-file-validate /usr/share/applications/nogforge.desktop && echo 'launcher entry installed and valid'"

echo "== the report before the bench"
X 'runuser -u javier -- env HOME=/home/javier nog clean --json 2>/dev/null | tail -1 | python3 -c "import json,sys; d=json.load(sys.stdin); print([(c[\"id\"],c[\"items\"]) for c in d[\"categories\"]])"; pacman -Q cliamp yt-dlp mpv | tr "\n" " "; echo; flatpak list --app --columns=application | wc -l'
echo OK
