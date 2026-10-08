"""Illustration scenes. Each scene is a function(params) -> svg string, registered with the panel
`kind` it is designed for:

  tall  460x660   cover-style slide   (text left, big illustration right)
  card  390x536   split-style slide   (text left, illustration right, callout box below)
  wide  940x280   statement slide     (heading on top, wide illustration, callout box below)

Scenes only describe *what* is shown. Which one to use is decided by the idea of the slide:

  gap     intention vs action, a missing step, "knowing is not doing"            tall
  hero    one thing in focus, with 1-3 supporting ideas around it                tall
  fork    a moment of choice with 2-4 possible outcomes (one can be highlighted) card
  loop    a repeating cycle of 3-4 stages                                         card
  steps   an ordered process, top to bottom (3-4 steps)                           card
  stat    one number / percentage                                                 card
  bridge  from A to B across a gap, with 2-4 enablers on the way                  wide
  flow    a left-to-right sequence of 3-5 stages                                  wide
"""
import math
import library as L
from library import G, MINT, GREY, GREY_L, halo, shadow, chevron, node, fit, icon, pt_on_circle

KINDS = {"tall": (460, 660), "card": (390, 536), "wide": (940, 280)}
SCENES = {}


def scene(kind):
    def deco(fn):
        SCENES[fn.__name__] = (kind, fn)
        return fn
    return deco


def wrap(kind, body):
    w, h = KINDS[kind]
    return f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


def _label(x, y, text, size=24, anchor="middle", maxc=15):
    """short caption (wrapped to <=2 lines) under/next to a node."""
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > maxc and cur: lines.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    y0 = y - (len(lines) - 1) * size * .6
    return "".join(f'<text x="{x}" y="{y0 + i * size * 1.2:.1f}" text-anchor="{anchor}" font-family="Poppins,sans-serif" '
                   f'font-weight="600" font-size="{size}" fill="#111">{ln}</text>' for i, ln in enumerate(lines[:2]))


def _item(x, default=None):
    if x is None:
        return default
    return x if isinstance(x, dict) else {"name": x}


def _need(p, key, lo, hi, what):
    v = p.get(key)
    if not isinstance(v, list) or not (lo <= len(v) <= hi):
        raise ValueError(f"scene needs '{key}': a list of {lo}-{hi} {what}")
    return v


# ───────────────────────────────── tall ─────────────────────────────────
@scene("tall")
def gap(p):
    """idea (top)  ····✕   |   from-object ↔ gap ↔ to-object, with a solid arrow arriving at `to`."""
    idea, way = p.get("idea", "bulb"), p.get("waypoint", "recycle")
    frm, to = p.get("from", "bottle"), p.get("to", "machine")
    b = [halo(106, 444, 104, .8), halo(360, 490, 86, .6),
         '<path d="M28 604H432" stroke="#b9c9c3" stroke-width="2" stroke-linecap="round"/>',
         shadow(105, 605, 66), shadow(360, 605, 76),
         fit(frm, 40, 262, 130, 341), fit(to, 290, 372, 140, 233),
         icon(idea, 105, 122, size=160, sw=4.4),
         f'<path d="M105 208v42" stroke="{G}" stroke-width="3.5" stroke-dasharray="2 10" stroke-linecap="round"/>',
         f'<path d="M188 112C228 28 348 28 382 128" fill="none" stroke="{G}" stroke-width="3.5" stroke-dasharray="3 12" stroke-linecap="round"/>',
         '<g transform="translate(284 52)"><circle r="34" fill="#fff" stroke="%s" stroke-width="3.5"/>%s</g>' % (G, icon(way, 0, 0, size=44, sw=3.6)),
         f'<circle cx="386" cy="142" r="13" fill="#fff" stroke="{G}" stroke-width="3.5"/>',
         f'<path d="M380 136l12 12M392 136l-12 12" stroke="{G}" stroke-width="3.2" stroke-linecap="round"/>',
         f'<circle cx="360" cy="236" r="7" fill="{G}"/><path d="M360 244V348" stroke="{G}" stroke-width="4.5" stroke-linecap="round"/>',
         f'<path d="M346 334l14 16 14-16" fill="none" stroke="{G}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>',
         f'<g stroke="{G}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none"><path d="M186 572H274" stroke-dasharray="1 10"/><path d="M186 560v24M274 560v24"/><path d="M200 563l-12 9 12 9M260 563l12 9-12 9"/></g>']
    return wrap("tall", "".join(b))


@scene("tall")
def hero(p):
    """One object in a big halo, up to 3 supporting ideas orbiting it."""
    obj = p.get("object", "bottle")
    badges = [_item(x) for x in (p.get("badges") or [])][:3]
    spots = [(86, 150), (384, 250), (92, 500)]
    b = [halo(230, 340, 196, .8), f'<path d="M60 590H400" stroke="#b9c9c3" stroke-width="2" stroke-linecap="round"/>',
         shadow(230, 591, 80)]
    for (x, y) in spots[:len(badges)]:
        b.append(f'<path d="M{x} {y}L230 340" stroke="{G}" stroke-width="3" stroke-dasharray="2 10" stroke-linecap="round"/>')
    b.append(fit(obj, 120, 110, 220, 480))
    for (x, y), it in zip(spots, badges):
        b.append(node(x, y, 46, it))
    return wrap("tall", "".join(b))


# ───────────────────────────────── card ─────────────────────────────────
@scene("card")
def fork(p):
    """object → arrow → 2-4 outcomes. Mark the one that matters with {"state": "go"}; fade lost ones with {"state": "lost"}."""
    obj = p.get("object", "bottle")
    opts = [_item(x) for x in _need(p, "options", 2, 4, "outcomes")]
    n = len(opts)
    pos = {2: [(104, 392), (286, 392)],
           3: [(104, 338), (286, 338), (195, 466)],
           4: [(104, 338), (286, 338), (104, 466), (286, 466)]}[n]
    r = 56 if n == 2 else 50
    b = [halo(195, 116, 92, .75), shadow(195, 214, 34), fit(obj, 160, 30, 70, 183),
         f'<path d="M195 236v26" stroke="{G}" stroke-width="3.5" stroke-linecap="round"/>',
         f'<path d="M184 254l11 12 11-12" fill="none" stroke="{G}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>']
    for (x, y), it in zip(pos, opts):
        it = dict(it)
        if "state" not in it:
            it.setdefault("grey", True)
        b.append(node(x, y, r, it))
    return wrap("card", "".join(b))


@scene("card")
def loop(p):
    """3-4 stages on a circular loop with direction arrows and a repeat symbol in the middle."""
    nodes = [_item(x) for x in _need(p, "nodes", 3, 4, "stages")]
    n = len(nodes)
    cx, cy = 195, 296
    R, r = (140, 58) if n == 3 else (126, 48)
    angles = [-90, 30, 150] if n == 3 else [-90, 0, 90, 180]
    mids = [-30, 90, 210] if n == 3 else [-45, 45, 135, 225]
    b = [halo(cx, cy, 120, .6),
         f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{G}" stroke-width="3.5" stroke-dasharray="2 10" stroke-linecap="round"/>']
    b += [chevron(*pt_on_circle(cx, cy, R, a), a + 90, 17) for a in mids]
    for a, it in zip(angles, nodes):
        x, y = pt_on_circle(cx, cy, R, a)
        b.append(node(x, y, r, it))
    b.append(icon(p.get("center", "repeat"), cx, cy - 6, size=66, sw=4.2))
    return wrap("card", "".join(b))


@scene("card")
def steps(p):
    """3-4 stages stacked top to bottom with down-arrows between them. Optional `labels` (one short caption per step)."""
    st = [_item(x) for x in _need(p, "steps", 3, 4, "steps")]
    labels = p.get("labels")
    if labels and len(labels) != len(st): raise ValueError("steps: 'labels' must have one entry per step")
    n = len(st)
    r = (52 if n == 3 else 40) if not labels else (48 if n == 3 else 40)
    cx = 195 if not labels else 28 + r + 24
    top, bottom = 40, 496
    gap_ = (bottom - top - n * 2 * r) / (n - 1)
    b = [halo(195, 268, 150, .55)] if not labels else [halo(cx + 40, 268, 150, .45)]
    ys = [top + r + i * (2 * r + gap_) for i in range(n)]
    for i in range(n - 1):
        y0, y1 = ys[i] + r, ys[i + 1] - r
        b.append(f'<path d="M{cx} {y0 + 4:.1f}V{y1 - 4:.1f}" stroke="{G}" stroke-width="3.5" stroke-dasharray="2 9" stroke-linecap="round"/>')
        b.append(chevron(cx, (y0 + y1) / 2, 90, 14))
    for i, (y, it) in enumerate(zip(ys, st)):
        b.append(node(cx, y, r, it))
        if labels:
            b.append(_label(cx + r + 20, y + 8, labels[i], size=24, anchor="start", maxc=13))
    return wrap("card", "".join(b))


@scene("card")
def stat(p):
    """A big number inside a donut. value = 0-100 (ring fill), text = what is printed (default '<value>%')."""
    v = float(p.get("value", 50))
    txt = str(p.get("text", f"{v:g}%"))
    cx, cy, R, sw = 195, 232, 108, 30
    circ = 2 * math.pi * R
    fs = 64 if len(txt) <= 4 else (52 if len(txt) <= 6 else 42)
    cap = str(p.get("caption", ""))
    words, lines, cur = cap.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 24 and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur: lines.append(cur)
    b = [halo(cx, cy, 150, .55),
         f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#cfe5da" stroke-width="{sw}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{G}" stroke-width="{sw}" stroke-linecap="round" '
         f'stroke-dasharray="{circ * v / 100:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>',
         f'<text x="{cx}" y="{cy + fs * .34:.1f}" text-anchor="middle" font-family="Poppins,sans-serif" font-weight="800" font-size="{fs}" fill="{G}">{txt}</text>']
    y = 398
    for ln in lines[:3]:
        b.append(f'<text x="{cx}" y="{y}" text-anchor="middle" font-family="Poppins,sans-serif" font-weight="500" font-size="22" fill="#222">{ln}</text>')
        y += 30
    if p.get("icon"):
        b.append(icon(p["icon"], cx, 470 if lines else 420, size=46, sw=3.6))
    return wrap("card", "".join(b))


# ───────────────────────────────── wide ─────────────────────────────────
@scene("wide")
def bridge(p):
    """from ⟶ to along an arc, with 2-4 enablers (icons/objects) sitting on the path. Pairs with a `gap` slide."""
    frm, to = p.get("from", "bottle"), p.get("to", "machine")
    stops = [_item(x) for x in (p.get("stops") or ["pin", "rupee", "repeat"])][:4]
    P0, C1, C2, P1 = (150, 172), (350, 36), (590, 36), (790, 172)
    def B(t):
        u = 1 - t
        return (u**3*P0[0] + 3*u*u*t*C1[0] + 3*u*t*t*C2[0] + t**3*P1[0],
                u**3*P0[1] + 3*u*u*t*C1[1] + 3*u*t*t*C2[1] + t**3*P1[1])
    ang = math.degrees(math.atan2(P1[1] - C2[1], P1[0] - C2[0]))
    b = [halo(98, 150, 104, .75), halo(842, 168, 96, .75),
         '<path d="M26 250H914" stroke="#b9c9c3" stroke-width="2" stroke-linecap="round"/>',
         shadow(98, 250, 46), shadow(848, 250, 56),
         fit(frm, 60, 50, 76, 199), fit(to, 800, 86, 96, 160),
         f'<path d="M{P0[0]} {P0[1]}C{C1[0]} {C1[1]} {C2[0]} {C2[1]} {P1[0]-18} {P1[1]-6}" fill="none" stroke="{G}" stroke-width="5" stroke-linecap="round"/>',
         f'<circle cx="{P0[0]}" cy="{P0[1]}" r="7" fill="{G}"/>']
    n = len(stops)
    for i, it in enumerate(stops):
        x, y = B((i + 1) / (n + 1))
        b.append(node(x, y, 38, it))
    b.append(chevron(P1[0] - 8, P1[1] - 3, ang, 15))
    return wrap("wide", "".join(b))


@scene("wide")
def flow(p):
    """3-5 stages left to right joined by arrows. Optional `labels` (one short caption per stage, shown under each node)."""
    st = [_item(x) for x in _need(p, "steps", 3, 5, "stages")]
    labels = p.get("labels")
    if labels and len(labels) != len(st): raise ValueError("flow: 'labels' must have one entry per stage")
    n = len(st)
    r = (62 if n <= 4 else 52) if not labels else (54 if n <= 4 else 46)
    xs = [100 + i * (940 - 200) / (n - 1) for i in range(n)]
    cy = 140 if not labels else 112
    b = []
    for i in range(n - 1):
        x0, x1 = xs[i] + r + 8, xs[i + 1] - r - 8
        b.append(f'<path d="M{x0:.1f} {cy}H{x1:.1f}" stroke="{G}" stroke-width="3.5" stroke-dasharray="2 9" stroke-linecap="round"/>')
        b.append(chevron((x0 + x1) / 2, cy, 0, 15))
    for i, (x, it) in enumerate(zip(xs, st)):
        b.append(node(x, cy, r, it))
        if labels:
            b.append(_label(x, cy + r + 34, labels[i], size=23, anchor="middle", maxc=16))
    return wrap("wide", "".join(b))


def render(visual):
    name = visual["scene"]
    if name not in SCENES:
        raise KeyError(f"unknown scene '{name}'. Available: {', '.join(SCENES)}")
    kind, fn = SCENES[name]
    params = {k: v for k, v in visual.items() if k != "scene"}
    return kind, fn(params)
