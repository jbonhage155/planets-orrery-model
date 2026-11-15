# Docs

Everything needed to understand, reproduce and look after the orrery. Read them in this order
if you are building one. The section numbers match the engineering design document.

| Document | What it covers |
|---|---|
| [mechanical-design.md](mechanical-design.md) | **4. Mechanical design.** Overall size and layout; the centre column of eight nested brass tubes on a steel rod (tube sizes, cut lengths, heights, washers, the ½ in gear levels); the 40-tooth 1:1 gears and how they are drilled and glued; the servo stands; the arms and collars; the planets and the Sun (ball sizes, orbit radii, paint colours, rings); the clear box (panel sizes, the sloped front, the sliding ceiling, the back door); where the electronics sit; open items to measure. |
| [electrical-design.md](electrical-design.md) | **5. Electrical design.** Block diagram, battery and power converters, power budget, the full wiring diagram and wiring table, the one-wire servo bus, numbering the servos, servo settings, the Pi and touchscreen, and electrical safety. |
| [software-design.md](software-design.md) | **6. Software design.** How the program is put together (server, screen, simulator), the planet-position maths and its accuracy, motion control (turning angles into servo steps, running, travel mode, calibration), every touchscreen tab, the 3D graphics, settings and tuning, safety features, setting up a Pi, deploying and testing, and a map of every source file. |
| [bill-of-materials.md](bill-of-materials.md) | **7. Bill of materials.** Every part by subsystem with its Amazon product number (ASIN) or source and quantity, the tools used, and parts that were tried and dropped. |
| [assembly-procedure.md](assembly-procedure.md) | **8. Assembly procedure.** The build step by step in ten phases: getting ready, painting, cutting the tubes, gears and washers, the first gear mesh test, the base and column, servos on their stands, the box, the electronics, arms and planets, then calibration and testing. Uses the printable [templates](../templates/). |
| [testing-and-verification.md](testing-and-verification.md) | **9. Testing and verification.** Planet-position accuracy against NASA JPL Horizons, the automatic software tests, servo bench tests, power and system tests, tests still to run, and known issues. |
| [operation-and-maintenance.md](operation-and-maintenance.md) | **10. Operation and maintenance.** Switching on and off, using each tab, travel mode for carrying, calibrating an arm, battery and charging, troubleshooting, and updating the software. |
| [Orrery-Engineering-Design-Document.pdf](Orrery-Engineering-Design-Document.pdf) | The engineering design document written for 3rd graders: what engineering documents are, with a short, picture-heavy version of all of the above, plus the project plan, design decisions and lessons learned. |
| [images/](images/) | Diagrams used in the docs: block diagram, wiring diagram, servo bus, how one tap reaches a motor, and a 3D view of the orrery. |

Notes marked **To check** are dimensions or results that were never measured on the finished
model; measure them on your own build.
