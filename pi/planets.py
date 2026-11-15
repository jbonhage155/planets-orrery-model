"""Where is each planet on a given date?

Method: NASA/JPL "Approximate Positions of the Planets" (E. M. Standish),
https://ssd.jpl.nasa.gov/planets/approx_pos.html, Table 1 (valid 1800-2050).
Each planet has six orbit numbers (Keplerian elements) plus how fast each one
drifts per century. We solve Kepler's equation and get the planet's angle
around the Sun (heliocentric ecliptic longitude), 0-360 deg, measured
counter-clockwise seen from above the Sun's north pole.

Port of arduino/planet_dial/planets.h. Checked against JPL Horizons by
test_planets.py.

Outside 1800-2100 (TIME TRAVEL, 26 Sep 2026) the same page's Table 2a/2b is used,
valid 3000 BC - 3000 AD (about a degree). Pluto is not in Table 2: its Table 1 row
is used with its slow drifts held at their 1800/2100 values (a few degrees off by
Roman times). Farther out than 3000 BC/AD nobody can say where the planets were
(their orbits are chaotic over millions of years): the drifts are held at their
3000 BC/AD values and only the average motion goes on, which gives a repeatable
guess, not a real position.
"""

import math
from datetime import date

BODY_NAMES = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
NUM_BODIES = len(BODY_NAMES)

# Per planet: (a, e, I, L, peri, node) at J2000 (au, -, deg, deg, deg, deg),
# then the change of each per Julian century.
# Pluto is not in the current JPL table; its row is from Standish's original
# 1800-2050 table. "Earth" is really the Earth-Moon barycentre.
ORBITS = [
    (0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593,
     0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081),
    (0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255,
     0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418),
    (1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0,
     0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0),
    (1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891,
     0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343),
    (5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909,
     -0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106),
    (9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448,
     -0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794),
    (19.18916464, 0.04725744, 0.77263783, 313.23810451, 170.95427630, 74.01692503,
     -0.00196176, -0.00004397, -0.00242939, 428.48202785, 0.40805281, 0.04240589),
    (30.06992276, 0.00859048, 1.77004347, -55.12002969, 44.96476227, 131.78422574,
     0.00026291, 0.00005105, 0.00035372, 218.45945325, -0.32241464, -0.00508664),
    (39.48211675, 0.24882730, 17.14001206, 238.92903833, 224.06891629, 110.30393684,
     -0.00031596, 0.00005170, 0.00004818, 145.20780515, -0.04062942, -0.01183482),
]

# Table 2a (3000 BC - 3000 AD), Mercury ... Neptune, same layout as ORBITS.
ORBITS_OLD = [
    (0.38709843, 0.20563661, 7.00559432, 252.25166724, 77.45771895, 48.33961819,
     0.00000000, 0.00002123, -0.00590158, 149472.67486623, 0.15940013, -0.12214182),
    (0.72332102, 0.00676399, 3.39777545, 181.97970850, 131.76755713, 76.67261496,
     -0.00000026, -0.00005107, 0.00043494, 58517.81560260, 0.05679648, -0.27274174),
    (1.00000018, 0.01673163, -0.00054346, 100.46691572, 102.93005885, -5.11260389,
     -0.00000003, -0.00003661, -0.01337178, 35999.37306329, 0.31795260, -0.24123856),
    (1.52371243, 0.09336511, 1.85181869, -4.56813164, -23.91744784, 49.71320984,
     0.00000097, 0.00009149, -0.00724757, 19140.29934243, 0.45223625, -0.26852431),
    (5.20248019, 0.04853590, 1.29861416, 34.33479152, 14.27495244, 100.29282654,
     -0.00002864, 0.00018026, -0.00322699, 3034.90371757, 0.18199196, 0.13024619),
    (9.54149883, 0.05550825, 2.49424102, 50.07571329, 92.86136063, 113.63998702,
     -0.00003065, -0.00032044, 0.00451969, 1222.11494724, 0.54179478, -0.25015002),
    (19.18797948, 0.04685740, 0.77298127, 314.20276625, 172.43404441, 73.96250215,
     -0.00020455, -0.00001550, -0.00180155, 428.49512595, 0.09266985, 0.05739699),
    (30.06952752, 0.00895439, 1.77005520, 304.22289287, 46.68158724, 131.78635853,
     0.00006447, 0.00000818, 0.00022400, 218.46515314, 0.01009938, -0.00606302),
]
# Table 2b: extra terms for the mean anomaly of Jupiter ... Neptune (b, c, s, f):
# M += b T^2 + c cos(f T) + s sin(f T), f T in degrees.
EXTRA_OLD = {4: (-0.00012452, 0.06064060, -0.35635438, 38.35125000),
             5: (0.00025899, -0.13434469, 0.87320147, 38.35125000),
             6: (0.00058331, -0.97731848, 0.17689245, 7.67025000),
             7: (-0.00041348, 0.68346318, -0.10162547, 7.67025000)}
NEW_T = (-2.0, 1.0)        # centuries from J2000 where Table 1 is used: 1800-2100
OLD_T = (-50.0, 10.0)      # Table 2: 3000 BC - 3000 AD

J2000 = date(2000, 1, 1)


def shortest_turn(from_deg, to_deg):
    """Smallest signed turn that takes you from one angle to the other (-180..+180)."""
    d = (to_deg - from_deg) % 360.0
    return d - 360.0 if d > 180.0 else d


def planet_longitude(body, days):
    """Angle of `body` (0 = Mercury .. 8 = Pluto) around the Sun, degrees 0-360.

    `days` = days since 2000-Jan-01 12:00 UT (the astronomers' "J2000").
    """
    T = days / 36525.0  # centuries since J2000
    extra = 0.0
    if NEW_T[0] <= T <= NEW_T[1] or body not in range(len(ORBITS_OLD)):
        a0, e0, I0, L0, peri0, node0, da, de, dI, dL, dperi, dnode = ORBITS[body]
        Td = min(max(T, NEW_T[0]), NEW_T[1])       # Pluto outside 1800-2100: drifts held
    else:
        a0, e0, I0, L0, peri0, node0, da, de, dI, dL, dperi, dnode = ORBITS_OLD[body]
        Td = min(max(T, OLD_T[0]), OLD_T[1])       # beyond 3000 BC/AD: drifts held (a guess)
        if body in EXTRA_OLD:
            b, c, s, f = EXTRA_OLD[body]
            extra = b * Td * Td + c * math.cos(math.radians(f * Td)) + s * math.sin(math.radians(f * Td))

    a = a0 + da * Td
    e = e0 + de * Td
    I = math.radians(I0 + dI * Td)
    peri = peri0 + dperi * Td
    node = node0 + dnode * Td
    L = (L0 + dL * T) % 360.0

    M = math.radians(shortest_turn(0, L - peri + extra))  # mean anomaly, -pi..pi
    w = math.radians(peri - node)                 # argument of perihelion
    N = math.radians(node)

    # Kepler's equation M = E - e sin E, solved by Newton's method.
    E = M + e * math.sin(M)
    for _ in range(6):
        E -= (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))

    # Position in the orbit's own plane, then tilted into the ecliptic.
    xo = a * (math.cos(E) - e)
    yo = a * math.sqrt(1.0 - e * e) * math.sin(E)
    x = ((math.cos(w) * math.cos(N) - math.sin(w) * math.sin(N) * math.cos(I)) * xo +
         (-math.sin(w) * math.cos(N) - math.cos(w) * math.sin(N) * math.cos(I)) * yo)
    y = ((math.cos(w) * math.sin(N) + math.sin(w) * math.cos(N) * math.cos(I)) * xo +
         (-math.sin(w) * math.sin(N) + math.cos(w) * math.cos(N) * math.cos(I)) * yo)
    return math.degrees(math.atan2(y, x)) % 360.0


# Calendar dates, for any day number (days since 2000-01-01) including BC: the Julian
# calendar before 15 Oct 1582 (the dates history books use), Gregorian from then on.
# Years are astronomers' years: 0 = 1 BC, -6 = 7 BC (Meeus, Astronomical Algorithms ch. 7).
JD_2000 = 2451544.5         # Julian Day of 2000-01-01 00:00


def day_from_cal(y, m, d):
    gregorian = (y, m, d) >= (1582, 10, 15)
    if m <= 2:
        y, m = y - 1, m + 12
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4) if gregorian else 0
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5 - JD_2000


def cal_from_day(day):
    Z = math.floor(round(day) + JD_2000 + 0.5)
    if Z < 2299161:
        A = Z
    else:
        alpha = math.floor((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - math.floor(alpha / 4)
    B = A + 1524
    C = math.floor((B - 122.1) / 365.25)
    D = math.floor(365.25 * C)
    E = math.floor((B - D) / 30.6001)
    d = B - D - math.floor(30.6001 * E)
    m = E - 1 if E < 14 else E - 13
    return [C - 4716 if m > 2 else C - 4715, m, d]


def year_text(y):
    """How a year is written: 7 BC, 79 AD, 1492."""
    return f"{1 - y} BC" if y <= 0 else f"{y} AD" if y < 1000 else str(y)


def longitudes(day):
    """All nine angles for a calendar date. Positions are taken at 12:00 UT, which
    makes the whole-day count since 2000-Jan-01 exactly the `days` argument."""
    days = (day - J2000).days
    return [planet_longitude(b, days) for b in range(NUM_BODIES)]
