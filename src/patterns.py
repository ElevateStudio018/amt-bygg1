"""Genererar AMT Byggs mönsterbibliotek (materialmönster i loggans färger).

Kör: python3 src/patterns.py  -> assets/patterns/*.svg + assets/css/patterns.css
"""
import math, random, base64, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAVY, BLUE, GOLD = '#122a6e', '#0a9cf0', '#d9a21b'


def wood(width=1600, height=900, spacing=34, stroke=BLUE, sw=1,
         knots=((1120, 250, 62, 118), (420, 690, 50, 92), (760, 120, 36, 70),
                (1430, 700, 44, 84), (180, 230, 34, 66), (900, 600, 30, 58), (640, 820, 24, 46))):
    """Träådring: jämnt fördelade vertikala linjer som glider isär runt kvistar.

    Förskjutningen är monoton i linjens läge, så grannlinjer korsas eller trycks aldrig ihop.
    knots = (x, y, öppningens halva bredd, halva höjd).
    """
    def warp(b, y):
        x = b
        for kx, ky, r, ry in knots:
            dx = b - kx
            t = (y - ky) / (ry * 1.6)
            x += (1 if dx >= 0 else -1) * r * math.exp(-t * t) * math.exp(-(dx / (2 * r)) ** 2)
        return x + 8 * math.sin(y / 170 + b / 260) + 3 * math.sin(y / 63 + b / 90)

    paths = []
    for b0 in range(-72, width + 80, spacing):
        b = b0 + spacing / 2
        d = 'M' + ' L'.join(f'{warp(b, y):.1f} {y}' for y in range(-20, height + 21, 10))
        paths.append(f'<path d="{d}"/>')
    for kx, ky, r, ry in knots:
        for f in ((.82, .58, .36, .15) if r > 40 else (.8, .5, .22)):
            paths.append(f'<ellipse cx="{kx}" cy="{ky}" rx="{r * f:.1f}" ry="{ry * f * .9:.1f}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid slice">'
            f'<g fill="none" stroke="{stroke}" stroke-width="{sw}" vector-effect="non-scaling-stroke">' + ''.join(paths) + '</g></svg>')


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
