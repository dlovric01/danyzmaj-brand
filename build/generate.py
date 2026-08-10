#!/usr/bin/env python3
"""Regenerate every danyzmaj logo asset from parameters.

The dragon is not a traced drawing — it is a parametric figure. The body is a
variable-width ribbon swept along a spine, the dorsal crest is placed on the
ribbon's own outward normals, and the head is a set of overlapping angular
masses. Everything is emitted as one filled path with fill-rule="nonzero";
the eye and nostril are subpaths wound the opposite way, so they are holes and
the mark stays single-colour on any ground.

Three cuts of the same animal: primary (>=96px), small (40-96px), tiny (16-40px).
Detail is removed as size drops so the silhouette never turns to mush.

    python3 build/generate.py          # writes logo/ + social/ + guide/

Wordmark outlines come from build/wordmark.json and build/archivo.json, produced
by build/outline.py, which needs fonttools:

    python3 -m venv build/.venv && build/.venv/bin/pip install fonttools
    cd build && .venv/bin/python outline.py

PNG rasters are not produced here (no rasteriser dependency); they were rendered
from these SVGs through a browser canvas at the sizes listed in README.md.
"""

import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / 'build'

INK, INK_SUNK = '#171210', '#100C0A'
CINNABAR, OXIDE, BRASS, BONE, BONE_DIM = '#DA3A20', '#8E1F0E', '#C08A2E', '#F2EDE4', '#CFC4B4'

# ── geometry helpers ────────────────────────────────────────────────────────

def catmull(pts, samples=18):
    """Centripetal-ish Catmull-Rom through (x, y, width) controls."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(len(P) - 3):
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        for s in range(samples):
            t = s / samples
            t2, t3 = t * t, t * t * t

            def c(a, b, cc, d):
                return 0.5 * ((2 * b) + (-a + cc) * t + (2 * a - 5 * b + 4 * cc - d) * t2
                              + (-a + 3 * b - 3 * cc + d) * t3)
            out.append((c(p0[0], p1[0], p2[0], p3[0]),
                        c(p0[1], p1[1], p2[1], p3[1]),
                        c(p0[2], p1[2], p2[2], p3[2])))
    out.append(tuple(pts[-1]))
    return out


def signed_area(pts):
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i][:2]
        x2, y2 = pts[(i + 1) % len(pts)][:2]
        a += x1 * y2 - x2 * y1
    return a / 2


def orient(pts, positive=True):
    return list(pts) if (signed_area(pts) > 0) == positive else list(pts)[::-1]


def poly(pts):
    d = 'M %.2f %.2f ' % tuple(pts[0][:2]) + ' '.join('L %.2f %.2f' % tuple(p[:2]) for p in pts[1:])
    return d + ' Z'


def polyO(pts):
    """Filled subpath. Every solid piece must share one winding direction or
    nonzero fill turns the overlap into a hole."""
    return poly(orient(pts, True))


def holeO(pts):
    """Reversed subpath — punches a hole in whatever it overlaps."""
    return poly(orient(pts, False))


def circle_path(cx, cy, r, ccw=False):
    sweep = 0 if ccw else 1
    return (f'M {cx - r:.2f} {cy:.2f} A {r:.2f} {r:.2f} 0 1 {sweep} {cx + r:.2f} {cy:.2f} '
            f'A {r:.2f} {r:.2f} 0 1 {sweep} {cx - r:.2f} {cy:.2f} Z')


def annulus(cx, cy, R, t):
    return circle_path(cx, cy, R, ccw=False) + ' ' + circle_path(cx, cy, R - t, ccw=True)


def ribbonO(pts, samples=18):
    """Variable-width stroke as a closed outline. Keep turns wide: the naive
    offset self-intersects on a tight corner and bites a notch out of the edge."""
    S = catmull(pts, samples)
    left, right, n = [], [], len(S)
    for i, (x, y, w) in enumerate(S):
        if i == 0:
            dx, dy = S[1][0] - x, S[1][1] - y
        elif i == n - 1:
            dx, dy = x - S[-2][0], y - S[-2][1]
        else:
            dx, dy = S[i + 1][0] - S[i - 1][0], S[i + 1][1] - S[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny, h = -dy / L, dx / L, w / 2
        left.append((x + nx * h, y + ny * h))
        right.append((x - nx * h, y - ny * h))
    return polyO(left + right[::-1])


def spikes_alongO(spine, specs, side=1, samples=18):
    """Dorsal crest. specs = [(t 0..1, height, halfwidth)], seated on the
    ribbon's edge and pointing along its outward normal, so the ridge follows
    the body around every bend instead of pointing blindly up."""
    S = catmull(spine, samples)
    n, out = len(S), []
    for (t, h, hw) in specs:
        i = max(1, min(n - 2, int(t * (n - 1))))
        x, y, w = S[i]
        dx, dy = S[i + 1][0] - S[i - 1][0], S[i + 1][1] - S[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        tx, ty = dx / L, dy / L
        nx, ny = -ty * side, tx * side
        bx, by = x + nx * (w / 2 - 0.8), y + ny * (w / 2 - 0.8)
        out.append(polyO([(bx - tx * hw, by - ty * hw),
                          (bx + nx * h + tx * hw * 0.35, by + ny * h + ty * hw * 0.35),
                          (bx + tx * hw, by + ty * hw)]))
    return out


def scale_pts(pts, k, cx, cy):
    return [((x - cx) * k + cx, (y - cy) * k + cy) for x, y in pts]

# ── the animal ─────────────────────────────────────────────────────────────

SKULL = [(40, 13.5), (29.0, 10.6), (20.0, 15.4), (16.5, 26.5), (24.0, 34.0), (38.5, 36.5)]


def head(k=0.88, gape=1.6, cx=39.0, cy=26.0, nostril=True, fang=True, horn2=True):
    """Overlapping masses: skull, upper jaw, lower jaw, snout hook, horns,
    barbel. Drawn as one polygon it became mush; as masses each is tunable."""
    S = lambda pts: scale_pts(pts, k, cx, cy)
    skull = S(SKULL)
    parts = [polyO(skull),
             polyO(S([(24, 18.5), (0.8, 26.8), (2.2, 29.4), (25.5, 30.4)])),               # upper jaw
             polyO(S([(30.5, 32.4 + gape), (8.0, 36.6 + gape),
                      (10.8, 40.4 + gape), (31.5, 38.0 + gape)])),                          # lower jaw
             polyO(S([(4.0, 26.0), (0.0, 31.4), (7.5, 29.6)])),                              # snout hook
             polyO(S([(33.0, 12.6), (62.0, 0.5), (46.5, 16.4)])),                            # main horn
             polyO(S([(27.0, 37.0 + gape), (24.0, 44.6 + gape), (31.5, 38.2 + gape)]))]      # chin barbel
    if fang:
        parts.append(polyO(S([(14.5, 29.6), (17.4, 35.2), (20.6, 29.9)])))
    if horn2:
        parts.append(polyO(S([(26.5, 11.0), (48.0, 5.0), (40.0, 17.2)])))
    holes = ' ' + holeO(S([(22.6, 19.2), (28.6, 17.4), (29.8, 21.4), (24.0, 23.4)]))         # eye
    if nostril:
        holes += ' ' + holeO(S([(8.0, 26.6), (11.4, 25.9), (9.6, 28.4)]))
    return ' '.join(parts) + holes


# spine of the Z: top bar, diagonal, bottom bar — one continuous body
SPINE_PRIMARY = [(38, 26, 12.4), (55, 24, 13.2), (70, 26.5, 13.6), (77.5, 33.5, 13.0),
                 (68, 45, 12.4), (56, 56, 11.6), (45.5, 66, 10.8), (41.5, 74, 10.0),
                 (49, 79.5, 9.2), (62, 82.5, 8.0), (76, 82.5, 6.6), (88, 80.5, 5.0)]
SPEAR_PRIMARY = [(74, 79.6), (86, 69.0), (89.5, 78.2), (101.5, 76.0), (92.5, 84.6), (90, 92.5), (74, 85.4)]
# The crest starts at t=0.30, not at the shoulder: any earlier and the first spike
# pinches against the horn tip, leaving a hairline of background along the neck's
# top edge that reads as a printing flaw on light grounds.
CREST_PRIMARY = [(0.30, 9.6, 3.9), (0.42, 8.6, 3.6), (0.54, 7.4, 3.2),
                 (0.66, 6.2, 2.8), (0.78, 4.8, 2.3)]

SPINE_SMALL = [(38, 26, 15.0), (55, 24, 15.8), (70, 26.5, 16.0), (77.5, 33.5, 15.6), (68, 45, 15.0),
               (56, 56, 14.0), (45.5, 66, 13.2), (41.5, 74, 12.4), (49, 79.5, 11.6),
               (62, 82.5, 10.4), (76, 82.5, 9.0), (88, 80.5, 7.0)]
SPEAR_SMALL = [(73, 77.6), (86, 67.5), (90, 77.0), (102, 75.0), (93, 85.4), (90.5, 93.5), (73, 86.4)]

# The tiny cut carries the heaviest body, so its bends are widened to keep the
# ribbon's inner offset from crossing itself and enclosing a sliver.
SPINE_TINY = [(38, 26, 16.4), (56, 24, 17.0), (70, 27, 17.0), (78, 33, 16.8), (74, 40, 16.4),
              (66, 48, 16.0), (56, 57, 15.2), (46, 66, 14.4), (42.5, 73, 13.8),
              (48, 78.5, 13.2), (60, 82, 12.0), (75, 82, 10.0), (88, 80, 7.6)]
SPEAR_TINY = [(72, 76.6), (87, 66.0), (91, 76.0), (103, 74.0), (94, 86.0), (91, 95.0), (72, 87.4)]


def dragon(hk=0.88, samples=12, spine=SPINE_PRIMARY, crest=CREST_PRIMARY,
           barb=SPEAR_PRIMARY, gape=1.6, **head_kw):
    return (' '.join([ribbonO(spine, samples), polyO(barb)]
                     + spikes_alongO(spine, crest, 1, samples))
            + ' ' + head(hk, gape, **head_kw))


# Verified invariant: flood-filling the rendered background leaves exactly the
# sanctioned holes and nothing else — primary: eye + nostril; small: eye; tiny: eye.
PRIMARY = dragon()
SMALL = dragon(hk=1.0, samples=10, spine=SPINE_SMALL, barb=SPEAR_SMALL, gape=2.2,
               crest=[(0.34, 10.5, 4.8), (0.50, 9.2, 4.2), (0.66, 7.6, 3.6)],
               nostril=False, fang=False)
TINY = dragon(hk=1.06, samples=10, spine=SPINE_TINY, barb=SPEAR_TINY, gape=2.6,
              crest=[(0.36, 11.0, 5.4), (0.56, 9.0, 4.6)],
              nostril=False, fang=False, horn2=False)

# Bounding boxes measured with SVGGraphicsElement.getBBox() in a real browser,
# then hard-coded so this script needs no renderer. Re-measure if geometry moves.
BBOX = {'primary': (4.68, 3.56, 96.82, 88.94),
        'small':   (0.00, 0.50, 102.00, 93.00),
        'tiny':   (-2.34, -1.03, 105.34, 96.03),
        'caps':    (2.23, -102.00, 811.47, 106.07)}
CUTS = {'primary': PRIMARY, 'small': SMALL, 'tiny': TINY}

# ── emit ───────────────────────────────────────────────────────────────────

def svg(vb, body, w, h, extra=''):
    return (f'<svg width="{w:g}" height="{h:g}" xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{vb}"{extra}>\n{body}\n</svg>\n')


def g(d, fill, tx=0.0, ty=0.0, s=1.0):
    t = f' transform="translate({tx:.3f} {ty:.3f}) scale({s:.5f})"' if (tx or ty or s != 1.0) else ''
    return f'  <path fill="{fill}" fill-rule="nonzero"{t} d="{d}"/>'


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def main():
    wm = json.loads((BUILD / 'wordmark.json').read_text())['caps']['d']
    domain = json.loads((BUILD / 'archivo.json').read_text())['domain']['d']
    wx, wy, ww, wh = BBOX['caps']

    def mark(fill, key='primary'):
        x, y, w, h = BBOX[key]
        return svg(f'0 0 {w:.2f} {h:.2f}', g(CUTS[key], fill, -x, -y), round(w, 2), round(h, 2))

    for key, stem in (('primary', 'mark'), ('small', 'mark-small'), ('tiny', 'mark-tiny')):
        write(f'logo/{stem}.svg', mark(CINNABAR, key))
        write(f'logo/{stem}-ink.svg', mark(INK, key))
    write('logo/mark-bone.svg', mark(BONE))

    for stem, fill in (('wordmark', INK), ('wordmark-bone', BONE), ('wordmark-cinnabar', CINNABAR)):
        write(f'logo/{stem}.svg', svg(f'0 0 {ww:.2f} {wh:.2f}', g(wm, fill, -wx, -wy), round(ww, 2), round(wh, 2)))

    def lockup_h(mark_fill, word_fill):
        mx, my, mw, mh = BBOX['primary']
        sm = 100.0 / mh
        MW, sw, gap = mw * sm, 0.44, 30.0
        x0 = MW + gap
        body = (g(PRIMARY, mark_fill, -mx * sm, -my * sm, sm) + '\n'
                + g(wm, word_fill, x0 - wx * sw, 72.0, sw))   # baseline on the cap-height centre
        return svg(f'0 0 {x0 + ww * sw:.2f} 100', body, round(x0 + ww * sw, 2), 100)

    write('logo/lockup-horizontal.svg', lockup_h(CINNABAR, INK))
    write('logo/lockup-horizontal-inverse.svg', lockup_h(CINNABAR, BONE))
    write('logo/lockup-horizontal-mono-ink.svg', lockup_h(INK, INK))
    write('logo/lockup-horizontal-mono-bone.svg', lockup_h(BONE, BONE))

    def lockup_v(mark_fill, word_fill):
        mx, my, mw, mh = BBOX['primary']
        sm = 100.0 / mh
        MW = mw * sm
        target = MW * 1.34
        sw = target / ww
        base = 100.0 + 20.0 + 100.0 * sw
        body = (g(PRIMARY, mark_fill, (target - MW) / 2 - mx * sm, -my * sm, sm) + '\n'
                + g(wm, word_fill, -wx * sw, base, sw))
        h = base + 4.07 * sw
        return svg(f'0 0 {target:.2f} {h:.2f}', body, round(target, 2), round(h, 2))

    write('logo/lockup-stacked.svg', lockup_v(CINNABAR, INK))
    write('logo/lockup-stacked-inverse.svg', lockup_v(CINNABAR, BONE))

    def seal(ring, fill, dw=116.0, dy=3.0):
        mx, my, mw, mh = BBOX['primary']
        s = dw / mw
        body = (g(annulus(100, 100, 96, 7.0), ring) + '\n' + g(annulus(100, 100, 83, 1.8), ring) + '\n'
                + g(PRIMARY, fill, (200 - dw) / 2 - mx * s, (200 - mh * s) / 2 + dy - my * s, s))
        return svg('0 0 200 200', body, 200, 200)

    write('logo/seal.svg', seal(CINNABAR, CINNABAR))
    write('logo/seal-ink.svg', seal(INK, INK))
    write('logo/seal-bone.svg', seal(BONE, BONE))

    def icon(size, rx, frac, key, bg=INK, fg=CINNABAR):
        mx, my, mw, mh = BBOX[key]
        s = (size * frac) / mw
        w, h = mw * s, mh * s
        body = (f'  <rect width="{size}" height="{size}" rx="{rx}" fill="{bg}"/>\n'
                + g(CUTS[key], fg, (size - w) / 2 - mx * s, (size - h) / 2 - my * s, s))
        return svg(f'0 0 {size} {size}', body, size, size)

    write('logo/favicon.svg', icon(64, 13, 0.80, 'tiny'))
    write('logo/favicon-bone.svg', icon(64, 13, 0.80, 'tiny', bg=BONE, fg=OXIDE))
    write('logo/app-icon.svg', icon(512, 0, 0.70, 'small'))
    write('logo/avatar.svg', icon(512, 0, 0.66, 'primary'))     # 0.66 keeps it inside a circle crop

    mx, my, mw, mh = BBOX['primary']
    H = 440.0
    s = H / mh
    sw, sd = 0.68, 0.26
    write('social/og.svg', svg('0 0 1200 630', '\n'.join([
        f'  <rect width="1200" height="630" fill="{INK}"/>',
        f'  <rect x="28.5" y="28.5" width="1143" height="573" fill="none" stroke="{BRASS}" stroke-width="1.5" opacity="0.5"/>',
        g(PRIMARY, CINNABAR, 1152 - mw * s - mx * s, (630 - H) / 2 - my * s, s),
        g(wm, BONE, 78 - wx * sw, 322.0, sw),
        f'  <rect x="78" y="356" width="{ww * sw:.1f}" height="1.5" fill="{BRASS}"/>',
        g(domain, BONE_DIM, 78.0, 410.0, sd)]), 1200, 630))

    # guide-only: the two misuse demos Plate 02 needs as real files
    write('guide/misuse-recoloured.svg', svg(f'0 0 {mw:.2f} {mh:.2f}',
          g(PRIMARY, '#4E8C3F', -mx, -my), round(mw, 2), round(mh, 2)))
    grad = ('  <defs><linearGradient id="g" x1="0" y1="1" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{CINNABAR}"/><stop offset="1" stop-color="{BRASS}"/>'
            '</linearGradient></defs>\n')
    write('guide/misuse-gradient.svg', svg(f'0 0 {mw:.2f} {mh:.2f}',
          grad + g(PRIMARY, 'url(#g)', -mx, -my), round(mw, 2), round(mh, 2)))

    print('wrote logo/, social/og.svg, guide/ from parameters')


if __name__ == '__main__':
    main()
