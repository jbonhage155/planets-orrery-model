# 9. Testing and Verification

The orrery was tested in layers: first the planet maths on a computer, then the software against a pretend servo, then one real servo on the bench, then the whole chain of servos, then the power system on the battery, and finally the built model. Each test below gives the method, what counted as a pass, and the result with its date. The two desk test suites were re-run on 14 Nov 2026 for this document.

## 9.1 Planet position accuracy

The model works out each planet's angle round the Sun from NASA/JPL's "Approximate Positions of the Planets" (Keplerian orbit elements and Kepler's equation). This was checked against **NASA JPL Horizons**, the professional ephemeris service, using the Sun-centred longitude of each planet.

| Test | Method / tool | Pass criterion | Result (date) |
|---|---|---|---|
| Modern dates (1800–2100) | test_pi.py (and the earlier C++ test) compare the code with Horizons on four dates: 1 Jan 2000, 18 Jun 2009, 21 Sep 2026, 17 Oct 2047 | Every planet well under 1° (about one gear tooth is 9°) | **Pass.** Worst error **0.145°** (Jupiter and Saturn); under 0.02° for the rest (20 Sep 2026; re-run 14 Nov 2026, all checks passed) |
| Old dates (3000 BC – 1800) | test_pi.py, JPL Table 2 elements, Horizons reference values for historical dates | Mercury–Neptune within 0.5° | **Pass.** Worst error **0.263°** (26 Sep 2026; re-run 14 Nov 2026) |
| Pluto, old dates | Horizons comparison | Information only (Pluto has no arm on the model) | 0.4° off in 1492; about 7° off by 7 BC. Shown only on the screen |
| Calendar | test_pi.py: Julian calendar before 15 Oct 1582, BC/AD years, day counting | All dates convert both ways | Pass (14 Nov 2026) |
| "All in a line" date (9 Dec 2149) | Day-by-day search 1900–3000, checked with Horizons | Every planet within about 15° of one line through the Sun | Pass (26 Sep 2026) |

What the model gets right: each planet's direction from the Sun, their relative speeds, and line-ups on the right dates. What is not to scale: distances and sizes.

## 9.2 Software desk tests

| Test | Method / tool | Pass criterion | Result (date) |
|---|---|---|---|
| Servo driver protocol | test_pi.py: the driver talks to a software "fake servo" that speaks the same packet format | All packets built and read back correctly | Pass. Caught two real bugs before any hardware: an echoed ping looked like a real reply (a scan "found" all 254 IDs), and the date dial clamped to the wrong day at 1800/2100 (Sep 2026). Re-run 14 Nov 2026: pass. Note: this proves the code is self-consistent, not that it matches a real servo |
| Multi-turn step logic | test_pi.py: short-way-round, forward-only, ±7-turn handling, saved home | All cases correct | Pass (14 Nov 2026) |
| Touchscreen rules | test_server.py: drives the program with no servos and a fake clock: speeds, slider release, settling, date editing, every TIME MACHINE moment, tabs, circular orbits, racing order, health report | Every rule gives the expected screen state | Pass (14 Nov 2026). Found one real glitch on 26 Sep 2026 (after a pause, the next Run showed the old run's end positions for one tick), fixed |
| Simulator matches the real screen | test_server.py plays the same taps through sim.js (the simulator's copy of the rules, run in node) and compares the result | Same screen state at every step | Pass: **101 steps compared**, no differences (14 Nov 2026) |
| Racing arms keep their order | test_server.py: each planet's top speed 75 % of the one inside it | Mercury > Venus > Earth > Mars at every speed | Pass (14 Nov 2026) |

## 9.3 Servo bench tests

Bench tests used the Pi, the Waveshare driver board and bare STS3215 servos (no gears or arms unless noted), first on an adjustable 7.3 V supply.

| Test | Method / tool | Pass criterion | Result (date) |
|---|---|---|---|
| First contact | servo_tool.py scan, info, goto, spin, one servo | Servo found and moves on command | Pass first time; board does not echo (25 Sep 2026) |
| Smoothness at speed | servo_tool.py spin, one servo, about 20 rpm | Smooth and quiet enough for a classroom | Pass; temperature 25 → 27 °C over the session (25 Sep 2026) |
| Torque cap vs speed | Spin at different power caps, read speed | Mercury's 20 rpm target reachable | **Found:** the cap limits speed. 15 % ≈ 7½ rpm (fails); 50 % ≈ 20 rpm; 75 % ≈ 40 rpm; flat out ≈ 50 rpm at 94 %. Cap raised to 80 % (25 Sep 2026) |
| Speed tour | speed_tour.py: one servo runs each planet's true rate with Mercury at 40 rpm. Slow planets stepped in position mode, fast ones in wheel mode | Measured within a few % of target | **Pass.** Neptune 3.3° (target 3.5°), Uranus 6.8 (6.9), Saturn 19.4 (19.6), Jupiter 48.4 (48.7) in 10 s; Pluto 6.9 (7.0) in 30 s. Mars 339/350, Earth 656/658, Venus 1050/1069, Mercury 2694/2731 steps/s. Silent at Pluto speed (25 Sep 2026) |
| Creep (slowest planet) | creep.py: goal stepped forward at 2.72 steps/s for 30 s | Follows without stalling or jerking | **Pass.** 7.0° in 30 s, never more than 5 steps behind, silent (25 Sep 2026) |
| Wheel-mode floor | Constant-speed mode at 3, 6, 11 and 25 steps/s | Information | **Found:** all came out at exactly 50 steps/s. Design response: slow arms are stepped in position mode (25 Sep 2026) |
| Relative step mode | Servo mode 3 | Information | Does not move these servos; not used (25 Sep 2026) |
| First run of the date logic | orrery.py, six servos: today → 12 × one month → 6 × one year → today | Every servo back on today's angles | **Pass.** Every servo within **0.1°** (25 Sep 2026) |
| Turn-count runaway | Observed after winding Mercury several turns | No unexpected motion | **Failed, then fixed.** A goal from the 0–4095 register sent Mercury several turns backwards. Switching to wheel mode and back was shown (on Saturn) to reset the count; the software now re-anchors (5.7). A backward jerk after re-anchoring was fixed on 7 Nov 2026 (25 Sep 2026) |
| Run-mode accuracy | orrery.py --run, 30 s at Mercury 20 rpm, six servos, true (Kepler) speeds | Arms stay on their true angles | **Pass.** Venus–Saturn within about 0.5°, Mercury within about 4° (it speeds up and slows down 2.3× each lap) (25 Sep 2026) |
| Run-mode stutter | 30 s replay after fixing the 5-second search for missing servos | Steady loop, no jerks | **Pass.** Steady 106 ms loop; Mercury within 0.4° after a 0.7 s spin-up; confirmed smooth by eye and ear (25 Sep 2026) |
| Numbering and roll call | number_chain.py, one servo at a time, then --roll-call | Every ID answers once, in order | Pass: 1–6 on 25 Sep 2026 (one duplicate ID fixed by hand), 7–9 on 28 Sep 2026. The model now uses 1–8 |
| Full-chain smoothness | Live program, 30 s at each speed, health sampled every second, 3D view showing | Loop near 100 ms, arms on target, no errors, no throttling | **Pass.** Loop 111–114 ms, CPU 33–50 %, at most 59 °C, never throttled, arms within 1–2° once up to speed, no errors. Very fast arms start up to 150° behind and catch up in about 7 s, by design (28 Sep 2026, nine servos) |
| Cable-bump recovery | Cable pulled out mid-run, then pushed back in while paused | Servos re-attach by themselves and return to the date | **Pass** after a software fix. 6 of 6 reconnected within seconds, every arm within 0.1° (26 Sep 2026) |
| Servo protection settings | Registers read from all servos | Information | Overload trips at 80 % load for 2 s; over-current 3.25 A for 2 s; motor off at 70 °C; firmware 3.10 (30 Sep 2026) |
| Hold (load) test | hold_test.py: Mercury with its gear, 400 steps/s (about 6 rpm), 30 % then 80 % power, the gear held back hard by hand about 3 s in each; stops early at 55 °C or any protection trip | Record held current; see whether protection trips | **Done.** A hard hold never slowed it, even at 30 %. Free: load about 11 %, current about 6 mA. Held at 30 %: load about 21 %, current 70–104 mA, then a brief catch-up to 500–550 steps/s on release, no position lost. Status byte never tripped. Temperature readings glitch (single 37–70 °C samples among 29–30 °C). Conclusion: the glue joints and Mercury's thin tube would fail before the servo's 70 °C cut-off, so a jam guard is needed (2 Oct 2026) |
| Live servo readings | One 15-byte read per servo per tick (position, speed, load, volts, temperature, status, current) | Loop timing unchanged | Pass: 0.61 ms per servo; loop 113 ms at 20 years/min (2 Oct 2026) |

## 9.4 System tests: power, Pi and mechanics

| Test | Method / tool | Pass criterion | Result (date) |
|---|---|---|---|
| Battery power-up | Battery → switch → converters → Pi and servos; switch off and on | Switch cuts all power; everything comes back up | **Pass** (3–4 Oct 2026) |
| Servo current on battery | DROK display / meter, all servos at 1,000 years/min, no arms | Well inside the battery's 3 A | **Pass.** About 1 A at 7.5 V (3–4 Oct 2026) |
| Pi supply | vcgencmd get_throttled while servos run on battery | 0x0 (no under-voltage, no throttling) | **Pass.** 0x0, 52 °C (3–4 Oct 2026) |
| Pi heat and load, open air | Settings/health screen readings with each tab showing | Below 70 °C, never throttled | **Pass.** 56–63 °C with 3D tabs, never throttled. CPU: RUN view about 29 % paused / 37 % running; SOLAR SYSTEM about 55 %; PLANETS about 40 %; GALAXY about 25 % at 52 °C (26 Sep – 14 Nov 2026) |
| Multi-touch | Virtual copy of the touch panel (pinch and tap), then real fingers | Pinch zooms; taps work | Pass on the 5 in screen (26 Sep 2026). (to check: 7 in screen) |
| Mechanical fit check | 3D model measures the gap between every pair of parts every 0.1 in | No part touches another | **Pass** at as-built ½ in levels. Closest: three servo-gear screws 0.05 in from a stand plate; Pi 0.12 in from a drawn servo cable (7 and 11 Nov 2026) |
| Neptune's arm clearance | Tube top measured after adding washers | Arm loop clear of the ceiling | **Pass.** Tube top 8¼ in, about ½ in clear (8 Nov 2026) |
| Each servo running geared | MANUAL mode from the settings screen, one servo at a time | Gear meshes through a full turn without tight spots or skipping | Column, gears and servos running by 9 Nov 2026. (to check: per-servo results not recorded) |
| Arm direction | First geared arm run from the screen | Planets turn anticlockwise seen from above | (to check: not recorded) |
| Electronics fit in the new box | Real screen and Pi held in the 11 Nov box shape | Nothing touches a servo | **Pass** (11 Nov 2026) |

## 9.5 Tests still to run

| Test | Method / tool | Pass criterion | Result (date) |
|---|---|---|---|
| Travel-mode line check | Settings → TRAVEL MODE with all arms on | All eight planets in one straight row | In progress (arms being clamped 14 Nov 2026) |
| Sky check | Today vs a sky app or NASA's Eyes | Each planet in the right direction | Not yet run |
| Speeds with arms on | Run at several speeds, listen and watch | No clicks, jerks or catching arms | Not yet run |
| Closed-box heat | Settings screen for 20 min with the box closed | Never "throttled" | Not yet run |
| Current with arms and tubes | DROK display or meter, planets running | Inside the 3 A battery limit with margin | Not yet run |
| Low-battery Pi supply | vcgencmd get_throttled at about 9.5 V with all servos starting | 0x0 | Not yet run |
| Battery run time | Charge full, run the planets, note the LED steps | At least 2 h running (need: 1–2 h) | Not yet run (estimate 2–3½ h non-stop) |
| Normal load vs speed, arms on | Read load at each speed | Baseline for the jam guard | Not yet run |

## 9.6 Known issues and open items

- **Jam (stall) guard not built.** A held or jammed arm makes its servo push through, and the glue joints or Mercury's thin tube would give way first. Plan: first a watch-only "working hard" flag (load well above normal for that speed), then switch a blocked servo off, retry gently, and show "Mars is blocked — check it" while the other planets keep going. Any power cap must follow speed, never limit top speed. Needs the normal load-vs-speed figures with arms on (9.5).
- **Arm calibration** in travel mode is under way; any arm off the line needs SAVE HOME.
- **Arm direction** on the geared model not recorded as checked (ARM_DIR = 1 assumed). (to check)
- **Box build** (phase 7) is the current job: sides, ceiling, back door, gluing, then electronics in.
- **Battery checks still owed:** current with arms on, Pi supply at a low battery, real run time.
- **Pi heat in the closed box:** watch the settings screen; if it ever shows "throttled", add or check heatsinks or draw the 3D view at 30 frames a second.
- **Strain relief:** servo power plug, chain cable, USB and the screen ribbon must all be tied down. A loose plug at the science fair would stop the show.
- **Power switch cuts a running Pi.** The Turn off button was removed (13 Nov 2026). Plan: a read-only file system, after deciding where the saved date, settings and arm homes are kept (they would stop saving otherwise).
- **Servo memory wear.** Each re-anchor writes the mode setting to the servo's permanent memory twice, and every Run/Pause does this for the fast planets. Estimate writes per day of science-fair use against the chip's rating; if it matters, keep fast planets in wheel mode at speed 0 while paused.
- **Occasional slow loop ticks** (worst 199–442 ms) seen on 28 Sep 2026; cause not found, possibly the test's own polling. Listen for jerks.
- **Temperature readings glitch**: single wrong samples. Act only on several readings in a row and smooth what the screen shows.
- **Gear-screw clearance:** Mercury's, Venus's and Earth's servo-gear screws pass 0.05 in from the stand plate four slots up; check while meshing, trim the plate corner if one touches. (to check)
- **Command-line bench tool** orrery.py --run still uses true Kepler speeds and the old Mercury-rpm scale, unlike the touchscreen; align it or mark it as a bench tool only.
- **Epoxy supply** is low; more is needed for elbows, magnets, planets and possibly the polycarbonate joints.
- **Housekeeping:** Pi operating-system updates not yet applied (do it with the builder present, then re-check the kiosk); the router still labels the Pi with an old name.
- **Ideas, not committed:** arms spinning backwards during a time trip (never tried on hardware); a family birthday moment; a "standing on each planet" sunrise view; highlighting the chosen planet on a small orbit map; tapping a moon for its facts.
