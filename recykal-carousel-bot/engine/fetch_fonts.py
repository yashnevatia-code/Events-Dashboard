#!/usr/bin/env python3
"""One-off: vendor Poppins (400-800; latin, latin-ext, devanagari for the rupee sign) into assets/fonts."""
import re, subprocess, pathlib

OUT = pathlib.Path(__file__).parent / "assets" / "fonts"
URL = "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def curl(*args):
    return subprocess.run(["curl", "-fsS", "-m", "60", *args], check=True, capture_output=True).stdout

css = curl("-A", UA, URL).decode()
out = []
for block in re.finditer(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S):
    subset, body = block.groups()
    if subset not in ("latin", "latin-ext", "devanagari"):
        continue
    weight = re.search(r"font-weight:\s*(\d+)", body).group(1)
    url = re.search(r"url\((https://[^)]+)\)", body).group(1)
    rng = re.search(r"unicode-range:\s*([^;]+);", body).group(1)
    name = f"poppins-{weight}-{subset}.woff2"
    (OUT / name).write_bytes(curl(url))
    out.append(f"@font-face{{font-family:'Poppins';font-style:normal;font-weight:{weight};font-display:block;"
               f"src:url('fonts/{name}') format('woff2');unicode-range:{rng}}}")
(OUT.parent / "fonts.css").write_text("\n".join(out) + "\n")
print(f"{len(out)} font faces written")
