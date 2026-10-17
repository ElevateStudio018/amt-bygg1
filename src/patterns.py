"""Genererar AMT Byggs mönsterbibliotek (materialmönster i loggans färger).

Kör: python3 src/patterns.py  -> assets/patterns/*.svg + assets/css/patterns.css
"""
import math, random, base64, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAVY, BLUE, GOLD = '#122a6e', '#0a9cf0', '#d9a21b'


WOOD_KNOTS = (
    # x, y, halva bredden, halva höjden, styrka (negativ = kvisten vänder åt andra hållet)
    (1240, 300, 80, 200, 4.4), (330, 520, 72, 190, -4.2), (820, 330, 46, 130, 3.4),
    (1520, 640, 56, 160, -3.6), (90, 300, 44, 130, 3.2), (640, 640, 40, 110, -3.0),
)


def wood(width=1600, height=900, spacing=30, stroke=BLUE, sw=1.2, knots=WOOD_KNOTS, step=5):
    """Träådring ritad som höjdkurvor i ett fält: f(x, y) = x + kvistar + svaj.

    Höjdkurvor kan aldrig korsa varandra, och runt varje kvist bildas slutna ringar
    av sig själva, som i riktigt trä.
    """
    def f(x, y):
        v = x + 10 * math.sin(y / 150 + x / 420) + 4 * math.sin(y / 55 + x / 130)
        for kx, ky, sx, sy, a in knots:
            dx, dy = (x - kx) / sx, (y - ky) / sy
            v += a * sx * math.exp(-dx * dx - dy * dy)
        return v

    pad = 40
    xs = list(range(-pad, width + pad + 1, step))
    ys = list(range(-pad, height + pad + 1, step))
    grid = [[f(x, y) for x in xs] for y in ys]
    lo = min(min(r) for r in grid); hi = max(max(r) for r in grid)
    paths = []
    level = math.floor(lo / spacing) * spacing + spacing / 2
    while level < hi:
        # marching squares: segment i varje ruta där kurvan passerar
        segs = []
        for j in range(len(ys) - 1):
            for i in range(len(xs) - 1):
                c = (grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i])
                pts = []
                corners = ((xs[i], ys[j]), (xs[i + 1], ys[j]), (xs[i + 1], ys[j + 1]), (xs[i], ys[j + 1]))
                for e in range(4):
                    v0, v1 = c[e], c[(e + 1) % 4]
                    if (v0 < level) != (v1 < level):
                        t = (level - v0) / (v1 - v0)
                        (x0, y0), (x1, y1) = corners[e], corners[(e + 1) % 4]
                        pts.append((round(x0 + t * (x1 - x0), 1), round(y0 + t * (y1 - y0), 1)))
                if len(pts) == 2:
                    segs.append((pts[0], pts[1]))
                elif len(pts) == 4:
                    segs.append((pts[0], pts[1])); segs.append((pts[2], pts[3]))
        # foga ihop segmenten till sammanhängande linjer
        nb = {}
        for a_, b_ in segs:
            nb.setdefault(a_, []).append(b_); nb.setdefault(b_, []).append(a_)
        seen = set()
        def walk(start):
            line = [start]; prev = None; cur = start
            while True:
                nxt = [n for n in nb[cur] if n != prev and (min(cur, n), max(cur, n)) not in seen]
                if not nxt:
                    return line
                n = nxt[0]; seen.add((min(cur, n), max(cur, n))); prev, cur = cur, n; line.append(cur)
                if cur == start:
                    return line
        ends = [p_ for p_, l in nb.items() if len(l) == 1]
        for st in ends + list(nb):
            if any((min(st, n), max(st, n)) not in seen for n in nb[st]):
                line = walk(st)
                if len(line) > 3:
                    line = line[::2] + ([line[-1]] if len(line) % 2 == 0 else [])
                    paths.append('<path d="M' + ' L'.join(f'{x:g} {y:g}' for x, y in line) + '"/>')
        level += spacing
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid slice">'
            f'<g fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" vector-effect="non-scaling-stroke">'
            + ''.join(paths) + '</g></svg>')


def tile(w, h, body, stroke, sw=1):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<g fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="square">{body}</g></svg>')


def herringbone(stroke, u=9):
    """Fiskbensparkett 1:4. Gitter (1,1)/(4,-4) ger en kvadratisk period på 8x8 enheter."""
    L, P = 4, 8
    rects = []
    for a in range(-12, 13):
        for b in range(-4, 5):
            ox, oy = a + 4 * b, a - 4 * b
            rects.append((ox, oy, L, 1))          # liggande bräda
            rects.append((ox + L, oy - 3, 1, L))  # stående bräda
    body = ''.join(f'<rect x="{x*u}" y="{y*u}" width="{w*u}" height="{h*u}"/>'
                   for x, y, w, h in rects if -L <= x <= P and -L <= y <= P)
    return tile(P * u, P * u, body, stroke)


def studs(stroke):
    """Regelverk i fasad: reglar c/c med förskjutna kortlingar."""
    w, h, t = 96, 180, 5
    body = (f'<path d="M.5 0V{h} M{t+.5} 0V{h} M{w/2+.5} 0V{h} M{w/2+t+.5} 0V{h}"/>'
            f'<path d="M{t} 70.5H{w/2} M{t} {70.5+t}H{w/2} M{w/2+t} 125.5H{w} M{w/2+t} {125.5+t}H{w}"/>')
    return tile(w, h, body, stroke)


def brick(stroke):
    # Löpförband
    w, h = 64, 32
    body = (f'<path d="M0 .5H{w} M0 {h/2+.5}H{w}"/>'
            f'<path d="M.5 0V{h/2} M{w/2+.5} {h/2}V{h}"/>')
    return tile(w, h, body, stroke)


def hatch(stroke, gap=10):
    # Snittmarkering i A:ets vinkel (~67°)
    a = math.radians(67)
    w = gap / math.sin(a) if False else 24
    h = w * math.tan(a)
    body = f'<path d="M0 {h:.2f} L{w} 0 M{-w} {h:.2f} L0 0 M{w} {h:.2f} L{2*w} 0"/>'
    return tile(round(w, 2), round(h, 2), body, stroke)


def grid(stroke):
    w = 120
    minor = ''.join(f'M{x} 0V{w} M0 {x}H{w} ' for x in range(24, w, 24))
    body = f'<path d="{minor}" opacity=".45"/><path d="M.5 0V{w} M0 .5H{w}"/>'
    return tile(w, w, body, stroke)


def uri(svg):
    return 'url("data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode() + '")'


def main():
    pdir = os.path.join(ROOT, 'assets', 'patterns')
    os.makedirs(pdir, exist_ok=True)
    open(os.path.join(pdir, 'wood-blue.svg'), 'w').write(wood())
    open(os.path.join(pdir, 'wood-navy.svg'), 'w').write(wood(stroke=NAVY))
    open(os.path.join(pdir, 'wood-gold.svg'), 'w').write(wood(stroke=GOLD))
    tones = {'blue': BLUE, 'navy': NAVY, 'gold': GOLD, 'white': '#ffffff'}
    gens = {'parquet': herringbone, 'studs': studs, 'brick': brick, 'hatch': hatch, 'grid': grid}
    css = ['/* Genererad av src/patterns.py – redigera inte för hand */']
    for name, fn in gens.items():
        for tname, col in tones.items():
            css.append(f'.pat-{name}.pat--{tname}{{--pat:{uri(fn(col))}}}')
    css.append('.pat-wood.pat--blue{--pat:url("../patterns/wood-blue.svg")}')
    css.append('.pat-wood.pat--navy{--pat:url("../patterns/wood-navy.svg")}')
    css.append('.pat-wood.pat--gold{--pat:url("../patterns/wood-gold.svg")}')
    open(os.path.join(ROOT, 'assets', 'css', 'patterns.css'), 'w').write('\n'.join(css) + '\n')


if __name__ == '__main__':
    main()
