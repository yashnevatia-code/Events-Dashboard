#!/usr/bin/env python3
"""Measure the vertical spacing of every slide in a built post, so white space is judged by numbers, not by eye.

    python3 -I engine/measure.py dist/<slug>/index.html

Prints, per slide: where the logo block ends, where the text block starts and ends, the gap above and below it
(to the callout box, or to the footer when there is no box), and the gaps between headline, rule and body paragraphs.
The agreed standard is in .claude/skills/recykal-carousel/SKILL.md (headline top 202, heading->rule 30, rule->body 28,
paragraph gap 26, callout box top 782).
"""
import glob, html, json, pathlib, re, subprocess, sys

JS = """<script>document.fonts.ready.then(()=>{const R=[];document.querySelectorAll('.slide').forEach((s,i)=>{
const b=s.getBoundingClientRect();
const q=(sel)=>{const e=s.querySelector(sel);if(!e)return null;const r=e.getBoundingClientRect();return [Math.round(r.top-b.top),Math.round(r.bottom-b.top),Math.round(r.left-b.left),Math.round(r.right-b.left)]};
const st=s.querySelector('.stack,.col');
const kids=st?[...st.children].map(c=>{const r=c.getBoundingClientRect();return [c.className||c.tagName,Math.round(r.top-b.top),Math.round(r.bottom-b.top)]}):[];
const paras=[...s.querySelectorAll('.body p')].map(p=>{const r=p.getBoundingClientRect();return [Math.round(r.top-b.top),Math.round(r.bottom-b.top)]});
R.push({slide:i+1,kids,paras,box:q('.box')})});
const pre=document.createElement('pre');pre.id='m';pre.textContent=JSON.stringify(R);document.body.appendChild(pre)})</script>"""

LOGO_BOTTOM = 134      # the template's logo block ends at y=134
FOOTER_TOP = 987       # the template's footer text starts at y=987


def chrome_bin():
    hits = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"))
    if not hits:
        sys.exit("Chromium not found under /opt/pw-browsers")
    return hits[-1]


def main(path):
    src = pathlib.Path(path).resolve()
    tmp = src.parent / "_measure.html"
    tmp.write_text(src.read_text().replace("</body>", JS + "</body>"))
    try:
        dom = subprocess.run([chrome_bin(), "--headless", "--no-sandbox", "--disable-gpu", "--virtual-time-budget=8000",
                              "--allow-file-access-from-files", "--dump-dom", tmp.as_uri()],
                             capture_output=True, text=True).stdout
    finally:
        tmp.unlink(missing_ok=True)
    m = re.search(r'<pre id="m">(.*?)</pre>', dom, re.S)
    if not m:
        sys.exit("measurement failed (no output from the page)")
    for r in json.loads(html.unescape(m.group(1))):
        kids = r["kids"]
        if not kids:
            print(f"slide {r['slide']}: no text block"); continue
        top, bot = kids[0][1], kids[-1][2]
        below = (f"box_top {r['box'][0]}  gap text->box {r['box'][0] - bot}" if r["box"]
                 else f"gap text->footer {FOOTER_TOP - bot}")
        line = f"slide {r['slide']}: text {top}-{bot} (h {bot - top}) | gap logo->text {top - LOGO_BOTTOM} | {below}"
        if len(kids) > 2:
            line += f" | heading->rule {kids[1][1] - kids[0][2]} | rule->body {kids[2][1] - kids[1][2]}"
        gaps = [r["paras"][i + 1][0] - r["paras"][i][1] for i in range(len(r["paras"]) - 1)]
        if gaps:
            line += f" | paragraph gaps {gaps}"
        print(line)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
