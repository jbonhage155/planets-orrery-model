# 10. Operation and Maintenance

This section is a practical guide for anyone using or looking after the orrery: switching it on and off, using the screen, carrying it, adjusting an arm, charging the battery, fixing common problems, and keeping the software up to date.

## 10.1 Switching on

1. Check the arms are free to turn: nothing resting on them, no one leaning over the model.
2. Make sure the battery's own switch (inside, on the TalentCell pack) is on. It is normally left on.
3. Press the **on/off rocker switch** on the left side of the box to "I".
4. The Pi takes about 25 seconds to start, then the screen shows "Starting…" and opens on the **ORBITS** tab, paused, showing the last saved date.
5. The arms then move **forward** to that date if they are not already there (arms within 30° are left alone). If travel mode was on when the model was switched off, the arms stay in their row and the gear shows a yellow dot.

## 10.2 Switching off

1. On ORBITS, tap **Pause** and wait until the status line says **Paused** and the arms have stopped. This saves the date the arms are showing, so nothing needs to move at the next start-up.
2. If the model is going to be carried, put it in **travel mode** first (section 10.4).
3. Flip the rocker switch to "O".

Notes: the on-screen Turn off button was removed on 13 November 2026, so the switch cuts power straight to the running Pi. This is normally fine, but there is a small risk to the SD card if it happens while the Pi is writing (to check: read-only file system not yet enabled). For a completely clean shutdown, an adult with a laptop can run *sudo poweroff* on the Pi (via *./deploy.sh ssh*); the screen then shows "Turning off…" and goes dark when it is safe to flip the switch. If the switch is flipped while the planets are running, the arms stop wherever they are and will move forward to the last saved date at the next start-up.

## 10.3 Using each tab

| Tab | To do this | Tap or gesture |
|---|---|---|
| ORBITS | Make the planets go round | ▶ Run. Change speed with − and + (1 to 100 years a minute). ❚❚ Pause stops and settles every arm on the true date. |
| ORBITS | Learn about a planet | Tap it in the picture: its PLANETS page opens. |
| TIME MACHINE | Visit a moment in history | Tap Vesuvius, Declaration of Independence, Moon landing or Today. Step back during the 3-2-1; tap anywhere to cancel. |
| TIME MACHINE | Choose any date (a birthday) | Pick a date, tap day / month / year, use the arrows (the year by 1, 10 or 100), then GO ▶. |
| PLANETS | Explore a planet | Tap a button along the top. Drag the globe to turn it, pinch to zoom, double-tap to reset. ⤢ for a full-screen globe, Facts to bring the facts back. |
| GALAXY | See where we live in the Milky Way | Watch the clock count millions of years. Tap "You are here" to fly in; Facts for the numbers. |
| SCALE | Compare true sizes | Tap a planet to fly to it; pinch out to see the whole Sun; double-tap to go back. |
| ⚙ Settings | Check health, travel mode, calibration | See sections 10.4 and 10.5. |

The planets keep running on every tab. A planet drawn faint with a coloured ring is "racing": too fast for its motor to keep exact position at that speed. This is normal; it settles on its true place when paused.

## 10.4 Travel mode (for carrying)

1. Tap the **⚙ gear**, then **TRAVEL MODE**. Step back for the countdown.
2. Every arm turns forward until all eight planets are in one row, pointing **away from the screen** (towards the back of the box). This takes up to about 7 seconds.
3. The settings panel says **TRAVEL MODE IS ON**, and the gear shows a **yellow dot**. Switch off and carry.
4. Travel mode survives switching off and on. To leave it, tap **Back to the date** in settings, or tap Run on ORBITS, a TIME MACHINE moment, or GO.

Travel mode is also the quick calibration check: if every planet is not on one straight line, an arm needs adjusting (section 10.5).

### What the yellow dot on the gear means

The small amber (yellow) dot on the settings gear means the model is **not simply following the date**: either **travel mode** is on (arms in their row) or **MANUAL** mode is on (motors handed to a person). Open the gear to see which. With neither on, there is no dot.

## 10.5 Calibrating an arm

Use this when one planet is not on the line in travel mode, for example after a gear slipped or an arm was knocked.

1. Put the model in travel mode (section 10.4) and note which planets are out of the row. In travel mode the servo list shows a **FROM ROW** column: how many degrees each arm is from the line (green within 2°, amber beyond).
2. Tap **MANUAL**. The motors go limp.
3. Tap the planet(s) to adjust in the servo list (a tick appears).
4. If the arm is far off, choose Forward or Reverse and slide the rpm slider to move it near the line, then slide back to 0.
5. Tap **↺ 1°** or **↺ 10°** to step it exactly onto the line (the direction follows Forward/Reverse).
6. Tap **SAVE HOME**, then **Tap to save** within 5 seconds. The screen confirms "Home saved: …".
7. Tap **AUTO** (countdown) and check all planets now sit in one row.

**RESET HOME** (also two taps) forgets a saved home for the picked planets. Use it if the arm was instead put right mechanically, by loosening its clamp and turning it on its tube while in travel mode: the arm then goes back to the built-in home.

## 10.6 Battery, charging and run time

| Item | Details |
|---|---|
| Battery | TalentCell 12 V, 6000 mAh (66.6 Wh), inside the box against the left wall. Its own switch stays on. |
| Charging | Plug the TalentCell's own 12.6 V charger into the charging socket in the **left wall** of the box. About **10 hours** from empty, so charge the night before. A shorter charge is fine. |
| Using while charging | Yes: the model runs normally with the charger plugged in, so at home it can run from the charger. |
| Charge level | The battery's five LEDs. The 7.5 V converter's display also shows the battery voltage: about 12.6 V full, 9 V empty. |
| Run time (estimated) | Planets turning non-stop: 2 to 3½ hours. Mixed use: 3½ to 5 hours. Paused, exploring tabs: 4½ to 6 hours. (to check) These are design estimates; the real run time with arms fitted has not yet been measured. |
| Low battery signs | The settings screen's Pi line shows "under-voltage", or the servo header shows a voltage below 6.5 V in amber. Charge the battery. |

## 10.7 Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Screen says "Waiting for the orrery…" or a red banner "Lost contact with the orrery – retrying" | The server is starting or restarting | Wait 10–20 seconds; it restarts by itself. If it persists, switch off and on. An adult can check with *sudo systemctl status orrery* and *journalctl -u orrery*. |
| Red banner "Servo problem: …" | A servo stopped answering mid-command (often a loose cable) | Pause. Check the servo cable chain and the power plug on the driver board. The program retries every second. |
| "7 of 8 planets connected", or a servo shows "not connected" in settings | Servo cable or power loose; servo unpowered | Pause the planets (missing servos are only searched for while paused, every 5 s). Reseat the cable; the servo re-attaches by itself and goes to the date. |
| A planet off its row in travel mode, or visibly off its true place | Gear slipped or arm moved on its tube | Calibrate it (section 10.5). |
| An arm turns the wrong way round | Direction setting wrong for the build | Should not happen on the finished model. Set *ARM_DIR = -1* in orrery.py and deploy (builder). |
| Tapping Run does nothing | Arms still settling on a new date (about 4½ s); or showing a deep-time date | Wait for "Paused", then tap Run again. |
| Arms do not follow the date at all; status says "Manual mode" | MANUAL is on (yellow dot on the gear) | Settings → AUTO, or open ORBITS or TIME MACHINE, which switch to AUTO. |
| Planets drawn faint with a coloured ring | Racing: too fast for the motor at this speed | Normal. Choose a slower speed, or pause. |
| A planet shown red in settings with a warning (overload, too hot, too much current) | Arm jammed or blocked; servo protection tripped | Pause, free the arm, check the gear and glue joints. Restart the model to re-enable the servo if it stays limp (to check). |
| Pinch-to-zoom does nothing; touches act like a mouse | The desktop's touch-as-mouse setting is back, or the touchscreen's name changed | Builder: re-run install-kiosk.sh, or add the panel's name to setup/labwc-rc.xml; apply with *kill -HUP $(pgrep -x labwc)* and reload the kiosk. |
| Screen flashes colours or goes blank while the Pi runs | Display ribbon cable bumped loose | Switch off, open the back door, reseat the ribbon (metal contacts towards the Pi's USB/Ethernet ports). |
| Desktop appears instead of the orrery screen | Kiosk autostart file missing | Builder: re-run install-kiosk.sh. |
| Pi temperature amber (158 °F+) or red (176 °F+); "throttled" shown | Hot room, closed box, heavy 3D tab | Open the back door for airflow, rest on a tab with less 3D (settings), fit the stick-on heatsinks. The Pi slows itself to stay safe; it will not be damaged. |
| "under-voltage" shown in settings | Battery low or a power lead loose | Charge the battery; check the Pi's USB-C power lead. |
| Wrong date at start-up | The model restores the last saved date by design | TIME MACHINE → Today. |

## 10.8 Maintenance

### Updating the orrery software

1. On the builder's Mac, run the tests locally first (*test_pi.py* and *test_server.py*).
2. Run *pi/deploy.sh*. It copies the code to the Pi and runs the tests there; both should end with "all checks passed".
3. Restart the service (*sudo systemctl restart orrery*; this stops a run in progress) and reload the kiosk, or simply reboot the Pi.

The saved date, calibration and settings live in the *pi* user's home folder, not in *~/orrery*, so a deploy never erases them.

### Operating-system updates

Do updates (*sudo apt update* then *sudo apt full-upgrade*) only with the builder present and not just before an event: a kernel or desktop update can need a reboot, and afterwards the kiosk and pinch-to-zoom should be checked.

### Rebuilding the SD card

1. **First, back up** *~/.orrery_home.json* (the arm calibration) and *~/.orrery_settings.json* from the Pi if it still starts.
2. Write a fresh card as in software-design.md, "Building a Pi from scratch" (plug the card reader straight into the computer, not through a hub, which can be 100 times slower).
3. Put the card in the Pi and switch on; it joins the Wi-Fi by itself.
4. Run *pi/deploy.sh*, then *setup/install-kiosk.sh*. The Pi reboots into the orrery screen.
5. Copy the backed-up calibration and settings files back to the Pi's home folder and restart the service. Without them, put the model in travel mode and check the row; recalibrate any arm that is off (section 10.5).

### Routine checks

- Before each event: charge the battery overnight, check in travel mode that all planets are in a row, and check settings shows all eight servos connected.
- Now and then: look at the servo temperatures and currents on the settings screen while running; an arm drawing much more current than the others may be rubbing or binding.
- Keep cables strain-relieved inside the box; a bumped cable is the most common cause of a stopped planet.
