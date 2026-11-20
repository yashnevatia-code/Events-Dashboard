#!/usr/bin/env python3
"""Measure how readable every line of text is, from the pixels, not by eye.

    python3 -I engine/legibility.py posts/<slug>/post.json

For each slide the page is rendered with the text hidden (photo, veil and boxes only). Behind every text line the script samples the
background and reports its brightness and busyness, then the contrast ratio of the line's colour (black, DRS green or white) against it.
A line fails when the contrast is under 4.5:1 for body-size text or 3:1 for large/bold text, or when the background is busy
(a face, an edge or a bright object behind the letters), which is how text "overlapping the photo" shows up in numbers.
Also prints the smallest text size per slide and the size at a 400 px phone width.
"""
import glob, html, json, pathlib, re, subprocess, sys
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

JS = """<script>document.fonts.ready.then(()=>{const R=[];document.querySelectorAll('.slide').forEach((s,i)=>{
const b=s.getBoundingClientRect();const lines=[];
s.querySelectorAll('.stack *, .box *').forEach(el=>{
  const cs=getComputedStyle(el);
  for(const n of el.childNodes){ if(n.nodeType!==3||!n.textContent.trim()) continue;
    const r=document.createRange(); r.selectNodeContents(n);
    for(const c of r.getClientRects()){ if(c.width<6) continue;
      lines.push({x0:c.left-b.left,y0:c.top-b.top,x1:c.right-b.left,y1:c.bottom-b.top,color:cs.color,size:parseFloat(cs.fontSize),weight:parseInt(cs.fontWeight),t:n.textContent.trim().slice(0,28)}); } } });
R.push({slide:i+1,lines}); });
const pre=document.createElement('pre');pre.id='m';pre.textContent=JSON.stringify(R);document.body.appendChild(pre)})</script>"""


def chrome_bin():
    hits = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    if not hits: sys.exit("Chromium not found")
    return hits[-1]


def run(*args):
    return subprocess.run([chrome_bin(), "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--virtual-time-budget=10000",
                           "--allow-file-access-from-files", *args], capture_output=True, text=True)


def lum(rgb):
    c = np.asarray(rgb, dtype=float) / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def parse_rgb(s):
    m = re.findall(r"[\d.]+", s)
    return [float(x) for x in m[:3]]


def main(post):
    post = pathlib.Path(post).resolve()
    spec = json.loads(post.read_text()); spec["_base"] = post.parent
    out = pathlib.Path("/tmp") / f"_legib_{spec['slug']}"
    out.mkdir(exist_ok=True)
    spec["_out"] = str(out)
    for sl in spec["slides"]:
        if sl.get("visual") and "image" in sl["visual"]:
            sl["visual"]["_base"] = post.parent; sl["visual"]["_out"] = str(out)
    bad_total = 0
    for i in range(len(spec["slides"])):
        page = out / f"s{i + 1}.html"
        page.write_text(build.page_html(spec, only=i, prep=True).replace("</body>", JS + "</body>"))
        dom = run("--dump-dom", page.as_uri()).stdout
        m = re.search(r'<pre id="m">(.*?)</pre>', dom, re.S)
        if not m: print(f"slide {i + 1}: could not measure"); continue
        lines = json.loads(html.unescape(m.group(1)))[0]["lines"]
        png = out / f"s{i + 1}.png"
        run("--window-size=1080,1400", "--force-device-scale-factor=1", f"--screenshot={png}", page.as_uri())
        img = np.asarray(Image.open(png).convert("RGB"))[:1080, :1080]
        worst = None; fails = []
        for ln in lines:
            x0, y0, x1, y1 = [int(round(v)) for v in (ln["x0"], ln["y0"], ln["x1"], ln["y1"])]
            x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(1080, x1), min(1080, y1)
            if x1 - x0 < 4 or y1 - y0 < 4: continue
            patch = img[y0:y1, x0:x1].reshape(-1, 3)
            bgl = lum(patch)
            bg_mean, bg_p10, bg_p90 = float(bgl.mean()), float(np.percentile(bgl, 10)), float(np.percentile(bgl, 90))
            tc = np.array(parse_rgb(ln["color"]))
            tl = float(lum(tc))
            # worst-case contrast against the part of the background that is least favourable for this colour
            ref = bg_p10 if tl < bg_mean else bg_p90
            cr = (max(tl, ref) + 0.05) / (min(tl, ref) + 0.05)
            large = ln["size"] >= 24 and ln["weight"] >= 600 or ln["size"] >= 36
            need = 3.0 if large else 4.5
            busy = float(np.percentile(bgl, 90) - np.percentile(bgl, 10))
            ok = cr >= need and busy <= 0.22
            if worst is None or cr < worst[0]: worst = (cr, ln["t"], busy)
            if not ok: fails.append((ln["t"], round(cr, 2), need, round(busy, 2), ln["size"]))
        smallest = min((l["size"] for l in lines), default=0)
        print(f"slide {i + 1}: {len(lines)} lines | smallest text {smallest:.0f}px (= {smallest * 400 / 1080:.1f}px on a 400px phone) | "
              f"worst contrast {worst[0]:.1f}:1 on '{worst[1]}' | {'OK' if not fails else 'FAIL ' + str(fails)}")
        bad_total += len(fails)
    print("legibility:", "all lines pass" if not bad_total else f"{bad_total} line(s) fail")
    return bad_total


if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    sys.exit(1 if main(sys.argv[1]) else 0)
