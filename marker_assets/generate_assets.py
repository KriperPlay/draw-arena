import math, random, os, sys

INK = "#141414"
PAPER = "#fffef7"
BG = "#f6f1e3"
OUT = "/mnt/user-data/outputs/marker_assets"


def f(v):
    return f"{v:.1f}"


# ---------- hand-drawn engine ----------
def resample(pts, step, closed=False):
    P = pts + [pts[0]] if closed else pts[:]
    out = [P[0]]
    for a, b in zip(P, P[1:]):
        L = math.dist(a, b)
        n = max(1, round(L / step))
        for i in range(1, n + 1):
            t = i / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    if closed:
        out.pop()
    return out


def wobble(pts, amp, rng):
    p = [rng.uniform(0, 6.28) for _ in range(4)]
    f1 = rng.uniform(.035, .07)
    f2 = rng.uniform(.10, .17)
    d = 0
    out = []
    for i, (x, y) in enumerate(pts):
        if i:
            d += math.dist(pts[i - 1], (x, y))
        ox = amp * (math.sin(f1 * d + p[0]) + .5 * math.sin(f2 * d + p[1])) + rng.gauss(0, amp * .1)
        oy = amp * (math.sin(f1 * d + p[2]) + .5 * math.sin(f2 * d + p[3])) + rng.gauss(0, amp * .1)
        out.append((x + ox, y + oy))
    return out


def path_d(pts, closed=False, k=1.0):
    n = len(pts)

    def P(i):
        return pts[i % n] if closed else pts[max(0, min(n - 1, i))]

    d = f"M{f(pts[0][0])},{f(pts[0][1])}"
    for i in (range(n) if closed else range(n - 1)):
        p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * k, p1[1] + (p2[1] - p0[1]) / 6 * k)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * k, p2[1] - (p3[1] - p1[1]) / 6 * k)
        d += f" C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}"
    if closed:
        d += " Z"
    return d


def stroke_el(d, sw):
    return (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def shape(pts, rng, fill=PAPER, sw=6, amp=1.6, step=12, k=1.0, tail=True):
    """closed outline with paper fill and marker overshoot at the seam"""
    r = resample(pts, step, True)
    w = wobble(r, amp, rng)
    out = ""
    if fill:
        out += f'<path d="{path_d(w, True, k)}" fill="{fill}" stroke="none"/>'
    if tail:
        t = [(x + rng.uniform(-1.8, 1.8), y + rng.uniform(-1.8, 1.8)) for x, y in w[:3]]
        sp = w + t
        out += stroke_el(path_d(sp, False, k), sw)
    else:
        out += stroke_el(path_d(w, True, k), sw)
    return out


def line(pts, rng, sw=5, amp=1.0, step=10, k=1.0):
    r = resample(pts, step, False)
    w = wobble(r, amp, rng)
    return stroke_el(path_d(w, False, k), sw)


def ellipse(cx, cy, rx, ry, n=20, rot=0.0):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot),
                    cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def blob(cx, cy, rx, ry, rng, n=16, var=.08):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        s = 1 + rng.uniform(-var, var)
        pts.append((cx + rx * s * math.cos(t), cy + ry * s * math.sin(t)))
    return pts


def rrect(x, y, w, h, r, n=6):
    pts = []
    for (cx, cy, a0) in [(x + w - r, y + r, -90), (x + w - r, y + h - r, 0),
                         (x + r, y + h - r, 90), (x + r, y + r, 180)]:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def dot(x, y, r, rng):
    return shape(ellipse(x, y, r, r * rng.uniform(.9, 1.1), 10), rng, fill=INK, sw=2, amp=.5, step=6)


def hatch(segs, rng, sw=4):
    return "".join(line(list(s), rng, sw=sw, amp=.8, step=8) for s in segs)


def svg(w, h, body, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">{b}{body}</svg>')


# ---------- stroke font (Cyrillic subset) ----------
GL = {
    'И': [[(0, 0), (0, 1)], [(.7, 0), (.7, 1)], [(0, 1), (.7, 0)]],
    'Г': [[(.7, 0), (0, 0), (0, 1)]],
    'Р': [[(0, 1), (0, 0), (.5, 0), (.7, .12), (.7, .4), (.5, .54), (0, .54)]],
    'А': [[(0, 1), (.35, 0), (.7, 1)], [(.12, .68), (.58, .68)]],
    'Т': [[(0, 0), (.7, 0)], [(.35, 0), (.35, 1)]],
    'Ь': [[(0, 0), (0, 1), (.5, 1), (.7, .85), (.7, .66), (.5, .5), (0, .5)]],
    'Н': [[(0, 0), (0, 1)], [(.7, 0), (.7, 1)], [(0, .5), (.7, .5)]],
    'С': [[(.7, .18), (.5, .02), (.25, 0), (.05, .18), (0, .5), (.05, .82), (.25, 1), (.5, .98), (.7, .82)]],
    'Й': [[(0, 0), (0, 1)], [(.7, 0), (.7, 1)], [(0, 1), (.7, 0)],
          [(.12, -.2), (.25, -.1), (.45, -.1), (.58, -.2)]],
    'К': [[(0, 0), (0, 1)], [(.7, 0), (0, .55)], [(.2, .42), (.7, 1)]],
}


def glyph_strokes(ch):
    if ch == 'О':
        return [[(.35 + .35 * math.cos(math.radians(a)), .5 + .5 * math.sin(math.radians(a)))
                 for a in range(-100, 290, 25)]]
    return GL[ch]


def text_w(s, h, gap=.26):
    return len(s) * .7 * h + (len(s) - 1) * gap * h


def text(s, x0, y0, h, rng, sw, gap=.26):
    out = ""
    x = x0
    for ch in s:
        for st in glyph_strokes(ch):
            pts = [(x + px * h, y0 + py * h) for px, py in st]
            out += line(pts, rng, sw=sw, amp=max(.8, h * .012), step=h / 7, k=.45)
        x += (.7 + gap) * h
    return out


# ---------- environment ----------
def blade(cx0, y0, h, lean, bw, r, sw=5):
    n = 10
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        cx = cx0 + lean * (t ** 1.7)
        w = bw * (1 - t) ** .9 / 2
        y = y0 - h * t
        left.append((cx - w, y))
        right.append((cx + w, y))
    pts = left + right[::-1][1:]
    return shape(pts, r, sw=sw, amp=1.0, step=9)


def ground_ticks(r, x1=70, x2=190, y=226):
    return (line([(x1, y), (x2, y + 1)], r, sw=4) +
            line([(x1 + 30, y + 11), (x2 - 30, y + 11)], r, sw=4))


def grass(variant):
    r = random.Random(100 + variant)
    sets = {
        1: [(80, 100, -50, 14), (176, 100, 40, 14), (100, 150, -40, 18), (156, 140, 50, 18), (128, 190, 10, 20)],
        2: [(70, 110, -30, 16), (186, 105, 34, 16), (92, 160, -24, 18), (166, 150, 36, 18),
            (112, 200, -8, 20), (146, 210, 22, 20), (128, 150, 6, 18)],
        3: [(106, 120, -26, 16), (154, 110, 28, 16), (130, 170, 8, 18)],
    }
    body = ""
    if variant in sets:
        for (x0, h, lean, bw) in sets[variant]:
            body += blade(x0, 220, h, lean, bw, r)
    else:  # flower
        body += blade(100, 220, 100, -40, 14, r) + blade(158, 220, 96, 42, 14, r)
        body += line([(128, 222), (126, 170), (131, 125), (130, 98)], r, sw=6, amp=1.2)
        cx, cy = 130, 80
        for i in range(6):
            a = i * math.pi / 3 + .3
            body += shape(ellipse(cx + 24 * math.cos(a), cy + 24 * math.sin(a), 17, 11, 14, a), r, sw=5, amp=.8, step=8)
        body += shape(ellipse(cx, cy, 13, 13, 12), r, sw=5, amp=.8, step=8)
        body += dot(cx, cy, 4, r)
    body += ground_ticks(r)
    return body


def rock(variant):
    r = random.Random(200 + variant)
    body = ""
    kw = dict(sw=6, amp=1.6, step=16, k=.55)
    if variant == 1:
        body += shape([(40, 190), (34, 140), (62, 92), (112, 66), (160, 72), (204, 108), (222, 160), (208, 200), (130, 214)], r, **kw)
        body += line([(120, 70), (116, 108), (140, 134)], r, sw=5)
        body += line([(116, 108), (94, 128)], r, sw=5)
        body += line([(66, 118), (76, 100), (96, 88)], r, sw=5)
        body += hatch([((160, 196), (192, 160)), ((140, 205), (200, 168)), ((184, 200), (208, 178))], r)
    elif variant == 2:
        body += shape(blob(196, 190, 26, 20, r, 10), r, sw=5, amp=1, step=10)
        body += shape([(30, 196), (40, 150), (90, 128), (150, 124), (206, 146), (222, 190), (180, 208), (70, 210)], r, **kw)
        body += line([(96, 130), (104, 160), (88, 182)], r, sw=5)
        body += line([(150, 126), (160, 150)], r, sw=5)
        body += hatch([((140, 196), (170, 166)), ((160, 200), (190, 172))], r)
    else:
        body += shape([(70, 208), (52, 150), (76, 96), (120, 44), (168, 70), (196, 128), (200, 196), (150, 214)], r, **kw)
        body += line([(120, 46), (124, 108), (100, 150), (104, 190)], r, sw=5)
        body += line([(124, 108), (194, 128)], r, sw=5)
        body += hatch([((160, 200), (188, 150)), ((140, 208), (186, 170)), ((172, 208), (196, 180))], r)
    body += ground_ticks(r, 60, 200, 226)
    return body


# ---------- enemies (256x256) ----------
def slime(r):
    pts = [(128 + 90 * math.cos(math.pi * i / 12), 204 - 118 * math.sin(math.pi * i / 12) ** .85) for i in range(13)]
    pts += [(76, 210), (128, 214), (180, 210)]
    b = shape(pts, r, sw=6, amp=1.8, step=14)
    b += dot(98, 146, 9, r) + dot(158, 146, 9, r)
    b += line([(110, 170), (128, 182), (146, 170)], r, sw=5)
    b += line([(66, 128), (72, 108), (88, 94)], r, sw=5)
    b += hatch([((170, 190), (196, 160)), ((150, 200), (190, 166)), ((186, 196), (204, 178))], r)
    b += line([(64, 228), (190, 228)], r, sw=4) + line([(92, 238), (160, 238)], r, sw=4)
    return b


def angry(r):
    b = ""
    b += line([(100, 190), (96, 226), (78, 230)], r, sw=7)
    b += line([(156, 190), (160, 226), (178, 230)], r, sw=7)
    b += shape(blob(128, 125, 82, 78, r, 18, .04), r, sw=6, amp=1.8, step=14)
    b += line([(80, 92), (116, 112)], r, sw=7) + line([(176, 92), (140, 112)], r, sw=7)
    b += dot(104, 128, 8, r) + dot(152, 128, 8, r)
    b += shape([(92, 154), (164, 154), (152, 188), (104, 188)], r, sw=5, amp=1, step=10, k=.5)
    b += line([(108, 154), (108, 168)], r, sw=4) + line([(128, 154), (128, 172)], r, sw=4) + line([(148, 154), (148, 168)], r, sw=4)
    b += hatch([((176, 170), (196, 140)), ((164, 186), (200, 152)), ((152, 196), (192, 170))], r)
    return b


def spiky(r):
    pts = []
    for i in range(28):
        a = i * math.pi / 14 - math.pi / 2
        rad = (108 if i % 2 == 0 else 78) * (1 + r.uniform(-.06, .06))
        pts.append((128 + rad * math.cos(a), 128 + rad * math.sin(a)))
    b = shape(pts, r, sw=6, amp=1.2, step=12, k=.4)
    b += shape(ellipse(128, 124, 32, 36, 16), r, sw=5, amp=1, step=10)
    b += dot(137, 128, 13, r)
    b += line([(92, 82), (126, 100), (162, 90)], r, sw=7)
    b += line([(104, 176), (116, 168), (128, 178), (140, 168), (152, 176)], r, sw=5)
    return b


def bat(r):
    wl = [(94, 118), (52, 88), (12, 80), (26, 112), (14, 136), (44, 138), (36, 164), (70, 150), (94, 160)]
    wr = [(256 - x, y) for x, y in wl]
    b = shape(wl, r, sw=6, amp=1.4, step=12, k=.6) + shape(wr, r, sw=6, amp=1.4, step=12, k=.6)
    for tip in [(12, 80), (14, 136), (36, 164)]:
        b += line([(92, 128), tip], r, sw=4)
        b += line([(164, 128), (256 - tip[0], tip[1])], r, sw=4)
    b += shape([(100, 104), (96, 66), (124, 92)], r, sw=6, amp=1, step=10, k=.5)
    b += shape([(156, 104), (160, 66), (132, 92)], r, sw=6, amp=1, step=10, k=.5)
    b += shape(ellipse(128, 138, 34, 44, 18), r, sw=6, amp=1.2, step=12)
    b += dot(116, 128, 6.5, r) + dot(140, 128, 6.5, r)
    b += line([(114, 152), (128, 160), (142, 152)], r, sw=5)
    b += shape([(117, 156), (120, 172), (125, 159)], r, fill=INK, sw=3, amp=.4, step=8, k=.5)
    b += shape([(139, 156), (136, 172), (131, 159)], r, fill=INK, sw=3, amp=.4, step=8, k=.5)
    return b


def ghost(r):
    pts = [(52, 210), (48, 130), (60, 70), (100, 40), (128, 36), (156, 40), (196, 70), (208, 130), (204, 210),
           (185, 226), (166, 208), (147, 226), (128, 208), (109, 226), (90, 208), (71, 226)]
    b = shape(pts, r, sw=6, amp=1.5, step=12, k=.9)
    b += shape(ellipse(104, 120, 10, 16, 12), r, fill=INK, sw=3, amp=.6, step=8)
    b += shape(ellipse(152, 120, 10, 16, 12), r, fill=INK, sw=3, amp=.6, step=8)
    b += shape(ellipse(128, 168, 13, 17, 12), r, fill=INK, sw=3, amp=.6, step=8)
    b += hatch([((176, 150), (194, 124)), ((170, 176), (198, 140)), ((176, 196), (200, 166))], r)
    return b


def brute(r):
    b = ""
    b += shape(rrect(76, 206, 36, 28, 10), r, sw=6, amp=1, step=10)
    b += shape(rrect(144, 206, 36, 28, 10), r, sw=6, amp=1, step=10)
    b += shape(rrect(18, 118, 42, 88, 18), r, sw=6, amp=1.2, step=12)
    b += shape(rrect(196, 118, 42, 88, 18), r, sw=6, amp=1.2, step=12)
    b += shape([(76, 92), (66, 50), (106, 84)], r, sw=6, amp=1, step=10, k=.5)
    b += shape([(180, 92), (190, 50), (150, 84)], r, sw=6, amp=1, step=10, k=.5)
    b += shape(rrect(46, 80, 164, 134, 38), r, sw=6, amp=1.8, step=14)
    b += line([(78, 112), (122, 126)], r, sw=8) + line([(178, 112), (134, 126)], r, sw=8)
    b += dot(100, 140, 7, r) + dot(156, 140, 7, r)
    b += line([(98, 182), (128, 176), (158, 182)], r, sw=6)
    b += line([(116, 96), (124, 106)], r, sw=4) + line([(124, 96), (116, 106)], r, sw=4)
    b += hatch([((170, 196), (196, 160)), ((150, 208), (200, 170)), ((60, 200), (80, 176))], r)
    return b


ENEMIES = [("enemy_01_slime", slime), ("enemy_02_angry", angry), ("enemy_03_spiky", spiky),
           ("enemy_04_bat", bat), ("enemy_05_ghost", ghost), ("enemy_06_brute", brute)]


def sprite(fn, seed):
    return fn(random.Random(seed))


# ---------- UI ----------
def gear(cx, cy, r):
    rin, rout = .74 * 38, 38
    k = r / 38
    pts = []
    for i in range(8):
        a = i * math.pi / 4
        for (rad, da) in [(rin, -.30), (rout, -.16), (rout, .16), (rin, .30)]:
            pts.append((cx + rad * k * math.cos(a + da), cy + rad * k * math.sin(a + da)))
    return pts


def button(label, icon, seed):
    r = random.Random(seed)
    W, H = 900, 250
    b = shape(rrect(44, 44, 840, 190, 46), r, fill=INK, sw=4, amp=2, step=26)
    b += shape(rrect(30, 30, 840, 190, 46), r, sw=9, amp=2.4, step=26)
    b += hatch([((826, 198), (844, 172)), ((842, 202), (860, 174))], r, sw=5)
    h = 76
    tw = text_w(label, h)
    icon_w = 60
    gap = 34
    total = icon_w + gap + tw
    x = 450 - total / 2
    cy = 125
    if icon == "play":
        b += shape([(x, cy - 38), (x + 58, cy), (x, cy + 38)], r, fill=INK, sw=6, amp=1, step=12, k=.4)
    else:
        b += shape(gear(x + 30, cy, 36), r, sw=5, amp=.8, step=9, k=.5)
        b += shape(ellipse(x + 30, cy, 11, 11, 12), r, sw=5, amp=.6, step=8)
    b += text(label, x + icon_w + gap, cy - h / 2, h, r, 9)
    return W, H, b


def sparkle(x, y, s, r):
    return (line([(x - s, y), (x + s, y)], r, sw=6, amp=.6) + line([(x, y - s), (x, y + s)], r, sw=6, amp=.6) +
            line([(x - s * .5, y - s * .5), (x + s * .5, y + s * .5)], r, sw=4, amp=.5) +
            line([(x - s * .5, y + s * .5), (x + s * .5, y - s * .5)], r, sw=4, amp=.5))


def place(inner, x, y, s):
    return f'<g transform="translate({x},{y}) scale({s})">{inner}</g>'


def menu_bg():
    r = random.Random(77)
    b = shape(rrect(36, 36, 1008, 1848, 40, 10), r, fill=None, sw=9, amp=3, step=28)
    h = 215
    title = "ИГРА"
    tx = 540 - text_w(title, h, .3) / 2
    b += text(title, tx, 290, h, r, 22, .3)
    ys = [550 + 9 * math.sin(i * .9) for i in range(0, 31)]
    b += line([(230 + i * 20, ys[i]) for i in range(31)], r, sw=12, amp=1.5, step=14)
    for (x, y, s) in [(100, 230, 30), (985, 360, 26), (880, 190, 22), (200, 590, 24), (950, 600, 20)]:
        b += sparkle(x, y, s, r)
    gy = 1760
    ground = [(80 + i * 30, gy + 6 * math.sin(i * .7)) for i in range(0, 33)]
    b += line(ground, r, sw=8, amp=2, step=16)
    b += place(rock(1), 40, 1545, 1.0)
    b += place(grass(2), 220, 1631, .6)
    b += place(sprite(slime, 11), 290, 1540, 1.0)
    b += place(grass(4), 500, 1625, .6)
    b += place(sprite(spiky, 12), 590, 1520, 1.0)
    b += place(grass(1), 800, 1631, .5)
    b += place(rock(3), 850, 1590, .7)
    b += place(sprite(ghost, 13), 770, 1330, .8)
    b += place(sprite(bat, 14), 60, 1330, .75)
    return b


# ---------- build ----------
def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def main():
    files = []  # (path, w, h, scale)
    for i in range(1, 5):
        files.append((f"{OUT}/environment/grass_0{i}.svg", svg(256, 256, grass(i)), 256, 256, 2))
    for i in range(1, 4):
        files.append((f"{OUT}/environment/rock_0{i}.svg", svg(256, 256, rock(i)), 256, 256, 2))
    for n, (name, fn) in enumerate(ENEMIES):
        files.append((f"{OUT}/enemies/{name}.svg", svg(256, 256, sprite(fn, 300 + n)), 256, 256, 2))
    w, h, pb = button("ИГРАТЬ", "play", 501)
    files.append((f"{OUT}/ui/btn_play.svg", svg(w, h, pb), w, h, 1))
    w, h, sb = button("НАСТРОЙКИ", "gear", 502)
    files.append((f"{OUT}/ui/btn_settings.svg", svg(w, h, sb), w, h, 1))
    bg = menu_bg()
    files.append((f"{OUT}/ui/main_menu_bg.svg", svg(1080, 1920, bg, BG), 1080, 1920, 1))
    full = bg + place(pb, 90, 700, 1) + place(sb, 90, 980, 1)
    files.append((f"{OUT}/ui/main_menu_1080x1920.svg", svg(1080, 1920, full, BG), 1080, 1920, 1))

    import cairosvg
    for path, content, w, h, sc in files:
        write(path, content)
        cairosvg.svg2png(bytestring=content.encode("utf-8"), write_to=path[:-4] + ".png",
                         output_width=int(w * sc), output_height=int(h * sc))
    print(len(files), "assets")


if __name__ == "__main__":
    main()
