#!/usr/bin/env python3
"""Grade several photos so they read as ONE series: match mean saturation and brightness to a common target.

    python3 -I engine/photo_series.py out_dir in1.png in2.png ... [--sat 0.2] [--lum 0.62] [--warm 0.03]

Prints the before/after stats. Output files are out_dir/<name>.jpg (max 2160 px, quality 92).
"""
import argparse, pathlib, sys
import numpy as np
from PIL import Image

def stats(im):
    hsv = np.asarray(im.convert("HSV")).astype(float) / 255
    a = np.asarray(im).astype(float) / 255
    lum = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    return float(hsv[..., 1].mean()), float(lum.mean())

def grade(im, tsat, tlum, warm):
    cur = im
    for _ in range(4):                       # saturation and brightness interact, so converge in a few passes
        s0, l0 = stats(cur)
        hsv = np.asarray(cur.convert("HSV")).astype(float)
        hsv[..., 1] = np.clip(hsv[..., 1] * float(np.clip(tsat / max(s0, 1e-3), 0.6, 1.5)), 0, 255)
        out = np.asarray(Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB")).astype(float) / 255
        lum = 0.2126 * out[..., 0] + 0.7152 * out[..., 1] + 0.0722 * out[..., 2]
        g = float(np.clip(np.log(tlum) / np.log(max(lum.mean(), 1e-3)), 0.8, 1.25))
        cur = Image.fromarray((np.clip(out, 0, 1) ** g * 255).astype(np.uint8))
    a = np.asarray(cur).astype(float)
    a[..., 0] *= 1 + warm; a[..., 2] *= 1 - warm
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("files", nargs="+")
    ap.add_argument("--sat", type=float, default=None); ap.add_argument("--lum", type=float, default=None); ap.add_argument("--warm", type=float, default=0.03)
    a = ap.parse_args(); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ims = {f: Image.open(f).convert("RGB") for f in a.files}
    st = {f: stats(im) for f, im in ims.items()}
    tsat = a.sat if a.sat is not None else float(np.median([v[0] for v in st.values()]))
    tlum = a.lum if a.lum is not None else float(np.median([v[1] for v in st.values()]))
    print(f"target saturation {tsat:.3f}, brightness {tlum:.3f}")
    for f, im in ims.items():
        g = grade(im, tsat, tlum, a.warm); w, h = g.size; k = min(1, 2160 / max(w, h))
        if k < 1: g = g.resize((int(w * k), int(h * k)), Image.LANCZOS)
        dst = out / (pathlib.Path(f).stem + ".jpg"); g.save(dst, "JPEG", quality=92, optimize=True)
        s1, l1 = stats(g); print(f"{pathlib.Path(f).name}: sat {st[f][0]:.3f} -> {s1:.3f} | brightness {st[f][1]:.3f} -> {l1:.3f}")
