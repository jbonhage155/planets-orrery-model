# 4. Mechanical Design

This section describes the physical model as it stands on 14 November 2026: the centre column, the gears, the servos and their stands, the arms, the planets and the clear box. All sizes are in inches unless they say mm. Heights are measured from the top face of the base plate (the floor inside the box) unless stated otherwise.

The design changed several times over two months. Where it helps, a short note says what a figure replaced. Items still to be measured or confirmed are marked **To check:**.

## 4.1 Overall layout and envelope

The model is a clear box with a column standing up out of its top. The Sun sits on the top of the column. Eight arms, one per planet, reach out from the column. Each arm is turned by its own motor (servo) inside the box. A 7 in touchscreen is set into the sloped front of the box, facing up at a child standing at the table.

The column stands **2¼ in behind the middle of the box** (3¾ in from the back edge, 6 in from either side). This keeps the outer arms from swinging far out over the screen, where hands reach in.

| Item | Size | Notes |
|---|---|---|
| Box footprint | 12 × 12 in | Chosen so the model fits on a desk or shelf. A 12 × 16 in box was considered and dropped. |
| Box height (inside) | 6¾ in, floor to ceiling underside | 11 Nov 2026 redesign. Replaced 7.85 in (Oct), 8½ in (18 Oct, nine planets) and 6½ in (Sept). |
| Box height (outside) | about 7⅛ in | ¼ in base + 6¾ in walls + ⅛ in ceiling (computed). |
| Feet | 0.6 in tall, 1 in across | Four rubber feet, bolted on. |
| Column | 13/32 in across at its widest | Eight nested brass tubes on a 1/8 in steel rod. |
| Tube tops above the floor | 8¼ in (Neptune) to about 12½ in (Mercury) | Neptune measured; the others estimated from the 3D model. |
| Sun | 4 in foam ball | Centre level with the planets, about 14½ in above the floor (design figure). |
| Table to top of the Sun | about 17 in | Design figure, 20 Oct 2026. |
| Planet sweep | 43½ in circle | Neptune's orbit radius is 21 in. Neptune passes about 13½ in in front of the box, 16 in past each side and 18 in behind it. Leave that much clear space. |
| Screen | 7 in touchscreen in the sloped front | Front panel leans back 37.1° from upright (was 35° in the Sept design). |

**Eight planets, not nine.** The first design had nine planets including Pluto. On 19 October 2026 Pluto was dropped from the physical model. The servo ring keeps its nine positions, with Pluto's position left empty. Pluto still appears in the touchscreen's 3D views and facts.

## 4.2 Key design rules

1. **1:1 gearing.** The servo gear and the tube gear are the same 40-tooth gear. One turn of the servo is one turn of the planet. The servo's angle *is* the planet's angle, so no conversion or gear ratio enters the software.
2. **Positions, not speeds.** The computer works out where each planet is for the chosen date and sends each servo to that angle. A speed error would add up forever; a position error cannot.
3. **The servos know where they are at power-on.** Each STS3215 servo has a 12-bit magnetic encoder (4096 steps per turn, about 0.09°). It reads its own shaft angle the moment it powers up. Because the gearing is 1:1, the model knows where every arm points without a homing sweep. Nothing drifts, and an arm that is bumped is put back. The servos run in multi-turn mode, so a planet can keep going round; the software re-anchors the turn counter before it runs out (about ±7 turns).
4. **The longer the arm, the lower it sits.** Neptune's arm is lowest and Mercury's highest, so arms can never hit each other.
5. **Every tube is shorter than the one inside it.** Each tube shows a bare end at the bottom (for its gear) and at the top (for its arm).
6. **Never pinch a tube.** The brass walls are only 0.014 in thick. No set screws, dimples or pins on the tubes. Gears are a snug slide, not a press fit. Arm collars are tightened only until snug. A pinched tube grips the tube inside it and two planets turn together.
7. **A slippery layer between tubes.** A nylon washer sits under every tube end except Mercury's. A drop of light oil between tubes. Oil, never grease: grease adds drag and collects dust in the tiny gaps.
8. **Neighbouring servos are far apart in height.** A servo body is 1.38 in tall but the gear levels are only ½ in apart. Servos next to each other round the ring are placed four or more levels apart so a servo body never dips into its neighbour's gear.
9. **Arms clamp on, they are not glued to the column.** A grabbed planet slips instead of straining a servo, nothing can glue two tubes together, and the arms come off for transport.
10. **Light planets.** Foam balls weigh well under a gram to a few grams. The inner arms move fast, and Mercury's thin tube and the glue joints are the weak points.
11. **Nothing that melts foam touches a planet.** Super glue (CA), acrylic cement and spray paint all melt polystyrene.
12. **A clear box.** Visitors can see how the model works.

## 4.3 The centre column

### How it is built

A fixed **1/8 in stainless steel rod** (the Sun post) stands in the middle. Its foot is epoxied 3/16 in deep into a 1/8 in hole drilled part-way into the base (not through), 6 in from either side and 3¾ in from the back edge. It is left uncut at its full 16 in length, so its tip is about 15 13/16 in above the floor. The extra length goes up inside the Sun.

Eight brass hobby tubes (K&S telescopic tubing, 0.014 in wall) slide over the rod, one inside the next like a telescope. Each size is 1/32 in bigger than the one before, so each tube is a loose, oiled sleeve on the one inside it and can turn on its own. Mercury's tube is the innermost and longest; Neptune's is the outermost and shortest.

A **1/8 in shaft collar** (Du-Bro 139) is clamped on the rod with its top **2 3/16 in** above the floor. It carries the whole stack. Mercury's tube stands on the collar, with its gear glued flush with the tube's bottom end and no washer. Every other tube stands on the gear of the tube inside it, with a nylon washer between. To raise or lower the whole stack, loosen the collar's set screw and slide it.

The rod is about 1/32 in narrower than the inside of Mercury's tube. That play is taken up with a few wraps of thread-seal (PTFE) tape on the rod, just above the collar and near Mercury's top, until the tube has no side play but still turns freely. (A 5/32 in brass sleeve over the rod was planned until 24 Oct 2026; it would not fit over the real rod.)

### How each tube is driven

Each planet has its own drive chain:

1. The servo stands on its stand inside the box and never moves.
2. A 40-tooth gear is bolted to the servo's output disc.
3. It meshes with a matching 40-tooth gear glued to the **bottom** end of that planet's tube.
4. The whole tube turns.
5. The arm clamped to the **top** end of the same tube swings, and the planet moves.

The other seven tubes stay still. The eight tube gears form a staircase inside the box: Mercury's lowest, Neptune's highest.

### Tube sizes and cut lengths

The eight largest tubes in the K&S assortment are used, every size in order. The four smallest (1/16, 3/32, 1/8 and 5/32 in) are spare. Each tube was cut once with a mini tube cutter, Neptune first (an easy practice cut) and working in to Mercury. After every cut the inward lip was reamed until the next smaller tube slid through under its own weight.

| Planet | Tube (outside) | Cut length | Washer under it (from the M2–M12 nylon kit) | Gear bottom above floor (as built) | Tube top above floor (approx.) |
|---|---|---|---|---|---|
| Sun post | 1/8 stainless rod | uncut, 16 in (406 mm) | — | — | 15 13/16 |
| Mercury | 3/16 | 10⅛ in (257 mm) | none (stands on the collar) | 2 3/16 | 12½ |
| Venus | 7/32 | 9 3/16 in (233 mm) | M5, as it comes | 2 11/16 | 11¾ |
| Earth | 1/4 | 8 1/16 in (204 mm) | M5, drilled to 7/32 | 3 3/16 | 11⅛ |
| Mars | 9/32 | 6⅞ in (175 mm) | M6, as it comes (snug) | 3 11/16 | 10½ |
| Jupiter | 5/16 | 5¾ in (146 mm) | M6, drilled to 9/32 | 4 3/16 | 9⅞ |
| Saturn | 11/32 | 4 9/16 in (117 mm) | M6, drilled to 5/16 | 4 11/16 | 9⅛ |
| Uranus | 3/8 | 3 7/16 in (87 mm) | M8, drilled to 11/32 | 5 3/16 | 8½ |
| Neptune | 13/32 | 2 5/16 in (58 mm) | M8, drilled to 3/8, plus ⅜ in of extra washers | about 6 3/32 | 8¼ (measured) |

Notes on the table:

- A washer has to slide over the tube inside and be stood on by the tube outside, a window of only 1/32 in. Most metric washers miss it, so a washer one size small is drilled out to the inner tube's size, clamped between two scraps of wood.
- Tube tops other than Neptune's are estimates from the 3D model (±⅛ in). **To check:** Measure Uranus's tube top; the model puts it near 8.53 in.
- Neptune's gear height: it was about 5 23/32 in on 7 Nov. On 8 Nov ⅜ in of washers went under Neptune's tube to lift its top clear of the lid, which lifts its gear by the same amount, to about 6 3/32 in (computed). **To check:** Measure.

### The ½ in levels, as built (7 November 2026)

The design spaced the gear levels 0.65 in apart, assuming gears with an 8 mm hub. The real gears are only about **4 mm** thick. The builder set each gear in the stack with calipers, **8.5 mm** from the top of the gear below to its own bottom face (a nylon washer in that gap), marked the tube there and epoxied the gear on the bench. With 4 mm gears, 8.5 mm gaps make the levels **½ in** apart (Mercury to Uranus, 3 in). Neptune's gap was opened to 12.5 mm so its stand plate clears the screws on Mars's servo gear.

The tubes, box design and stand rods had already been cut for the 0.65 in design and were kept. So the gears step ½ in, but the tube tops (and arms) step about 0.65 in. The only effect is spare rod above the stand nuts and a little extra tube above each gear.

**Neptune and the lid (7–8 Nov 2026).** With the lower gears, Neptune's tube top came out at 7⅞ in, too close to the lid as it was then drawn (7.6 in) to leave room for its arm. Rather than cut a new tube, ⅜ in of nylon washers went under Neptune's tube (the most allowed, so Neptune's arm does not crowd Uranus's). Its tube top is now **8¼ in**, and its stand was raised to match. Since 11 Nov the ceiling is lower still (6¾ in), so Neptune now has plenty of room.

### What holds the column upright

The column is held at its foot by the epoxied Sun post. The stack is kept from floating up by the arm collars: a collar on top of Mercury's tube stops the stack rising, Uranus's collar sits just above Neptune's tube top, and each arm's collar and weight hold the tube below it down. A separate climbing-stop collar under the lid on Neptune's tube was planned on 7 Nov and dropped on 11 Nov.

The ceiling has a ¾ in slot round the column, which leaves about 11/64 in of play each way. Since 11 Nov it is **no longer a bearing** for the top of the column. (Before that, a 13/32 in hole reamed in the lid was the column's top bearing.) **To check:** The older stands notes said the 16 in rod flexes without a top bearing and uses the lid's hole as a temporary top support while meshing gears, and the arms page says "keep the lid: it holds the top of the column". Confirm the column runs true with only the slotted ceiling, or add a top support.

### Column risks and fixes

| Risk | Fix |
|---|---|
| Tubes bind. A tube cutter rolls a lip inward on every cut. | Ream every cut end until the next size down drops through under its own weight. Never use a dented tube. |
| One tube drags its neighbour. | The servos hold position and correct it. Light oil between tubes, never grease. |
| A gear slips on its tube. | Epoxy inside the bore and in the gear's moulded slots, which key it so it cannot spin. |
| Arms sag or wobble. | About ¾–1 in of sag at Neptune's tip (estimate), accepted. Speed ramps in software for wobble. |
| Column leans. | Post epoxied square in the base, checked from two sides while it set. See the (to check) above. |

## 4.4 Gears

### The gear chosen

The servo has no gear teeth of its own, only a splined output shaft. So the two gears only have to match each other. Both are the same **module-1, 40-tooth, LEGO Technic-pattern ABS gear** (part 3649 pattern). This was decided on 20 September 2026, replacing the plan to 3D-print gears. No 3D printer was bought.

| Property | Value |
|---|---|
| Module / teeth | Module 1, 40 teeth. 40:40 gives 1:1. |
| Pitch diameter = centre distance | 40.0 mm = **1.575 in**. Each servo shaft sits 1.575 in from the column's centre. |
| Outside diameter | about 41.6 mm (1.64 in) |
| Thickness | about 4 mm as built (the design assumed an 8 mm hub) |
| Tooth height / overlap | 2.25 mm tall; at 40.0 mm centres the teeth overlap by about 2 mm |
| Material | ABS, injection moulded. Takes epoxy and CA, unlike acetal or nylon. |
| Centre hole | Cross-axle hole, smaller than every tube; drilled out to each tube's size |
| Largest possible bore | 11.2 mm (7/16 in) before it breaks into the four holes 8 mm out (holes 4.8 mm across) |
| Weight | 3.6 g |
| Quantity | 16 used (8 servo + 8 tube); 24 on hand, 8 spare |

Why this gear: injection-moulded teeth are better than a print, ABS glues, and one part covers every tube size. Rejected: brass MOD 0.8 servo gears (about $180 for 18), RC-car spur gears (32 pitch is module 0.794 and cannot mesh with module 1), and acetal or nylon gears (nothing glues to them).

### Tube gears: bore per planet

Every tube gear is drilled to its own tube's size with the matching bit from a 29-piece fractional set (1/64 in steps), slowly, with the gear clamped flat. A tight hole is eased with a tapered reamer from both faces so it stays straight. The aim is a snug slide, not a press fit.

| Planet | Tube | Bore | Drill | Plastic left at the four holes |
|---|---|---|---|---|
| Mercury | 3/16 | 4.76 mm | 3/16 | 3.2 mm |
| Venus | 7/32 | 5.56 mm | 7/32 | 2.8 mm |
| Earth | 1/4 | 6.35 mm | 1/4 | 2.4 mm |
| Mars | 9/32 | 7.14 mm | 9/32 | 2.0 mm |
| Jupiter | 5/16 | 7.94 mm | 5/16 | 1.6 mm |
| Saturn | 11/32 | 8.73 mm | 11/32 | 1.2 mm |
| Uranus | 3/8 | 9.52 mm | 3/8 | 0.8 mm |
| Neptune | 13/32 | 10.32 mm | 13/32 | 0.4 mm (the bore just touches the holes; epoxy fills them) |

### Fixing gears to tubes

- 5-minute epoxy goes **inside** the bore and into the eight moulded slots round it, never on the faces. The slots act as a key.
- Both faces stay flat and clean: the next tube's washer sits on the top face, and the bottom face is close to the washer below. A fillet of glue could lift a tube or glue two planets together.
- Masking tape round the tube on each side of the gear, faces wiped with alcohol, tape peeled before the epoxy sets.
- All gluing done on the bench, one tube at a time, before anything goes in the box.

### Fixing gears to the servos

Each servo came with a metal 25-tooth disc horn (about 20 mm across, four M3 tapped holes on a 14 mm circle). The servo gear is bolted to this disc with four **M3 × 10 or 12 mm screws**, each with a washer, through the gear's own 4.8 mm holes. The gear's holes are 8 mm out and the disc's are 7 mm out, so the screws bear on the inner edges of the gear's holes, which tends to centre the gear. Before mounting, each servo gear is spun on the bench and nudged until its wobble is small. **To check:** Sources differ on how much sideways adjustment this leaves (one set of build notes says about ±0.9 mm, another almost none).

### Setting the mesh

- **Budget.** The gears run smoothly until the teeth have pulled apart by about ¾ mm (0.03 in). The total wobble of both gears plus any play in the tube must stay inside that. A gear with more than about 0.65 mm of swing is replaced from the spares.
- **Matching high spots.** Each gear's high spot is marked with a dot. Because the pair is 1:1, the same teeth meet on every turn, so meshing the dots as mirror images makes the two wobbles cancel instead of add.
- **Height.** A steel ruler is laid across both gears' top faces and the stand's two thumb nuts are turned until it sits flat on both.
- **Distance.** A strip of printer paper is held between the teeth and the servo is moved in until the paper is just gripped. That leaves about a paper's thickness of clearance at the tight spot.
- **Test.** Slow and fast runs (up to Mercury's top speed of about 20 rpm), listening for clicks, jumps or a groan once per turn. Seen from above, a tube must turn anticlockwise when its planet moves forward; if not, a software setting is flipped.

**Slotted mounts.** The September design called for slotted screw holes so each servo could be slid in to set the mesh. As built, the stand plates have **snug round holes, no slots**. If a servo needs to move toward or away from the column, both its rod holes are eased a little in that direction with a deburring tool or rolled sandpaper.

**Backlash.** Technic teeth are moulded with generous backlash. Expect a little more than 1° of slack when a planet reverses: a small jog, not drift, because the servos hold absolute position.

## 4.5 Servos and servo stands

### The servo

Each planet has one **Feetech STS3215** serial-bus servo (7.4 V, 19 kg·cm, labelled 1:345 gear ratio), run at 7.5 V. Its body is 1.78 × 0.97 × 1.38 in. All eight are chained on one three-wire bus (ground, power, signal) with the 8½ in cables that come with them. Each has its own ID number: 1 Mercury through 8 Neptune. The gearbox is 345:1, so a servo (and a meshed tube) cannot be turned by hand.

### The servo ring

The servos stand in a ring round the column, shafts 1.575 in from its centre. The ring has **nine positions 40° apart**; Pluto's is left empty. Eight servos spaced evenly (45°) were tried in every order and fitted worse (0.11 in best clearance against 0.22 in). Neighbours round the ring are four or more gear levels apart.

Seen from above, going anticlockwise from the front of the box:

| Position | 1 (front) | 2 | 3 (right) | 4 | 5 | 6 (back) | 7 | 8 (left) | 9 |
|---|---|---|---|---|---|---|---|---|---|
| Planet | Mercury | Jupiter | empty | Mars | Neptune | Earth | Uranus | Venus | Saturn |

The ring is turned this way so the tall stands stay out from under the screen.

### The adjustable stand

Each servo sits on a small screw-jack stand whose height is set by turning a nut:

- **Plate:** 2 × 1⅞ in, ⅛ in clear acrylic, under the whole servo, running 5/32 in past its far end so the far screw holes are ¼ in from the edge (closer and acrylic cracks).
- **Servo to plate:** four M2 × 10 mm self-tapping screws up through 7/64 in holes in the plate into the servo's four Ø1.6 mm holes (a 24.45 × 20.5 mm rectangle). M2 nylon washers on each screw fill the 1/16 in gap between the plate and the servo's holes. (M3 screws were planned until 25 Oct 2026; they will not start in the servo's holes.)
- **Rods:** two M5 stainless threaded rods beside the servo's outer end, standing in the base with a nut on top of the base and a washer and nut underneath.
- **Height:** a knurled thumb nut under the plate (0.8 mm per turn), with a ¼ in SAE washer. A plain lock nut on top, no washer (no room beside the servo).
- **Rod holes:** 13/64 in, 0.42 in from the plate's far edge, **1⅜ in apart** on the plate. The base holes are 1.3 in apart; the rods are eased apart about 1/32 in to take the plate and spring back to grip it. (1.3 in on the plate put the top nut's corners against the servo.)
- **Base holes:** 16 holes, 13/64 in, drilled through a full-size paper template centred on the Sun post.
- **Cables:** plugged in before the servo is screwed down; they lie flat under it and leave from its sides. The chain runs driver board → Mercury → Venus → … → Neptune, each cable along its plate's edge and round the **outside** of the ring to the next plate (about 6.9 in needed per hop, so about 1½ in of slack).

| Servo ID | Planet | Plate top above floor (as built, ½ in levels) | Rod length, each of two (as cut) |
|---|---|---|---|
| 1 | Mercury | about 0.67 | 35 mm |
| 2 | Venus | 1.17 | 51 mm |
| 3 | Earth | 1.67 | 68 mm |
| 4 | Mars | 2.17 | 84 mm |
| 5 | Jupiter | 2.67 | 101 mm |
| 6 | Saturn | 3.17 | 117 mm |
| 7 | Uranus | 3.67 | 134 mm |
| 8 | Neptune | about 4.19, then raised with Neptune's tube | 150 mm |

The rods were cut for the 0.65 in design (rod length = plate height + 0.8 in), from seven 250 mm rods: 150 + 84 (×2), 134 + 101 (×2), 117 + 117, 68 + 68 + 51 + 51, and 35 + 35. With ½ in levels the plates sit lower than the rods were cut for, which only leaves spare rod above the nuts. **To check:** Neptune's plate height after its ⅜ in raise on 8 Nov (about 4 9/16 in if raised the full amount) is not recorded.

**Closest clearances** (3D model fit check at ½ in levels): the M3 screws on Mercury's, Venus's and Earth's servo gears pass 0.05 in from the stand plates four positions up (Jupiter, Saturn, Uranus). If one touches, a corner is snapped off that plate or the screw washers are left out. Every gear, tube and servo body otherwise clears.

## 4.6 Arms

Each arm is an L: out from the column, then up to the planet. It has four parts:

1. **Collar:** an aluminium split-ring stop collar clamped on the top of the planet's tube (7 Nov 2026; replaced a loop of wire round the tube, because the 3/32 in music wire is too stiff to bend a tight loop).
2. **Arm rod:** a straight piece of 3/32 in steel music wire, epoxied 3/16 in deep into a 3/32 in hole drilled radially through the collar's solid side (opposite the split).
3. **Elbow:** an aquarium air-line elbow at the orbit radius, the 90° joint between the arm and the upright (8 Nov 2026; the wire is not bent). Its bore is about 3 mm for the 2.4 mm wire; gel super glue or 5-minute epoxy fills the gap. Each weighs under 1 g.
4. **Upright:** a short straight piece of the same wire, up into the planet.

Arms are not epoxied to the column (decided 9 Nov 2026). The rod is epoxied into its collar on the bench, with the collar's bore plugged by a scrap of the same tube and the far end propped level. The collar then goes on its tube with only its clamp screw, tightened until snug. The direction it points does not matter: the software's home calibration takes care of it.

| Planet | Tube | Collar | Fit | Orbit radius | Arm rod cut length (calculated) |
|---|---|---|---|---|---|
| Mercury | 3/16 | 3/16 | exact | 3½ | 3 5/16 |
| Venus | 7/32 | 7/32 | exact | 5 7/16 | 5 3/16 |
| Earth | 1/4 | 1/4 | exact | 7½ | 7¼ |
| Mars | 9/32 | 5/16 | 1/32 loose | 9½ | 9¼ |
| Jupiter | 5/16 | 5/16 | exact | 12 3/16 | 11 15/16 |
| Saturn | 11/32 | 3/8 | 1/32 loose | 15 7/16 | 15 1/16 |
| Uranus | 3/8 | 3/8 | exact | 18 5/16 | 17 15/16 |
| Neptune | 13/32 | 7/16 | 1/32 loose | 21 | 20⅝ |

Cut length = orbit radius − distance from the column's centre to the rod's inner end − elbow offset, rounded to the nearest 1/16 in (halfway rounds up). The figures above assume the rod goes 3/16 in into the collar and an elbow offset of ⅛ in. **To check:** The elbow offset is to be measured on a real elbow before cutting; the lengths change with it. Mercury's collar wall was assumed (3/16 in), not measured.

- **Collars:** two 8-piece sets (1/8–1/2 in) supply two 5/16, two 3/8, two 7/16 and one each of 3/16, 7/32 and 1/4. The three loose ones (Mars, Saturn, Neptune) get one wrap of electrical tape on the tube under the collar, ends butted, kept inside the collar's ⅜ in band.
- **Uranus and Neptune:** Neptune's tube top is only about ¼ in below Uranus's, so Uranus's collar overhangs its own tube top by about ⅛ in. Its arm hole is drilled below the collar's middle (at most g − ⅛ in above the collar's bottom, where g is the gap between the two tube tops) so the rod still meets Uranus's tube. Neptune's collar sits lower on its tube, with its arm about ½ in under Uranus's. **To check:** Neptune's final arm height was being reset for the lower 11 Nov ceiling; the 3D model (model-3d/) shows a ½ in placeholder.
- **Material:** K&S 506 music wire, 3/32 in × 36 in rods. The eight arms and uprights use about 10½ ft of the 30 ft bought. Neptune, Uranus and Saturn are cut first, one per rod; shorter arms and uprights come from what is left. The wire is cut with a compact bolt cutter.
- **Droop:** a long thin wire sags under its own weight and the planet's: about ¾–1 in at Neptune's tip and about ½ in at Uranus's (rough estimate). The builder accepted this.
- **Uprights:** each upright is cut so its planet's centre lands level with the Sun's centre. The design figure is 2.3 in for Mercury (so Mercury's arm clears the Sun's underside by 0.3 in), each next planet ½ in longer, to 5.8 in for Neptune. **To check:** As built the arms step about 0.65 in rather than ½ in, so cut each upright to the measured height.
- **Travel mode (home position):** a button on the touchscreen sends every arm to point straight away from the screen, the planets in one row. Arms are clamped on in this position, and the model is carried in it.

## 4.7 The planets and the Sun

The planets are **polystyrene foam balls**, painted with brush-on acrylic craft paint. Foam was chosen because it is light (the inner arms move fast), soft if a moving arm meets a hand, and cheap. Ready-made planet sets were all too big, too small or all one size.

Planet sizes are not to scale with each other or with the distances; they were chosen as big as the spacing allows. The orbits were laid out on the floor with the real balls on 24 Oct 2026 so there is about **1 1/16 in of empty space** between every pair of neighbours, Sun to Mercury included.

| Body | Ball size | Orbit radius from column | Ring | Main colour | Details |
|---|---|---|---|---|---|
| Sun | 4 in | — | — | Medium Yellow | Orange swirls |
| Mercury | 0.79 in | 3½ | — | Grey | Tiny black crater dots |
| Venus | 1.0 in | 5 7/16 | — | Yellow Ochre | White cloud streaks |
| Earth | 1.0 in | 7½ | — | Cobalt Blue | Green land, white ice caps and clouds |
| Mars | 0.79 in | 9½ | — | Burnt Sienna | Burnt Umber patches, small white ice cap |
| Jupiter | 2.4 in | 12 3/16 | — | Titanium White | Ochre and Sienna stripes, red Great Red Spot |
| Saturn | 2.0 in nominal (1⅞ measured) | 15 7/16 | 3 in, ~½ in band, tilted 25° | Yellow Ochre | Thin white stripes |
| Uranus | 1.6 in nominal (1 9/16 measured) | 18 5/16 | 2¼ in, ~⅛ in band, nearly upright | Cerulean Blue | Almost plain |
| Neptune | 1.6 in nominal | 21 | 2¼ in, ~⅛ in band, tilted 28° | Cobalt Blue | Dark blue storm spot, white wind streaks |

- **Painting:** two thin base coats about 20 minutes apart (foam soaks up the first), then details with a sponge or dry brush. Every colour straight from the bottle, no mixing. Each ball is painted on a bamboo skewer, which also makes the hole for its upright.
- **Rings:** cut from 2 mm craft foam using a printed full-size template, the hole 1/16 in smaller than the ball so the foam grips. Saturn's ring slides over the ball to its middle (replacing an earlier plan to cut the ball in half). Uranus's and Neptune's are cut into a C shape that wraps round the ball, gap at the bottom round the upright. Glued with white or tacky glue, or epoxy.
- **Ring direction:** a planet keeps the same direction relative to its arm all the way round, so each ring is set once when the ball goes on its upright. Uranus's ring faces the Sun like a wheel rolling sideways. Saturn and Neptune tilt about the direction of travel. With rings set this way, the tightest gap is about ⅝ in (Saturn's ring to Uranus). **To check:** The rings template (14 Nov) says the edge toward the Sun goes *up*; the arms page says the low edge points in along the arm. Follow the newer rings page unless decided otherwise.
- **Fixing:** each ball is pushed onto its upright with 5-minute epoxy or white glue. Never super glue, acrylic cement or spray paint: they melt polystyrene.
- **The Sun:** a straight pilot hole is made first, about 3½ in deep, then the ball is pushed down over the rod tip until its bottom is about ⅛ in above Mercury's tube, checked level with the planets and glued at the bottom with epoxy or white glue. If it sits too high, the rod is trimmed with the bolt cutter.

## 4.8 The box (enclosure)

The box is **clear** so visitors can see the mechanism. The base is ¼ in cast acrylic. The sides are ⅛ in acrylic. The sloped front and the ceiling are ⅛ in **polycarbonate**, which bends instead of cracking, so long cuts and the screen opening are safe. Every cut is made with a Dremel 3100 rotary tool, a Dremel 565 cutting guide and a ⅛ in spiral bit run along a clamped straightedge, at about 15,000–20,000 rpm (dial 4–6). Score-and-snap was tried for long cuts in acrylic and ran off the line, so it is used only for short cuts such as the stand plates.

**Revision.** The box below is the **11 November 2026** design: a lower ceiling, one sloped front panel from floor to ceiling, and a ceiling that slides out the back. It replaced a 7.85 in tall box with a short upright front wall, a separate 5 in sloped strip at 35° and a lift-off lid with a hole for the column.

### Cut list

| Panel | Material | Size | Notes |
|---|---|---|---|
| Base | ¼ in acrylic | 12 × 12 | Everything stands on it. Sun post hole: 1/8 in, 3/16 in deep (not through), 6 in from either side and 3¾ in from the back edge. 16 stand-rod holes, 13/64 in, from the paper template. Four 1/8 in feet holes, 0.9 in in from both edges at each corner. |
| Sides ×2 | ⅛ in acrylic | 12 deep × 6¾ tall | Stand on the base, flush with its edges. Front corner cut along the slope: from 3/32 in back at the floor to 5 3/16 in back along the top edge. Left side carries the switch and charging-socket holes (section 4.9). Right side gets standoff holes for the converters, marked from the parts. |
| Sloped front | ⅛ in polycarbonate | 8⅜ × 12 | One piece, with the screen opening already cut. Stands on the base, outside face flush with the base's front edge, and leans back **37.1° from upright** until its top corner meets the ceiling (about 5 1/16 in back from the front edge, computed). Covers the sides' sloped edges and is glued to them. No separate front wall. |
| Screen opening | (in the front panel) | about 6 11/16 × 4 1/16 | The size of the screen's metal tray plus 1/32 in. Cut small and filed to fit. Drilled ¼ in at each corner, then four straight cuts hole to hole from a full-size template. |
| Ceiling | ⅛ in polycarbonate | 12 wide × 6 15/16 deep | **Not glued.** Lies on the side walls' top edges and the front panel's top corner, and slides out the back. A ¾ in wide slot runs from its back edge to a ¾ in round end at the column (3¾ in from the back, 6 in from the side), so it clears the column and the tubes need not be perfectly upright. |
| Back door | ⅛ in acrylic | 11 11/16 × 6 23/32 | **Lift-off**, held by four pairs of magnets. Sits between the sides, on the base and under the ceiling, flush with the back edges. 1 in finger hole on the middle line, 0.9 in below its top edge (step bit). Length trimmed to the real opening once the sides are glued. |
| Magnet blocks ×4 | ¼ in acrylic (or two ⅛ in scraps) | ¾ × ¾ | Glued into the four inside corners of the back opening, back faces 0.36 in in from the back edge (door ⅛ in + two 3 mm magnets) so the door lands flush. Top blocks' tops below 6¾ in. |
| Magnets ×8 | neodymium, 8 × 3 mm | — | Epoxied (acrylic cement does not hold metal): one on each block, one on the door opposite each. Each pair checked to attract before gluing. |
| Stand plates ×8 (+4 spare) | ⅛ in acrylic | 2 × 1⅞ | From a 4 11/16 in strip off the back-door sheet (section 4.5). |

### The screen in the sloped front

The screen is a Freenove 7 in touchscreen (800 × 480, capacitive) with a black glass front, 7⅝ × 4⅜ in. Its metal tray behind the glass is smaller (about 6⅝ × 4.0 in). The screen goes in **from the front** (9 Nov 2026): the tray and the Raspberry Pi bolted to it pass through the opening, and the glass lip sticks to the outside face of the panel with the 3M tape already on its back. The glass hides the cut edge, so no cleats or frame are needed. The lip is 9/16 in at the left end, 7/16 in at the right, ¼ in at the top and only ⅛ in at the bottom, so the bottom of the opening has little to spare.

The tilt puts the screen facing up at a child standing at the table. In fit checks the Pi clears the nearest servo (Saturn's) by about ¼ in, and the builder confirmed with the real screen and Pi that nothing touches a servo.

### Assembly and gluing

1. Cut the sides and their holes while they lie flat. Tape them to the base and measure the gap between them (planned 11.75 in).
2. Glue the sides to the base with acrylic solvent cement (it wicks into the joint), outdoors or at an open window.
3. Fix anything on the floor near the front (the driver board's standoffs) before the front panel goes on.
4. Glue the sloped front to the sides. Acrylic cement may not hold polycarbonate: test on offcuts first, and use 5-minute epoxy if the test joint peels.
5. Fit the magnet blocks and the back door.
6. Fit the screen, Pi and electronics through the open top. Run the model.
7. Slide the ceiling in last, then clamp the arms on.

## 4.9 Electronics placement in the box

The servos stay within about 3 in of the column, which leaves the walls free for the power parts. Positions are seen from the front.

| Part | Size | Where |
|---|---|---|
| Raspberry Pi 4B (with stick-on heatsinks) | 3.35 × 2.2 × 0.8 | Screwed to the screen's metal back plate, under the slope. The screen takes its 5 V through spring pins pressing on the Pi's header, so the Pi must be screwed down. |
| Battery (TalentCell 12 V, 66.6 Wh) | 5.7 × 3.35 × 1.1 | On its edge along the left wall, LEDs facing in, from 1.4 in inside the back edge forward. Velcro to the base. Its 12 V jack at the top so the plug clears the lower magnet block. |
| Charging socket (5.5 × 2.1 mm panel mount) | 8 mm hole | Left wall, behind the battery: centre 1.45 in above the bottom of the box (1.2 in up the panel's own edge) and 1.0 in from the back edge. |
| On/off switch (20 mm round rocker, no light) | 20 mm hole, ~1.1 in deep inside | Left wall, near the front: centre 1.55 in above the bottom of the box (1.3 in up the panel) and 4.0 in from the front. Cuts all power. |
| 12 V → 7.5 V converter (servos) | 3.22 × 2.04 × 1.25 | Right wall on 0.1 in nylon standoffs, 0.3 in off the floor, centred 2.8 in behind the box's centre. |
| 12 V → 5 V USB-C converter (Pi) | 1.8 × 1.26 × 0.7 | Right wall, just in front of the centre. |
| Servo driver board | 1.65 × 1.3 × 0.6 | Floor, front left, on standoffs. |

The back door gives access to the battery, converters and servos for repairs. The screen and the front of the box cannot be reached past the servo ring from the back, which is why they go in through the open top.

## 4.10 Feet and other structural details

- **Feet:** four rubber feet, 1 in across and 0.6 in tall, each with a steel washer in a recess. Each is held by an M3 × 16 mm screw, head down in the foot's recess with a nylon washer under the head, up through the base, with a nut on top (fitted 25 Oct 2026). The 0.6 in height clears the stand-rod nuts under the base (about 0.35 in) and stops the acrylic base passing servo noise into the table. (The September plan said ¾ in tall feet; the chosen part is 0.6 in.)
- **Cable strain relief:** a bump during testing once unplugged the servo chain and the screen ribbon. All cables (servo power, chain, USB, screen ribbon) are to be strain-relieved before the model travels.
- **Transport:** put the model in travel mode, then unclamp the arms. With the arms off, the ceiling slides out.

## 4.11 Open items

- **To check:** Top support for the column now that the ceiling slot no longer acts as a bearing (section 4.3).
- **To check:** Elbow offset to be measured before the arm rods are cut (section 4.6).
- **To check:** Neptune's arm height under the lowered ceiling, and Uranus's tube-top height.
- **To check:** Neptune's gear and stand-plate heights after the 8 Nov raise.
- **To check:** Upright lengths: set by measurement, since the arms step about 0.65 in, not ½ in.
- **To check:** Saturn's and Neptune's ring tilt direction (two sets of build notes disagree).
