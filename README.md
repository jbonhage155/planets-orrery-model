# Date-Dial Orrery

A school science project: a model of the solar system where you **pick any date on a
touchscreen and the eight planets swing round the Sun to where they really were** (or will
be) on that day.

A Raspberry Pi works out each planet's position with NASA JPL's formulas and sends it to
eight smart servo motors, one per planet. Each servo turns a brass tube through a pair of
40-tooth gears (1:1). The eight tubes are nested like a telescope, so all the drives come up
through one hole, and each tube carries an arm with a painted foam planet.

**Start here:** [`docs/Orrery-Engineering-Design-Document.pdf`](docs/Orrery-Engineering-Design-Document.pdf),
the engineering design document. It covers the requirements, mechanical and electrical
design, wiring diagram, software, parts list, assembly, tests and lessons learned, written
for 3rd graders.

## What's here

| Folder | What's inside |
|---|---|
| [`pi/`](pi/) | The program that runs on the Pi: planet maths (`planets.py`), servo bus driver (`feetech.py`), arm control (`orrery.py`), the touchscreen server (`server.py`), the screen itself (`ui/`), bench tools and tests |
| [`site/`](site/) | The 3D model of the whole orrery (`index.html`) and the printable build pages: build checklist, column and servo stands with the base drilling and servo plate templates, box cutting and screen opening templates, panel templates, arms, Saturn's rings and the painting guide |
| [`docs/`](docs/) | The engineering design document (PDF) |

## The parts, in short

- Raspberry Pi 4B and a 7 in DSI touchscreen (Freenove FNK0078H)
- 8 × Feetech STS3215 bus servos and a Waveshare Bus Servo Adapter (A) (USB)
- K&S telescoping brass tubes on a 1/8 in steel rod; 16 × 40-tooth Technic-style gears
- TalentCell 12 V battery, a 12 → 7.5 V buck (servos) and a 12 → 5 V USB-C buck (Pi)
- 1/8 in clear acrylic and polycarbonate for the box and servo plates; threaded rod stands
- Foam balls and acrylic craft paint for the planets

The design document has the full bill of materials and the wiring diagram.

## Running the software

On a Raspberry Pi (Raspberry Pi OS with desktop), with the servos numbered 1 (Mercury) to 8
(Neptune) — `pi/number_chain.py` numbers factory-fresh servos one at a time:

```bash
# from your computer: copy pi/ to the Pi and run the desk tests there
PI_HOST=planets.local ./pi/deploy.sh
# then install the service and the full-screen kiosk (reboots the Pi)
PI_HOST=planets.local ./pi/setup/install-kiosk.sh
```

Without any hardware, on any computer:

```bash
cd pi
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python test_pi.py          # planet maths vs NASA JPL Horizons, servo driver
.venv/bin/python test_server.py      # the screen's rules (and the website simulator, if node is installed)
.venv/bin/python server.py --dry-run # the touchscreen app with no servos: open http://localhost:8080
```

To see the 3D model and the build pages, serve the repository root and open `/site/`:

```bash
python3 -m http.server 8000     # then http://localhost:8000/site/
```

The model's front panel runs the real touchscreen page in simulation mode (`pi/ui/sim.js`).
The photos printed on some of the model's parts (sellers' pictures) are not included, so those
parts show in plain colours.
Printable templates must be printed at 100 % ("actual size"): every one has a 2 in bar to
check with a ruler.

## Credits

- Planet positions: NASA JPL, *Approximate Positions of the Planets* (Standish), checked
  against JPL Horizons.
- Planet maps: [Solar System Scope](https://www.solarsystemscope.com/textures/) (CC BY 4.0);
  Pluto: NASA / JHU APL / SwRI (public domain). See `pi/ui/tex/CREDITS.md`.
- 3D graphics: [three.js](https://threejs.org/) (MIT licence), included as `three.min.js`.
