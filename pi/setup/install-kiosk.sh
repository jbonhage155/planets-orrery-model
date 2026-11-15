#!/usr/bin/env bash
# Run from your computer after ../deploy.sh: installs the orrery server as a service and
# the full-screen kiosk on the Pi's touchscreen, turns off screen blanking, gives the
# touchscreen real multi-touch (labwc-rc.xml: pinch-to-zoom on the PLANETS tab), makes the
# screen go dark at the end of a shutdown (blank-screen: the Turn off button), reboots.
#   ./install-kiosk.sh            (PI_HOST=planets.local ./install-kiosk.sh)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PI_HOST="${PI_HOST:-planets.local}"
scp -q "$HERE/orrery.service" "$HERE/orrery-kiosk.desktop" "$HERE/labwc-rc.xml" "$HERE/blank-screen" "pi@$PI_HOST:/tmp/"
ssh "pi@$PI_HOST" '
  set -e
  sudo install -m 644 /tmp/orrery.service /etc/systemd/system/orrery.service
  mkdir -p ~/.config/autostart && install -m 644 /tmp/orrery-kiosk.desktop ~/.config/autostart/
  mkdir -p ~/.config/labwc && install -m 644 /tmp/labwc-rc.xml ~/.config/labwc/rc.xml
  sudo install -D -m 755 /tmp/blank-screen /usr/lib/systemd/system-shutdown/orrery-blank-screen
  sudo systemctl daemon-reload && sudo systemctl enable --now orrery
  sudo raspi-config nonint do_blanking 1        # 1 = screen never blanks
  sleep 3; systemctl is-active orrery; curl -sf -o /dev/null http://localhost:8080/api/state && echo "server answers"
  sudo systemctl reboot'
echo "Pi rebooting: the screen should come up full screen in about a minute."
