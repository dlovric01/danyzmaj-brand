import json, sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform


def outline(fontpath, text, axes, cap_height=100.0, tracking=0.0, target='cap'):
    f = TTFont(fontpath)
    f = instancer.instantiateVariableFont(f, axes, inplace=False)
    upem = f['head'].unitsPerEm
    os2 = f['OS/2']
    ref = getattr(os2, 'sCapHeight', None) or int(upem * 0.7)
    if target == 'x':
        ref = getattr(os2, 'sxHeight', None) or int(upem * 0.5)
    k = cap_height / ref
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    parts, pen_x = [], 0.0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            raise SystemExit('missing glyph for %r' % ch)
        g = gs[name]
        sp = SVGPathPen(gs, ntos=lambda v: format(v, '.2f'))
        g.draw(TransformPen(sp, Transform(k, 0, 0, -k, pen_x, 0)))
        d = sp.getCommands()
        if d:
            parts.append(d)
        pen_x += g.width * k + tracking * cap_height
    total = pen_x - (tracking * cap_height if text else 0)
    return {'d': ' '.join(parts), 'advance': round(total, 2), 'cap': cap_height,
            'ascender': round(f['hhea'].ascender * k, 2), 'descender': round(f['hhea'].descender * k, 2)}


def has(fontpath, ch):
    return ord(ch) in TTFont(fontpath).getBestCmap()


if __name__ == '__main__':
    B = 'BodoniModa.ttf'
    out = {
        'caps':  outline(B, 'DANYZMAJ', {'opsz': 96, 'wght': 700}, 100.0, 0.055),
        'caps_light': outline(B, 'DANYZMAJ', {'opsz': 96, 'wght': 500}, 100.0, 0.075),
        'lower': outline(B, 'danyzmaj', {'opsz': 96, 'wght': 700}, 100.0, 0.01),
        'cyr_ok': has(B, '\u0417'),
    }
    if out['cyr_ok']:
        out['cyr'] = outline(B, '\u0417\u041c\u0410\u0408', {'opsz': 96, 'wght': 700}, 100.0, 0.06)
    json.dump(out, open('wordmark.json', 'w'))
    print(json.dumps({k: (v if isinstance(v, bool) else {kk: vv for kk, vv in v.items() if kk != 'd'}) for k, v in out.items()}, indent=1))
