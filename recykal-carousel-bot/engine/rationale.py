#!/usr/bin/env python3
"""Design-rationale PDF for a post: one page per slide (slide image, then why it looks the way it does).

    python3 engine/rationale.py posts/<slug>/rationale.json     (needs dist/<slug>/slide-N.png from build.py)

rationale.json: {"slug", "title", "overview": [..], "rules": [..], "weak_spots": [..],
                 "slides": [{"title", "says", "shows": [..], "icons": [["name", "meaning"], ..]}]}
"""
import html, json, pathlib, subprocess, sys, glob, os, shutil
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(ROOT))
import build as B

def main(path):
    path = pathlib.Path(path).resolve()
    d = json.loads(path.read_text())
    out = REPO / "dist" / d["slug"]
    slides = sorted(out.glob("slide-*.png"), key=lambda p: int(p.stem.split("-")[1]))
    # continuity strip: the road band of every slide, joined
    bands = [Image.open(p).convert("RGB").crop((0, 350, 1080, 640)) for p in slides]
    rows = [bands[i:i + 2] for i in range(0, len(bands), 2)]
    strip = Image.new("RGB", (2160, 300 * len(rows) + 14 * (len(rows) - 1)), "white")
    for r, row in enumerate(rows):
        for c, im in enumerate(row): strip.paste(im, (c * 1080, r * 314))
    strip.save(out / "_strip.png")
    fonts = (B.ASSETS / "fonts.css").read_text().replace("url('fonts/", f"url('{(B.ASSETS / 'fonts').as_uri()}/")
    e = lambda s: html.escape(s, quote=False)
    li = lambda items: "".join(f"<li>{e(x)}</li>" for x in items)
    pages = [f'''<section class="pg"><div class="kick">DESIGN RATIONALE</div><h1>{e(d["title"])}</h1>
      <p class="lead">{e(d["overview"][0])}</p><img class="strip" src="{(out / "_strip.png").as_uri()}"><div class="cap">The road on slides 1+2 (top row) and 3+4 (bottom row), side by side as they sit in the carousel: the road never breaks at the slide edge.</div>
      <h3>How to read the visuals</h3><ul>{li(d["rules"])}</ul>
      <h3>Honest weak spots</h3><ul class="weak">{li(d["weak_spots"])}</ul></section>''']
    for i, (s, p) in enumerate(zip(d["slides"], slides), 1):
        icons = "".join(f"<tr><td class='in'>{e(n)}</td><td>{e(m)}</td></tr>" for n, m in s["icons"])
        pages.append(f'''<section class="pg"><div class="kick">SLIDE {i} OF {len(slides)}</div><h2>{e(s["title"])}</h2>
          <img class="slide" src="{p.as_uri()}"><div class="cols"><div><h3>What it communicates</h3><p>{e(s["says"])}</p>
          <h3>What the picture shows</h3><ul>{li(s["shows"])}</ul></div><div><h3>Icon by icon</h3><table>{icons}</table></div></div></section>''')
    css = """@page{size:A4;margin:0} *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:Poppins,sans-serif;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact}
    .pg{width:794px;height:1123px;padding:38px 46px;page-break-after:always;overflow:hidden} .pg:last-child{page-break-after:auto}
    .kick{font-size:11px;font-weight:700;letter-spacing:1.4px;color:#049769} h1{font-size:27px;font-weight:800;margin:6px 0 10px;line-height:1.2}
    h2{font-size:19px;font-weight:800;margin:4px 0 12px;line-height:1.25} h3{font-size:12.5px;font-weight:700;color:#049769;margin:12px 0 5px}
    .lead{font-size:13px;line-height:1.5;margin-bottom:14px} .strip{width:100%;border:1px solid #e3ece7;border-radius:10px} .cap{font-size:10.5px;color:#667;margin:4px 0 4px}
    .slide{width:560px;height:560px;display:block;margin:0 auto 4px;border:1px solid #e3ece7;border-radius:10px}
    ul{padding-left:17px;font-size:11.8px;line-height:1.5} li{margin-bottom:3px} .weak li::marker{color:#999}
    p{font-size:11.8px;line-height:1.5} .cols{display:grid;grid-template-columns:1.05fr 1fr;gap:22px;margin-top:2px}
    table{border-collapse:collapse;font-size:11.2px;line-height:1.4} td{padding:3px 8px 4px 0;vertical-align:top;border-bottom:1px solid #edf2ef} td.in{font-weight:700;color:#049769;white-space:nowrap;width:98px}"""
    page = out / "_rationale.html"
    page.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{fonts}{css}</style></head><body>{''.join(pages)}</body></html>")
    pdf = out / f"{d['slug']}-design-rationale.pdf"
    B.chrome("--no-pdf-header-footer", f"--print-to-pdf={pdf}", page.as_uri())
    page.unlink(); (out / "_strip.png").unlink()
    print("wrote", pdf.relative_to(REPO))

if __name__ == "__main__":
    main(sys.argv[1])
