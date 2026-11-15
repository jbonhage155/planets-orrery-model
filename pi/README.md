# Pi software

The program that runs on the Raspberry Pi 4B inside the box. It works out where every planet
is, drives the eight servos, and shows the touchscreen app. Written in Python 3 (only needs
**pyserial**) plus a web page for the screen. It also runs on a laptop with no hardware
(`--dry-run`), which is how most of it was developed and tested.

How it works, in one line: the touchscreen is a web page (`ui/index.html`) shown full screen
in Chromium; every tap goes to `server.py`, which runs a loop ten times a second that works out
each planet's angle (`planets.py`), turns it into servo steps (`orrery.py`) and sends it down
the servo bus (`feetech.py`). The full explanation, with the function-by-function path of a
tap, is in [../docs/software-design.md](../docs/software-design.md).

## Files

| File | What it does |
|---|---|
| `server.py` | **The main program** (runs as the `orrery` service). Web server for the screen and the admin page, the tabs and modes, run speed, travel mode, manual mode, and the motion loop. `python3 server.py` with the servos on USB, `--dry-run` without. |
| `planets.py` | Where each planet is on any date: NASA JPL's *Approximate Positions of the Planets* (Keplerian elements, Table 1 for 1800–2050, Tables 2a/2b for 3000 BC–3000 AD), and the Julian/Gregorian calendar. |
| `orrery.py` | Arm control: turns planet angles into servo step counts (4,096 steps a turn, forward only), runs the arms smoothly, re-anchors the servos' turn counters, re-attaches a servo that drops off the bus, and keeps each arm's saved home position. Also a small command-line version of the orrery (`--keys`, `--run`). |
| `feetech.py` | Driver for the Feetech STS3215 serial-bus servos: builds and checks the byte packets, reads and writes the servo's registers (position, speed, torque limit, temperature, current). |
| `servo_tool.py` | Bench tool: `scan`, `info N`, `set-id N` (with exactly one servo connected), `goto N degrees`, `spin N --rpm 20`. |
| `number_chain.py` | Numbers factory-fresh servos one at a time (they all arrive as ID 1) and wiggles each one so you can label it; `--roll-call` wiggles every servo in ID order. |
| `test_pi.py` | Desk tests, no hardware: planet maths against NASA JPL Horizons (worst error 0.145° for 1800–2100), the servo driver against a fake servo, the step maths. |
| `test_server.py` | Desk tests of the screen's rules with a fake clock, and checks that `ui/sim.js` gives the same results (needs Node.js for that part). |
| `requirements.txt` | Python packages (pyserial; the rest are only for an old knob/LCD option). |
| `deploy.sh` | Copies this folder to the Pi (`~/orrery`) and runs both test suites there. `./deploy.sh ssh` opens a shell on the Pi. |
| `ui/index.html` | The touchscreen app: tab bar, every tab's drawing, taps, the 3-2-1 countdown. |
| `ui/planets.js` | The 3D views on the screen (three.js): planet globes with moons, the solar system, the true-size SCALE view, the GALAXY view. |
| `ui/sim.js` | A JavaScript copy of the server's rules, so the same screen can run with no Pi (used by the 3D model). |
| `ui/admin.html` | Admin page for a laptop or phone on the same Wi-Fi: live servo readings and the tuning settings. |
| `ui/tex/` | Planet surface maps (see `CREDITS.md`). |
| `setup/install-kiosk.sh` | One-time setup on the Pi: installs the `orrery` service, the full-screen kiosk, real multi-touch for the screen, no screen blanking; then reboots. |
| `setup/orrery.service`, `setup/orrery-kiosk.desktop`, `setup/labwc-rc.xml`, `setup/blank-screen` | The files `install-kiosk.sh` puts in place. |

## Setting up a Pi

1. Write **Raspberry Pi OS (64-bit, with desktop)** to a microSD card with Raspberry Pi
   Imager. In its settings set the host name to `planets`, the user to `pi`, your Wi-Fi and
   time zone, and turn on SSH.
2. Add `dtoverlay=vc4-kms-dsi-7inch` to `config.txt` on the card's boot partition (the
   Freenove 7 in DSI touchscreen needs it).
3. Boot the Pi, then from your computer:

   ```bash
   PI_HOST=planets.local ./deploy.sh                 # copy the code, run the tests on the Pi
   PI_HOST=planets.local ./setup/install-kiosk.sh    # service + full-screen kiosk, reboots
   ```

The Pi now starts straight into the orrery screen. It also answers at
`http://planets.local:8080/` (the screen) and `http://planets.local:8080/admin` from any
browser on the same Wi-Fi.

## Numbering the servos

Every STS3215 leaves the factory as **ID 1**, and they share one cable, so each needs its own
number first: **1 Mercury, 2 Venus, 3 Earth, 4 Mars, 5 Jupiter, 6 Saturn, 7 Uranus,
8 Neptune**. Stop the service first (`sudo systemctl stop orrery`), then either connect **one
servo at a time** and run `python3 servo_tool.py set-id N`, or use `number_chain.py`
(`--first 2 --last 8`), which numbers each new servo as you add it and wiggles it. Mercury
keeps ID 1. Check with `python3 number_chain.py --roll-call`.

## Trying it without hardware

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python test_pi.py
.venv/bin/python test_server.py
.venv/bin/python server.py --dry-run      # then open http://localhost:8080
```

## Files it saves on the Pi

In the `pi` user's home folder, so a new deploy never erases them:
`~/.planet_dial.json` (the date the planets are on), `~/.orrery_settings.json` (tuning
settings from the admin page) and `~/.orrery_home.json` (each arm's calibrated home). Back
up `~/.orrery_home.json` before rebuilding the SD card.
