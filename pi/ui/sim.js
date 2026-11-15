// Browser stand-in for server.py, so the real touchscreen page (index.html) can run
// without a Pi or servos: index.html?sim loads this and talks to window.orrerySim
// instead of /api/state and /api/action. Used by the website's front-panel mock-up.
// Keep it in step with server.py (Orrery.act / state / tick): same speeds, same
// slider-applies-on-release / arrow-key choose-then-Run rules, same in-place date editing, same circular orbits and "racing".
(function () {
  const NAMES = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto'];
  // JPL "Approximate Positions of the Planets", as pi/planets.py (a, e, I, L, peri, node, then rates per century).
  const ORBITS = [
    [0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593, 0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081],
    [0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255, 0.00000390, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418],
    [1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0, 0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0],
    [1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891, 0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343],
    [5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909, -0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106],
    [9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448, -0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794],
    [19.18916464, 0.04725744, 0.77263783, 313.23810451, 170.95427630, 74.01692503, -0.00196176, -0.00004397, -0.00242939, 428.48202785, 0.40805281, 0.04240589],
    [30.06992276, 0.00859048, 1.77004347, -55.12002969, 44.96476227, 131.78422574, 0.00026291, 0.00005105, 0.00035372, 218.45945325, -0.32241464, -0.00508664],
    [39.48211675, 0.24882730, 17.14001206, 238.92903833, 224.06891629, 110.30393684, -0.00031596, 0.00005170, 0.00004818, 145.20780515, -0.04062942, -0.01183482],
  ];
  // Table 2a/2b (3000 BC - 3000 AD), Mercury ... Neptune, used outside 1800-2100 (as planets.py).
  const ORBITS_OLD = [
    [0.38709843, 0.20563661, 7.00559432, 252.25166724, 77.45771895, 48.33961819, 0.00000000, 0.00002123, -0.00590158, 149472.67486623, 0.15940013, -0.12214182],
    [0.72332102, 0.00676399, 3.39777545, 181.97970850, 131.76755713, 76.67261496, -0.00000026, -0.00005107, 0.00043494, 58517.81560260, 0.05679648, -0.27274174],
    [1.00000018, 0.01673163, -0.00054346, 100.46691572, 102.93005885, -5.11260389, -0.00000003, -0.00003661, -0.01337178, 35999.37306329, 0.31795260, -0.24123856],
    [1.52371243, 0.09336511, 1.85181869, -4.56813164, -23.91744784, 49.71320984, 0.00000097, 0.00009149, -0.00724757, 19140.29934243, 0.45223625, -0.26852431],
    [5.20248019, 0.04853590, 1.29861416, 34.33479152, 14.27495244, 100.29282654, -0.00002864, 0.00018026, -0.00322699, 3034.90371757, 0.18199196, 0.13024619],
    [9.54149883, 0.05550825, 2.49424102, 50.07571329, 92.86136063, 113.63998702, -0.00003065, -0.00032044, 0.00451969, 1222.11494724, 0.54179478, -0.25015002],
    [19.18797948, 0.04685740, 0.77298127, 314.20276625, 172.43404441, 73.96250215, -0.00020455, -0.00001550, -0.00180155, 428.49512595, 0.09266985, 0.05739699],
    [30.06952752, 0.00895439, 1.77005520, 304.22289287, 46.68158724, 131.78635853, 0.00006447, 0.00000818, 0.00022400, 218.46515314, 0.01009938, -0.00606302],
  ];
  const EXTRA_OLD = { 4:[-0.00012452, 0.06064060, -0.35635438, 38.35125], 5:[0.00025899, -0.13434469, 0.87320147, 38.35125],
                      6:[0.00058331, -0.97731848, 0.17689245, 7.67025], 7:[-0.00041348, 0.68346318, -0.10162547, 7.67025] };
  const RAD = Math.PI / 180, DAY_MS = 86400000, EPOCH = Date.UTC(2000, 0, 1);   // day 0 = 2000-01-01
  const clampT = (T, lo, hi) => Math.min(Math.max(T, lo), hi);
  function longitude(b, days) {
    const T = days / 36525, recent = (T >= -2 && T <= 1) || b > 7;
    const el = recent ? ORBITS[b] : ORBITS_OLD[b], Td = recent ? clampT(T, -2, 1) : clampT(T, -50, 10);   // drifts held outside the tables
    let extra = 0;
    if (!recent && EXTRA_OLD[b]) { const [bb, c, s, f] = EXTRA_OLD[b]; extra = bb * Td * Td + c * Math.cos(f * Td * RAD) + s * Math.sin(f * Td * RAD); }
    const e = el[1] + el[7] * Td, I = (el[2] + el[8] * Td) * RAD, L = (el[3] + el[9] * T) % 360, peri = el[4] + el[10] * Td, node = el[5] + el[11] * Td;
    let M = ((L - peri + extra) % 360 + 540) % 360 - 180; M *= RAD;
    const w = (peri - node) * RAD, N = node * RAD;
    let E = M + e * Math.sin(M);
    for (let i = 0; i < 6; i++) E -= (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
    const a = el[0] + el[6] * Td, xo = a * (Math.cos(E) - e), yo = a * Math.sqrt(1 - e * e) * Math.sin(E);
    const x = (Math.cos(w) * Math.cos(N) - Math.sin(w) * Math.sin(N) * Math.cos(I)) * xo + (-Math.sin(w) * Math.cos(N) - Math.cos(w) * Math.sin(N) * Math.cos(I)) * yo;
    const y = (Math.cos(w) * Math.sin(N) + Math.sin(w) * Math.cos(N) * Math.cos(I)) * xo + (-Math.sin(w) * Math.sin(N) + Math.cos(w) * Math.cos(N) * Math.cos(I)) * yo;
    return (Math.atan2(y, x) / RAD + 360) % 360;
  }
  const lonsAt = day => NAMES.map((_, b) => longitude(b, day));

  const STEPS = [0, 1, 2, 5, 10, 20, 50, 100], YPM_MIN = 1, YPM_MAX = 100, CAP_RPM = 40, RACE_STEP_PCT = 75, MOVE_S = 4.5;
  const MEAN = ORBITS.map(o => o[9] / 36525);
  const dayOf = (y, m, d) => Math.round((Date.UTC(y, m - 1, d) - EPOCH) / DAY_MS);
  const ymdOf = day => { const d = new Date(EPOCH + Math.round(day) * DAY_MS); return [d.getUTCFullYear(), d.getUTCMonth() + 1, d.getUTCDate()]; };
  // Any date, BC too: Julian calendar before 15 Oct 1582, Gregorian after; 0 = 1 BC (as planets.py).
  const JD_2000 = 2451544.5, fl = Math.floor;
  function dayFromCal(y, m, d) {
    const greg = y * 10000 + m * 100 + d >= 15821015;
    if (m <= 2) { y -= 1; m += 12; }
    const A = fl(y / 100), B = greg ? 2 - A + fl(A / 4) : 0;
    return fl(365.25 * (y + 4716)) + fl(30.6001 * (m + 1)) + d + B - 1524.5 - JD_2000;
  }
  function calFromDay(day) {
    const Z = fl(Math.round(day) + JD_2000 + 0.5), al = fl((Z - 1867216.25) / 36524.25), A = Z < 2299161 ? Z : Z + 1 + al - fl(al / 4);
    const B = A + 1524, C = fl((B - 122.1) / 365.25), D = fl(365.25 * C), E = fl((B - D) / 30.6001), m = E < 14 ? E - 1 : E - 13;
    return [m > 2 ? C - 4716 : C - 4715, m, B - D - fl(30.6001 * E)];
  }
  const yearText = y => y <= 0 ? `${1 - y} BC` : y < 1000 ? `${y} AD` : String(y);
  // TIME TRAVEL: the same moments as server.py's EVENTS (dates in the calendar of the time, or years ago).
  const EVENTS = [[[79, 8, 24]], [[1776, 7, 4]], [[1969, 7, 20]], [null, null]];
  function eventDay(k) {
    const [cal, ago] = EVENTS[k];
    if (cal) return dayFromCal(...cal);
    if (!ago) return today();
    let day = Math.round(-ago * 365.25);
    return day;
  }
  const dim = (y, m) => Math.round(dayFromCal(y + fl(m / 12), m % 12 + 1, 1) - dayFromCal(y, m, 1));   // Julian leap years before 1582
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const now = () => performance.now() / 1000;
  const today = () => { const t = new Date(); return dayOf(t.getFullYear(), t.getMonth() + 1, t.getDate()); };
  const RUN_LO = dayFromCal(-2999, 1, 1), RUN_HI = dayOf(9999, 12, 31);
  // Typed dates: 1 AD - 3000 AD in the calendar of the time (server.py PICK_YEARS). Not
  // dayOf/ymdOf here: Date.UTC reads years 0-99 as 1900-1999.
  const PICK_YEARS = [1, 3000], LO = dayFromCal(1, 1, 1), HI = dayFromCal(3000, 12, 31);
  const entryOf = day => calFromDay(Math.min(Math.max(day, LO), HI));
  function nice(v) { return v < 0.5 ? 0 : STEPS.slice(1).reduce((b, s) => Math.abs(Math.log10(s) - Math.log10(v)) < Math.abs(Math.log10(b) - Math.log10(v)) ? s : b, 1); }
  function stepFrom(v, n) {
    let i = n > 0 ? STEPS.findIndex(s => s > v + 1e-9) : STEPS.map(s => s < v - 1e-9).lastIndexOf(true);
    if (n > 0) i = (i < 0 ? STEPS.length : i) + n - 1; else i = Math.max(i, 0) + n + 1;
    return STEPS[Math.min(Math.max(i, 0), STEPS.length - 1)];
  }

  const PICKED = EVENTS.length;                                            // o.trip after Pick a date's GO (as server.py)
  const o = { day:today(), mode:'run', planet:7, ypm:2, ypm_set:2, paused:true, entry:ymdOf(today()), field:0, editing:null,
              moving_until:0, run_from:null, racing:NAMES.map(() => false), run_lon:null, t_day:now(), glide:null, trip:null, deep:null };
  // Manual mode (settings screen, 8 Nov 2026), as server.py: on at start-up; eight servos (no Pluto).
  const SERVOS = 8, MAN_RPM = [0, 1, 2, 3, 5, 10, 15, 20, 30, 40];
  Object.assign(o, { manual:false, man_sel:Array(SERVOS).fill(false), man_rpm:0, man_dir:1 });
  // TRAVEL MODE (settings; LINE UP until 13 Nov 2026), as server.py: no arms here, so only the state.
  const LAP_S = 7.5, HOME_LON = 90;                           // travel mode: every arm away from the screen
  o.lined_up = false;
  function line(on) { o.lined_up = on; o.paused = true; o.trip = null; o.moving_until = now() + LAP_S; }
  const running = () => !o.paused && o.ypm > 0;              // keeps running on the PLANETS tab
  // ?sim&ypm=50: start already running at that speed (the website's mock-up does). Sim only;
  // the real Pi (server.py) still starts paused at 2.
  const startYpm = Number(new URLSearchParams(location.search).get('ypm'));
  if (STEPS.includes(startYpm) && startYpm > 0) { o.ypm = o.ypm_set = startYpm; o.paused = false; }

  function jump(day, deep = null) {
    const from = viewDay();
    o.day = deep ? day : Math.min(Math.max(day, RUN_LO), RUN_HI); o.paused = true; o.deep = deep; o.trip = null;
    o.moving_until = now() + MOVE_S; o.glide = { from, to:o.day, t0:now() };   // the 3D model's arms glide there
  }
  function nudge(field, n) {
    let [y, m, d] = o.entry;
    if (field === 0) [y, m, d] = calFromDay(dayFromCal(y, m, Math.min(d, dim(y, m))) + n);
    else if (field === 1) { const k = y * 12 + m - 1 + n; y = Math.floor(k / 12); m = k - y * 12 + 1; }
    else y = Math.min(Math.max(y + n, PICK_YEARS[0]), PICK_YEARS[1]);
    o.entry = [y, m, Math.min(d, dim(y, m))];
  }
  function act(a) {
    const what = a.do; let editWas = null;
    if (what !== 'nudge' && what !== 'edit') { editWas = o.editing; o.editing = null; }
    if (o.lined_up && (['travel', 'go', 'today', 'hold', 'press'].includes(what) || (what === 'speed' && a.apply))) line(false);
    const travel = k => { jump(eventDay(k), EVENTS[k][1]); o.trip = k; if (!EVENTS[k][1]) o.entry = entryOf(o.day); };
    if (what === 'tab') {
      const mode = ['planets', 'travel', 'galaxy', 'scale', 'health'].includes(a.mode) ? a.mode : 'run';   // 'system' (old SOLAR SYSTEM) = RUN
      if (mode === 'planets' && o.mode !== 'planets') o.planet = 7;               // PLANETS always opens on Saturn
      if ((mode === 'travel' || mode === 'run') && o.manual) { o.manual = false; o.man_rpm = 0; }   // TIME MACHINE, ORBITS: back to AUTO (server.py)
      o.mode = mode;
    }
    else if (what === 'travel') travel(((a.n | 0) % EVENTS.length + EVENTS.length) % EVENTS.length);
    else if (what === 'planet') o.planet = (((a.n | 0) % 11) + 11) % 11;      // 0 = Sun, 1 = Mercury ... 5 = asteroid belt ...
    else if (what === 'edit') {
      if (o.mode === 'travel') {                                                 // TIME TRAVEL: Pick a date
        if (running()) o.paused = true;
        if (o.editing === null) o.entry = entryOf(o.day >= LO && o.day <= HI && !o.deep ? o.day : today());   // starts at the planets' date
        o.trip = null;
        o.editing = o.field = ((a.field | 0) % 3 + 3) % 3;
      }
    }
    else if (what === 'turn') {
      const n = a.n | 0;
      if (editWas !== null) { o.editing = editWas; nudge(editWas, n); }
      else if (o.mode === 'run') o.ypm_set = stepFrom(o.ypm_set, n);
      else if (o.mode === 'travel') travel((((o.trip !== null && o.trip < EVENTS.length ? o.trip : EVENTS.length - 1) + n) % EVENTS.length + EVENTS.length) % EVENTS.length);
      else o.planet = ((o.planet + n) % 11 + 11) % 11;
    }
    else if (what === 'speed') {
      o.ypm_set = nice(Math.max(+a.ypm || 0, 0));
      if (a.apply) {                                                              // slider let go: takes effect now
        if (o.ypm_set === 0) o.paused = true;
        else if (running()) o.ypm = o.ypm_set;
        else if (now() >= o.moving_until && !o.deep) { o.ypm = o.ypm_set; o.paused = false; o.glide = null; o.trip = null; }
      }
    }
    else if (what === 'go' || (what === 'press' && editWas !== null)) { const [y, m, d] = o.entry; jump(dayFromCal(y, m, d)); o.trip = PICKED; }
    else if (what === 'cancel') {}
    else if (what === 'manual') { const on = !!a.on; if (on !== o.manual) { o.manual = on; o.man_rpm = 0; } }
    else if (what === 'mpick') {
      if (o.manual) {
        if ('all' in a) o.man_sel = Array(SERVOS).fill(!!a.all);
        else { const k = a.p | 0; if (k >= 0 && k < SERVOS) o.man_sel[k] = !o.man_sel[k]; }
      }
    }
    else if (what === 'mspeed') { if (o.manual) { const r = Math.max(+a.rpm || 0, 0); o.man_rpm = MAN_RPM.reduce((b, v) => Math.abs(v - r) < Math.abs(b - r) ? v : b, 0); } }
    else if (what === 'mdir') { if (o.manual) o.man_dir = (a.dir | 0) < 0 ? -1 : 1; }
    else if (what === 'mstop') o.man_rpm = 0;
    else if (what === 'lineup') { const on = !!a.on; if (on !== o.lined_up) line(on); }
    else if (what === 'mnudge' || what === 'home' || what === 'unhome') {}                            // no servos here
    else if (what === 'poweroff') {                                               // Turn off: no Pi here, so come back after a bit
      if (!o.off) { o.off = true; o.paused = true; o.trip = null; o.man_rpm = 0; setTimeout(() => { o.off = false; }, 6000); }
    }
    else if (what === 'press') {
      if (now() < o.moving_until && !running()) {}                               // settling on a date
      else if (o.deep) {}                                                         // no running on from deep time
      else if (running() && o.ypm_set !== 0 && o.ypm_set !== o.ypm) o.ypm = o.ypm_set;
      else if (running()) o.paused = true;
      else { if (o.ypm_set === 0) o.ypm_set = 2; o.ypm = o.ypm_set; o.paused = false; o.glide = null; o.trip = null; }
    }
    else if (what === 'hold' || what === 'today') { jump(today()); o.entry = entryOf(o.day); }
    else if (what === 'nudge') { o.field = ((a.field | 0) % 3 + 3) % 3; if (o.editing !== null) o.editing = o.field; nudge(o.field, a.n | 0); }
    else return { error:`unknown action ${what}` };
    return { ok:true };
  }
  function tick() {
    const t = now(), dt = t - o.t_day; o.t_day = t;
    if (running()) {
      if (!o.run_from) o.run_from = [o.day, lonsAt(o.day)];
      const perS = o.ypm * 365.25 / 60;
      o.day += perS * dt;
      if (o.day < RUN_LO || o.day > RUN_HI) { o.day = Math.min(Math.max(o.day, RUN_LO), RUN_HI); o.paused = true; }
      const [d0, l0] = o.run_from;
      o.racing = MEAN.map((r, b) => Math.abs(r * perS) > CAP_RPM * (RACE_STEP_PCT / 100) ** b * 6);   // server.cap_rpm(b)
      o.run_lon = MEAN.map((r, b) => ((l0[b] + r * (o.day - d0)) % 360 + 360) % 360);
    } else if (o.run_from) { o.run_from = null; o.racing = NAMES.map(() => false); }
  }
  setInterval(tick, 100);

  function state() {
    tick();
    const run = running(), [y, m, d] = calFromDay(o.day);
    return {
      mode:o.mode, planet:o.planet, running:run, paused:o.paused, years_per_min:o.ypm, ypm_set:o.ypm_set, ypm_min:YPM_MIN, ypm_max:YPM_MAX, steps:STEPS,
      racing:run ? o.racing : NAMES.map(() => false), date:dateText(o.day), ymd:[y, m, d], trip:o.trip, deep:o.deep,
      entry:o.entry, field:o.field, editing:o.editing, moving:now() < o.moving_until, off:!!o.off,
      lon:(run && o.run_lon ? o.run_lon : lonsAt(o.day)).map((a, b) => o.lined_up && !run && b < SERVOS ? HOME_LON : Math.round(a * 100) / 100),
      day:o.day, mean:MEAN, names:NAMES, servos:[], servo_names:NAMES.slice(0, SERVOS), sim:true, error:'',
      manual:o.manual, lined_up:o.lined_up, home_set:Array(SERVOS).fill(false), note:'', man:{ sel:[...o.man_sel], rpm:o.man_rpm, dir:o.man_dir, steps:MAN_RPM },
    };
  }
  // For the website's 3D model: the date the arms show right now (gliding after GO / Today).
  function viewDay() {
    if (o.glide) {
      const k = Math.min((now() - o.glide.t0) / MOVE_S, 1), e = k < 0.5 ? 2 * k * k : 1 - (-2 * k + 2) ** 2 / 2;
      if (k >= 1) o.glide = null; else return o.glide.from + (o.glide.to - o.glide.from) * e;
    }
    return running() ? o.day + o.ypm * 365.25 / 60 * (now() - o.t_day) : o.day;
  }
  function dateText(day) {
    if (o.deep && Math.abs(day - o.day) < 1) return `${(o.deep / 1e6).toLocaleString()} million years ago`;
    const [y, m, d] = calFromDay(day); return `${d} ${MON[m - 1]} ${yearText(y)}`;
  }
  // The website's 3D model uses these for the arms and the date label, so it matches the screen.
  window.orrerySim = { state, act, viewDay, today, lonAt:longitude, dateText };
})();
