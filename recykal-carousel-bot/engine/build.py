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
    return re.sub(r"\*\*(.+?)\*\*", lambda m: f'<span class="{cls}">{m.group(1)}</span>', esc(s), flags=re.S).replace("\n", "<br>")

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
        st = []
        if v.get("position"): st.append(f'object-position:{v["position"]}')
        if v.get("zoom") or v.get("shift_x") or v.get("shift_y"):      # pan / zoom a full-bleed photo (kind "bg")
            st.append(f'transform:translate({v.get("shift_x", 0)}px,{v.get("shift_y", 0)}px) scale({v.get("zoom", 1)});transform-origin:{v.get("origin", "50% 50%")}')
        if v.get("shift_y"):   # panned up: let the photo's bottom edge dissolve instead of ending hard
            m = "linear-gradient(180deg,#000 0,#000 calc(100% - 120px),transparent 100%)"
            st.append(f"-webkit-mask-image:{m};mask-image:{m}")
        pos = f' style="{";".join(st)}"' if st else ""
        return v.get("kind", "card"), f'<img src="{path.as_uri()}" alt=""{pos}>'
    return S.render(v)

def render_slide(i, n, s, footer, logo_uri, progress=False):
    v = s.get("visual")
    kind, inner = (None, "")
    if v:
        kind, inner = visual_html(v)
    layout = {"tall": "cover", "card": "split", "col": "split", "wide": "statement", "band": "journey", "top": "etop", "bottom": "ebottom", "bg": "bgphoto", None: "text"}[kind]
    hsize = s.get("heading_size")
    hcls = "h2" if layout == "split" else "h1"
    hstyle = f' style="font-size:{hsize}px"' if hsize else ""
    bs = []
    if s.get("body_size"): bs.append(f'font-size:{s["body_size"]}px')
    if s.get("text_width"): bs.append(f'max-width:{s["text_width"]}px')       # bg-photo layout: keep copy clear of the photo subject
    bstyle = f' style="{";".join(bs)}"' if bs else ""
    sstyle = f' style="width:{s["text_width"]}px"' if s.get("text_width") else ""
    vstyle = ""
    if s.get("veil_end"):        # where the white fade behind the copy ends (% of width); narrower = more of the photo stays clear
        e = float(s["veil_end"]); stops = [(0, 1), (.2 * e, .99), (.4 * e, .95), (.55 * e, .82), (.7 * e, .55), (.85 * e, .24), (e, 0)]
        g = ",".join(f"rgba(255,255,255,{a}) {x:.0f}%" for x, a in stops)
        vstyle = f' style="background:linear-gradient(90deg,{g}),linear-gradient(180deg,rgba(255,255,255,.75) 0,rgba(255,255,255,0) 190px)"'
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
    if kind == "col" and callout:
        print(f"  note: slide {i}: tall-card scenes ('{(v or {}).get('scene')}') have no callout box; callout skipped", file=sys.stderr)
        callout = ""
    nobox = " nobox" if layout == "split" and not callout else ""
    nobox += " span" if s.get("heading_span") and layout == "split" else ""
    if layout in ("cover", "split"):
        top = " top" if s.get("align") == "top" and layout == "split" else ""
        if s.get("heading_span") and layout == "split":     # headline across the full width, text + visual below it
            inner = inner.replace('viewBox="0 0 390 536"', 'viewBox="0 84 390 368"')   # crop empty margins so the visual fills the shorter panel
            main = f'<div class="hd">{heading}<div class="rule"></div></div><div class="col">{body}</div><div class="illus">{inner}</div>'
        else:
            main = f'<div class="col{top}">{heading}{rule}{body}</div><div class="illus">{inner}</div>'
    elif layout in ("etop", "ebottom"):       # photo-led editorial layouts: full-bleed photo, copy on white above/below it
        ph = int((v or {}).get("height", 520)) if layout == "etop" else None   # optional shorter photo on "top" slides
        sty_i = f' style="height:{ph}px"' if ph else ""
        sty_s = f' style="top:{ph + 40}px"' if ph else ""
        main = f'<div class="illus"{sty_i}>{inner}</div><div class="stack"{sty_s}>{heading}{rule}{body}</div>'
    elif layout == "bgphoto":       # realistic full-bleed photo as the base layer, copy on a white veil, DRS green callout
        main = f'<div class="bgimg">{inner}</div><div class="veil"{vstyle}></div><div class="veil2"></div><div class="stack"{sstyle}>{heading}{rule}{body}</div>'
    elif layout == "journey":
        rule_j = '<div class="rule"></div>' if heading else ""
        main = f'<div class="stack">{heading}{rule_j}</div><div class="illus">{inner}</div>' + (f'<div class="jbody">{body}</div>' if body else "")
    elif layout == "statement":
        main = f'<div class="stack">{heading}{rule}<div class="illus">{inner}</div></div>'
        if body:  # statement slides carry heading + visual (+ callout); body text would not fit
            print(f"  note: slide {i}: body text ignored on wide-scene slides (use the callout)", file=sys.stderr)
    else:
        main = f'<div class="stack">{heading}{rule}{body}</div>'
    last = i == n
    dots = ""
    if progress:
        dots = '<div class="dots' + (" last" if last else "") + '">' + "".join(f'<span class="{"on" if k + 1 == i else ""}"></span>' for k in range(n)) + "</div>"
    return (f'<section class="slide layout-{layout}{nobox}" data-layout="{layout}">'
            f'<img class="logo" src="{logo_uri}" alt="Recykal – Sustainable Circularity">'
            f'{main}{callout}<div class="url">{esc(footer)}</div>{dots}'
            f'{"" if last else f"<div class=next>{ARROW}</div>"}<div class="bar"></div></section>')


QA_JS = r"""
(function(){
  const rect=(el,s)=>{const a=el.getBoundingClientRect(),b=s.getBoundingClientRect();return{l:a.left-b.left,t:a.top-b.top,r:a.right-b.left,b:a.bottom-b.top,h:a.height}};
  const fs=el=>parseFloat(getComputedStyle(el).fontSize);
  function viol(s){
    const v=[], col=s.querySelector('.col,.stack'), box=s.querySelector('.box'), hd=s.querySelector('.hd');
    if(hd){ const b=rect(hd,s).b; if(b>318) v.push({k:'text-bottom',px:Math.round(b-318)}); }
    if(s.dataset.layout==='journey'){
      const st=s.querySelector('.stack'), jb=s.querySelector('.jbody');
      if(st){ const b=rect(st,s).b; if(b>372) v.push({k:'text-bottom',px:Math.round(b-372)}); }
      if(jb){ const lim=box?rect(box,s).t-16:930, b=rect(jb,s).b; if(b>lim) v.push({k:'text-bottom',px:Math.round(b-lim)}); }
      if(box){ const p=box.querySelector('p'), ph=p.getBoundingClientRect().height, lh=parseFloat(getComputedStyle(p).lineHeight);
        if(ph>box.clientHeight-24) v.push({k:'box-text',px:1}); else if(ph/lh>2.5 && fs(p)>22) v.push({k:'box-lines',px:0}); }
      const hj=s.querySelector('.h1'); if(hj && hj.scrollWidth>hj.clientWidth+1) v.push({k:'text-wide',px:1});
      return v;
    }
    const limit = s.dataset.layout==='ebottom' ? 548 : (box ? rect(box,s).t-22 : 930);
    const fixed = col && getComputedStyle(col).display==='flex';
    if(fixed){ const ch=[...col.children]; if(ch.length){ const H=ch[ch.length-1].getBoundingClientRect().bottom-ch[0].getBoundingClientRect().top; if(H>col.clientHeight+1) v.push({k:'text-bottom',px:Math.round(H-col.clientHeight)}); } }
    else if(col){ const c=rect(col,s);
      if(c.b>limit) v.push({k:'text-bottom',px:Math.round(c.b-limit)});
      if(c.t<150) v.push({k:'text-top',px:Math.round(150-c.t)}); }
    const hh=s.querySelector('.h1,.h2'); if(hh && hh.scrollWidth>hh.clientWidth+1) v.push({k:'text-wide',px:hh.scrollWidth-hh.clientWidth});
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
    body = "\n".join(render_slide(i + 1, len(slides), s, footer, logo, bool(spec.get("progress"))) for i, s in enumerate(slides))
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
    if not ((1 if spec.get("draft") else 2) <= len(sl) <= 12): errs.append(f"need 2-12 slides, got {len(sl)}")
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
    rat = spec_path.parent / "rationale.json"
    if rat.exists():       # keep the design-rationale PDF in step with the slides
        subprocess.run([sys.executable, "-I", str(ROOT / "rationale.py"), str(rat)], check=True, capture_output=True)
        print(f"  + design rationale PDF")
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
            "ring": {"scene": "ring", "nodes": ["factory", "people", "truck", "recycle"]},
            "ring_card (consumer missing)": {"scene": "ring_card", "nodes": ["factory", {"icon": "people", "state": "lost"}, "truck", "recycle"]},
            "track": {"scene": "track", "nodes": ["factory", {"icon": "people", "state": "go"}, "truck", "recycle"]},
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
