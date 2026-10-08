#!/usr/bin/env python3
"""Recykal LinkedIn carousel builder.

    python3 engine/build.py posts/<slug>/post.json     build one post  -> dist/<slug>/
    python3 engine/build.py --all                       build every post in posts/
    python3 engine/build.py --library                   render the icon/object/scene catalogue -> dist/_library.png

Outputs (dist/<slug>/):  <slug>-linkedin-carousel.pdf  slide-N.png (1080x1080)  caption.txt  qa.json  index.html
Needs: Chromium (PLAYWRIGHT_BROWSERS_PATH or CHROME env var) and poppler-utils (pdftoppm).
"""
import argparse, glob, html, json, os, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import library as L          # noqa: E402
import scenes as S           # noqa: E402

REPO = ROOT.parent
ASSETS = ROOT / "assets"
ARROW = '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'


# ───────────────────────────── text helpers ─────────────────────────────
def esc(s): return html.escape(str(s), quote=False)

def emph(s, cls):
    """escape, then turn **phrase** into a green highlight span."""
    return re.sub(r"\*\*(.+?)\*\*", lambda m: f'<span class="{cls}">{m.group(1)}</span>', esc(s))

def paras(body):
    if not body: return []
    return [body] if isinstance(body, str) else list(body)


# ───────────────────────────── slide rendering ─────────────────────────────
def callout_html(c):
    style = c.get("style", "line")
    ic = L.icon(c.get("icon", "arrow"), 32, 32, size=34, sw=3.4, color=("#fff" if style == "line" else L.G))
    size = c.get("size")
    fs = size or 25      # the page script shrinks it (min 22) if it would run to 3 lines
    return (f'<div class="box {style}"><div class="ico"><svg width="64" height="64" viewBox="0 0 64 64">{ic}</svg></div>'
            f'<p style="font-size:{fs}px">{emph(c["text"], "g")}</p></div>')

def visual_html(v):
    """-> (kind, inner html). v is {"scene": ...} or {"image": path, "kind": "card|tall"}."""
    if "image" in v:
        path = pathlib.Path(v["image"])
        if not path.is_absolute():
            path = (v.get("_base") or pathlib.Path.cwd()) / path
        if not path.exists():
            raise FileNotFoundError(f"image not found: {path}")
        return v.get("kind", "card"), f'<img src="{path.as_uri()}" alt="">'
    return S.render(v)

def render_slide(i, n, s, footer, logo_uri):
    v = s.get("visual")
    kind, inner = (None, "")
    if v:
        kind, inner = visual_html(v)
    layout = {"tall": "cover", "card": "split", "wide": "statement", None: "text"}[kind]
    hsize = s.get("heading_size")
    hcls = "h2" if layout == "split" else "h1"
    hstyle = f' style="font-size:{hsize}px"' if hsize else ""
    bstyle = f' style="font-size:{s["body_size"]}px"' if s.get("body_size") else ""
    heading = f'<h1 class="{hcls}"{hstyle}>{emph(s["heading"], "g")}</h1>' if s.get("heading") else ""
    body = ""
    if s.get("body"):
        body += f'<div class="body"{bstyle}>' + "".join(f"<p>{emph(t, 'g sb')}</p>" for t in paras(s["body"])) + "</div>"
    if s.get("bullets"):
        body += '<ul class="bul"' + bstyle + '>' + "".join(f"<li>{emph(t, 'g sb')}</li>" for t in s["bullets"]) + "</ul>"
    rule = '<div class="rule"></div>' if heading and (body or layout == "statement") else ""
    callout = callout_html(s["callout"]) if s.get("callout") and layout != "cover" else ""
    if layout == "cover" and s.get("callout"):
        print(f"  note: slide {i}: cover-style slides (tall scene) have no callout box; callout skipped", file=sys.stderr)
    nobox = " nobox" if layout == "split" and not callout else ""
    if layout in ("cover", "split"):
        main = f'<div class="col">{heading}{rule}{body}</div><div class="illus">{inner}</div>'
    elif layout == "statement":
        main = f'<div class="stack">{heading}{rule}<div class="illus">{inner}</div></div>'
        if body:  # statement slides carry heading + visual (+ callout); body text would not fit
            print(f"  note: slide {i}: body text ignored on wide-scene slides (use the callout)", file=sys.stderr)
    else:
        main = f'<div class="stack">{heading}{rule}{body}</div>'
    last = i == n
    return (f'<section class="slide layout-{layout}{nobox}" data-layout="{layout}">'
            f'<img class="logo" src="{logo_uri}" alt="Recykal – Sustainable Circularity">'
            f'{main}{callout}<div class="url">{esc(footer)}</div>'
            f'{"" if last else f"<div class=next>{ARROW}</div>"}<div class="bar"></div></section>')


QA_JS = r"""
(function(){
  const rect=(el,s)=>{const a=el.getBoundingClientRect(),b=s.getBoundingClientRect();return{l:a.left-b.left,t:a.top-b.top,r:a.right-b.left,b:a.bottom-b.top,h:a.height}};
  const fs=el=>parseFloat(getComputedStyle(el).fontSize);
  function viol(s){
    const v=[], col=s.querySelector('.col,.stack'), box=s.querySelector('.box');
    const limit = box ? rect(box,s).t-22 : 930;
    if(col){ const c=rect(col,s);
      if(c.b>limit) v.push({k:'text-bottom',px:Math.round(c.b-limit)});
      if(c.t<150) v.push({k:'text-top',px:Math.round(150-c.t)}); }
    if(box){ const p=box.querySelector('p'), ph=p.getBoundingClientRect().height, lh=parseFloat(getComputedStyle(p).lineHeight);
      if(ph>box.clientHeight-24) v.push({k:'box-text',px:Math.round(ph-box.clientHeight+24)});
      else if(ph/lh>2.5 && fs(p)>22) v.push({k:'box-lines',px:0}); }
    return v;
  }
  function shrink(el,min,step){ if(!el) return false; const f=fs(el); if(f<=min) return false; el.style.fontSize=(f-step)+'px'; return true; }
  document.fonts.ready.then(()=>{
    const report=[];
    document.querySelectorAll('.slide').forEach((s,i)=>{
      let g=0;
      while(g++<60){
        const v=viol(s); if(!v.length) break; let ch=false;
        for(const x of v){
          if(x.k==='box-text'||x.k==='box-lines') ch=shrink(s.querySelector('.box p'),20,.5)||ch;
          else { const h=s.querySelector('.h1,.h2'); ch=(h&&shrink(h,h.classList.contains('h1')?40:28,1))||shrink(s.querySelector('.body,.bul'),19,.5)||ch; }
        }
        if(!ch) break;
      }
      const h=s.querySelector('.h1,.h2'), b=s.querySelector('.body,.bul'), p=s.querySelector('.box p');
      report.push({slide:i+1,layout:s.dataset.layout,heading_px:h?+fs(h).toFixed(1):null,body_px:b?+fs(b).toFixed(1):null,
        heading_lines:h?Math.round(h.getBoundingClientRect().height/parseFloat(getComputedStyle(h).lineHeight)):0,
        callout_px:p?+fs(p).toFixed(1):null,callout_lines:p?Math.round(p.getBoundingClientRect().height/parseFloat(getComputedStyle(p).lineHeight)):0,
        problems:viol(s)});
    });
    const pre=document.createElement('pre'); pre.id='qa-out'; pre.textContent=JSON.stringify(report); document.body.appendChild(pre);
  });
})();
"""


def page_html(spec):
    fonts_css = (ASSETS / "fonts.css").read_text().replace("url('fonts/", f"url('{(ASSETS / 'fonts').as_uri()}/")
    css = (ROOT / "theme.css").read_text()
    logo = (ASSETS / "logo.svg").as_uri()
    footer = spec.get("footer", "www.recykal.com")
    slides = spec["slides"]
    base = spec.get("_base")
    for sl in slides:
        if sl.get("visual") and "image" in sl["visual"]:
            sl["visual"]["_base"] = base
    body = "\n".join(render_slide(i + 1, len(slides), s, footer, logo) for i, s in enumerate(slides))
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(spec.get("title", spec["slug"]))}</title>'
            f'<style>{fonts_css}\n{css}</style></head><body>{L.DEFS}\n{body}\n<script>{QA_JS}</script></body></html>')


# ───────────────────────────── chrome / pdf / png ─────────────────────────────
def chrome_bin():
    if os.environ.get("CHROME"): return os.environ["CHROME"]
    for pat in (os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers") + "/chromium-*/chrome-linux*/chrome",):
        hits = sorted(glob.glob(pat))
        if hits: return hits[-1]
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        if shutil.which(name): return shutil.which(name)
    sys.exit("Chromium not found: set CHROME=/path/to/chrome")

def chrome(*args):
    return subprocess.run([chrome_bin(), "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                           "--virtual-time-budget=12000", "--allow-file-access-from-files", *args],
                          capture_output=True, text=True)


def validate(spec):
    errs = []
    if not spec.get("slug"): errs.append("missing 'slug'")
    sl = spec.get("slides") or []
    if not (2 <= len(sl) <= 12): errs.append(f"need 2-12 slides, got {len(sl)}")
    for i, s in enumerate(sl, 1):
        if not (s.get("heading") or s.get("body") or s.get("bullets")): errs.append(f"slide {i}: no text")
        if s.get("callout") and not s["callout"].get("text"): errs.append(f"slide {i}: callout needs text")
        v = s.get("visual")
        if v and "scene" in v and v["scene"] not in S.SCENES: errs.append(f"slide {i}: unknown scene '{v['scene']}'")
    cap = spec.get("caption", "")
    if len(cap) > 2900: errs.append("caption over LinkedIn's 3000-character limit")
    return errs


def build(spec_path):
    spec_path = pathlib.Path(spec_path).resolve()
    spec = json.loads(spec_path.read_text())
    spec["_base"] = spec_path.parent
    errs = validate(spec)
    if errs: sys.exit("spec errors:\n  " + "\n  ".join(errs))
    slug = spec["slug"]
    out = REPO / "dist" / slug
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)

    page = out / "index.html"
    page.write_text(page_html(spec))
    uri = page.as_uri()

    dom = chrome("--dump-dom", uri).stdout
    m = re.search(r'<pre id="qa-out">(.*?)</pre>', dom, re.S)
    qa = json.loads(html.unescape(m.group(1))) if m else []
    (out / "qa.json").write_text(json.dumps(qa, indent=1))

    pdf = out / f"{slug}-linkedin-carousel.pdf"
    chrome("--no-pdf-header-footer", f"--print-to-pdf={pdf}", uri)
    if not pdf.exists(): sys.exit("PDF export failed")
    subprocess.run(["pdftoppm", "-r", "96", "-png", str(pdf), str(out / "slide")], check=True)
    for p in out.glob("slide-*.png"):                       # slide-1.png (not slide-01.png)
        n = int(p.stem.split("-")[1]); p.rename(out / f"slide-{n}.png")

    cap = (spec.get("caption", "").strip() + "\n\n" + " ".join(spec.get("hashtags", []))).strip()
    (out / "caption.txt").write_text(cap + "\n")

    bad = [r for r in qa if [x for x in r["problems"] if x["k"] != "box-lines"] or r["heading_lines"] > 6 or r["callout_lines"] > 3]
    print(f"built {out.relative_to(REPO)}  ({len(spec['slides'])} slides)")
    for r in qa:
        flag = "  <-- CHECK" if r in bad else ""
        print(f"  slide {r['slide']}: {r['layout']:<9} heading {r['heading_px']}px/{r['heading_lines']}L  body {r['body_px']}px  callout {r['callout_px']}px/{r['callout_lines']}L{flag}")
        for pr in [x for x in r["problems"] if x["k"] != "box-lines"]: print(f"      ! {pr['k']} still over by {pr['px']}px after auto-shrink: shorten the copy")
    if len(spec.get("hashtags", [])) > 8: print("  note: more than 8 hashtags; LinkedIn favours 3-5")
    return out


def library_sheet():
    """Catalogue of every object, icon and scene (for choosing what to draw)."""
    cells = ['<div class="cat">']
    cells.append("<h2>Objects</h2><div class='row'>" + "".join(
        f'<figure><svg viewBox="0 0 120 220" width="120" height="220">{L.fit(n, 5, 10, 110, 200)}</svg><figcaption>{n}</figcaption></figure>' for n in L.OBJECTS) + "</div>")
    cells.append("<h2>Icons</h2><div class='row'>" + "".join(
        f'<figure><svg viewBox="0 0 90 90" width="90" height="90"><circle cx="45" cy="45" r="40" fill="#EAF6F0"/>{L.icon(n, 45, 45, size=46, sw=3.2)}</svg><figcaption>{n}</figcaption></figure>' for n in L.ICONS) + "</div>")
    demo = {"gap": {"scene": "gap"}, "hero": {"scene": "hero", "object": "can", "badges": ["leaf", "rupee", "people"]},
            "fork": {"scene": "fork", "options": [{"icon": "home"}, {"icon": "machine", "state": "go"}, {"icon": "bin"}, {"icon": "landfill", "state": "lost"}]},
            "loop": {"scene": "loop", "nodes": ["bottle", "machine", "coin"]},
            "steps": {"scene": "steps", "steps": ["bottle", "truck", "factory", "recycle"]},
            "stat": {"scene": "stat", "value": 72, "caption": "of packaging is never recovered", "icon": "recycle"},
            "bridge": {"scene": "bridge"}, "flow": {"scene": "flow", "steps": ["bottle", "machine", "coin", "recycle"]}}
    cells.append("<h2>Scenes</h2><div class='row'>" + "".join(
        f'<figure class="sc"><div class="illus-demo">{S.render(v)[1]}</div><figcaption>{k}</figcaption></figure>' for k, v in demo.items()) + "</div></div>")
    css = ("body{font-family:Poppins,sans-serif;margin:24px;width:1500px}h2{margin:18px 0 8px}.row{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-end}"
           "figure{text-align:center;font-size:13px}.sc svg{background:#EAF6F0;border-radius:18px}")
    fonts_css = (ASSETS / "fonts.css").read_text().replace("url('fonts/", f"url('{(ASSETS / 'fonts').as_uri()}/")
    out = REPO / "dist"; out.mkdir(exist_ok=True)
    page = out / "_library.html"
    page.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{fonts_css}{css}</style></head><body>{L.DEFS}{''.join(cells)}</body></html>")
    chrome("--window-size=1560,3500", f"--screenshot={out / '_library.png'}", page.as_uri())
    print("wrote dist/_library.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--library", action="store_true")
    a = ap.parse_args()
    if a.library: library_sheet()
    elif a.all:
        for f in sorted(glob.glob(str(REPO / "posts" / "*" / "post.json"))): build(f)
    elif a.spec: build(a.spec)
    else: ap.print_help()
