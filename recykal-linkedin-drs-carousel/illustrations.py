#!/usr/bin/env python3
"""Draws the four slide illustrations (inline SVG) and injects them into carousel.html.

Story across the carousel (each visual builds on the previous one):
  1  intention  -> a gap -> action      (knowing is not doing)
  2  the choice moment                  (retained / returned / discarded / forgotten)
  3  the system around the choice       (return -> refund -> recover, repeatable loop)
  4  the gap from slide 1, now bridged  (conditions that help people act)
"""
import math, re, pathlib

G = "#049769"          # DRS green
MINT = "#D3ECE0"       # halo
GREY = "#9fb0a9"

DEFS = f'''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <linearGradient id="glass" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity=".95"/>
      <stop offset=".45" stop-color="#e4f0ec" stop-opacity=".75"/>
      <stop offset="1" stop-color="#fff" stop-opacity=".95"/>
    </linearGradient>
    <symbol id="bottle" viewBox="0 0 100 262">
      <path d="M41 16h18v20c0 14 29 22 29 50v156c0 12-9 20-21 20H33c-12 0-21-8-21-20V86c0-28 29-36 29-50z" fill="url(#glass)" stroke="#a9bab4" stroke-width="2.5"/>
      <rect x="12" y="118" width="76" height="58" fill="{G}"/>
      <path d="M50 129c-8 11-12 17-12 23a12 12 0 0 0 24 0c0-6-4-12-12-23z" fill="#fff"/>
      <path d="M13 108h74M13 186h74" stroke="#a9bab4" stroke-width="2" opacity=".7"/>
      <path d="M16 238c20 5 48 5 68 0" fill="none" stroke="#a9bab4" stroke-width="2" opacity=".7"/>
      <path d="M23 96v140" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".85"/>
      <rect x="36" y="31" width="28" height="4" rx="2" fill="#a9bab4"/>
      <rect x="38" y="2" width="24" height="17" rx="4" fill="{G}"/>
      <path d="M44 6v9M50 6v9M56 6v9" stroke="#fff" stroke-width="1.6" opacity=".5"/>
    </symbol>
    <symbol id="machine" viewBox="0 0 150 250">
      <rect x="2" y="2" width="146" height="246" rx="16" fill="#fff" stroke="#c3d0ca" stroke-width="3"/>
      <path d="M2 18A16 16 0 0 1 18 2h114a16 16 0 0 1 16 16v26H2z" fill="{G}"/>
      <rect x="48" y="17" width="54" height="10" rx="5" fill="#fff" opacity=".9"/>
      <rect x="18" y="60" width="114" height="48" rx="8" fill="#12302a"/>
      <rect x="30" y="74" width="56" height="7" rx="3.5" fill="{G}"/>
      <rect x="30" y="90" width="38" height="7" rx="3.5" fill="#6fd1ab" opacity=".6"/>
      <circle cx="110" cy="84" r="10" fill="{G}"/>
      <path d="M105 84l4 4 7-8" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="75" cy="170" r="42" fill="#e8eeeb" stroke="#c3d0ca" stroke-width="3"/>
      <circle cx="75" cy="170" r="31" fill="#1d2b27"/>
      <circle cx="75" cy="170" r="22" fill="#0d1613"/>
      <path d="M52 156a26 26 0 0 1 30-14" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".25"/>
      <rect x="16" y="228" width="118" height="9" rx="4.5" fill="#e3eae7"/>
    </symbol>
    <symbol id="coin" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="48" fill="{G}"/>
      <circle cx="50" cy="50" r="38" fill="none" stroke="#fff" stroke-width="2.5" opacity=".55"/>
      <text x="50" y="68" text-anchor="middle" font-family="Poppins,sans-serif" font-weight="700" font-size="52" fill="#fff">₹</text>
    </symbol>
  </defs>
</svg>'''

def chevron(x, y, deg, r=14):
    """green disc with a white chevron pointing along `deg` (0 = right)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({deg:.1f})">'
            f'<circle r="{r}" fill="{G}"/>'
            f'<path d="M-5 -8l9 8-9 8" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></g>')

def shadow(cx, cy, rx):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="7" fill="#0b3d2e" opacity=".10"/>'

LINE = f'fill="none" stroke="{G}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"'

# ───────────────────────── slide 1: intention → gap → action ─────────────────────────
def illus1():
    return f'''<svg viewBox="0 0 460 660" width="460" height="660" xmlns="http://www.w3.org/2000/svg">
  <circle cx="106" cy="444" r="104" fill="{MINT}" opacity=".8"/>
  <circle cx="360" cy="490" r="86" fill="{MINT}" opacity=".6"/>
  <path d="M28 604H432" stroke="#b9c9c3" stroke-width="2" stroke-linecap="round"/>
  {shadow(105,605,66)}{shadow(360,605,76)}
  <use href="#bottle" x="40" y="262" width="130" height="341"/>
  <use href="#machine" x="290" y="372" width="140" height="233"/>
  <!-- knowing: the idea -->
  <g transform="translate(105 122) scale(1.55) translate(-92 -88)" {LINE} stroke-width="3">
    <path d="M92 62a24 24 0 0 0-14 43v9h28v-9a24 24 0 0 0-14-43z"/>
    <path d="M82 124h20M85 133h14"/>
    <path d="M92 40v-9M62 52l-6-6M122 52l6-6M50 88h-9M134 88h9"/>
  </g>
  <path d="M105 208v42" stroke="{G}" stroke-width="3.5" stroke-dasharray="2 10" stroke-linecap="round"/>
  <!-- intention: dashed path (through "recycle it") that never arrives -->
  <path d="M188 112C228 28 348 28 382 128" fill="none" stroke="{G}" stroke-width="3.5" stroke-dasharray="3 12" stroke-linecap="round"/>
  <g transform="translate(284 52)">
    <circle r="34" fill="#fff" stroke="{G}" stroke-width="3.5"/>
    <g transform="scale(.95)" {LINE} stroke-width="3.4">
      <path d="M-13 -3a13 13 0 0 1 22-7M11-17v8h-8"/><path d="M13 3a13 13 0 0 1-22 7M-11 17v-8h8"/>
    </g>
  </g>
  <circle cx="386" cy="142" r="13" fill="#fff" stroke="{G}" stroke-width="3.5"/>
  <path d="M380 136l12 12M392 136l-12 12" stroke="{G}" stroke-width="3.2" stroke-linecap="round"/>
  <!-- action: the solid arrow into the return point -->
  <circle cx="360" cy="236" r="7" fill="{G}"/>
  <path d="M360 244V348" stroke="{G}" stroke-width="4.5" stroke-linecap="round"/>
  <path d="M346 334l14 16 14-16" fill="none" stroke="{G}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
  <!-- the gap, measured on the ground -->
  <g stroke="{G}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" fill="none">
    <path d="M186 572H274" stroke-dasharray="1 10"/>
    <path d="M186 560v24M274 560v24"/>
    <path d="M200 563l-12 9 12 9M260 563l12 9-12 9"/>
  </g>
</svg>'''

# ───────────────────────── slide 2: the choice moment ─────────────────────────
def illus2():
    def node(cx, cy, icon, state):
        if state == "go":      ring, fill, ic = G, G, "#fff"
        elif state == "lost":  ring, fill, ic = "#b3c0ba", "#f4f8f6", "#8da09a"
        else:                  ring, fill, ic = "#b3c0ba", "#fff", "#8da09a"
        dash = ' stroke-dasharray="5 7"' if state == "lost" else ""
        body = f'<circle cx="{cx}" cy="{cy}" r="50" fill="{fill}" stroke="{ring}" stroke-width="3.5"{dash}/>'
        return body + f'<g transform="translate({cx} {cy})" fill="none" stroke="{ic}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">{icon}</g>'
    retained  = '<path d="M-19-2L0-19 19-2"/><path d="M-14 0V19H14V0"/><path d="M-4 19v-10h8v10"/>'
    returned  = '<rect x="-16" y="-22" width="32" height="44" rx="5"/><path d="M-16-12H16" stroke-width="3"/><rect x="-9" y="-19" width="18" height="4" rx="2" fill="#fff" stroke="none"/><rect x="-9" y="-7" width="18" height="7" rx="2"/><circle cx="0" cy="11" r="5.5"/>'
    discarded = '<path d="M-16-10H16M-4-16h8"/><path d="M-11-10l2 28H9l2-28"/><path d="M-3-3v14M3-3v14"/>'
    bag = ('<path d="M-14 1C-14-11-5-16 0-16 5-16 14-11 14 1 14 9 8 13 0 13-8 13-14 9-14 1z" fill="#f4f8f6"/>'
           '<path d="M0-16l-4-6M0-16l5-5"/>')
    def at(x, y, k, body, rot=0):
        return f'<g transform="translate({x} {y}) rotate({rot}) scale({k})">{body}</g>'
    bottle = '<path d="M-2-13h4v5c0 2 5 3 5 7v13h-14v-13c0-4 5-5 5-7z" fill="#f4f8f6"/><path d="M-5 2h10" stroke-width="2.2"/>'
    can    = '<rect x="-6" y="-9" width="12" height="18" rx="2.5" fill="#f4f8f6"/><path d="M-6-4h12M-6 4h12" stroke-width="2.2"/>'
    forgotten = ('<g transform="scale(.95) translate(0 2)" stroke-width="3.2">'
                 + at(-27,-8,.95,bottle,-38) + at(30,-4,.95,can,24) + at(4,-3,1.12,bag)
                 + at(-19,13,.95,bag) + at(22,14,.88,bag) + at(2,19,.6,bag)
                 + '<path d="M-40 28H40"/>'
                 '<path d="M-26-34q5-6 10 0 5-6 10 0M12-37q4-5 8 0 4-5 8 0" stroke-width="2.6"/>'
                 '</g>')
    return f'''<svg viewBox="0 0 390 536" width="390" height="536" xmlns="http://www.w3.org/2000/svg">
  <circle cx="195" cy="116" r="92" fill="{MINT}" opacity=".75"/>
  {shadow(195,214,34)}
  <use href="#bottle" x="160" y="30" width="70" height="183"/>
  <path d="M195 236v26" stroke="{G}" stroke-width="3.5" stroke-linecap="round"/>
  <path d="M184 254l11 12 11-12" fill="none" stroke="{G}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
  {node(104,338,retained,"idle")}
  {node(286,338,returned,"go")}
  {node(104,466,discarded,"idle")}
  {node(286,466,forgotten,"lost")}
</svg>'''

# ───────────────────────── slide 3: the system around the choice ─────────────────────────
def illus3():
    cx, cy, R = 195, 296, 140
    def pt(deg): return cx + R*math.cos(math.radians(deg)), cy + R*math.sin(math.radians(deg))
    top, right, left = pt(-90), pt(30), pt(150)
    arrows = "".join(chevron(*pt(a), a + 90, 17) for a in (-30, 90, 210))
    def node(p): return f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="58" fill="#fff" stroke="{G}" stroke-width="3.5"/>'
    return f'''<svg viewBox="0 0 390 536" width="390" height="536" xmlns="http://www.w3.org/2000/svg">
  <circle cx="{cx}" cy="{cy}" r="120" fill="{MINT}" opacity=".6"/>
  <circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{G}" stroke-width="3.5" stroke-dasharray="2 10" stroke-linecap="round"/>
  {arrows}
  {node(top)}{node(right)}{node(left)}
  <use href="#bottle" x="{top[0]-20:.1f}" y="{top[1]-50:.1f}" width="40" height="104"/>
  <use href="#machine" x="{right[0]-29:.1f}" y="{right[1]-48:.1f}" width="58" height="97"/>
  <use href="#coin" x="{left[0]-34:.1f}" y="{left[1]-34:.1f}" width="68" height="68"/>
  <g transform="translate({cx} {cy-10}) scale(1.5)" {LINE} stroke-width="2.6">
    <path d="M-16 -4a16 16 0 0 1 27-9M13-22v10h-10"/>
    <path d="M16 4a16 16 0 0 1-27 9M-13 22v-10h10"/>
  </g>
</svg>'''

# ───────────────────────── slide 4: the gap from slide 1, bridged ─────────────────────────
def illus4():
    P0, C1, C2, P1 = (150, 172), (350, 36), (590, 36), (790, 172)
    def B(t):
        u = 1 - t
        x = u**3*P0[0] + 3*u*u*t*C1[0] + 3*u*t*t*C2[0] + t**3*P1[0]
        y = u**3*P0[1] + 3*u*u*t*C1[1] + 3*u*t*t*C2[1] + t**3*P1[1]
        return x, y
    ang = math.degrees(math.atan2(P1[1]-C2[1], P1[0]-C2[0]))
    pin   = f'<g transform="translate(0 2)" fill="none" stroke="{G}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"><path d="M0-17a11 11 0 0 1 11 11c0 8-11 21-11 21s-11-13-11-21a11 11 0 0 1 11-11z"/><circle cy="-6" r="4"/></g>'
    coin  = '<use href="#coin" x="-20" y="-20" width="40" height="40"/>'
    again = f'<g fill="none" stroke="{G}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"><path d="M-14-4a14 14 0 0 1 23-8M14-18v9h-9"/><path d="M14 4a14 14 0 0 1-23 8M-14 18v-9h9"/></g>'
    nodes = ""
    for t, icon in ((.25, pin), (.5, coin), (.75, again)):
        x, y = B(t)
        nodes += f'<g transform="translate({x:.1f} {y:.1f})"><circle r="38" fill="#fff" stroke="{G}" stroke-width="3.5"/>{icon}</g>'
    return f'''<svg viewBox="0 0 940 280" width="940" height="280" xmlns="http://www.w3.org/2000/svg">
  <circle cx="98" cy="150" r="104" fill="{MINT}" opacity=".75"/>
  <circle cx="842" cy="168" r="96" fill="{MINT}" opacity=".75"/>
  <path d="M26 250H914" stroke="#b9c9c3" stroke-width="2" stroke-linecap="round"/>
  {shadow(98,250,46)}{shadow(848,250,56)}
  <use href="#bottle" x="60" y="50" width="76" height="199"/>
  <use href="#machine" x="800" y="86" width="96" height="160"/>
  <path d="M{P0[0]} {P0[1]}C{C1[0]} {C1[1]} {C2[0]} {C2[1]} {P1[0]-18} {P1[1]-6}" fill="none" stroke="{G}" stroke-width="5" stroke-linecap="round"/>
  <circle cx="{P0[0]}" cy="{P0[1]}" r="7" fill="{G}"/>
  {nodes}
  {chevron(P1[0]-8, P1[1]-3, ang, 15)}
</svg>'''

def main():
    p = pathlib.Path(__file__).with_name("carousel.html")
    s = p.read_text()
    for tag, body in (("DEFS", DEFS), ("ILLUS1", illus1()), ("ILLUS2", illus2()), ("ILLUS3", illus3()), ("ILLUS4", illus4())):
        s, n = re.subn(rf"<!--{tag}-->.*?<!--/{tag}-->", lambda m: f"<!--{tag}-->{body}<!--/{tag}-->", s, flags=re.S)
        assert n == 1, tag
    p.write_text(s)

if __name__ == "__main__":
    main()
