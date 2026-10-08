"""Visual vocabulary for the Recykal carousel bot.

OBJECTS  full-colour illustrated things (bottle, can, machine, ...)  -> placed with fit()
ICONS    single-colour line icons on a 48x48 grid centred on 0,0     -> placed with icon()

Everything is plain SVG so scenes stay vector-sharp in the PDF.
"""
import math

G = "#049769"        # DRS green
MINT = "#D3ECE0"     # halo behind objects
PANEL = "#EAF6F0"    # illustration panel background
GREY = "#8da09a"
GREY_L = "#b3c0ba"
LINE_G = "#a9bab4"   # glass outline

# ─────────────────────────────── objects ───────────────────────────────
# name: (viewBox width, viewBox height, inner svg)
OBJECTS = {
    "bottle": (100, 262, f'''
      <path d="M41 16h18v20c0 14 29 22 29 50v156c0 12-9 20-21 20H33c-12 0-21-8-21-20V86c0-28 29-36 29-50z" fill="url(#glass)" stroke="{LINE_G}" stroke-width="2.5"/>
      <rect x="12" y="118" width="76" height="58" fill="{G}"/>
      <path d="M50 129c-8 11-12 17-12 23a12 12 0 0 0 24 0c0-6-4-12-12-23z" fill="#fff"/>
      <path d="M13 108h74M13 186h74" stroke="{LINE_G}" stroke-width="2" opacity=".7"/>
      <path d="M16 238c20 5 48 5 68 0" fill="none" stroke="{LINE_G}" stroke-width="2" opacity=".7"/>
      <path d="M23 96v140" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".85"/>
      <rect x="36" y="31" width="28" height="4" rx="2" fill="{LINE_G}"/>
      <rect x="38" y="2" width="24" height="17" rx="4" fill="{G}"/>
      <path d="M44 6v9M50 6v9M56 6v9" stroke="#fff" stroke-width="1.6" opacity=".5"/>'''),

    "can": (80, 130, f'''
      <path d="M8 16c0-6 6-8 12-8h40c6 0 12 2 12 8v98c0 6-6 9-12 9H20c-6 0-12-3-12-9z" fill="url(#metal)" stroke="{LINE_G}" stroke-width="2.5"/>
      <rect x="8" y="44" width="64" height="44" fill="{G}"/>
      <path d="M40 52c-6 8-9 12-9 17a9 9 0 0 0 18 0c0-5-3-9-9-17z" fill="#fff"/>
      <ellipse cx="40" cy="12" rx="29" ry="5" fill="#eef3f1" stroke="{LINE_G}" stroke-width="2"/>
      <ellipse cx="40" cy="11" rx="9" ry="2.6" fill="none" stroke="{LINE_G}" stroke-width="2"/>
      <path d="M16 20v92" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".7"/>
      <path d="M12 118c18 4 38 4 56 0" fill="none" stroke="{LINE_G}" stroke-width="2" opacity=".7"/>'''),

    "glass": (80, 262, f'''
      <path d="M32 8h16v66c0 15 24 22 24 50v122c0 10-8 16-18 16H26c-10 0-18-6-18-16V124c0-28 24-35 24-50z" fill="url(#gglass)" stroke="#1a6e50" stroke-width="2.5"/>
      <rect x="9" y="140" width="62" height="64" fill="#f4faf7" opacity=".92"/>
      <path d="M28 160h24M32 172h16M34 184h12" stroke="{G}" stroke-width="3" stroke-linecap="round"/>
      <rect x="30" y="2" width="20" height="10" rx="3" fill="{G}"/>
      <path d="M20 100v130" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".45"/>'''),

    "machine": (150, 250, f'''
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
      <rect x="16" y="228" width="118" height="9" rx="4.5" fill="#e3eae7"/>'''),

    "coin": (100, 100, f'''
      <circle cx="50" cy="50" r="48" fill="{G}"/>
      <circle cx="50" cy="50" r="38" fill="none" stroke="#fff" stroke-width="2.5" opacity=".55"/>
      <text x="50" y="68" text-anchor="middle" font-family="Poppins,sans-serif" font-weight="700" font-size="52" fill="#fff">₹</text>'''),

    "crate": (170, 120, f'''
      <rect x="22" y="6" width="22" height="46" rx="6" fill="url(#glass)" stroke="{LINE_G}" stroke-width="2.5"/>
      <rect x="29" y="0" width="8" height="10" rx="2" fill="{G}"/>
      <rect x="74" y="6" width="22" height="46" rx="6" fill="url(#glass)" stroke="{LINE_G}" stroke-width="2.5"/>
      <rect x="81" y="0" width="8" height="10" rx="2" fill="{G}"/>
      <rect x="126" y="6" width="22" height="46" rx="6" fill="url(#glass)" stroke="{LINE_G}" stroke-width="2.5"/>
      <rect x="133" y="0" width="8" height="10" rx="2" fill="{G}"/>
      <rect x="3" y="40" width="164" height="76" rx="10" fill="#fff" stroke="#c3d0ca" stroke-width="3"/>
      <rect x="3" y="40" width="164" height="18" rx="9" fill="{G}"/>
      <path d="M20 74h130M20 90h130M20 104h130" stroke="#d9e3df" stroke-width="5" stroke-linecap="round"/>'''),

    "bag": (120, 130, f'''
      <path d="M22 52C14 70 14 96 28 112c10 10 54 10 64 0 14-16 14-42 6-60-6-12-14-18-24-22l6-16-14 8-14-8 6 16c-10 4-18 10-24 22z" fill="#f4f8f6" stroke="#9fb0a9" stroke-width="3" stroke-linejoin="round"/>
      <path d="M38 62c-6 14-4 34 4 44M84 66c4 12 4 26-2 38" fill="none" stroke="#d3ddd9" stroke-width="3" stroke-linecap="round"/>
      <path d="M46 28c6-6 22-6 28 0" fill="none" stroke="#9fb0a9" stroke-width="3" stroke-linecap="round"/>'''),

    "kiosk": (210, 230, f'''
      <path d="M0 52L22 12h166l22 40z" fill="#dfe8e4" stroke="#b6c4be" stroke-width="3" stroke-linejoin="round"/>
      <rect x="14" y="52" width="182" height="168" fill="#fff" stroke="#c3d0ca" stroke-width="3"/>
      <rect x="28" y="66" width="154" height="84" rx="4" fill="url(#glass)" stroke="#b6c4be" stroke-width="3"/>
      <path d="M80 66v84M130 66v84" stroke="#b6c4be" stroke-width="3"/>
      <rect x="14" y="150" width="182" height="14" fill="{G}"/>
      <rect x="40" y="172" width="130" height="38" rx="4" fill="#f1f5f3" stroke="#d3ddd9" stroke-width="2"/>
      <rect x="86" y="24" width="38" height="14" rx="3" fill="{G}"/>
      <path d="M0 224h210" stroke="#b6c4be" stroke-width="3" stroke-linecap="round"/>'''),
}

DEFS = f'''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <linearGradient id="glass" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity=".95"/><stop offset=".45" stop-color="#e4f0ec" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity=".95"/>
    </linearGradient>
    <linearGradient id="metal" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="#cfd8d4"/><stop offset=".4" stop-color="#f7faf9"/><stop offset="1" stop-color="#c3cdc9"/>
    </linearGradient>
    <linearGradient id="gglass" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="#2c9a74"/><stop offset=".5" stop-color="#52c398"/><stop offset="1" stop-color="#1f7f5c"/>
    </linearGradient>
    {"".join(f'<symbol id="obj-{n}" viewBox="0 0 {w} {h}">{inner}</symbol>' for n, (w, h, inner) in OBJECTS.items())}
  </defs>
</svg>'''

# ─────────────────────────────── icons ───────────────────────────────
# 48x48 grid centred on 0,0. Stroke only (fill none) unless a path says otherwise. '@C' = icon colour.
ICONS = {
    "bulb":      '<path d="M0-14a11 11 0 0 0-6.4 20v4h12.8v-4A11 11 0 0 0 0-14z"/><path d="M-4 14h8M-3 18h6"/><path d="M0-18v-5M-14-13l-3-3M14-13l3-3M-19-3h-4M19-3h4"/>',
    "repeat":    '<path d="M-14-4a14 14 0 0 1 23-8M14-18v9h-9"/><path d="M14 4a14 14 0 0 1-23 8M-14 18v-9h9"/>',
    "recycle":   '<g><path d="M-5-17A17 17 0 0 1 14-9"/><path d="M8-10l6 1-1 7"/></g><g transform="rotate(120)"><path d="M-5-17A17 17 0 0 1 14-9"/><path d="M8-10l6 1-1 7"/></g><g transform="rotate(240)"><path d="M-5-17A17 17 0 0 1 14-9"/><path d="M8-10l6 1-1 7"/></g>',
    "home":      '<path d="M-19-2L0-19 19-2"/><path d="M-14 0V19H14V0"/><path d="M-4 19v-10h8v10"/>',
    "bin":       '<path d="M-16-10H16M-4-16h8"/><path d="M-11-10l2 28H9l2-28"/><path d="M-3-3v14M3-3v14"/>',
    "landfill":  '<path d="M-24 21H24"/><path d="M3 21L8 8 12 11 16-2 20 6 24 21"/><path d="M-24 14V6h5l3 4v4"/><path d="M-24 14H-2"/><path d="M-2 11L-15 3.5l3.5-6.1L1.5 4.9z"/><circle cx="-19" cy="17.5" r="2.8"/><circle cx="-9" cy="17.5" r="2.8"/><path d="M-4-16q2-2.6 4 0 2-2.6 4 0M10-19q1.8-2.2 3.6 0 1.8-2.2 3.6 0"/>',
    "machine":   '<rect x="-16" y="-22" width="32" height="44" rx="5"/><path d="M-16-12H16"/><rect x="-9" y="-7" width="18" height="7" rx="2"/><circle cx="0" cy="11" r="5.5"/>',
    "pin":       '<path d="M0-19a11 11 0 0 1 11 11c0 8-11 23-11 23S-11 0-11-8a11 11 0 0 1 11-11z"/><circle cy="-8" r="4"/>',
    "check":     '<path d="M-14 1l9 9 19-20"/>',
    "arrow-right": '<path d="M-16 0H16M6-10l10 10-10 10"/>',
    "arrow-down":  '<path d="M0-16V16M-10 6l10 10 10-10"/>',
    "arrow-up":    '<path d="M0 16V-16M-10-6l10-10 10 10"/>',
    "rupee":     '<path d="M-9-13H10M-9-5H10"/><path d="M-9-13H-2c10 0 10 14 0 14H-9"/><path d="M-9 1l15 15"/>',
    "truck":     '<path d="M-24-12h26v20h-26z"/><path d="M2-4h10l8 8v4H2z"/><circle cx="-14" cy="12" r="4"/><circle cx="12" cy="12" r="4"/>',
    "factory":   '<path d="M-22 18V0l11 7V0l11 7V-14h14v32z"/><path d="M0-14V-22h10v8"/><path d="M-4 8v6M6 8v6M-14 12v2"/>',
    "people":    '<circle cx="-8" cy="-8" r="6"/><path d="M-20 16c0-8 5-12 12-12s12 4 12 12"/><circle cx="12" cy="-6" r="5"/><path d="M8 4c8-2 14 2 14 10"/>',
    "leaf":      '<path d="M-16 14C-16-6 0-18 18-18 18 0 6 14-16 14z"/><path d="M-16 14L4-6"/>',
    "globe":     '<circle r="17"/><ellipse rx="7.5" ry="17"/><path d="M-17 0H17M-14-9H14M-14 9H14"/>',
    "clock":     '<circle r="17"/><path d="M0-9V0l7 5"/>',
    "chart-up":  '<path d="M-18-18V16H18"/><path d="M-11 6l8-9 6 5 12-14"/><path d="M8-12h7v7"/>',
    "shield":    '<path d="M0-19l16 6v9c0 10-7 17-16 21-9-4-16-11-16-21v-9z"/><path d="M-6 0l5 5 9-10"/>',
    "box":       '<path d="M0-18l16 8v16l-16 8-16-8v-16z"/><path d="M-16-10l16 8 16-8M0-2v16"/>',
    "bottle":    '<path d="M-4-20h8v6c0 3 7 4 7 10V16a4 4 0 0 1-4 4H-7a4 4 0 0 1-4-4V-4c0-6 7-7 7-10z"/><path d="M-11 0h22M-11 10h22"/>',
    "can":       '<path d="M-10-14h20v28a4 4 0 0 1-4 4h-12a4 4 0 0 1-4-4z"/><ellipse cy="-14" rx="10" ry="3"/><path d="M-10 0h20"/>',
    "target":    '<circle r="17"/><circle r="9"/><circle r="2" fill="@C"/>',
    "doc":       '<path d="M-12-18h16l10 10v26H-12z"/><path d="M4-18v10h10M-6 0h12M-6 7h12"/>',
    "calendar":  '<rect x="-17" y="-15" width="34" height="32" rx="4"/><path d="M-17-5H17M-8-20v8M8-20v8"/><path d="M-9 4h4M-2 4h4M5 4h4M-9 11h4M-2 11h4" />',
    "search":    '<circle cx="-3" cy="-3" r="12"/><path d="M6 6l12 12"/>',
    "megaphone": '<path d="M-18-4h8l14-10V18L-10 8h-8z"/><path d="M-10 8l3 12h6l-3-10"/><path d="M10-6c4 3 4 9 0 12"/>',
    "scale":     '<path d="M0-18V18M-10 18H10M-18-12H18"/><path d="M-18-12l-8 14h16zM18-12l-8 14h16z"/>',
    "dots":      '<circle cx="-15" r="3" fill="@C"/><circle r="3" fill="@C"/><circle cx="15" r="3" fill="@C"/>',
    "x":         '<path d="M-12-12l24 24M12-12l-24 24"/>',
    "phone":     '<rect x="-11" y="-20" width="22" height="40" rx="5"/><path d="M-3 14h6"/>',
}
ICON_ALIASES = {"arrow": "arrow-right", "return": "machine", "reverse-vending": "machine", "rvm": "machine",
                "refund": "rupee", "money": "rupee", "idea": "bulb", "knowing": "bulb", "retain": "home",
                "discard": "bin", "waste": "bin", "forgotten": "dots", "tick": "check", "growth": "chart-up",
                "location": "pin", "access": "pin", "loop": "repeat", "circular": "recycle", "policy": "doc",
                "law": "scale", "community": "people", "world": "globe", "time": "clock"}

ICON_SCALE = {"landfill": 1.7, "truck": 1.15, "factory": 1.1}   # icons that need more room to stay legible

def resolve_icon(name):
    name = ICON_ALIASES.get(name, name)
    if name not in ICONS:
        raise KeyError(f"unknown icon '{name}'. Available: {', '.join(sorted(ICONS))}")
    return name

# ─────────────────────────────── helpers ───────────────────────────────
def icon(name, cx, cy, size=48, sw=3.5, color=G):
    """Line icon centred at cx,cy; `size` is the 48-unit grid in px; `sw` is the on-screen stroke width."""
    name = resolve_icon(name)
    k = size * ICON_SCALE.get(name, 1) / 48
    inner = ICONS[name].replace("@C", color)
    return (f'<g transform="translate({cx:.1f} {cy:.1f}) scale({k:.4f})" fill="none" stroke="{color}" '
            f'stroke-width="{sw / k:.3f}" stroke-linecap="round" stroke-linejoin="round">{inner}</g>')

def fit(name, x, y, w, h, align="bottom", opacity=None):
    """Draw OBJECTS[name] inside the box x,y,w,h preserving aspect ratio (centred, bottom-aligned by default)."""
    if name not in OBJECTS:
        raise KeyError(f"unknown object '{name}'. Available: {', '.join(OBJECTS)}")
    ow, oh, _ = OBJECTS[name]
    s = min(w / ow, h / oh)
    dw, dh = ow * s, oh * s
    dx = x + (w - dw) / 2
    dy = y + (h - dh) if align == "bottom" else y + (h - dh) / 2
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<use href="#obj-{name}" x="{dx:.1f}" y="{dy:.1f}" width="{dw:.1f}" height="{dh:.1f}"{op}/>'

def is_object(name): return name in OBJECTS

def shadow(cx, cy, rx):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="7" fill="#0b3d2e" opacity=".10"/>'

def chevron(x, y, deg, r=14):
    """green disc with a white chevron pointing along `deg` (0 = right)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({deg:.1f})"><circle r="{r}" fill="{G}"/>'
            f'<path d="M-5 -8l9 8-9 8" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></g>')

def node(cx, cy, r, item, state="idle"):
    """Round node holding an object or icon. state: idle | go (filled green) | lost (faded, dashed)."""
    item = item if isinstance(item, dict) else {"name": item}
    # {"icon": x} forces the line icon, {"obj": x} forces the illustration, a bare name prefers the illustration
    force = "icon" if item.get("icon") else "obj" if item.get("obj") else None
    name = item.get("obj") or item.get("icon") or item.get("name")
    state = item.get("state", state)
    if state == "go":      ring, fill, ic = G, G, "#fff"
    elif state == "lost":  ring, fill, ic = GREY_L, "#f4f8f6", GREY
    else:                  ring, fill, ic = (G if not item.get("grey") else GREY_L), "#fff", (G if not item.get("grey") else GREY)
    dash = ' stroke-dasharray="5 7"' if state == "lost" else ""
    body = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" stroke="{ring}" stroke-width="3.5"{dash}/>'
    if force != "icon" and is_object(name):
        ow, oh, _ = OBJECTS[name]
        box = r * 1.62
        return body + fit(name, cx - box / 2, cy - box / 2, box, box, align="center", opacity=0.55 if state == "lost" else None)
    return body + icon(name, cx, cy, size=r * 0.95, sw=3.8, color=ic)

def halo(cx, cy, r, op=.75):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{MINT}" opacity="{op}"/>'

def pt_on_circle(cx, cy, R, deg):
    return cx + R * math.cos(math.radians(deg)), cy + R * math.sin(math.radians(deg))
