#!/usr/bin/env python3
"""Shared SVG helpers for the study-page diagram generators."""
import math, os, html

out = []


def e(s):
    return html.escape(str(s), quote=False)


def rect(x, y, w, h, cls='box', rx=6, extra=''):
    return f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" {extra}/>'


def text(x, y, s, cls='', anchor='middle'):
    a = '' if anchor == 'middle' else f' text-anchor="{anchor}"'
    return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor if anchor != "middle" else "middle"}">{e(s)}</text>'


def line(x1, y1, x2, y2, cls='ln'):
    return f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


def head(x, y, ux, uy, hc):
    px, py = -uy, ux
    bx, by = x - ux * 9, y - uy * 9
    return f'<polygon class="{hc}" points="{x:.1f},{y:.1f} {bx + px * 4.5:.1f},{by + py * 4.5:.1f} {bx - px * 4.5:.1f},{by - py * 4.5:.1f}"/>'


HC = {'lna': 'ah', 'lnc': 'ahc', 'lnd': 'ahd', 'lnr': 'ahr', 'lng': 'ah', 'ln': 'ahd'}


def arrow(x1, y1, x2, y2, cls='lna'):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    bx, by = x2 - ux * 8, y2 - uy * 8
    return (f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{bx:.1f}" y2="{by:.1f}"/>' + head(x2, y2, ux, uy, HC[cls]))


def poly_arrow(pts, cls='lna'):
    """polyline with arrowhead on the last segment"""
    (xa, ya), (xb, yb) = pts[-2], pts[-1]
    dx, dy = xb - xa, yb - ya
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    bx, by = xb - ux * 8, yb - uy * 8
    body = ' '.join(f'{x},{y}' for x, y in pts[:-1]) + f' {bx:.1f},{by:.1f}'
    return f'<polyline class="{cls}" points="{body}"/>' + head(xb, yb, ux, uy, HC[cls])


def svg(w, h, label, body):
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(label)}"><title>{e(label)}</title>{body}</svg>'


def add(key, title, cap, svgstr):
    assert '`' not in svgstr
    out.append(f'DIAGRAMS.{key}={{title:{title!r},cap:{cap!r},svg:`{svgstr}`}};')



def bracket(x1, x2, y, label, cls):
    return [line(x1, y, x2, y, 'ln'), line(x1, y - 6, x1, y, 'ln'), line(x2, y - 6, x2, y, 'ln'), text((x1 + x2) / 2, y + 20, label, 's ' + cls)]


UB = 20  # px per bit for fld()
X0 = 96


def fld(row_y, hi, lo, label, cls='dl', sub=None, ub=None, x0=None):
    """One field of a 32-bit register/DW row; bit 31 at the left."""
    ub = ub or UB
    x0 = X0 if x0 is None else x0
    x = x0 + (31 - hi) * ub
    w = (hi - lo + 1) * ub
    s = [rect(x, row_y, w, 40, cls, 2)]
    subtxt = sub or (f'[{hi}:{lo}]' if hi != lo else f'[{hi}]')
    if w >= 60:
        s += [text(x + w / 2, row_y + 19, label, 's h'), text(x + w / 2, row_y + 33, subtxt, 'xs d')]
    elif w >= 40:
        s += [text(x + w / 2, row_y + 19, label, 's h'), text(x + w / 2, row_y + 33, subtxt, 'xs d')]
    else:
        s += [text(x + w / 2, row_y + 24, label, 'xs h')]
    return s


def write(root, name='diagrams.js'):
    with open(os.path.join(root, name), 'w', encoding='utf-8') as f:
        f.write('var DIAGRAMS={};\n' + '\n'.join(out) + '\n')
    print('wrote', name, 'with', len(out), 'diagrams')
