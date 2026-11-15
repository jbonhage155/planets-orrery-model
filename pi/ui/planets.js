// The PLANETS tab (26 Sep 2026, replaced GO TO DATE): a fact page and a 3D globe for the
// Sun and each planet, so visitors can learn about them while the orrery runs.
// index.html draws the words on its 2D canvas; this file owns the globe, a WebGL canvas
// (#p3) laid over the screen (the left part, or all of it below the planet buttons when
// the facts are hidden). Drag = look all round it (poles too), pinch or scroll = zoom,
// double-tap = back to the starting view. three.js is ui/three.min.js (r149, the same
// file as the website). The Pi 4's GPU does WebGL 2 in the kiosk (checked 26 Sep: ANGLE
// on Broadcom V3D). Surface maps are in tex/ (sources in tex/CREDITS.md).
(function () {
  const SSS = 'Maps: Solar System Scope, CC BY 4.0', NASA = 'Map: NASA / JHUAPL / SwRI (New Horizons)';
  // Page 0 is the Sun, then Mercury ... Mars, the asteroid belt (13 Nov 2026), Jupiter ... Pluto.
  // BODIES (below) is the nine planets alone, in the orrery's order (planets.py).
  // tilt = axial tilt (degrees; over 90 = spins backwards), turn = hours for one spin,
  // halo = atmosphere colour and strength. Facts from NASA's pages (US units).
  const INFO = [
    { name:'Sun', color:'#ffb300', tag:'Our star: a giant ball of glowing gas', tex:'sun', tilt:7.25, turn:609.1, star:true, credit:SSS,
      glows:[[1.1, [1.0, 0.7, 0.3], 0.9], [1.7, [1.0, 0.45, 0.1], 0.3]],
      facts:[['From Earth', '93 million miles'], ['Age', '4.6 billion years'], ['One spin', '27 days', 'at its middle'],
             ['Planets', '8', 'plus dwarf planets'], ['Width', '865,000 miles', '109 Earths'], ['Temperature', '10,000 °F', 'surface']],
      fun:'Sunlight takes about 8 minutes to reach Earth, so you always see the Sun as it was 8 minutes ago!' },
    { name:'Mercury', au:0.387, color:'#9a9a9a', tag:'The smallest planet, and the closest to the Sun', tex:'mercury', tilt:0.03, turn:1407.6, halo:null, credit:SSS,
      facts:[['From the Sun', '36 million miles'], ['One year', '88 Earth days'], ['One day', '176 Earth days', 'sunrise to sunrise'],
             ['Moons', 'None'], ['Width', '3,032 miles', '⅓ of Earth'], ['Temperature', '−290 to 800 °F']],
      fun:'A day on Mercury, from one sunrise to the next, lasts as long as two whole Mercury years!' },
    { name:'Venus', au:0.723, color:'#e8c27a', tag:'The hottest planet, hidden under thick clouds', tex:'venus', tilt:177.4, turn:5832.5, halo:[1.0, 0.85, 0.55, 0.9], credit:SSS,
      facts:[['From the Sun', '67 million miles'], ['One year', '225 Earth days'], ['One day', '117 Earth days', 'sunrise to sunrise'],
             ['Moons', 'None'], ['Width', '7,521 miles', 'almost Earth'], ['Temperature', '870 °F', 'hot enough to melt lead']],
      fun:'Venus spins backwards compared with most planets, so there the Sun rises in the west and sets in the east.' },
    { name:'Earth', au:1, color:'#3a8ee6', tag:'Our home, the only planet known to have life', tex:'earth', tilt:23.4, turn:23.93, halo:[0.35, 0.6, 1.0, 1.0], credit:SSS,
      clouds:'earth_clouds', night:'earth_night', gloss:1,
      facts:[['From the Sun', '93 million miles'], ['One year', '365¼ days'], ['One day', '24 hours'],
             ['Moons', '1', 'the Moon'], ['Width', '7,918 miles'], ['Temperature', '59 °F', 'on average']],
      fun:'Oceans cover more than two-thirds of Earth, which is why it looks like a blue marble from space.' },
    { name:'Mars', au:1.524, color:'#d9534f', tag:'The red planet: its dusty ground is full of rust', tex:'mars', tilt:25.2, turn:24.62, halo:[1.0, 0.6, 0.4, 0.45], credit:SSS,
      facts:[['From the Sun', '142 million miles'], ['One year', '687 Earth days'], ['One day', '24 hours 40 min'],
             ['Moons', '2', 'Phobos, Deimos'], ['Width', '4,212 miles', '½ of Earth'], ['Temperature', '−80 °F', 'on average']],
      fun:'Mars has the tallest volcano in the solar system, Olympus Mons. It is about 2½ times as tall as Mount Everest.' },
    { name:'Asteroid belt', short:'Asteroids', au:2.77, color:'#b8a48c', tag:'Millions of rocks left over from when the planets formed', belt:true, tilt:4, turn:9.07, halo:null,
      credit:'A drawing, not photos · ' + SSS,
      facts:[['From the Sun', '250 million miles'], ['One year', '3 to 6 Earth years'], ['Asteroids', 'Over a million'],
             ['Biggest', 'Ceres', '590 miles wide'], ['All together', 'Smaller than our Moon'], ['Made of', 'Rock and metal']],
      fun:'The asteroids are so far apart that spacecraft fly straight through the belt without hitting a thing!' },
    { name:'Jupiter', au:5.2, color:'#d8a06a', tag:'The biggest planet, a giant ball of gas', tex:'jupiter', tilt:3.1, turn:9.93, halo:[1.0, 0.85, 0.65, 0.45], credit:SSS,
      facts:[['From the Sun', '484 million miles'], ['One year', '12 Earth years'], ['One day', '10 hours', 'fastest spinner'],
             ['Moons', 'Over 90'], ['Width', '86,881 miles', '11 Earths'], ['Temperature', '−166 °F', 'cloud tops']],
      fun:'More than 1,300 Earths could fit inside Jupiter. Its Great Red Spot is a storm wider than the whole Earth!' },
    { name:'Saturn', au:9.58, color:'#e6d08a', tag:'The planet with the biggest, brightest rings', tex:'saturn', tilt:26.7, turn:10.66, halo:[1.0, 0.9, 0.7, 0.4], credit:SSS,
      rings:{ tex:'saturn_ring', inner:1.2, outer:2.3, opacity:1 },
      facts:[['From the Sun', '886 million miles'], ['One year', '29½ Earth years'], ['One day', '10½ hours'],
             ['Moons', 'Over 270'], ['Width', '72,367 miles', '9 Earths'], ['Temperature', '−220 °F', 'cloud tops']],
      fun:'Saturn is so light for its size that it would float in water, if you could find a bathtub big enough!' },
    { name:'Uranus', au:19.2, color:'#7fe0d8', tag:'The ice giant that spins on its side', tex:'uranus', tilt:97.8, turn:17.24, halo:[0.55, 0.9, 1.0, 0.8], credit:SSS,
      rings:{ tex:null, inner:1.64, outer:2.0, opacity:0.7 },
      facts:[['From the Sun', '1.8 billion miles'], ['One year', '84 Earth years'], ['One day', '17 hours'],
             ['Moons', 'Over 25'], ['Width', '31,518 miles', '4 Earths'], ['Temperature', '−320 °F', 'cloud tops']],
      fun:'Uranus is tipped right over, so each pole gets 42 years of sunshine, then 42 years of darkness.' },
    { name:'Neptune', au:30.1, color:'#4666ff', tag:'The windiest planet, and the farthest from the Sun', tex:'neptune', tilt:28.3, turn:16.11, halo:[0.4, 0.55, 1.0, 0.85], credit:SSS,
      facts:[['From the Sun', '2.8 billion miles'], ['One year', '165 Earth years'], ['One day', '16 hours'],
             ['Moons', '16'], ['Width', '30,599 miles', '4 Earths'], ['Temperature', '−330 °F', 'cloud tops']],
      fun:'Neptune was found in 1846 using math, before anyone had seen it. Since then it has gone round the Sun only once.' },
    // The last page (14 Nov 2026, the user; it was Pluto's): the five dwarf planets, all
    // together or one at a time (DWARFS below; index.html has the buttons to choose).
    { name:'Dwarf planets', short:'Dwarfs', au:39.5, color:'#c9b29b', tag:'Small round worlds that are not quite planets', dwarfs:true, tilt:0, turn:24,
      credit:'Pluto: NASA / JHUAPL / SwRI · the others are drawings', note:'True sizes next to each other · drag, pinch to zoom',
      facts:[['How many', '5', 'named so far'], ['Biggest', 'Pluto', '1,477 miles wide'], ['Closest', 'Ceres', 'in the asteroid belt'],
             ['Farthest', 'Eris', '6.3 billion miles'], ['Since', '2006', 'when Pluto joined'], ['Shape', 'Round', 'like a planet']],
      fun:'A dwarf planet is round like a planet, but it shares its path round the Sun with lots of other rocks or lumps of ice.' },
  ];
  // The dwarf planets, nearest the Sun first. Pluto has a real map (New Horizons, 2015);
  // the others are a tinted, cratered ball (tint, texMix): Ceres has been visited (Dawn),
  // but there is no map of it here, and nobody has seen Haumea, Makemake or Eris up close.
  // km = radius, for the all-together picture; shape = stretched (Haumea, an egg).
  const DRAWN = 'A drawing: no spacecraft has been there · drag, pinch to zoom';
  const DWARFS = [
    { name:'Ceres', au:2.77, km:470, color:'#a9a49c', tag:'The biggest asteroid, and the only dwarf planet in the asteroid belt', tint:'#8d8983', texMix:0.9, tilt:4, turn:9.07, halo:null,
      credit:'A drawing · ' + SSS, note:'A drawing, not a photo · drag, pinch to zoom',
      facts:[['From the Sun', '257 million miles'], ['One year', '4.6 Earth years'], ['One day', '9 hours'],
             ['Moons', 'None'], ['Width', '588 miles'], ['Found', '1801']],
      fun:'Ceres was called a planet for about 50 years after it was found. A spacecraft named Dawn orbited it in 2015.' },
    { name:'Pluto', au:39.5, km:1188, color:'#c9b29b', tag:'The most famous dwarf planet, at the icy edge of the solar system', tex:'pluto', tilt:119.6, turn:153.3, halo:[0.5, 0.7, 1.0, 0.35], credit:NASA,
      facts:[['From the Sun', '3.7 billion miles'], ['One year', '248 Earth years'], ['One day', '6½ Earth days'],
             ['Moons', '5', 'the biggest is Charon'], ['Width', '1,477 miles', 'smaller than our Moon'], ['Temperature', '−380 °F']],
      fun:'Pluto has a giant heart-shaped plain of ice, first seen when the New Horizons spacecraft flew past in 2015.' },
    { name:'Haumea', au:43.1, km:780, color:'#e8e4dc', tag:'An egg-shaped world with a ring of its own', tint:'#b3afa8', texMix:0.3, shape:[1.25, 0.64, 1.0], tilt:20, turn:3.92, halo:null,
      rings:{ tex:null, inner:2.1, outer:2.3, opacity:0.45 }, credit:'A drawing · ' + SSS, note:DRAWN,
      facts:[['From the Sun', '4 billion miles'], ['One year', '285 Earth years'], ['One day', '4 hours', 'fastest of all'],
             ['Moons', '2', 'Hiʻiaka, Namaka'], ['Width', '1,000 miles', 'the long way 1,400'], ['Found', '2004']],
      fun:'Haumea spins so fast, once every 4 hours, that it has been stretched into the shape of an egg!' },
    { name:'Makemake', au:45.8, km:715, color:'#c98a6a', tag:'A reddish, frozen world out beyond Pluto', tint:'#b5745a', texMix:0.35, tilt:10, turn:22.8, halo:null,
      credit:'A drawing · ' + SSS, note:DRAWN,
      facts:[['From the Sun', '4.3 billion miles'], ['One year', '305 Earth years'], ['One day', '23 hours'],
             ['Moons', '1', 'nicknamed MK2'], ['Width', '888 miles'], ['Found', '2005']],
      fun:'Makemake was found just after Easter, so its nickname was “Easterbunny” until it got its real name.' },
    { name:'Eris', au:67.7, km:1163, color:'#eef0f4', tag:'Almost Pluto’s twin, far out in the dark', tint:'#b9b6b2', texMix:0.3, tilt:78, turn:378, halo:null,
      credit:'A drawing · ' + SSS, note:DRAWN,
      facts:[['From the Sun', '6.3 billion miles'], ['One year', '557 Earth years'], ['One day', '16 Earth days'],
             ['Moons', '1', 'Dysnomia'], ['Width', '1,445 miles', 'nearly Pluto’s size'], ['Found', '2005']],
      fun:'Finding Eris in 2005 made astronomers decide what a planet is. That is why Pluto is now called a dwarf planet.' },
  ];

  // Moons (26 Sep): the big named ones (the giants have dozens of tiny ones too).
  // [name, distance in planet radii, radius / planet's radius, days per orbit, colour,
  //  how much of the cratered Moon map shows through (0 = smooth), tilt of its orbit to
  //  the planet's equator in degrees (Triton: 157 = backwards)]. Real distances would
  //  put most moons far off screen, so each system is squeezed into `band` (planet radii,
  //  log scale, order kept), and small moons are drawn bigger than life; the Moon and
  //  Charon are big enough to show at their true size next to their planet.
  const MOONS = {
    Earth:   { band:[2.4, 2.4], plane:'orbit', list:[['Moon', 60.3, 0.273, 27.32, '#c8c8c8', 1, 5.1]] },
    Mars:    { band:[1.75, 2.6], list:[['Phobos', 2.76, 0.0033, 0.319, '#8a7a6a', 1], ['Deimos', 6.92, 0.0018, 1.263, '#a08f7c', 1]] },
    Jupiter: { band:[1.8, 3.1], list:[['Io', 5.9, 0.026, 1.769, '#e8cf5a', 0.45], ['Europa', 9.4, 0.022, 3.551, '#e6dccb', 0.35],
                                      ['Ganymede', 15.0, 0.038, 7.155, '#a89c8c', 0.9], ['Callisto', 26.3, 0.034, 16.69, '#8f8070', 1]] },
    Saturn:  { band:[2.6, 3.9], list:[['Mimas', 3.08, 0.0033, 0.942, '#bdbdbd', 1], ['Enceladus', 3.95, 0.0042, 1.37, '#f4f8ff', 0.3],
                                      ['Tethys', 4.89, 0.0088, 1.888, '#dcdcdc', 0.7], ['Dione', 6.26, 0.0093, 2.737, '#d0d0d0', 0.8],
                                      ['Rhea', 8.74, 0.0127, 4.518, '#c8c8c8', 0.9], ['Titan', 20.3, 0.0445, 15.95, '#d9a441', 0.08],
                                      ['Iapetus', 59.1, 0.0122, 79.3, '#9c8a70', 1, 15]] },
    Uranus:  { band:[2.25, 3.1], list:[['Miranda', 5.08, 0.0093, 1.413, '#bdbdbd', 1], ['Ariel', 7.47, 0.0226, 2.52, '#cfcfcf', 0.8],
                                       ['Umbriel', 10.4, 0.023, 4.144, '#7d7d7d', 1], ['Titania', 17.1, 0.031, 8.706, '#bfb3a8', 0.9],
                                       ['Oberon', 22.8, 0.0299, 13.46, '#a89a8e', 1]] },
    Neptune: { band:[1.9, 2.9], list:[['Proteus', 4.75, 0.0085, 1.122, '#8a8a8a', 1], ['Triton', 14.3, 0.0546, 5.877, '#e8c8c0', 0.5, 157]] },
    Pluto:   { band:[1.9, 3.1], list:[['Charon', 16.5, 0.51, 6.387, '#a9a39e', 0.9], ['Styx', 36.2, 0.005, 20.16, '#bbbbbb', 1],
                                      ['Nix', 41.0, 0.021, 24.85, '#cccccc', 1], ['Kerberos', 48.7, 0.008, 32.17, '#999999', 1],
                                      ['Hydra', 54.5, 0.021, 38.2, '#cccccc', 1]] },
    Haumea:  { band:[2.7, 3.3], list:[['Namaka', 32, 0.1, 18.3, '#cfcfcf', 1], ['Hiʻiaka', 62, 0.2, 49.5, '#dddddd', 1]] },
    Makemake:{ band:[2.3, 2.3], list:[['MK2', 29, 0.12, 18, '#6a625c', 1]] },
    Eris:    { band:[2.5, 2.5], list:[['Dysnomia', 32, 0.3, 15.8, '#77726c', 1]] },
  };
  // Visible speeds, squashed like the spins: one orbit of the Moon ~1 min, Io ~20 s.
  const moonRate = days => 0.4 * Math.pow(days, -0.4);
  INFO.concat(DWARFS).forEach(P => { P.moons = MOONS[P.name] || null; });
  const BODIES = INFO.filter(P => !P.star && !P.belt && !P.dwarfs).concat(DWARFS[1]), PAGE_OF = BODIES.map(P => INFO.indexOf(P)), BELT_PAGE = INFO.findIndex(P => P.belt);

  const cv = document.getElementById('p3');
  let R = null;
  try { if (window.THREE) R = new THREE.WebGLRenderer({ canvas:cv, antialias:true, preserveDrawingBuffer:true }); } catch (e) { R = null; }
  // No WebGL: index.html draws a flat disc instead.
  if (!R) { window.PlanetView = { INFO, DWARFS, ok:false, show() {}, hide() {}, reset() {} }; return; }

  // The Sun is in the picture (chosen 26 Sep, "C far" of four tried): a fixed place in
  // space 3x the starting camera distance away, low in the sky (7° up) and to the left,
  // drawn in true perspective. It is farther than the camera, so turning to the sunny
  // side it is behind you, never in front of the planet, and the moons never seem to
  // touch it. The view opens sunlit with the Sun just off the left edge; turn round and
  // it comes in from the side and then sits behind the night side, moving across the
  // sky as you turn. Its light arrives in parallel rays from where it is drawn, as from
  // the real, far-away Sun. The shaders work in view space: SUN_POS_V is a point far off
  // in the Sun's direction. (Dropped: the Sun beside the planet, always in the starting
  // view — from Mercury to Mars it swung round like a small moon and was in front of the
  // sunny side; the Sun fixed while the planet turns; light not from where the Sun is.)
  const SUN_DIR = new THREE.Vector3(-0.9, 0.12, 0.4).normalize(), SUN_POS_V = new THREE.Vector3(), CENTRE_V = new THREE.Vector3();
  const SUN_W = new THREE.Vector3();
  const scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(30, 1, 0.05, 800);
  scene.background = new THREE.Color(0x02030a);
  const loader = new THREE.TextureLoader(), aniso = R.capabilities.getMaxAnisotropy();
  const tex = name => { const t = loader.load(`tex/${name}.${name === 'saturn_ring' ? 'png' : 'jpg'}`); t.anisotropy = aniso; return t; };

  const VERT = `varying vec2 vUv; varying vec3 vN, vP, vL;
    void main() { vUv = uv; vL = position; vN = normalize(normalMatrix * normal);
      vec4 p = modelViewMatrix * vec4(position, 1.0); vP = p.xyz; gl_Position = projectionMatrix * p; }`;
  // Surface: day side lit by the Sun (worked in linear light), Earth's city lights on the
  // night side and a sun glint on its oceans, and a thin lit haze at the edge of the disc.
  const SURFACE = `uniform sampler2D map, night; uniform float hasNight, gloss, fade; uniform vec3 sunPos; uniform vec4 halo;
    varying vec2 vUv; varying vec3 vN, vP;
    vec3 lin(vec3 c) { return pow(c, vec3(2.2)); }
    void main() {
      vec3 sun = normalize(sunPos - vP), n = normalize(vN), v = normalize(-vP), c = lin(texture2D(map, vUv).rgb);
      float d = dot(n, sun), day = smoothstep(-0.05, 0.25, d);
      vec3 col = c * (max(d, 0.0) * 1.4 + 0.03);
      if (hasNight > 0.5) col += lin(texture2D(night, vUv).rgb) * (1.0 - day) * 1.4;
      float ocean = gloss * smoothstep(0.02, 0.1, c.b - c.r);
      col += vec3(1.0, 0.95, 0.85) * ocean * pow(max(dot(reflect(-sun, n), v), 0.0), 30.0) * 0.6 * day;
      float rim = pow(1.0 - max(dot(n, v), 0.0), 3.0);
      col = mix(col, lin(halo.rgb) * (0.05 + 1.3 * smoothstep(-0.25, 0.6, d)), rim * halo.a * 0.8);
      gl_FragColor = vec4(pow(col, vec3(1.0 / 2.2)) * fade, 1.0);
    }`;
  // The Sun shines by itself: its map, gently boiling (the picture wobbles a little over
  // time), darker toward its edge the way the real Sun looks ("limb darkening").
  const STAR = `uniform sampler2D map; uniform float fade, time, hot; varying vec2 vUv; varying vec3 vN, vP;
    void main() {
      vec3 n = normalize(vN), v = normalize(-vP);
      vec2 uv = vUv + 0.003 * vec2(sin(vUv.y * 90.0 + time * 0.8), cos(vUv.x * 140.0 + time * 0.6));
      vec3 c = texture2D(map, uv).rgb;
      float mu = max(dot(n, v), 0.0);
      vec3 col = c * 1.05 * (0.35 + 0.65 * pow(mu, 0.6)) + vec3(1.0, 0.45, 0.1) * 0.1 * (1.0 - mu);
      vec3 glare = mix(vec3(1.0, 0.55, 0.15), vec3(1.0, 0.98, 0.9), pow(mu, 0.4)) * (1.02 + 0.25 * (dot(c, vec3(0.3, 0.5, 0.2)) - 0.5));
      gl_FragColor = vec4(mix(col, glare * (0.6 + 0.5 * pow(mu, 0.3)), hot) * fade, 1.0);
    }`;
  const CLOUDS = `uniform sampler2D map; uniform vec3 sunPos; uniform float fade; varying vec2 vUv; varying vec3 vN, vP;
    void main() { vec3 sun = normalize(sunPos - vP); float d = dot(normalize(vN), sun), a = texture2D(map, vUv).r;
      gl_FragColor = vec4(vec3(clamp(d * 1.3 + 0.03, 0.0, 1.0)), a * 0.9 * fade); }`;
  // Moons: the Moon's grey map tinted to each moon's colour, lit by the Sun, and dark
  // while in the planet's shadow (an eclipse).
  const MOON = `uniform sampler2D map; uniform vec3 sunPos, centre, tint; uniform float fade, radius, texMix;
    varying vec2 vUv; varying vec3 vN, vP;
    void main() { vec3 n = normalize(vN), sun = normalize(sunPos - vP);
      float l = texture2D(map, vUv).r;
      vec3 c = pow(tint, vec3(2.2)) * mix(1.0, l * 1.8, texMix);
      vec3 toC = centre - vP; float along = dot(toC, sun), shade = 1.0;
      if (along > 0.0) shade = smoothstep(radius * 0.95, radius * 1.05, length(toC - sun * along));
      vec3 col = c * (max(dot(n, sun), 0.0) * 1.4 * shade + 0.03);
      gl_FragColor = vec4(pow(col, vec3(1.0 / 2.2)) * fade, 1.0); }`;
  // Asteroids: the same grey cratered map, tinted, lit by the Sun.
  const ROCK = `uniform sampler2D map; uniform vec3 sunPos, tint; uniform float fade, texMix, amb; varying vec2 vUv; varying vec3 vN, vP;
    void main() { vec3 n = normalize(vN), sun = normalize(sunPos - vP);
      vec3 c = pow(tint, vec3(2.2)) * mix(1.0, texture2D(map, vUv).r * 1.8, texMix);
      vec3 col = c * (max(dot(n, sun), 0.0) * 1.4 + amb);
      gl_FragColor = vec4(pow(col, vec3(1.0 / 2.2)) * fade, 1.0); }`;
  // Glow: the back of a slightly bigger sphere, bright just outside the planet's edge and
  // fading to nothing at its own edge; stronger on the sunny side (even = 1: all round,
  // for the Sun's corona). Added on top (additive).
  const GLOW = `uniform vec4 halo; uniform vec3 sunPos; uniform float fade, limb, even; varying vec3 vN, vP;
    void main() { vec3 n = normalize(vN), v = normalize(-vP), sun = normalize(sunPos - vP);
      float x = clamp(-dot(n, v) / limb, 0.0, 1.0), side = smoothstep(-0.5, 0.8, dot(normalize(n - v * dot(n, v)), sun));
      gl_FragColor = vec4(halo.rgb * pow(x, 2.2) * halo.a * mix(0.12 + 0.9 * side, 1.0, even) * fade, 1.0); }`;
  // Rings: colour and see-through-ness by distance from the planet's centre, lit on
  // either face, and dark where the planet's shadow falls across them.
  const RINGS = `uniform sampler2D map; uniform vec3 sunPos, centre; uniform float rIn, rOut, fade, radius, opacity;
    varying vec3 vN, vP, vL;
    void main() { vec3 sun = normalize(sunPos - vP); float u = (length(vL.xy) - rIn) / (rOut - rIn); if (u < 0.0 || u > 1.0) discard;
      vec4 t = texture2D(map, vec2(u, 0.5));
      vec3 toC = centre - vP; float along = dot(toC, sun), shade = 1.0;
      if (along > 0.0) shade = mix(0.06, 1.0, smoothstep(radius * 0.97, radius * 1.03, length(toC - sun * along)));
      float lit = (0.3 + 0.8 * abs(dot(normalize(vN), sun))) * shade;
      gl_FragColor = vec4(t.rgb * lit, t.a * opacity * fade); }`;

  // Uranus's rings are thin dark hoops; drawn here rather than from a picture.
  function hoops() {
    const w = 256, a = new Uint8Array(w * 4), lines = [[0, 0.5], [0.07, 0.5], [0.11, 0.6], [0.19, 0.5], [0.5, 0.6], [0.56, 0.6], [0.63, 0.7], [0.97, 1]];
    for (let i = 0; i < w; i++) {
      const k = lines.reduce((s, [u, b]) => s + b * Math.exp(-(((i / (w - 1) - u) * w / 2.5) ** 2)), 0);
      a.set([175, 180, 195, Math.min(255, 230 * k)], i * 4);
    }
    const t = new THREE.DataTexture(a, w, 1, THREE.RGBAFormat);
    t.magFilter = THREE.LinearFilter; t.minFilter = THREE.LinearMipmapLinearFilter; t.generateMipmaps = true;
    t.anisotropy = aniso; t.needsUpdate = true; return t;
  }
  // "N" / "S" floating just off each pole.
  function label(text) {
    const c = document.createElement('canvas'); c.width = c.height = 64;
    const x = c.getContext('2d');
    x.font = '700 44px system-ui, sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle';
    x.lineJoin = 'round'; x.lineWidth = 6; x.strokeStyle = 'rgba(2,3,10,0.8)'; x.strokeText(text, 32, 34); x.fillStyle = '#cfdcff'; x.fillText(text, 32, 34);
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map:new THREE.CanvasTexture(c), transparent:true, opacity:0, depthWrite:false }));
    s.scale.setScalar(0.26); return s;
  }

  // A moon's name, always the same size on screen, just above the moon.
  function nameTag(text, lift) {
    const c = document.createElement('canvas'); c.width = 256; c.height = 64;
    const x = c.getContext('2d');
    x.font = '600 34px system-ui, sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle';
    x.lineJoin = 'round'; x.lineWidth = 7; x.strokeStyle = 'rgba(2,3,10,0.85)'; x.strokeText(text, 128, 34); x.fillStyle = '#dfe6ff'; x.fillText(text, 128, 34);
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map:new THREE.CanvasTexture(c), transparent:true, opacity:0, depthWrite:false, sizeAttenuation:false }));
    s.scale.set(0.16, 0.04, 1);                             // name ~14 px tall on the Pi's screen
    s.center.set(0.5, -0.35 - lift); return s;
  }
  const moonMap = tex('moon');
  // A lumpy rock: a ball pushed in and out by a few broad waves and squashed a little
  // (the same seed always gives the same rock). Which way each bit of surface faces is
  // worked out from the shape itself, so there is no seam down the back.
  function lump(seed, rough, wSeg = 40, hSeg = 28) {
    let s = seed; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
    const waves = Array.from({ length:7 }, (_, k) => ({ v:new THREE.Vector3(rnd() * 2 - 1, rnd() * 2 - 1, rnd() * 2 - 1).normalize(),
      f:1.5 + k * 0.9 + rnd(), ph:rnd() * 6.28, a:rough / (1 + k * 0.6) }));
    const sq = [1 + rough * 1.2 * rnd(), 1 - rough * rnd(), 1 - rough * 0.6 * rnd()];
    const at = d => { let r = 1; waves.forEach(w => { r += w.a * Math.sin(d.dot(w.v) * w.f + w.ph); }); return new THREE.Vector3(d.x * sq[0], d.y * sq[1], d.z * sq[2]).multiplyScalar(r); };
    const geo = new THREE.SphereGeometry(1, wSeg, hSeg), pos = geo.attributes.position, nor = geo.attributes.normal;
    const d = new THREE.Vector3(), t1 = new THREE.Vector3(), t2 = new THREE.Vector3(), n = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      d.fromBufferAttribute(pos, i).normalize();
      t1.set(-d.z, 0, d.x); if (t1.lengthSq() < 1e-6) t1.set(1, 0, 0); t1.normalize(); t2.crossVectors(d, t1);
      const p = at(d), a = at(d.clone().addScaledVector(t1, 0.02).normalize()).sub(p), b = at(d.clone().addScaledVector(t2, 0.02).normalize()).sub(p);
      n.crossVectors(a, b).normalize(); if (n.dot(d) < 0) n.negate();
      pos.setXYZ(i, p.x, p.y, p.z); nor.setXYZ(i, n.x, n.y, n.z);
    }
    geo.computeBoundingSphere(); return geo;
  }
  // The asteroid belt's page (13 Nov 2026; redone 14 Nov, the user: it should show the
  // belt): the Sun in the middle, Mars going round inside and Jupiter outside, and between
  // them the belt, thousands of specks and a few dozen tumbling rocks, with the four
  // biggest named. Lit from the Sun in the middle. Rocks far bigger than life, and the
  // belt far more crowded. Zoom in and the camera ends up among the rocks.
  // [name, radius, distance from the Sun, angle, colour, lumpiness (0 = a ball), seed]
  const ROCKS = [['Ceres', 0.15, 3.25, 1.35, '#a09b94', 0, 1], ['Vesta', 0.09, 2.8, 2.25, '#c2b8a8', 0.11, 7],
                 ['Pallas', 0.09, 3.45, 0.55, '#a8a49e', 0.08, 23], ['Hygiea', 0.078, 3.7, 3.0, '#8a847e', 0.05, 41]];
  function buildBelt(P) {
    const u = [], root = new THREE.Group(), tilt = new THREE.Group(), spin = new THREE.Group();
    root.rotation.set(0.62, 0, 0); root.add(tilt); tilt.add(spin);
    const mat = (frag, uniforms, opts = {}) => { u.push(uniforms); return new THREE.ShaderMaterial(Object.assign({ vertexShader:VERT, fragmentShader:frag, uniforms }, opts)); };
    const lit = () => ({ sunPos:{ value:CENTRE_V }, fade:{ value:0 } });
    const rockMat = (colour, texMix) => mat(ROCK, Object.assign(lit(), { map:{ value:moonMap }, tint:{ value:new THREE.Color(colour) }, texMix:{ value:texMix }, amb:{ value:0.16 } }));
    let s = 99; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
    const axisOf = () => new THREE.Vector3(rnd() - 0.5, rnd() + 0.3, rnd() - 0.5).normalize();
    const rocks = [], tags = [], moons = [], mats = [], ball = new THREE.SphereGeometry(1, 48, 32);
    // The Sun, with its corona.
    const time = { value:0 }, sun = new THREE.Mesh(ball, mat(STAR, { map:{ value:tex('sun') }, fade:{ value:0 }, time, hot:{ value:0 } }));
    INFO[0].glows.forEach(([g, rgb, k]) => {
      const m = new THREE.Mesh(ball, mat(GLOW, Object.assign(lit(), { halo:{ value:new THREE.Vector4(rgb[0], rgb[1], rgb[2], k) }, limb:{ value:Math.sqrt(1 - 1 / (g * g)) }, even:{ value:1 } }),
        { side:THREE.BackSide, transparent:true, depthWrite:false, blending:THREE.AdditiveBlending }));
      m.scale.setScalar(g); sun.add(m);
    });
    sun.scale.setScalar(0.42); tilt.add(sun);
    const sunTag = nameTag('Sun', 0); sunTag.position.set(0, 0.62, 0); tilt.add(sunTag); tags.push(sunTag);
    // Mars inside the belt, Jupiter outside: [planet, orbit, size, speed, where it starts].
    [[BODIES[3], 1.9, 0.1, 0.11, 2.4], [BODIES[4], 4.75, 0.3, 0.035, 0.9]].forEach(([Q, r, size, rate, a0]) => {
      const ring = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(
        Array.from({ length:200 }, (_, j) => new THREE.Vector3(r * Math.cos(j / 200 * Math.PI * 2), 0, r * Math.sin(j / 200 * Math.PI * 2)))),
        new THREE.LineBasicMaterial({ color:0x8fa3d8, transparent:true, opacity:0, depthWrite:false }));
      const pivot = new THREE.Group(); pivot.rotation.y = a0;
      const globe = new THREE.Mesh(ball, mat(SURFACE, Object.assign(lit(), { map:{ value:tex(Q.tex) }, night:{ value:null }, hasNight:{ value:0 }, gloss:{ value:0 },
        halo:{ value:new THREE.Vector4(...Q.halo) } })));
      globe.scale.setScalar(size); globe.position.x = r;
      const tag = nameTag(Q.name, 0); tag.position.set(r, size * 1.3, 0);
      pivot.add(globe, tag); tilt.add(ring, pivot);
      moons.push({ pivot, rate, ring }); tags.push(tag);
    });
    // The belt: specks, thickest in the middle of the band.
    const where = () => { const a = rnd() * Math.PI * 2, r = 3.25 + (rnd() + rnd() + rnd() - 1.5) / 1.5 * 0.8; return [r * Math.cos(a), (rnd() - 0.5) * 0.3, r * Math.sin(a)]; };
    const speck = dot();
    [[2600, 1.7, 0.75], [260, 2.8, 0.9]].forEach(([n, size, k]) => {
      const pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) { const b = 0.4 + 0.6 * rnd(), warm = rnd() * 0.25; pos.set(where(), i * 3); col.set([b, b * (1 - warm * 0.35), b * (1 - warm)], i * 3); }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
      const m = new THREE.PointsMaterial({ size, map:speck, sizeAttenuation:false, vertexColors:true, transparent:true, opacity:0, depthWrite:false });
      spin.add(new THREE.Points(geo, m)); mats.push([m, k]);
    });
    // Tumbling rocks among them, and the four biggest with their names.
    const shapes = [3, 11, 17, 29].map(seed => lump(seed, 0.22, 14, 10)), greys = ['#9a958e', '#b3aa9c', '#7d7974'].map(c => rockMat(c, 0.6));
    for (let k = 0; k < 80; k++) {
      const m = new THREE.Mesh(shapes[k % shapes.length], greys[k % greys.length]);
      m.scale.setScalar(0.02 + 0.05 * rnd() * rnd()); m.position.set(...where()); m.rotation.set(rnd() * 6, rnd() * 6, 0); spin.add(m);
      rocks.push({ mesh:m, axis:axisOf(), rate:0.2 + 0.6 * rnd() });
    }
    ROCKS.forEach(([name, size, r, a, colour, rough, seed]) => {
      const m = new THREE.Mesh(rough ? lump(seed, rough) : ball, rockMat(colour, 0.9));
      m.scale.setScalar(size); m.position.set(r * Math.cos(a), 0, r * Math.sin(a)); m.rotation.set(seed, seed * 2, 0);
      const tag = nameTag(name, 0); tag.position.copy(m.position); tag.position.y += size * 1.3;
      spin.add(m, tag); tags.push(tag); rocks.push({ mesh:m, axis:axisOf(), rate:0.12 + 0.1 * rnd() });
    });
    const axis = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ transparent:true, opacity:0 }));   // no pole line here
    return { root, spin, clouds:null, axis, poles:[], moons, tags, u, radius:{ value:1 }, ringU:null, rate:0.03, time,
             fitV:4.0, fitH:5.4, star:false, own:true, near:2.5, rocks, mats };
  }
  // The dwarf planets all together (14 Nov 2026): the five side by side at their true
  // sizes, nearest the Sun on the left, each spinning, with its name.
  function buildDwarfs() {
    const u = [], root = new THREE.Group(), spins = [], tags = [], ball = new THREE.SphereGeometry(1, 64, 40), gap = 0.45;
    const mat = (frag, uniforms) => { u.push(uniforms); return new THREE.ShaderMaterial({ vertexShader:VERT, fragmentShader:frag, uniforms }); };
    const big = Math.max(...DWARFS.map(D => D.km)), wide = D => D.km / big * (D.shape ? D.shape[0] : 1);
    const half = (DWARFS.reduce((w, D) => w + 2 * wide(D), 0) + gap * (DWARFS.length - 1)) / 2;
    let x = -half;
    DWARFS.forEach(D => {
      const r = D.km / big, tilt = new THREE.Group(), spin = new THREE.Group();
      const m = new THREE.Mesh(ball, D.tint
        ? mat(ROCK, Object.assign(common(), { map:{ value:moonMap }, tint:{ value:new THREE.Color(D.tint) }, texMix:{ value:D.texMix }, amb:{ value:0.03 } }))
        : mat(SURFACE, Object.assign(common(), { map:{ value:tex(D.tex) }, night:{ value:null }, hasNight:{ value:0 }, gloss:{ value:0 }, halo:{ value:new THREE.Vector4(...D.halo) } })));
      if (D.shape) m.scale.set(...D.shape);
      tilt.rotation.z = Math.min(D.tilt, 30) * Math.PI / 180; tilt.scale.setScalar(r); tilt.position.x = x + wide(D);
      spin.add(m); tilt.add(spin); root.add(tilt);
      const tag = nameTag(D.name, 0); tag.position.set(x + wide(D), r + 0.12, 0); root.add(tag); tags.push(tag);
      spins.push({ spin, rate:0.25 * Math.pow(24 / D.turn, 0.4) });
      x += 2 * wide(D) + gap;
    });
    root.rotation.set(0.12, 0, 0);
    const axis = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ transparent:true, opacity:0 }));
    return { root, spin:new THREE.Group(), clouds:null, axis, poles:[], moons:[], tags, u, radius:{ value:1 }, ringU:null, rate:0, time:null,
             fitV:1.9, fitH:half + 0.35, star:false, near:1.6, spins };
  }

  // Stars all round (fixed: the planet turns, the sky doesn't).
  function stars(into) {
    const n = 1800, pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const z = Math.random() * 2 - 1, a = Math.random() * Math.PI * 2, r = Math.sqrt(1 - z * z), b = 0.35 + Math.random() ** 3 * 0.65, warm = Math.random();
      pos.set([600 * r * Math.cos(a), 600 * r * Math.sin(a), 600 * z], i * 3);
      col.set([b * (0.85 + 0.15 * warm), b * 0.92, b * (1 - 0.15 * warm)], i * 3);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    into.add(new THREE.Points(geo, new THREE.PointsMaterial({ size:1.6, sizeAttenuation:false, vertexColors:true })));
  }
  stars(scene);

  const common = () => ({ sunPos:{ value:SUN_POS_V }, fade:{ value:0 } });
  function build(P) {
    if (P.belt) return buildBelt(P);
    if (P.dwarfs) return buildDwarfs();
    const halo = new THREE.Vector4(...(P.halo || [0, 0, 0, 0])), u = [];
    const root = new THREE.Group(), tilt = new THREE.Group(), spin = new THREE.Group();
    root.rotation.set(0.3, 0.55, 0);                        // from a little above its orbit, turned so a
                                                            // sideways axis (Uranus) leans toward us and its rings open up
    tilt.rotation.z = P.tilt * Math.PI / 180;               // north pole leans toward the Sun side
    root.add(tilt); tilt.add(spin);
    const mat = (frag, uniforms, opts = {}) => { const m = new THREE.ShaderMaterial(Object.assign({ vertexShader:VERT, fragmentShader:frag, uniforms }, opts)); u.push(uniforms); return m; };
    const ball = new THREE.SphereGeometry(1, 96, 64);
    let time = null;
    if (P.star) {
      time = { value:0 };
      spin.add(new THREE.Mesh(ball, mat(STAR, Object.assign(common(), { map:{ value:tex(P.tex) }, time, hot:{ value:0 } }))));
    } else if (P.tint) {                                    // no map of it: a tinted, cratered ball (maybe stretched)
      const m = new THREE.Mesh(ball, mat(ROCK, Object.assign(common(), { map:{ value:moonMap }, tint:{ value:new THREE.Color(P.tint) }, texMix:{ value:P.texMix }, amb:{ value:0.03 } })));
      if (P.shape) m.scale.set(...P.shape);
      spin.add(m);
    } else {
      spin.add(new THREE.Mesh(ball, mat(SURFACE, Object.assign(common(), {
        map:{ value:tex(P.tex) }, night:{ value:P.night ? tex(P.night) : null }, hasNight:{ value:P.night ? 1 : 0 },
        gloss:{ value:P.gloss || 0 }, halo:{ value:halo } }))));
    }
    let clouds = null;
    if (P.clouds) {
      clouds = new THREE.Mesh(ball, mat(CLOUDS, Object.assign(common(), { map:{ value:tex(P.clouds) } }), { transparent:true, depthWrite:false }));
      clouds.scale.setScalar(1.012); tilt.add(clouds);
    }
    (P.glows || (P.halo ? [[1.14, P.halo, P.halo[3]]] : [])).forEach(([s, rgb, k]) => {
      const glow = new THREE.Mesh(ball, mat(GLOW, Object.assign(common(), { halo:{ value:new THREE.Vector4(rgb[0], rgb[1], rgb[2], k) },
        limb:{ value:Math.sqrt(1 - 1 / (s * s)) }, even:{ value:P.star ? 1 : 0 } }),
        { side:THREE.BackSide, transparent:true, depthWrite:false, blending:THREE.AdditiveBlending }));
      glow.scale.setScalar(s); tilt.add(glow);
    });
    const radius = { value:1 };                             // the planet's size now (it grows in on arrival)
    let ringU = null;
    if (P.rings) {
      const r = P.rings;
      ringU = Object.assign(common(), { map:{ value:r.tex ? tex(r.tex) : hoops() }, rIn:{ value:r.inner }, rOut:{ value:r.outer },
        opacity:{ value:r.opacity }, centre:{ value:CENTRE_V }, radius });
      const ring = new THREE.Mesh(new THREE.RingGeometry(r.inner, r.outer, 192, 1), mat(RINGS, ringU, { side:THREE.DoubleSide, transparent:true, depthWrite:false }));
      ring.rotation.x = -Math.PI / 2; tilt.add(ring);
    }
    // The spin axis poking out of each pole, with N and S. North is the pole on the
    // north side of the orbit (IAU rule for the Sun and planets), so for Venus and Uranus,
    // which spin backwards, it is the end the spin runs clockwise round. Pluto, a dwarf
    // planet, follows the newer right-hand rule (IAU 2009), like New Horizons' maps.
    const axis = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, -1.35, 0), new THREE.Vector3(0, 1.35, 0)]),
      new THREE.LineBasicMaterial({ color:0x9fb4ff, transparent:true, opacity:0 }));
    const up = P.tilt > 90 && P.name !== 'Pluto' ? -1 : 1, poleN = label('N'), poleS = label('S');
    poleN.position.set(0, 1.5 * up, 0); poleS.position.set(0, -1.5 * up, 0);
    tilt.add(axis, poleN, poleS);
    // Visible spin speed: slow ones turn slowly, fast ones faster (squashed so Venus still
    // visibly turns and Jupiter doesn't blur). Earth: one turn in ~25 s.
    let rate = 0.25 * Math.pow(24 / P.turn, 0.4);
    const far = P.rings ? P.rings.outer + 0.15 : 1.6;           // room for the N and S labels
    let fitV = far, fitH = far;
    const moons = [], tags = [];
    if (P.moons) {
      const M = P.moons, [lo, hi] = M.band, d = M.list.map(m => Math.log(m[1])), d0 = Math.min(...d), d1 = Math.max(...d);
      root.updateMatrixWorld(true);
      M.list.forEach(([name, , ratio, days, colour, texMix, inc = 0], k) => {
        const r = d1 > d0 ? lo + (hi - lo) * (d[k] - d0) / (d1 - d0) : lo;
        const size = ratio >= 0.2 ? ratio : Math.max(0.045, 0.3 * Math.sqrt(ratio));
        // Its orbit's plane: the planet's equator (tilted with it), or for our Moon the
        // plane Earth orbits the Sun in; then the orbit's own tilt.
        const plane = new THREE.Group(); plane.rotation.x = inc * Math.PI / 180;
        (M.plane === 'orbit' ? root : tilt).add(plane);
        const ring = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(
          Array.from({ length:160 }, (_, j) => new THREE.Vector3(r * Math.cos(j / 160 * Math.PI * 2), 0, r * Math.sin(j / 160 * Math.PI * 2)))),
          new THREE.LineBasicMaterial({ color:0x8fa3d8, transparent:true, opacity:0, depthWrite:false }));
        const pivot = new THREE.Group(); pivot.rotation.y = k * 2.4 + 0.8;
        const ball2 = new THREE.Mesh(new THREE.SphereGeometry(size, 32, 20), mat(MOON, Object.assign(common(), {
          map:{ value:moonMap }, tint:{ value:new THREE.Color(colour) }, texMix:{ value:texMix }, centre:{ value:CENTRE_V }, radius })));
        ball2.position.x = r;                                    // the same face always toward the planet, like the real ones
        const tag = nameTag(name, size * 6); tag.position.x = r;
        pivot.add(ball2, tag); plane.add(ring, pivot);
        moons.push({ pivot, rate:moonRate(days), ring }); tags.push(tag);
        // Room on screen at the starting view for this orbit (it is seen as an ellipse).
        plane.updateMatrixWorld(true);
        const n = new THREE.Vector3(0, 1, 0).transformDirection(plane.matrixWorld);
        fitV = Math.max(fitV, r * Math.sqrt(1 - n.y * n.y) + size + 0.25);
        fitH = Math.max(fitH, r * Math.sqrt(1 - n.x * n.x) + size + 0.2);
      });
      if (P.name === 'Pluto') rate = moons[0].rate;         // Pluto and Charon face each other for ever
    }
    return { root, spin, clouds, axis, poles:[poleN, poleS], moons, tags, u, radius, ringU, rate, time, fitV, fitH, star:!!P.star, near:2.1 };   // closest: the globe just fills the view (maps are 1024 px)
  }

  // Where the camera is: round the planet (az), above/below it (el), and how far
  // (zoom x the distance that fits the whole planet on screen).
  const HOME = { az:0, el:0, zoom:1 }, EL_MAX = 1.45, ZOOM_OUT = 2.6;
  let view = { ...HOME, vaz:0, vel:0 }, goal = null;
  // The Sun in the background of every planet (not on the Sun's own page), smaller and
  // fainter the farther the planet is from it (au = distance from the Sun, Earth = 1):
  // from Mercury to Mars a white-hot ball (sunBall, below), from Jupiter out a small
  // bright disc in a soft glow, from Pluto little more than a faint glow. Not true size
  // (from Saturn out that would be under a pixel), just the feel of it. Set every frame.
  function glowTex(stops) {
    const c = document.createElement('canvas'); c.width = c.height = 128;
    const x = c.getContext('2d'), g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
    stops.forEach(([at, colour]) => g.addColorStop(at, colour));
    x.fillStyle = g; x.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c);
  }
  const sprite = (map, opts) => new THREE.Sprite(new THREE.SpriteMaterial(Object.assign({ map, transparent:true, depthWrite:false, sizeAttenuation:false }, opts)));
  const sunDisc = sprite(glowTex([[0, '#fffdf2'], [0.55, '#ffe9ad'], [0.85, '#ffb347'], [0.95, 'rgba(255,150,40,1)'], [1, 'rgba(255,150,40,0)']]));
  const sunGlow = sprite(glowTex([[0, 'rgba(255,235,180,1)'], [0.1, 'rgba(255,200,120,0.6)'], [0.35, 'rgba(255,150,60,0.18)'], [1, 'rgba(255,120,40,0)']]),
                         { blending:THREE.AdditiveBlending });
  const sunTag = nameTag('Sun', 0);
  // From Mercury to Mars the Sun is a real ball: white-hot middle, orange edge, corona.
  const sunU = { map:{ value:tex('sun') }, fade:{ value:0 }, time:{ value:0 }, hot:{ value:1 } };
  const sunBall = new THREE.Mesh(new THREE.SphereGeometry(1, 64, 40), new THREE.ShaderMaterial({ vertexShader:VERT, fragmentShader:STAR, uniforms:sunU }));
  const coronaU = INFO[0].glows.map(([s, rgb, k]) => {
    const u = { halo:{ value:new THREE.Vector4(rgb[0], rgb[1], rgb[2], k) }, sunPos:{ value:SUN_POS_V }, fade:{ value:0 },
      limb:{ value:Math.sqrt(1 - 1 / (s * s)) }, even:{ value:1 } };
    const m = new THREE.Mesh(sunBall.geometry, new THREE.ShaderMaterial({ vertexShader:VERT, fragmentShader:GLOW, uniforms:u,
      side:THREE.BackSide, transparent:true, depthWrite:false, blending:THREE.AdditiveBlending }));
    m.scale.setScalar(s); sunBall.add(m); return u;
  });
  const UP = new THREE.Vector3();
  scene.add(sunGlow, sunDisc, sunBall, sunTag);

  const built = {};
  let cur = -1, curP = null, since = 0, visible = false, last = 0, dist = 5, base = 5;
  let sys = false, planetView = null;                      // sys: showing the SOLAR SYSTEM tab
  function start() { if (!visible) { visible = true; cv.style.display = 'block'; last = performance.now(); requestAnimationFrame(frame); } }
  // Page i; on the dwarf planets' page sub = 0 for all together, 1 ... for one of DWARFS.
  function show(i, sub = 0) {
    start();
    lab.style.display = 'none';
    if (sys || scl || gal) { sys = scl = gal = false; view = planetView || { ...HOME, vaz:0, vel:0 }; goal = null; since = performance.now(); }
    const P = INFO[i].dwarfs && sub ? DWARFS[sub - 1] : INFO[i], key = P.name;
    if (key === cur) return;
    if (cur !== -1) scene.remove(built[cur].root);
    cur = key; curP = P; built[key] = built[key] || build(P); scene.add(built[key].root);
    built[key].spin.rotation.y = -1.2; since = performance.now();
    view = { ...HOME, vaz:0, vel:0 }; goal = null;
  }
  function hide() { visible = false; cv.style.display = 'none'; lab.style.display = 'none'; pts.clear(); pinch = null; }
  function reset() { if (gal) galHome(); else if (scl) scaleHome(); else goal = sys ? { az:0, el:SYS_VIEWS[sysCtx].el, zoom:1 } : { ...HOME }; view.vaz = view.vel = 0; }
  const zoomRange = () => gal ? GAL_Z : scl ? SCL_Z : sys ? [0.18, 1.5] : [built[cur].near / base, ZOOM_OUT];
  const clampView = () => { const [lo, hi] = zoomRange(); view.zoom = Math.min(Math.max(view.zoom, lo), hi); view.el = Math.min(Math.max(view.el, -EL_MAX), EL_MAX); };
  // Double-tap glides home; a flick coasts and slows down.
  function steer(dt) {
    if (goal) {
      const g = Math.min(dt * 6, 1);
      view.az += (goal.az - view.az) * g; view.el += (goal.el - view.el) * g; view.zoom += (goal.zoom - view.zoom) * g;
      if (Math.abs(view.az - goal.az) + Math.abs(view.el - goal.el) + Math.abs(view.zoom - goal.zoom) < 0.002) goal = null;
    } else if (!pts.size) {
      view.az += view.vaz * dt; view.el += view.vel * dt;
      const f = Math.pow(0.05, dt); view.vaz *= f; view.vel *= f;
    }
    clampView();
  }
  function placeCam(tx = 0, tz = 0) {                      // round the point (tx, 0, tz)
    const ce = Math.cos(view.el);
    cam.position.set(tx + dist * Math.sin(view.az) * ce, dist * Math.sin(view.el), tz + dist * Math.cos(view.az) * ce);
    cam.lookAt(tx, 0, tz); cam.updateProjectionMatrix(); cam.updateMatrixWorld();
  }

  function frame(t) {
    if (!visible) return;
    requestAnimationFrame(frame);
    const dt = Math.min((t - last) / 1000, 0.1); last = t;
    const w = cv.clientWidth, h = cv.clientHeight;
    if (!w || !h) return;
    const px = Math.min(window.devicePixelRatio || 1, 2);
    if (cv.width !== Math.round(w * px) || cv.height !== Math.round(h * px)) { R.setPixelRatio(px); R.setSize(w, h, false); }
    if (gal) { frameGalaxy(t, dt, w, h); return; }
    if (scl) { frameScale(t, dt, w, h); return; }
    if (sys) { frameSystem(t, dt, w, h); return; }
    const B = built[cur], k = Math.min((t - since) / 700, 1), e = 1 - (1 - k) ** 3;   // arrive: grow, fade in, spin up
    cam.aspect = w / h;
    const tan = Math.tan(15 * Math.PI / 180);
    base = Math.max(B.fitV / tan, B.fitH / (tan * cam.aspect)) * 1.05;
    steer(dt);
    dist += (base * view.zoom - dist) * Math.min(dt * 10, 1);
    placeCam();
    const au = curP.au || 1, inner = au < 2, perPx = 2 * tan / h, pxPer = 1 / perPx;
    // The Sun, 3x the starting camera distance (full screen) away. Its size is an angle
    // seen from the planet: inner planets 3.4° x (1 AU / distance) (Mercury 9°, Earth
    // 3.4°, Mars 2.3°), a white-hot ball; from Jupiter out a spark (Jupiter 0.7°), never
    // under 3 px.
    const D = 3 * B.fitV / tan * 1.05, size = D * (inner ? 0.06 / au : 0.0239 * Math.pow(au, -0.45));
    SUN_W.copy(SUN_DIR).multiplyScalar(D);
    const sunPx = Math.max(size / cam.position.distanceTo(SUN_W) * pxPer, 3), glowPx = sunPx * (inner ? 2.5 : 7.5 * Math.pow(au, 0.1));
    sunBall.scale.setScalar(size / 2);
    const toSun = cam.position.distanceTo(SUN_W);
    [sunBall, sunDisc, sunGlow].forEach(o => o.position.copy(SUN_W));
    const noSun = B.star || B.own;                          // the Sun's own page, or a page with its own Sun in it
    sunBall.visible = inner && !noSun; sunDisc.visible = !sunBall.visible && !noSun; sunGlow.visible = sunTag.visible = !noSun;
    sunDisc.scale.setScalar(sunPx * perPx);
    sunGlow.scale.setScalar(glowPx * perPx);
    sunGlow.material.opacity = Math.min(Math.max(Math.pow(au, -0.5), 0.6), 1.5) * e;   // never fainter than a visible haze
    UP.set(0, 1, 0).applyQuaternion(cam.quaternion);        // name just above it on screen
    sunTag.position.copy(SUN_W).addScaledVector(UP, (sunPx / 2 + 6) / pxPer * toSun);
    sunDisc.material.opacity = e; sunTag.material.opacity = 0.6 * e;
    sunU.fade.value = e; sunU.time.value = t / 1000; coronaU.forEach(u => { u.fade.value = e; });
    CENTRE_V.set(0, 0, 0).applyMatrix4(cam.matrixWorldInverse);
    SUN_POS_V.copy(SUN_DIR).transformDirection(cam.matrixWorldInverse).multiplyScalar(1e4).add(CENTRE_V);
    B.spin.rotation.y += B.rate * dt + (1 - e) * 3 * dt;
    if (B.clouds) B.clouds.rotation.y = B.spin.rotation.y * 1.08;
    if (B.time) B.time.value = t / 1000;
    B.root.scale.setScalar(0.7 + 0.3 * e);
    B.axis.material.opacity = 0.45 * e;
    B.poles.forEach(p => { p.material.opacity = 0.9 * e; });
    B.moons.forEach(m => { m.pivot.rotation.y += m.rate * dt; m.ring.material.opacity = 0.22 * e; });
    if (B.rocks) B.rocks.forEach(r => r.mesh.rotateOnAxis(r.axis, r.rate * dt));
    if (B.spins) B.spins.forEach(x => { x.spin.rotation.y += x.rate * dt; });
    if (B.mats) B.mats.forEach(([m, k]) => { m.opacity = k * e; });
    B.tags.forEach(s => { s.material.opacity = 0.95 * e; });
    B.u.forEach(u => { u.fade.value = e; });
    B.radius.value = B.root.scale.x;
    R.render(scene, cam);
  }

  // The solar system view (26 Sep; RUN and TIME TRAVEL): the Sun in the middle and the planets round it, each
  // where the orrery puts it for its date (S.lon, degrees, counter-clockwise seen from
  // above, as on the RUN screen's map), moving while it runs. Lit by the Sun in the
  // middle, so every planet's day side faces it. Not to scale, like the orrery itself:
  // the orbits are spaced out evenly-ish (ORBIT, all in one flat plane) and the planets
  // are drawn far bigger than life, the small ones most (width ~ real width ^ 0.7). Drag
  // to turn, pinch to zoom, double-tap = home, tap a planet (or the Sun) to open its page.
  // 13 Nov 2026 (the user): Pluto left this view (the model has eight arms) and the asteroid
  // belt came in between Mars and Jupiter: a ring of specks that goes round with the date
  // (BELT_RATE, one lap in about 4.6 years, as Ceres); tap it for its PLANETS page.
  const ORBIT = [2.9, 4.4, 5.9, 7.4, 10.5, 13.1, 15.3, 17.3];                 // Mercury ... Neptune
  const KM = [2440, 6052, 6371, 3390, 69911, 58232, 25362, 24622];            // real radii, km
  const SYS_N = ORBIT.length, BELT_R = 8.75, BELT_W = 0.55, BELT_RATE = 360 / (4.6 * 365.25);   // degrees a day
  const SUN_R = 2.15, SYS_R = ORBIT[SYS_N - 1] + 0.6, SYS_BIG = 1.25;      // Sun and planets drawn bigger since 15 Nov 2026
  // The same scene on three tabs, each with its own camera (26 Sep): SOLAR SYSTEM from a
  // little above; TIME TRAVEL (a wide panel under the heading) steeper, to fill it; RUN
  // (a tall panel beside the controls) nearly from above, like the old flat map.
  // 14 Nov 2026 (the user): RUN looks from the same angle as TIME TRAVEL, and every visit
  // starts from the starting angle (the screen at the bottom of the picture), so the
  // picture always matches the model in front of it, e.g. the row in travel mode.
  // 15 Nov 2026 (the user: bigger, use the width, a little cut off is fine): RUN's wide panel
  // is looked at from lower down, so the orbits make a wide oval that fills it, and fitted
  // tight (Neptune's orbit just touching the edges, names and all may run off a little).
  const SYS_VIEWS = { system:{ el:0.5, tight:true }, travel:{ el:0.8 }, run:{ el:1.2 } };
  Object.values(SYS_VIEWS).forEach(v => { v.view = { az:0, el:v.el, zoom:1, vaz:0, vel:0 }; });
  let sysCtx = 'system';
  // Framing: the camera distance (and how far toward the near side it aims, so the orbit
  // ellipse sits in the middle) that just fits Neptune's orbit and the names above it, for
  // a tilt and a panel shape. Worked out by trying, once per tilt and shape.
  const fits = {}, fitCam = new THREE.PerspectiveCamera(30, 1, 0.1, 5000), V3 = new THREE.Vector3();
  function sysFit(el, aspect, tight) {
    const key = el + '|' + aspect.toFixed(3) + (tight ? 't' : '');
    if (fits[key]) return fits[key];
    fitCam.aspect = aspect; fitCam.updateProjectionMatrix();
    const pts = [];
    for (let j = 0; j < 72; j++) { const a = j / 72 * Math.PI * 2; (tight ? [0] : [0, 1.1]).forEach(y => pts.push([(SYS_R + (tight ? -0.6 : 0.3)) * Math.cos(a), y, (SYS_R + (tight ? -0.6 : 0.3)) * Math.sin(a)])); }
    const mx = tight ? 0.985 : 0.96, my = tight ? 0.97 : 0.93;
    const ok = (d, off) => {
      fitCam.position.set(0, d * Math.sin(el), off + d * Math.cos(el)); fitCam.lookAt(0, 0, off); fitCam.updateMatrixWorld();
      return pts.every(([x, y, z]) => { V3.set(x, y, z).project(fitCam); return V3.z < 1 && Math.abs(V3.x) < mx && Math.abs(V3.y) < my; });
    };
    let best = null;
    for (let off = 0; off <= SYS_R * 0.4; off += SYS_R * 0.05) {
      let lo = 5, hi = 400;
      if (!ok(hi, off)) continue;
      for (let i = 0; i < 30; i++) { const mid = (lo + hi) / 2; if (ok(mid, off)) hi = mid; else lo = mid; }
      if (!best || hi < best.d * 0.99) best = { d:hi, off };   // aim off-centre only if it really helps
    }
    return (fits[key] = best || { d:SYS_R * 4, off:0 });
  }
  const SYS_SUN_V = new THREE.Vector3();                   // the Sun's centre, view space
  let sysScene = null, sysBodies = [], sysSun = null, sysSince = 0, sysState = null, sysBelt = null;
  function dot() {                                         // a soft round speck
    const c = document.createElement('canvas'); c.width = c.height = 32;
    const x = c.getContext('2d'), g = x.createRadialGradient(16, 16, 0, 16, 16, 16);
    g.addColorStop(0, '#fff'); g.addColorStop(0.55, '#fff'); g.addColorStop(1, 'rgba(255,255,255,0)');
    x.fillStyle = g; x.fillRect(0, 0, 32, 32); return new THREE.CanvasTexture(c);
  }
  function buildBelt3() {
    const group = new THREE.Group(), map = dot();
    let s = 5; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
    [[1000, 1.5], [70, 2.4]].forEach(([n, size]) => {       // many faint specks, a few bigger ones (quieter since 14 Nov 2026)
      const pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) {
        const a = rnd() * Math.PI * 2, r = BELT_R + (rnd() + rnd() + rnd() - 1.5) / 1.5 * BELT_W, b = 0.3 + 0.45 * rnd(), warm = rnd() * 0.25;
        pos.set([r * Math.cos(a), (rnd() - 0.5) * 0.3, r * Math.sin(a)], i * 3);
        col.set([b, b * (1 - warm * 0.35), b * (1 - warm)], i * 3);
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
      group.add(new THREE.Points(geo, new THREE.PointsMaterial({ size, map, sizeAttenuation:false, vertexColors:true, transparent:true, opacity:0, depthWrite:false })));
    });
    const tag = nameTag('Asteroid belt', 0); tag.position.set(BELT_R, 0.35, 0); group.add(tag);
    sysScene.add(group);
    tag.visible = false;                                    // names are drawn by sysLabels now
    sysBelt = { group, tag, lon:null };
  }
  function buildSystem() {
    sysScene = new THREE.Scene(); sysScene.background = new THREE.Color(0x02030a); stars(sysScene);
    const u = [], mat = (frag, uniforms, opts = {}) => { u.push(uniforms); return new THREE.ShaderMaterial(Object.assign({ vertexShader:VERT, fragmentShader:frag, uniforms }, opts)); };
    const ball = new THREE.SphereGeometry(1, 64, 40);
    const glowMesh = (s, rgb, k, even) => {
      const m = new THREE.Mesh(ball, mat(GLOW, { halo:{ value:new THREE.Vector4(rgb[0], rgb[1], rgb[2], k) }, sunPos:{ value:SYS_SUN_V }, fade:{ value:0 },
        limb:{ value:Math.sqrt(1 - 1 / (s * s)) }, even:{ value:even } }, { side:THREE.BackSide, transparent:true, depthWrite:false, blending:THREE.AdditiveBlending }));
      m.scale.setScalar(s); return m;
    };
    // The Sun: its boiling map and corona, as on its own page.
    const sunT = { value:0 }, sunMesh = new THREE.Mesh(ball, mat(STAR, { map:{ value:tex('sun') }, fade:{ value:0 }, time:sunT, hot:{ value:0 } }));
    INFO[0].glows.forEach(([g, rgb, k]) => sunMesh.add(glowMesh(g, rgb, k, 1)));
    sunMesh.scale.setScalar(SUN_R);
    const sunName = nameTag('Sun', -1.35);                // hangs below the Sun on screen (placed every frame)
    sysScene.add(sunMesh, sunName);
    sunName.visible = false;
    sysSun = { mesh:sunMesh, time:sunT, tag:sunName };
    buildBelt3();
    for (let p = 0; p < SYS_N; p++) {
      const P = BODIES[p], r = SYS_BIG * (0.36 + 0.5 * Math.pow(KM[p] / KM[4], 0.7));
      const holder = new THREE.Group(), tilt = new THREE.Group(), spin = new THREE.Group();
      tilt.rotation.z = P.tilt * Math.PI / 180; holder.add(tilt); tilt.add(spin);
      const halo = new THREE.Vector4(...(P.halo || [0, 0, 0, 0]));
      const globe = new THREE.Mesh(ball, mat(SURFACE, { sunPos:{ value:SYS_SUN_V }, fade:{ value:0 }, map:{ value:tex(P.tex) },
        night:{ value:P.night ? tex(P.night) : null }, hasNight:{ value:P.night ? 1 : 0 }, gloss:{ value:P.gloss || 0 }, halo:{ value:halo } }));
      globe.scale.setScalar(r); spin.add(globe);
      if (P.halo) { const g = glowMesh(1.14, P.halo, P.halo[3], 0); g.scale.multiplyScalar(r); tilt.add(g); }
      let clouds = null;
      if (P.clouds) {
        clouds = new THREE.Mesh(ball, mat(CLOUDS, { sunPos:{ value:SYS_SUN_V }, fade:{ value:0 }, map:{ value:tex(P.clouds) } }, { transparent:true, depthWrite:false }));
        clouds.scale.setScalar(r * 1.012); tilt.add(clouds);
      }
      const centre = new THREE.Vector3();
      if (P.rings) {
        const q = P.rings, ring = new THREE.Mesh(new THREE.RingGeometry(q.inner, q.outer, 128, 1), mat(RINGS, { sunPos:{ value:SYS_SUN_V }, fade:{ value:0 },
          map:{ value:q.tex ? tex(q.tex) : hoops() }, rIn:{ value:q.inner }, rOut:{ value:q.outer }, opacity:{ value:q.opacity }, centre:{ value:centre }, radius:{ value:r } },
          { side:THREE.DoubleSide, transparent:true, depthWrite:false }));
        ring.rotation.x = -Math.PI / 2; ring.scale.setScalar(r); tilt.add(ring);
      }
      const tag = nameTag(P.name, 0); tag.position.set(0, r * (P.rings ? 1.45 : 1.08), 0); tag.visible = false; holder.add(tag);
      const line = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(
        Array.from({ length:256 }, (_, j) => new THREE.Vector3(ORBIT[p] * Math.cos(j / 256 * Math.PI * 2), 0, ORBIT[p] * Math.sin(j / 256 * Math.PI * 2)))),
        new THREE.LineBasicMaterial({ color:0x3a4a82, transparent:true, opacity:0, depthWrite:false }));
      sysScene.add(holder, line);
      sysBodies.push({ holder, spin, clouds, tag, line, centre, r, lon:null, colour:new THREE.Color(P.color), rate:0.25 * Math.pow(24 / P.turn, 0.4) });
    }
    sysSun.u = u;
  }
  // index.html calls this on every redraw of the SOLAR SYSTEM, TIME TRAVEL and RUN tabs
  // with the orrery's state (V: lon, running, years_per_min, mean). ctx = which tab (its
  // own camera); pick = false: a tap doesn't open a planet's page (TIME TRAVEL, RUN).
  let sysPick = true;
  function system(st, { ctx = 'system', pick = true } = {}) {
    start(); sysState = st; sysPick = pick;
    if (!sysScene) buildSystem();
    if (!sys || ctx !== sysCtx || scl || gal) {
      if (scl || gal) { scl = gal = false; sys = false; }
      if (!sys) { if (cur !== -1) planetView = view; sysSince = performance.now(); }
      sys = true; sysCtx = ctx; view = SYS_VIEWS[ctx].view; goal = null;
      Object.assign(view, { az:0, el:SYS_VIEWS[ctx].el, zoom:1, vaz:0, vel:0 });
    }
  }
  const DEG = Math.PI / 180;
  function frameSystem(t, dt, w, h) {
    const k = Math.min((t - sysSince) / 700, 1), e = 1 - (1 - k) ** 3, tan = Math.tan(15 * DEG);
    cam.aspect = w / h;
    const F = sysFit(SYS_VIEWS[sysCtx].el, cam.aspect, SYS_VIEWS[sysCtx].tight);   // the whole system, just fitting
    base = F.d;
    steer(dt);
    dist += (base * view.zoom - dist) * Math.min(dt * 10, 1);
    placeCam(F.off * Math.sin(view.az), F.off * Math.cos(view.az));
    SYS_SUN_V.set(0, 0, 0).applyMatrix4(cam.matrixWorldInverse);
    const st = sysState || {}, run = !!st.running;
    sysBodies.forEach((b, p) => {
      // Where the orrery says; glide there after a jump (Today, GO), follow exactly while running.
      const want = st.lon ? st.lon[p] : 0;
      if (b.lon === null || run) b.lon = want;
      else b.lon += (((want - b.lon) % 360 + 540) % 360 - 180) * Math.min(dt * 4, 1);
      b.holder.position.set(ORBIT[p] * Math.cos(b.lon * DEG), 0, -ORBIT[p] * Math.sin(b.lon * DEG));
      // Too fast to see (over 1.5 turns a second): a blur round its orbit instead, as on the RUN map.
      const blur = run && st.mean && st.mean[p] * st.years_per_min * 365.25 / 60 > 540;
      b.holder.visible = !blur;
      b.line.material.color.set(blur ? b.colour : 0x3a4a82); b.line.material.opacity = (blur ? 0.9 : 0.55) * e;
      b.spin.rotation.y += b.rate * dt;
      if (b.clouds) b.clouds.rotation.y = b.spin.rotation.y * 1.08;
      b.centre.copy(b.holder.position).applyMatrix4(cam.matrixWorldInverse);
      b.tag.material.opacity = 0.9 * e;
      // Travel mode: the planets stand in one row, so the names go beside them, left and right by turns.
      b.tag.center.set(st.lined_up && !run ? p % 2 : 0.5, st.lined_up && !run ? 0.5 : -0.35);
    });
    // The belt turns with the date, gliding after a jump like the planets.
    const beltWant = (((st.day || 0) * BELT_RATE) % 360 + 360) % 360;
    if (sysBelt.lon === null || run) sysBelt.lon = beltWant;
    else sysBelt.lon += (((beltWant - sysBelt.lon) % 360 + 540) % 360 - 180) * Math.min(dt * 4, 1);
    sysBelt.group.rotation.y = sysBelt.lon * DEG;
    sysBelt.group.children.forEach(c => { c.material.opacity = (c === sysBelt.tag ? (st.lined_up && !run ? 0 : 0.55) : 0.6) * e; });   // no belt name over the travel-mode row
    sysSun.time.value = t / 1000; sysSun.tag.material.opacity = 0.9 * e;
    sysSun.tag.position.set(0, -1, 0).applyQuaternion(cam.quaternion).multiplyScalar(SUN_R * 1.15);
    sysSun.u.forEach(u => { u.fade.value = e; });
    R.render(sysScene, cam);
    sysLabels(w, h, st, run, e);
  }
  // A tap on the SOLAR SYSTEM tab: the Sun or the planet nearest the finger (on screen),
  // if close enough, opens its page (index.html's onPick, with 0 = Sun, 1 = Mercury ...).
  // Names in the solar system view (15 Nov 2026, the user: smaller, on a floating line): drawn
  // flat on a canvas laid over the 3D one, each name small at the end of a short slanted
  // line from its planet. A name goes up-right if there is room, else up-left, down-right,
  // down-left, then further out, so names never sit on each other or on a planet (in the
  // travel-mode row they fan out to both sides). A name keeps its place while it still fits.
  const lab = document.createElement('canvas'), lg = lab.getContext('2d');
  lab.style.cssText = 'position:absolute;pointer-events:none;display:none';
  cv.after(lab);
  const LAB_DIRS = [[1, -1], [-1, -1], [1, 1], [-1, 1]], labKept = {}, ORIGIN = new THREE.Vector3();
  function sysLabels(w, h, st, run, e) {
    const k = cv.parentElement.clientWidth / 800, px = Math.min(window.devicePixelRatio || 1, 2), tan = Math.tan(15 * DEG);
    if (lab.width !== Math.round(w * px) || lab.height !== Math.round(h * px)) { lab.width = Math.round(w * px); lab.height = Math.round(h * px); }
    Object.assign(lab.style, { display:'block', left:cv.offsetLeft + 'px', top:cv.offsetTop + 'px', width:w + 'px', height:h + 'px' });
    lg.setTransform(px, 0, 0, px, 0, 0); lg.clearRect(0, 0, w, h); lg.globalAlpha = e;
    lg.font = `600 ${(12.5 * k).toFixed(1)}px system-ui, sans-serif`; lg.textBaseline = 'middle'; lg.lineJoin = 'round';
    const items = [], th = 15 * k;
    const add = (name, pos, r, dim) => {
      const d = cam.position.distanceTo(pos); V3.copy(pos).project(cam);
      if (V3.z < 1) items.push({ name, x:(V3.x + 1) / 2 * w, y:(1 - V3.y) / 2 * h, r:r / d / tan * h / 2, tw:lg.measureText(name).width, dim });
    };
    add('Sun', ORIGIN, SUN_R);
    sysBodies.forEach((b, p) => { if (b.holder.visible) add(BODIES[p].name, b.holder.position, b.r * (BODIES[p].rings ? 1.5 : 1)); });
    if (!(st.lined_up && !run)) add('Asteroid belt', V3b.set(BELT_R * Math.cos(sysBelt.lon * DEG), 0, -BELT_R * Math.sin(sysBelt.lon * DEG)), 0, true);
    const placed = [];
    const clash = q => q.x0 < 2 || q.x1 > w - 2 || q.y0 < 2 || q.y1 > h - 2 ||
      placed.some(o => q.x0 < o.x1 + 3 && q.x1 > o.x0 - 3 && q.y0 < o.y1 + 1 && q.y1 > o.y0 - 1) ||
      items.some(o => { const cx = Math.min(Math.max(o.x, q.x0), q.x1), cy = Math.min(Math.max(o.y, q.y0), q.y1); return Math.hypot(o.x - cx, o.y - cy) < o.r + 2; });
    const text = (name, x, y, align, dim) => {
      lg.textAlign = align; lg.lineWidth = 3 * k; lg.strokeStyle = 'rgba(2,3,10,0.85)'; lg.strokeText(name, x, y);
      lg.fillStyle = dim ? '#9aa6c9' : '#e6ebff'; lg.fillText(name, x, y);
    };
    items.forEach((it, n) => {
      if (!n) {                                             // the Sun: its name straight under it
        const y = it.y + it.r + 11 * k; placed.push({ x0:it.x - it.tw / 2, x1:it.x + it.tw / 2, y0:y - th / 2, y1:y + th / 2 });
        text(it.name, it.x, y, 'center'); return;
      }
      const spot = c => {
        const [dx, dy] = LAB_DIRS[c % 4], L = [9, 22, 36, 52][c >> 2] * k, sx = it.x + dx * it.r * 0.72, sy = it.y + dy * it.r * 0.72, ex = sx + dx * L, ey = sy + dy * L * 0.8;
        const x0 = dx > 0 ? ex + 3 * k : ex - 3 * k - it.tw;
        return { sx, sy, ex, ey, dx, x0, x1:x0 + it.tw, y0:ey - th / 2, y1:ey + th / 2 };
      };
      // The first free spot; the spot it had before wins if still free and its line is no longer.
      let q = null, c = 0;
      for (; c < 16 && !q; c++) { const t = spot(c); if (!clash(t)) q = t; }
      c -= 1;
      const was = labKept[it.name];
      if (was !== undefined && was !== c && (!q || (was >> 2) <= (c >> 2))) { const t = spot(was); if (!clash(t)) { q = t; c = was; } }
      if (q && e >= 1) labKept[it.name] = c;               // not while the view is still flying in
      if (!q) { if (it.dim) return; q = spot(0); }          // nowhere free: the belt's name is left out, a planet's goes first choice
      placed.push(q);
      lg.strokeStyle = it.dim ? 'rgba(143,163,216,0.4)' : 'rgba(159,180,255,0.7)'; lg.lineWidth = 1 * k;
      lg.beginPath(); lg.moveTo(q.sx, q.sy); lg.lineTo(q.ex, q.ey); lg.stroke();
      text(it.name, q.dx > 0 ? q.x0 : q.x1, q.ey, q.dx > 0 ? 'left' : 'right', it.dim);
    });
  }
  const V3b = new THREE.Vector3();
  const pickRay = new THREE.Raycaster(), FLAT = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  function pickAt(x, y) {
    const rect = cv.getBoundingClientRect(), w = rect.width, h = rect.height, tan = Math.tan(15 * DEG);
    let best = null;
    [[0, new THREE.Vector3(), SUN_R]].concat(sysBodies.map((b, i) => [PAGE_OF[i], b.holder.position.clone(), b.r, b.holder.visible]))
      .forEach(([n, pos, r, shown = true]) => {
        if (!shown) return;
        const d = cam.position.distanceTo(pos), s = pos.project(cam);
        const sx = rect.left + (s.x + 1) / 2 * w, sy = rect.top + (1 - s.y) / 2 * h, reach = Math.max(r / d / tan * h / 2 + 12, 30);
        const off = Math.hypot(sx - x, sy - y);
        if (s.z < 1 && off < reach && (!best || off / reach < best.k)) best = { n, k:off / reach };
      });
    if (!best) {                                            // no planet there: on the asteroid belt?
      pickRay.setFromCamera({ x:(x - rect.left) / w * 2 - 1, y:1 - (y - rect.top) / h * 2 }, cam);
      const hit = pickRay.ray.intersectPlane(FLAT, V3);
      if (hit && Math.abs(Math.hypot(hit.x, hit.z) - BELT_R) < BELT_W + 0.35) best = { n:BELT_PAGE };
    }
    if (best && sysPick && window.PlanetView.onPick) window.PlanetView.onPick(best.n);
  }

  // SCALE tab (26 Sep, the user's idea): the Sun and the nine planets side by side at
  // their true sizes, all to one scale, in 3D with their real maps, lit by the Sun (a real
  // ball, 109 Earths wide). Handled like SOLAR SYSTEM: one finger spins round, two fingers
  // zoom (from close enough to fill the screen with Mercury to far enough to see the whole
  // Sun), a tap on a planet or the Sun flies to it, double-tap = back to the start. It
  // opens far enough out to show all nine beside the Sun's edge (SCL_Z0, the view the user
  // set on the Pi, 26 Sep); pinch in for the small ones. World units: Earth's radius is
  // about 4.8; the gaps between planets are not to scale (true gaps would be huge).
  const KM_R = [2439.7, 6051.8, 6371, 3389.5, 69911, 58232, 25362, 24622, 1188.3], SUN_KM = 695700, SCL_K = 4.8 / 6371;
  const SCL_EL = 0.12, SCL_TGT = new THREE.Vector3(), SCL_HOME = new THREE.Vector3(), SCL_UP = new THREE.Vector3();
  let scl = false, sclScene = null, sclCam = null, sclBodies = [], sclSun = null, sclSince = 0, sclU = [], sclGoalT = null;
  const sclView = { az:0, el:SCL_EL, zoom:1, vaz:0, vel:0 };
  const SCALE_SUN_V = new THREE.Vector3();                 // the Sun's centre, view space (it lights the planets)
  function tagSprite(lines, colour) {                      // a name (1-2 lines), the same size on screen at any distance
    const c = document.createElement('canvas'); c.width = 256; c.height = 16 + 40 * lines.length;
    const x = c.getContext('2d');
    x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round'; x.lineWidth = 7; x.strokeStyle = 'rgba(2,3,10,0.9)';
    lines.forEach(([text, font, fill], i) => { x.font = font; x.strokeText(text, 128, 26 + i * 40); x.fillStyle = fill || colour; x.fillText(text, 128, 26 + i * 40); });
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map:new THREE.CanvasTexture(c), transparent:true, depthWrite:false, depthTest:false, sizeAttenuation:false }));
    sp.scale.set(0.165, 0.062 * c.height / 96, 1); return sp;
  }
  function buildScale() {
    sclScene = new THREE.Scene(); sclScene.background = new THREE.Color(0x02030a);
    sclCam = new THREE.PerspectiveCamera(30, 1, 0.5, 60000);
    // Stars ride with the camera, very far out (the view zooms out thousands of units).
    const sky = new THREE.Group(); stars(sky); sky.scale.setScalar(80); sclCam.add(sky); sclScene.add(sclCam);
    const mat = (frag, uniforms, opts = {}) => { sclU.push(uniforms); return new THREE.ShaderMaterial(Object.assign({ vertexShader:VERT, fragmentShader:frag, uniforms }, opts)); };
    const ball = new THREE.SphereGeometry(1, 96, 64);
    const glow = (s, rgb, k, even) => {
      const m = new THREE.Mesh(ball, mat(GLOW, { halo:{ value:new THREE.Vector4(rgb[0], rgb[1], rgb[2], k) }, sunPos:{ value:SCALE_SUN_V }, fade:{ value:0 },
        limb:{ value:Math.sqrt(1 - 1 / (s * s)) }, even:{ value:even } }, { side:THREE.BackSide, transparent:true, depthWrite:false, blending:THREE.AdditiveBlending }));
      m.scale.setScalar(s); return m;
    };
    const R = SUN_KM * SCL_K, y = 0, gap = 25;
    const time = { value:0 }, sun = new THREE.Mesh(ball, mat(STAR, { map:{ value:tex('sun') }, fade:{ value:0 }, time, hot:{ value:0 } }));
    INFO[0].glows.forEach(([s, rgb, k]) => sun.add(glow(s, rgb, k, 1)));
    sun.scale.setScalar(R); sun.position.set(-R, y, 0);     // its right-hand edge at x = 0
    const sunTag = tagSprite([['Sun', '700 34px system-ui, sans-serif', '#ffe28a'], ['109 Earths wide', '600 24px system-ui, sans-serif', '#ffe9c0']]);
    sclScene.add(sun, sunTag);
    sclSun = { mesh:sun, time, tag:sunTag, R, centre:sun.position };
    let x = gap;
    for (let p = 0; p < 9; p++) {
      const P = BODIES[p], r = KM_R[p] * SCL_K, span = P.rings ? P.rings.outer : 1, half = r * span;
      const holder = new THREE.Group(), tilt = new THREE.Group(), spin = new THREE.Group();
      tilt.rotation.z = P.tilt * DEG; holder.add(tilt); tilt.add(spin);
      spin.add(new THREE.Mesh(ball, mat(SURFACE, { sunPos:{ value:SCALE_SUN_V }, fade:{ value:0 }, map:{ value:tex(P.tex) },
        night:{ value:P.night ? tex(P.night) : null }, hasNight:{ value:P.night ? 1 : 0 }, gloss:{ value:P.gloss || 0 },
        halo:{ value:new THREE.Vector4(...(P.halo || [0, 0, 0, 0])) } })));
      if (P.halo) tilt.add(glow(1.14, P.halo, P.halo[3], 0));
      const centre = new THREE.Vector3(), radius = { value:r };
      if (P.rings) {
        const q = P.rings, ring = new THREE.Mesh(new THREE.RingGeometry(q.inner, q.outer, 128, 1), mat(RINGS, { sunPos:{ value:SCALE_SUN_V }, fade:{ value:0 },
          map:{ value:q.tex ? tex(q.tex) : hoops() }, rIn:{ value:q.inner }, rOut:{ value:q.outer }, opacity:{ value:q.opacity }, centre:{ value:centre }, radius },
          { side:THREE.DoubleSide, transparent:true, depthWrite:false }));
        ring.rotation.x = -Math.PI / 2; tilt.add(ring);
      }
      holder.position.set(x + half, y, 0); holder.scale.setScalar(r);
      const tag = tagSprite([[P.name, '700 30px system-ui, sans-serif', '#eef2ff']]);   // just the name (the user: no "N Earths")
      const lead = new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]),
        new THREE.LineBasicMaterial({ color:0x8fa3d8, transparent:true, opacity:0.6, depthTest:false }));
      sclScene.add(holder, tag, lead);
      sclBodies.push({ holder, spin, tag, lead, centre, r, span, rate:0.25 * Math.pow(24 / P.turn, 0.4) });
      x += 2 * half + gap;
    }
    // Aim: halfway from the Sun's edge to just past Jupiter (zoom 1 fits that span; SCL_Z0 shows all).
    SCL_HOME.set((-60 + sclBodies[4].holder.position.x + sclBodies[4].r + 20) / 2, 0, 0);
    SCL_TGT.copy(SCL_HOME);
  }
  function scale() {
    start();
    if (!sclScene) buildScale();
    lab.style.display = 'none';
    if (!scl) {                                              // each visit starts at the start
      if (!sys && !gal && cur !== -1) planetView = view;
      gal = false; scl = true; sclSince = performance.now();
      Object.assign(sclView, { az:0, el:SCL_EL, zoom:SCL_Z0, vaz:0, vel:0 }); view = sclView; goal = null;
      SCL_TGT.copy(SCL_HOME); sclGoalT = null;
    }
  }
  function scaleHome() { goal = { az:0, el:SCL_EL, zoom:SCL_Z0 }; sclGoalT = SCL_HOME.clone(); }
  // A tap: fly to the planet (or the Sun) under the finger, near enough to fill much of the view.
  function pickScale(x, y) {
    const rect = cv.getBoundingClientRect(), tan = Math.tan(15 * DEG);
    let best = null;
    sclBodies.forEach(b => {
      const pos = b.holder.position, d = sclCam.position.distanceTo(pos), s = pos.clone().project(sclCam);
      const sx = rect.left + (s.x + 1) / 2 * rect.width, sy = rect.top + (1 - s.y) / 2 * rect.height;
      const reach = Math.max(b.r * b.span / d / tan * rect.height / 2 + 12, 26), off = Math.hypot(sx - x, sy - y);
      if (s.z < 1 && off < reach && (!best || off / reach < best.k)) best = { k:off / reach, pos, size:b.r * b.span };
    });
    if (!best) {                                            // the Sun: anywhere on its ball
      const c = sclSun.centre, d = sclCam.position.distanceTo(c), s = c.clone().project(sclCam);
      const sx = rect.left + (s.x + 1) / 2 * rect.width, sy = rect.top + (1 - s.y) / 2 * rect.height;
      if (s.z < 1 && Math.hypot(sx - x, sy - y) < sclSun.R / d / tan * rect.height / 2) best = { pos:c, size:sclSun.R };
    }
    if (!best) return;
    sclGoalT = best.pos.clone();
    goal = { az:view.az, el:view.el, zoom:Math.min(Math.max(best.size * 6.5 / base, SCL_Z[0]), SCL_Z[1]) };
  }
  const SCL_Z = [0.04, 10];                                // zoom range, times the Sun-to-Jupiter fit (10: the whole Sun)
  const SCL_Z0 = 3.6;                                      // the start: all nine planets (matched to the user's view, 26 Sep)
  function frameScale(t, dt, w, h) {
    const k = Math.min((t - sclSince) / 700, 1), e = 1 - (1 - k) ** 3, tan = Math.tan(15 * DEG);
    sclCam.aspect = w / h;
    const J = sclBodies[4], half = (J.holder.position.x + J.r + 20 + 60) / 2;
    base = Math.max(half / (tan * sclCam.aspect), J.r * 1.6 / tan);
    steer(dt);
    if (sclGoalT) { SCL_TGT.lerp(sclGoalT, Math.min(dt * 5, 1)); if (SCL_TGT.distanceTo(sclGoalT) < 0.01) sclGoalT = null; }
    dist += (base * view.zoom - dist) * Math.min(dt * 10, 1);
    const ce = Math.cos(view.el);
    sclCam.position.set(SCL_TGT.x + dist * Math.sin(view.az) * ce, SCL_TGT.y + dist * Math.sin(view.el), SCL_TGT.z + dist * Math.cos(view.az) * ce);
    const c = sclSun.centre, out = sclCam.position.clone().sub(c);   // never inside the Sun
    if (out.length() < sclSun.R * 1.03) sclCam.position.copy(c).addScaledVector(out.normalize(), sclSun.R * 1.03);
    sclCam.lookAt(SCL_TGT); sclCam.updateProjectionMatrix(); sclCam.updateMatrixWorld();
    SCALE_SUN_V.copy(c).applyMatrix4(sclCam.matrixWorldInverse);
    // Names: same size on screen; big planets just below, tiny ones further off on a thin
    // line, above and below by turns (all "below" = down on the screen).
    SCL_UP.set(0, 1, 0).applyQuaternion(sclCam.quaternion);
    const pxScale = h / 416;
    // Far out the row is so short on screen that names would pile up: then only the Sun's.
    const a0 = sclBodies[0].holder.position.clone().project(sclCam), a8 = sclBodies[8].holder.position.clone().project(sclCam);
    const names = Math.hypot((a8.x - a0.x) * w, (a8.y - a0.y) * h) / 2 / 8 > 34 * pxScale;
    sclBodies.forEach((b, p) => {
      b.spin.rotation.y += b.rate * dt;
      const pos = b.holder.position, wpp = 2 * sclCam.position.distanceTo(pos) * tan / h;   // world units per screen pixel there
      const tiny = b.r / wpp < 12 * pxScale, up = tiny && p % 2 === 1;
      const off = tiny ? b.r + 46 * pxScale * wpp : Math.max(b.r * (b.span > 1 ? 0.8 : 1), 3 * wpp) + 20 * pxScale * wpp;
      b.tag.position.copy(pos).addScaledVector(SCL_UP, up ? off : -off);
      b.lead.visible = tiny;
      if (tiny) {
        const a = pos.clone().addScaledVector(SCL_UP, (up ? 1 : -1) * (b.r + 3 * wpp)), z = pos.clone().addScaledVector(SCL_UP, (up ? 1 : -1) * (off - 12 * pxScale * wpp));
        const g = b.lead.geometry.attributes.position; g.setXYZ(0, a.x, a.y, a.z); g.setXYZ(1, z.x, z.y, z.z); g.needsUpdate = true;
      }
      b.centre.copy(pos).applyMatrix4(sclCam.matrixWorldInverse);
      b.tag.visible = names; if (!names) b.lead.visible = false;
      b.tag.material.opacity = e;
    });
    // The Sun's name: on the part of its ball facing the camera, a little down the screen.
    V3.copy(sclCam.position).sub(c).normalize();
    sclSun.tag.position.copy(c).addScaledVector(V3, sclSun.R).addScaledVector(SCL_UP, -0.25 * Math.min(sclSun.R, sclCam.position.distanceTo(c) * tan));
    sclSun.time.value = t / 1000; sclSun.tag.material.opacity = e;
    sclU.forEach(u => { u.fade.value = e; });
    R.render(sclScene, sclCam);
  }

  // GALAXY tab (14 Nov 2026, the user's idea): where the solar system is in the Milky Way.
  // The galaxy seen from outside, in 3D, slowly turning: a bar in the middle, spiral arms,
  // and "You are here" at the Sun, with the Sun's path round the centre and the distance to
  // it. Handled like SCALE: one finger turns the view, two fingers zoom, tap "You are here"
  // (or the centre) to fly in and follow it, double-tap = back to the start; each visit
  // starts at the start.
  // A drawing, not a photo: nobody has seen the Milky Way from outside. The shape follows
  // the usual map (NASA/JPL-Caltech, R. Hurt, 2008-2017): 1 unit = 1,000 light-years, the
  // disc 100,000 across, the Sun 26,000 from the centre. Looking down from the north, the
  // Sun at the bottom, the galaxy turns clockwise and the arms trail: four arms 90° apart,
  // each r = 10.8 x e^(0.2217 x angle) (12.5° pitch), which puts Scutum-Centaurus 15,
  // Sagittarius 22, Perseus 31 and the Outer arm 43 thousand light-years out on the Sun's
  // side, and starts the two big arms (Scutum-Centaurus, Perseus) at the ends of the bar
  // (27° from the line to the Sun, the near end to the left). The Sun sits in a short arm
  // of its own (Orion) between Sagittarius and Perseus.
  // Later the same day (the user: better graphics, turning, fewer names): the picture is
  // worked out on the graphics chip, once, into a 2048 px picture (GAL_FRAG: arms that
  // wander and clump, dark dust along their inside edges, pink clouds where stars are born,
  // the yellow bar and bulge, a grain of faint stars), and the whole galaxy turns, one lap
  // in GAL_LAP seconds (really about 230 million years), all in one piece (the real one's
  // middle laps faster than its edge). The arms' names went: just "You are here", the
  // centre and the distance.
  const GAL_R = 50, GAL_SUN = 26, GAL_K = Math.tan(12.5 * Math.PI / 180), GAL_BAR = -117 * Math.PI / 180, GAL_EL = 0.52, GAL_EXT = 56, GAL_LAP = 150, GAL_LAP_MY = 230;   // one lap: 150 s on the screen, 230 million years really
  const GAL_ARMS = [{ turn:0, from:9, big:false }, { turn:1, from:13, big:true }, { turn:2, from:12, big:false }, { turn:3, from:13, big:true }];   // Norma (Outer), Scutum-Centaurus, Sagittarius, Perseus
  // A point on an arm, in the flat map (x right, y up, the Sun at (0, -26)): d = angle on
  // from the Sun's side, counter-clockwise.
  const galArm = (turn, d) => { const r = 10.8 * Math.exp(GAL_K * (d + turn * Math.PI / 2)), a = -Math.PI / 2 + d; return [r * Math.cos(a), r * Math.sin(a), r]; };
  const galSpur = d => { const r = GAL_SUN * Math.exp(GAL_K * d), a = -Math.PI / 2 + d; return [r * Math.cos(a), r * Math.sin(a), r]; };   // the Orion Arm
  const galW = (x, y, h = 0) => new THREE.Vector3(x, h, -y);                    // map -> world
  const GAL_SUN_W = galW(0, -GAL_SUN), GAL_Z = [0.22, 1.7], GAL_TGT = new THREE.Vector3(), GAL_SUN_NOW = new THREE.Vector3();
  let gal = false, galScene = null, galCam = null, galSince = 0, galFollow = null, galFade = [], galSpin = null, galT0 = 0;
  const galView = { az:0, el:GAL_EL, zoom:1, vaz:0, vel:0 };
  function galRnd(seed) { let s = seed; return () => (s = (s * 16807) % 2147483647) / 2147483647; }   // the same galaxy every time
  // The galaxy's light, seen flat from above: p = place in the map, thousands of light-years.
  const GAL_FRAG = `varying vec2 vUv; uniform float ext, kk, bar;
    const float PI = 3.14159265;
    float hash(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
    const mat2 TURN = mat2(0.8, 0.6, -0.6, 0.8);            // each finer layer of noise is turned, so no grid shows
    vec2 grad(vec2 i) { float a = hash(i) * 6.2831853; return vec2(cos(a), sin(a)); }
    float noise(vec2 p) { vec2 i = floor(p), f = fract(p), u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);   // smooth, with no grid showing; about 0 to 1
      float a = dot(grad(i), f), b = dot(grad(i + vec2(1.0, 0.0)), f - vec2(1.0, 0.0)), c = dot(grad(i + vec2(0.0, 1.0)), f - vec2(0.0, 1.0)), d = dot(grad(i + vec2(1.0, 1.0)), f - vec2(1.0, 1.0));
      return 0.5 + 0.7 * mix(mix(a, b, u.x), mix(c, d, u.x), u.y); }
    // Round soft patches, one in some of the squares of a grid (rare = how many squares stay empty).
    float blobs(vec2 g, float rare) { vec2 id = floor(g), f = fract(g) - 0.5, o = vec2(hash(id + 3.1), hash(id + 7.7)) - 0.5;
      return smoothstep(0.36, 0.0, length(f - o * 0.5)) * step(rare, hash(id + 11.3)); }
    float fbm(vec2 p) { float a = 0.5, s = 0.0; for (int i = 0; i < 5; i++) { s += a * noise(p); p = TURN * p * 2.03 + 17.0; a *= 0.5; } return s; }
    float ridge(vec2 p) { float a = 0.5, s = 0.0; for (int i = 0; i < 4; i++) { s += a * (1.0 - abs(noise(p) * 2.0 - 1.0)); p = TURN * p * 2.1 + 31.0; a *= 0.5; } return s; }
    void main() {
      vec2 p = (vUv * 2.0 - 1.0) * ext;
      float r = length(p), th = atan(p.y, p.x);
      float n1 = fbm(p * 0.16), n2 = fbm(p * 0.55 + 40.0), n3 = fbm(p * 1.9 + 80.0);
      // The four arms: how far this place is from the nearest one (they wander a little).
      float d0 = th + PI / 2.0;
      float psi = d0 - log(max(r, 0.5) / 10.8) / kk + (n1 - 0.5) * 1.0 + (n2 - 0.5) * 0.3;
      float j = floor(-psi / (PI / 2.0) + 0.5), q = psi + j * PI / 2.0, big = step(0.5, mod(j, 2.0));
      float wide = mix(1.25, 1.75, big) * (0.55 + r / 50.0), d = r * q * 0.2164;
      // Light from the nearest arm and from the next one over (so there is no edge halfway between them).
      float q2 = q - sign(q) * PI / 2.0, wide2 = mix(1.75, 1.25, big) * (0.55 + r / 50.0), d2 = r * q2 * 0.2164;
      float arm = (exp(-d * d / (wide * wide)) + 0.42 * exp(-d * d / (wide * wide * 6.5))) * mix(0.62, 1.0, big)
                + (exp(-d2 * d2 / (wide2 * wide2)) + 0.42 * exp(-d2 * d2 / (wide2 * wide2 * 6.5))) * mix(1.0, 0.62, big);
      arm *= smoothstep(8.0, 14.0, r) * (1.0 - smoothstep(40.0, 53.0, r));
      // The Sun's own short arm (Orion).
      float ds = atan(sin(d0), cos(d0)), dsp = r * (ds - log(max(r, 0.5) / 26.0) / kk + (n2 - 0.5) * 0.12) * 0.2164;
      arm += (exp(-dsp * dsp / 1.1) + 0.4 * exp(-dsp * dsp / 6.0)) * smoothstep(-0.6, -0.25, ds) * (1.0 - smoothstep(0.3, 0.7, ds)) * 0.5;
      float fall = exp(-r / 27.0);
      float arms = arm * fall * (0.4 + 1.3 * smoothstep(0.3, 0.7, n2) + 0.3 * n3) * 2.1;
      float disc = exp(-r / 17.0) * (0.6 + 0.8 * smoothstep(0.3, 0.7, n1));
      // Dark dust: a lane along the inside edge of each arm, and wisps everywhere.
      float fil = ridge(p * 0.45 + 9.0);
      float lane = exp(-pow((d - 1.0 * wide) / (0.7 * wide), 2.0)) * smoothstep(8.0, 14.0, r) * (1.0 - smoothstep(38.0, 50.0, r));
      float dust = clamp(lane * (0.1 + 0.75 * fil) + 0.3 * smoothstep(0.78, 1.0, fil) * smoothstep(5.0, 12.0, r), 0.0, 0.8);
      // Bright young star clusters, and pink clouds where stars are being born, in the arms.
      float knots = blobs(p * 1.1 + 5.0, 0.5) * 1.5 * arm * fall;
      float glow = blobs(p * 0.85 + 60.0, 0.72) * 1.5 * arm * fall;
      // The bar and the bulge: old, yellow stars.
      float cb = cos(bar), sb = sin(bar);
      vec2 b = vec2(p.x * cb + p.y * sb, -p.x * sb + p.y * cb);
      float barL = exp(-(b.x * b.x / 85.0 + b.y * b.y / 7.0)), bulge = exp(-r * r / 22.0), core = exp(-r * r / 2.2);
      vec3 c = vec3(0.78, 0.80, 0.95) * disc * 0.55 + vec3(0.45, 0.66, 1.0) * arms + vec3(0.8, 0.9, 1.0) * knots + vec3(1.0, 0.28, 0.45) * glow * 0.95;
      // A grain of single stars (seen when zoomed in).
      vec2 g = p * 8.0, id = floor(g), f = fract(g) - 0.5, o = vec2(hash(id + 3.1), hash(id + 7.7)) - 0.5;
      c += vec3(0.9, 0.93, 1.0) * smoothstep(0.22, 0.0, length(f - o * 0.6)) * pow(hash(id), 6.0) * (disc * 1.2 + arms * 2.0 + 0.01) * 0.9;
      c *= 1.0 - dust;
      c += vec3(1.0, 0.80, 0.55) * (barL * 1.0 + bulge * 1.3) * (1.0 - 0.3 * dust) + vec3(1.0, 0.95, 0.85) * core * 1.4;
      c *= 1.0 - smoothstep(46.0, 54.5, r);
      gl_FragColor = vec4(1.0 - exp(-c * 1.75), 1.0);
    }`;
  function galPicture() {
    const N = Math.min(2048, R.capabilities.maxTextureSize);
    const rt = new THREE.WebGLRenderTarget(N, N, { minFilter:THREE.LinearMipmapLinearFilter, magFilter:THREE.LinearFilter, generateMipmaps:true, depthBuffer:false });
    rt.texture.anisotropy = aniso;
    const sc = new THREE.Scene(), quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({ fragmentShader:GAL_FRAG,
      vertexShader:'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }',
      uniforms:{ ext:{ value:GAL_EXT }, kk:{ value:GAL_K }, bar:{ value:GAL_BAR } }, depthTest:false, depthWrite:false }));
    quad.frustumCulled = false; sc.add(quad);
    R.setRenderTarget(rt); R.render(sc, new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)); R.setRenderTarget(null);
    quad.geometry.dispose(); quad.material.dispose();
    return rt.texture;
  }
  function buildGalaxy() {
    galScene = new THREE.Scene(); galScene.background = new THREE.Color(0x02030a);
    galCam = new THREE.PerspectiveCamera(30, 1, 0.5, 6000);
    const sky = new THREE.Group(); stars(sky); sky.scale.setScalar(4); sky.children[0].material.opacity = 0.4; sky.children[0].material.transparent = true;
    galScene.add(sky);
    galSpin = new THREE.Group(); galScene.add(galSpin);     // everything that turns
    const fade = (m, o) => { m.transparent = true; m.opacity = 0; galFade.push([m, o]); return m; };
    // The picture, lying flat.
    const flat = new THREE.Mesh(new THREE.PlaneGeometry(2 * GAL_EXT, 2 * GAL_EXT),
      fade(new THREE.MeshBasicMaterial({ map:galPicture(), blending:THREE.AdditiveBlending, depthWrite:false, side:THREE.DoubleSide }), 1));
    flat.rotation.x = -Math.PI / 2; galSpin.add(flat);
    // Stars with a little height, soft and faint, so the galaxy is a thin disc with a fat
    // middle when seen from the side (where the flat picture thins to nothing).
    const rnd = galRnd(8675309), pos = [], col = [], bell = () => (rnd() + rnd() + rnd() - 1.5) / 1.5;
    const star = (mx, my, h, [r, g, b], k) => { pos.push(mx, h, -my); col.push(r * k, g * k, b * k); };
    const TINT = { blue:[0.7, 0.82, 1], white:[1, 0.97, 0.92], gold:[1, 0.82, 0.58] };
    GAL_ARMS.concat([{ spur:true, big:false }]).forEach(A => {
      const d0 = A.spur ? -0.42 : Math.log(A.from / 10.8) / GAL_K - A.turn * Math.PI / 2, d1 = A.spur ? 0.5 : Math.log(GAL_R / 10.8) / GAL_K - A.turn * Math.PI / 2;
      const n = Math.round((d1 - d0) * (A.big ? 330 : 230));
      for (let i = 0; i < n; i++) {
        const d = d0 + (d1 - d0) * rnd(), [ax, ay, r] = A.spur ? galSpur(d) : galArm(A.turn, d), wide = 1.5 * (0.7 + r / GAL_R);
        star(ax + bell() * wide, ay + bell() * wide, bell() * 0.55, rnd() < 0.7 ? TINT.blue : TINT.white, (0.14 + 0.45 * rnd() ** 3) * (1 - 0.5 * r / GAL_R));
      }
    });
    for (let i = 0; i < 2200; i++) {                       // between the arms: fewer toward the edge
      const r = -15 * Math.log(1 - rnd() * 0.955), a = rnd() * Math.PI * 2;
      if (r < GAL_R) star(r * Math.cos(a), r * Math.sin(a), bell() * 0.7, rnd() < 0.5 ? TINT.white : TINT.gold, 0.08 + 0.22 * rnd() ** 3);
    }
    for (let i = 0; i < 1600; i++) {                       // the bulge and the bar
      const along = bell() * 9, across = bell() * 3.2, cb = Math.cos(GAL_BAR), sb = Math.sin(GAL_BAR);
      star(along * cb - across * sb, along * sb + across * cb, bell() * 2.8 * Math.exp(-Math.abs(along) / 8), TINT.gold, 0.12 + 0.25 * rnd() ** 2);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3)); geo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(col), 3));
    galSpin.add(new THREE.Points(geo, fade(new THREE.PointsMaterial({ map:dot(), size:2.6, sizeAttenuation:false, vertexColors:true, blending:THREE.AdditiveBlending, depthWrite:false }), 1)));
    // The bulge's glow, a ball of light that shows from the side too.
    const glow = new THREE.Sprite(fade(new THREE.SpriteMaterial({ map:glowTex([[0, 'rgba(255,236,200,0.8)'], [0.2, 'rgba(255,212,150,0.36)'], [0.5, 'rgba(255,190,120,0.1)'], [1, 'rgba(255,180,110,0)']]),
      blending:THREE.AdditiveBlending, depthWrite:false }), 0.8));
    glow.scale.setScalar(16); galSpin.add(glow);
    // The Sun's path round the centre (one lap in about 230 million years) and the line to the centre.
    const ring = [];
    for (let j = 0; j <= 180; j++) { const a = j / 180 * Math.PI * 2; ring.push(galW(GAL_SUN * Math.cos(a), GAL_SUN * Math.sin(a), 0.05)); }
    galSpin.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(ring), fade(new THREE.LineBasicMaterial({ color:0xffd36b, depthWrite:false }), 0.55)));
    galSpin.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([galW(0, 0, 0.05), galW(0, -GAL_SUN, 0.05)]),
      fade(new THREE.LineBasicMaterial({ color:0xffffff, depthWrite:false }), 0.5)));
  }
  function galaxy() {
    start();
    if (!galScene) buildGalaxy();
    if (!gal) {                                              // each visit starts at the start
      if (!sys && !scl && cur !== -1) planetView = view;
      scl = false; gal = true; galSince = galT0 = performance.now();
      Object.assign(galView, { az:0, el:GAL_EL, zoom:1, vaz:0, vel:0 }); view = galView; goal = null;
      GAL_TGT.set(0, 0, 0); galFollow = null;
    }
  }
  function galHome() { goal = { az:0, el:GAL_EL, zoom:1 }; galFollow = null; }
  // A tap near "You are here" flies in to the Sun and stays with it; near the centre, to the centre.
  function pickGalaxy(x, y) {
    const rect = cv.getBoundingClientRect();
    let best = null;
    [[GAL_SUN_NOW, 0.3, 'sun'], [ORIGIN, 0.38, null]].forEach(([pos, zoom, follow]) => {
      const s = V3.copy(pos).project(galCam), off = Math.hypot(rect.left + (s.x + 1) / 2 * rect.width - x, rect.top + (1 - s.y) / 2 * rect.height - y);
      if (s.z < 1 && off < 46 && (!best || off < best.off)) best = { zoom, follow, off };
    });
    if (!best) return;
    galFollow = best.follow; goal = { az:view.az, el:view.el, zoom:best.zoom };
  }
  function frameGalaxy(t, dt, w, h) {
    const k = Math.min((t - galSince) / 900, 1), e = 1 - (1 - k) ** 3, tan = Math.tan(15 * DEG);
    galCam.aspect = w / h;
    base = Math.max(GAL_R * 1.04 / (tan * galCam.aspect), GAL_R * 1.3 * Math.sin(GAL_EL) / tan);   // the whole disc, at the starting tilt
    // Clockwise seen from the north (above); every visit starts with the Sun at the front.
    galSpin.rotation.y = -(t - galT0) / 1000 / GAL_LAP * Math.PI * 2;
    GAL_SUN_NOW.copy(GAL_SUN_W).applyAxisAngle(V3.set(0, 1, 0), galSpin.rotation.y);
    steer(dt);
    dist += (base * view.zoom - dist) * Math.min(dt * 10, 1);
    GAL_TGT.lerp(galFollow === 'sun' ? GAL_SUN_NOW : ORIGIN, Math.min(dt * 5, 1));
    const ce = Math.cos(view.el);
    galCam.position.set(GAL_TGT.x + dist * Math.sin(view.az) * ce, GAL_TGT.y + dist * Math.sin(view.el), GAL_TGT.z + dist * Math.cos(view.az) * ce);
    galCam.lookAt(GAL_TGT); galCam.updateProjectionMatrix(); galCam.updateMatrixWorld();
    galFade.forEach(([m, o]) => { m.opacity = o * e; });
    R.render(galScene, galCam);
    galLabels(w, h, e, t);
  }
  // The few words over the galaxy: "You are here" at the Sun (a ring that pulses), the
  // centre, and the distance between them.
  function galLabels(w, h, e, t) {
    const k = cv.parentElement.clientWidth / 800, px = Math.min(window.devicePixelRatio || 1, 2);
    if (lab.width !== Math.round(w * px) || lab.height !== Math.round(h * px)) { lab.width = Math.round(w * px); lab.height = Math.round(h * px); }
    Object.assign(lab.style, { display:'block', left:cv.offsetLeft + 'px', top:cv.offsetTop + 'px', width:w + 'px', height:h + 'px' });
    lg.setTransform(px, 0, 0, px, 0, 0); lg.clearRect(0, 0, w, h); lg.textBaseline = 'middle'; lg.lineJoin = 'round';
    const at = pos => { V3.copy(pos).project(galCam); return V3.z < 1 ? [(V3.x + 1) / 2 * w, (1 - V3.y) / 2 * h] : null; };
    const text = (s, x, y, size, weight, fill, align = 'center') => {
      lg.font = `${weight} ${(size * k).toFixed(1)}px system-ui, sans-serif`; lg.textAlign = align;
      lg.lineWidth = 3.5 * k; lg.strokeStyle = 'rgba(2,3,10,0.85)'; lg.strokeText(s, x, y); lg.fillStyle = fill; lg.fillText(s, x, y);
    };
    lg.globalAlpha = e;
    const c = at(ORIGIN), s = at(GAL_SUN_NOW);
    if (c) text('Centre of the galaxy', c[0], c[1] - 15 * k, 12.5, 700, '#ffe2b0');
    const len = c && s ? Math.hypot(c[0] - s[0], c[1] - s[1]) : 0;
    if (len > 95 * k) {                                   // beside the middle of the line (not when the line is short: the Sun on the far side, or seen side-on)
      let nx = -(s[1] - c[1]) / len, ny = (s[0] - c[0]) / len;
      if (ny > 0.3 || (Math.abs(ny) <= 0.3 && nx < 0)) { nx = -nx; ny = -ny; }   // above the line; to the right of an upright one
      lg.font = `600 ${(11.5 * k).toFixed(1)}px system-ui, sans-serif`;
      const half = lg.measureText('26,000 light-years').width / 2;
      text('26,000 light-years', (c[0] + s[0]) / 2 + nx * (9 * k + Math.abs(nx) * half), (c[1] + s[1]) / 2 + ny * 9 * k, 11.5, 600, '#ffffff');
    }
    if (s) {
      const beat = (t / 1600) % 1;
      lg.strokeStyle = '#ffd400'; lg.lineWidth = 2 * k;
      lg.beginPath(); lg.arc(s[0], s[1], 7 * k, 0, 7); lg.stroke();
      lg.globalAlpha = e * (1 - beat); lg.beginPath(); lg.arc(s[0], s[1], (7 + 16 * beat) * k, 0, 7); lg.stroke();
      lg.globalAlpha = e; lg.fillStyle = '#fff'; lg.beginPath(); lg.arc(s[0], s[1], 2.2 * k, 0, 7); lg.fill();
      const below = s[1] < h - 62 * k && !(c && s[1] < c[1]), y = below ? s[1] + 24 * k : s[1] - 38 * k;   // on the far side of the centre: above the ring, clear of the centre's name
      text('You are here', s[0], y, 17, 800, '#ffd400');
      text(view.zoom < 0.45 ? 'The Sun and all its planets: far too small to see' : 'the Sun and all its planets', s[0], y + 17 * k, 11.5, 600, '#fff3c4');
    }
    // The clock, top left: every visit starts at today, and the years go by as the galaxy
    // turns (one lap = 230 million years, so about 1.5 million years every second).
    const my = Math.floor((t - galT0) / 1000 / GAL_LAP * GAL_LAP_MY * 10) / 10, laps = Math.floor(my / GAL_LAP_MY);
    lg.globalAlpha = e;
    text(my < 0.1 ? 'Today' : `${my.toLocaleString('en-US', { minimumFractionDigits:1, maximumFractionDigits:1 })} million years`, 12 * k, 22 * k, 19, 800, '#ffffff', 'left');
    text(my < 0.1 ? 'watch the years go by…' : 'from today' + (laps ? ` · ${laps} ${laps === 1 ? 'lap' : 'laps'} of the galaxy` : ''), 12 * k, 43 * k, 12, 600, '#ffd36b', 'left');
    lg.globalAlpha = 1;
  }

  // Touch: one finger drags the view round the planet (sideways = round it, up/down =
  // over the poles) and flicks coast; two fingers pinch to zoom; double-tap = home.
  // Mouse: drag, wheel = zoom, double-click = home.
  const pts = new Map();
  let pinch = null, lastTap = { t:0, x:0, y:0 };
  const spread = () => { const [a, b] = [...pts.values()]; return Math.hypot(a.x - b.x, a.y - b.y); };
  let press = null;                                        // this touch, to tell a tap from a drag
  cv.addEventListener('pointerdown', e => {
    if (cur === -1 && !sys && !scl && !gal) return;
    press = pts.size ? null : { x:e.clientX, y:e.clientY, t:performance.now() };
    try { cv.setPointerCapture(e.pointerId); } catch (err) { /* pointer already gone */ }
    const now = performance.now();
    pts.set(e.pointerId, { x:e.clientX, y:e.clientY, t:now });
    view.vaz = view.vel = 0; goal = null;
    if (pts.size === 2) pinch = { d:Math.max(spread(), 1), zoom:view.zoom };
    if (pts.size === 1) {
      if (now - lastTap.t < 350 && Math.hypot(e.clientX - lastTap.x, e.clientY - lastTap.y) < 40) { reset(); lastTap.t = 0; }
      else lastTap = { t:now, x:e.clientX, y:e.clientY };
    }
  });
  cv.addEventListener('pointermove', e => {
    const p = pts.get(e.pointerId);
    if (!p) return;
    const now = performance.now(), dx = e.clientX - p.x, dy = e.clientY - p.y, secs = Math.max((now - p.t) / 1000, 0.008);
    Object.assign(p, { x:e.clientX, y:e.clientY, t:now });
    if (pts.size >= 2) { if (pinch) { view.zoom = pinch.zoom * pinch.d / Math.max(spread(), 1); clampView(); } return; }
    const k = Math.PI * 1.4 / cv.clientWidth;
    view.az -= dx * k; view.el += dy * k; clampView();
    view.vaz = -dx * k / secs * 0.6; view.vel = dy * k / secs * 0.6;
  });
  ['pointerup', 'pointercancel'].forEach(n => cv.addEventListener(n, e => {
    const p = pts.get(e.pointerId);
    if (press && n === 'pointerup' && (sys || scl || gal) && pts.size === 1 && performance.now() - press.t < 450 &&
        Math.hypot(e.clientX - press.x, e.clientY - press.y) < 14) (gal ? pickGalaxy : scl ? pickScale : pickAt)(e.clientX, e.clientY);   // a tap: visit / fly to what's there
    press = null;
    if (p && performance.now() - p.t > 120) view.vaz = view.vel = 0;   // held still before letting go
    view.vaz = Math.max(Math.min(view.vaz, 6), -6); view.vel = Math.max(Math.min(view.vel, 4), -4);
    pts.delete(e.pointerId);
    if (pts.size < 2) pinch = null;
    if (pts.size) view.vaz = view.vel = 0;                // lifted one finger of a pinch: no flick
  }));
  cv.addEventListener('wheel', e => { e.preventDefault(); goal = null; view.zoom *= Math.exp(e.deltaY * 0.0015); clampView(); }, { passive:false });

  window.PlanetView = { INFO, DWARFS, ok:true, show, hide, reset, system, scale, galaxy, onPick:null };
})();
