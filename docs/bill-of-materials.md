# 7. Bill of Materials

## 7.1 How to read this list

- The list shows what the finished model uses, as ordered. Most parts came from Amazon; the number in the "Part / ASIN or source" column is the Amazon product number (ASIN). Two tools came from Home Depot.
- "Owned" means the part was already in the house.
- Parts that were tried and dropped are in section 7.10, so you can skip them.

## 7.2 Motion: servos and driver

| Item | Part / ASIN or source | Qty | Notes / status |
|---|---|---|---|
| Feetech STS3215 serial-bus servo, 7.4 V / 19 kg, 6-pack | B0FQHCV9GP | 1 | In use: six of the eight planet servos. Each comes with a metal 25T disc horn, an idler disc, a bus cable and screws. |
| Feetech STS3215 servo, 7.4 V, 2-pack | B0FVS63YNN | 1 | In use: the other two planet servos. |
| Serial-bus servo driver board (USB and UART) | B0CTMM4LWK | 1 | In use. Connects the Pi (USB) to the one-wire servo bus; feeds 7.5 V to the chain. |
| Adjustable 3.5–12 V 5 A bench supply, LCD, 14 tips | B08BL55LMB | 1 | Bench supply for servo tests. Not in the finished model (it runs on the battery). |
| Servo bus cables, 8½ in | included with servos | 8 | In use, daisy-chained board → Mercury → … → Neptune. |
| Metal 25T servo disc horns | included with servos | 8 | In use: the servo gears bolt to them. Separate aluminium discs (B07D56FVK5) were not needed. |

**Servo count.** Eight servos are used, one per planet (IDs 1 Mercury to 8 Neptune). A spare or two is worth having: a spare stays at the factory ID 1 until it replaces one.

## 7.3 Electronics and power

| Item | Part / ASIN or source | Qty | Notes / status |
|---|---|---|---|
| Raspberry Pi 4B + microSD card | owned | 1 | In use: the brain. Runs the planet maths and the touchscreen app. |
| Freenove 7 in DSI touchscreen, glass front, 800 × 480 (FNK0078H) | B0FFG7259M | 1 | In use. Replaced the 5 in screen on 27 Sep 2026. Glass mounted on the front of the sloped panel with its own 3M tape. |
| Pi 4 stick-on heatsinks (20 pcs) | B07217N5LS | 1 kit | In use: one set of four on the Pi inside the closed box. |
| TalentCell 12 V 6000 mAh battery (66.6 Wh), YB1206000-USB | B00ME3ZH7C | 1 | In use. Runs the model about 2–3½ h with the planets turning non-stop; runs while charging. Charger and DC Y-splitter included. |
| DROK 12 V → 7.5 V buck converter, 12 A, with voltmeter | B078Q1624B | 1 | In use: powers the servos. Set to 7.5 V before connecting. |
| 12 V → 5 V 5 A buck converter, USB-C lead | B0CRVW7N2J | 1 | In use: powers the Pi and, through it, the screen. |
| DaierTek 20 mm round rocker switch, 2-pin, no light (5-pack) | B07S1MV462 | 1 pack | In use: the box's on/off switch (one of five). |
| 5.5 × 2.1 mm panel-mount DC socket extension | B0D45MGRZL | 1 | In use: charging socket in the left wall. |
| 18 AWG red/black silicone wire, 30 ft | B07FMRDP87 | 1 | In use: 12 V and 7.5 V wiring. |
| WAGO 221 lever connectors, 12 pc | B0CJ5QF4Z2 | 1 | In use: splits the 12 V rail to both converters, no soldering. |
| M3 nylon standoff kit, 320 pc | B07TP2YYQB | 1 | In use: converters and driver board off the walls and floor. |
| VELCRO heavy-duty strips, 4 × 2 in, 8 sets | B09BNPX3XJ | 1 | In use: holds the battery; cable runs. |
| USB-A to USB-C data cable | owned | 1 | In use: Pi to driver board. |

## 7.4 Centre column: tubes and rod

| Item | Part / ASIN or source | Qty | Notes / status |
|---|---|---|---|
| K&S #3400 brass telescoping tube assortment, 12 tubes × 12 in, 1/16–13/32 in, 0.014 in wall | B07VLNMCRC | 1 | In use: the eight largest tubes (3/16–13/32 in) are the planet tubes. Four small sizes spare. No spare pack was bought. |
| 1/8 in × 16 in 304 stainless rod, 10 pcs | B0DYK9ZK3G | 1 | In use: one is the Sun post, uncut. Nine spare. |
| Du-Bro 139 1/8 in shaft collars, 4-pack | B0006N6N4I | 1 | In use: one carries the column, top 2 3/16 in above the floor. Three spare. |
| Nylon washer assortment M2–M12 | B0G1SVH6KP | 1 | In use: washers under the tube ends (some drilled out), ⅜ in stack under Neptune, M2 spacers under the servos, M3 under the foot screws. |
| 3-IN-ONE multi-purpose drip oil, 4 oz | B0002YVAIK | 1 | In use: one drop between tubes. |
| Thread-seal (PTFE) or masking tape | household | — | Takes up Mercury's play on the rod. |

## 7.5 Gears

| Item | Part / ASIN or source | Qty | Notes / status |
|---|---|---|---|
| Gobricks GDS-1099 Technic gear, 40 tooth, module 1, ABS, 10 pcs | B0CWLT3RHK | 2 packs | In use: the 16 planet gears come from these 20. Spares kept. |
| 16-pc Technic gear pack including 4 × 40T | B0CM6R626Q | 1 | Used for early gear tests; the four 40T gears are spares. 24 × 40T on hand in total. |
| M3 stainless screw kit, 6–20 mm, with nuts and washers, 400 pc | B0CNJW37NJ | 1 | In use: 4 × M3 × 10–12 mm per servo gear (32), and the M3 × 16 foot screws. |
| 5-minute epoxy | owned | — | Gears to tubes, Sun post to base, arm rods, magnets, planets. More needed (supply ran low). |

## 7.6 Structure: enclosure, stands and hardware

| Item | Part / ASIN or source | Qty | Notes / status |
|---|---|---|---|
| KINLINK clear cast acrylic 12 × 12 × ⅛ in, 4-pack | B0BYSHVDDL | 1 | In use: sides, back door, stand plates. |
| CALPALMY clear acrylic 12 × 12 × ¼ in, 2-pack | B085L5V796 | 1 | In use: base; magnet blocks from the second sheet. |
| Robosource clear polycarbonate 12 × 12 × ⅛ in | B07VVGL6GV | 2 | In use: sloped front and ceiling (replaced acrylic, 7–10 Nov 2026). **To check:** The design notes mention four sheets on hand on 10 Nov and two more ordered; only two are counted here. |
| Berkland acrylic cement, 4 oz, with needle applicator | B0DS69HMN6 | 1 | In use: acrylic joints. Test on polycarbonate first. |
| QIATOL M5 × 250 mm stainless threaded rod, 4-pack | B0GJ4KDR8X | 2 | In use: 16 stand rods cut from 7 rods; one rod spare. |
| uxcell M5 knurled thumb nuts, 20-pack | B0D7PWB5QV | 1 | In use: 16 height adjusters. |
| Swpeet M5 nuts and washers, 150 pc | B0B1DXSWNR | 2 | In use: rod nuts above and below the base, lock nuts, ¼ in SAE washers. |
| LBY M2–M3 self-tapping screw assortment, 600 pc | B07GL2WLDD | 1 | In use: four M2 × 10 mm per servo (32), servo to plate. |
| Neodymium disc magnets 8 × 3 mm, 40-pack | B09QY94RBP | 1 | In use: 8 for the back door. |
| Antrader rubber feet, 1 × 0.6 in, 24-pack | B07FR2V9KD | 1 | In use: 4 feet. |

## 7.7 Arms

| Item | Part / ASIN or source | Qty | Notes / status |
|---|---|---|---|
| True Position Tools aluminium split-ring stop collars, 8-pc set, 1/8–1/2 in | B06XTD5KXB | 2 | In use: one collar per tube top (arm hubs). 1/8 and 1/2 in spare. |
| K&S 506 music wire, 3/32 in × 36 in, 10 rods | B0006MZN9K | 1 | In use: arm rods and uprights, about 10½ ft of 30 ft. |
| AQUANEAT aquarium air-line connectors, 40 pc (10 elbows used) | B08LMZ86QC | 1 | In use: the 90° joint at each arm's tip. |
| Electrical tape | household | — | One wrap under the three loose collars. |

## 7.8 Planets and paint

| Item | Part / ASIN or source | Qty | Notes / status |
|---|---|---|---|
| FFchuanhe polystyrene balls, 60 pc, 0.79–2.4 in, with brushes and palette | B0B862S9SX | 1 | In use: all eight planets; many spares. |
| Polystyrene balls 4 in, 2 pc | B0H5JC5NJ1 | 1 | In use: the Sun, plus a spare. |
| Caliart acrylic paint set, 24 colours, 12 brushes | B08BNNV3JY | 1 | In use: every planet colour straight from the bottle. |
| OISAKLD 2 mm EVA craft foam, 10 sheets 9 × 12 in | B0BXKJ4CD3 | 1 | In use: rings for Saturn, Uranus and Neptune. |
| White or tacky glue, bamboo skewers | household | — | Rings, painting handles. |

## 7.9 Tools

| Item | Part / ASIN or source | Qty | Notes / status |
|---|---|---|---|
| Mini tube cutter, 1/8–1⅛ in | B0947KCVJC | 1 | Cut the brass tubes. |
| 29-piece HSS drill bit set, 1/16–1/2 in by 64ths | B0B5XGRV2S | 1 | Gear bores, washers, panel holes. |
| T-handle tapered reamer, 1/8–1/2 in | B0BXG6QZKB | 1 | Eases gear bores and washers. |
| Acrylic scoring knife | B08Y7RZ1WD | 1 | Short cuts only (stand plates). |
| NEIKO step drill bit ⅛–½ in | B001CBNPBW | 1 | Charging socket and other panel holes. |
| ZELCAN step drill bit ¼–1⅜ in | B076QC5BWR | 1 | Switch hole, finger hole. |
| Knipex CoBolt 71 01 200 compact bolt cutter | B000SOSC4Y | 1 | Cuts the music wire and M5 rod. |
| Dremel 3100 rotary tool kit | Home Depot SKU 1011141921 | 1 | Cuts all box panels and the screen opening. |
| Dremel 565 multipurpose cutting kit (guide + ⅛ in spiral bits) | Home Depot SKU 257429 | 1 | Bought with the 3100. |
| Deburring tool / round file, hacksaw, drill, calipers, steel ruler, square, clamps, safety glasses | owned | — | General workshop tools. |

## 7.10 Tried and not used

| Item | Part / ASIN or source | Qty | Notes / status |
|---|---|---|---|
| Freenove 5 in DSI touchscreen (FNK0078) | B0B455LDKH | 1 | Replaced by the 7 in screen: bigger and easier for kids to use. |
| KY-040 rotary encoders, 5-pack | B07F26CT6B | 1 | Date knob dropped: the touchscreen does everything. |
| Aluminium knob, 44 × 25 mm | B099DHHGGQ | 1 | Dropped with the encoder. |
| M3 self-tapping screws, 200 pc | B09DB4NYF7 | 1 | Not needed: the servos take M2 screws. |
| ELEGOO jumper wires, 120 pc | B01EV70C78 | 1 | Not needed: nothing is wired to the Pi's pins. |
| Bob Smith thin CA glue, 1 oz | B01MZY4X9D | 1 | Not needed (was for a rod sleeve that was dropped). Never use CA on foam: it melts it. |
| Arduino Mega, 16×2 LCD, DS3231 clock, brass MOD 0.8 gear, aluminium servo discs | various | — | Considered, never bought (replaced by the Pi, the touchscreen, Wi-Fi time, Technic gears and the servos' own discs). |
