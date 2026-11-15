#!/usr/bin/env bash
# Copy this folder to the Pi (~/orrery) and run the desk tests there.
#   PI_HOST=planets.local ./deploy.sh        (default host: planets.local, user pi)
#   ./deploy.sh ssh                           just open a shell on the Pi
# It does not restart anything: after a change run `sudo systemctl restart orrery` on the Pi.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PI_HOST="${PI_HOST:-planets.local}"
if [[ "${1:-}" == ssh ]]; then exec ssh "pi@$PI_HOST"; fi
rsync -a --delete --exclude .venv --exclude __pycache__ --exclude setup "$HERE/" "pi@$PI_HOST:orrery/"
ssh "pi@$PI_HOST" 'cd ~/orrery && python3 test_pi.py 2>&1 | tail -3 && python3 test_server.py 2>&1 | tail -3'
