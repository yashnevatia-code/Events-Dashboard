#!/usr/bin/env python3
"""Prepare a generated photo for a carousel: mild, consistent colour grade + sensible file size.

    python3 engine/photo_prepare.py in.png out.jpg [--sat 0.9] [--warm 0] [--contrast 1.0] [--max 2400]

--sat   colour saturation multiplier (<1 mutes)       --warm  white-balance shift: negative = cooler, positive = warmer (-10..10)
Use small values only: the aim is for all images in a carousel to feel like one series, not a filter look.
"""
import argparse
from PIL import Image, ImageEnhance

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--sat", type=float, default=0.92)
ap.add_argument("--warm", type=float, default=0)
ap.add_argument("--contrast", type=float, default=1.0)
ap.add_argument("--max", type=int, default=2400)
a = ap.parse_args()

im = Image.open(a.src).convert("RGB")
if max(im.size) > a.max:
    k = a.max / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(a.sat)
im = ImageEnhance.Contrast(im).enhance(a.contrast)
if a.warm:
    r, g, b = im.split()
    w = a.warm / 100
    r = r.point(lambda v: max(0, min(255, v * (1 + w)))); b = b.point(lambda v: max(0, min(255, v * (1 - w))))
    im = Image.merge("RGB", (r, g, b))
im.save(a.dst, quality=90, optimize=True)
print(a.dst, im.size)
