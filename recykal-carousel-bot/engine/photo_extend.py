#!/usr/bin/env python3
"""Place a photo smaller / shifted inside the square slide and fill the empty strips by extending the photo itself.

    python3 -I engine/photo_extend.py in.jpg out.jpg --zoom 0.85 [--shift-y -40] [--fade-bottom 160]

Used when the subject has to sit further to the right than the generated composition put it. The old way (shrink the photo and
cover the gap with white fades) made the tops, bottoms and edges of the photos look hazy and washed out. Here the photo is anchored
to the bottom-right corner, scaled by --zoom and moved by --shift-y (px on a 1080 slide, negative = up); the strips that are left
are filled with the nearest photo colours, blurred very heavily and feathered into the photo, so the slide stays edge to edge photography.
--fade-bottom N optionally dissolves the bottom N px (slide px) to white, for a photo that ends above the footer.
"""
import argparse, sys
import numpy as np
from PIL import Image, ImageFilter

SIZE = 2160      # 2x of the 1080 slide


def extend(src, dst, zoom=1.0, shift_y=0, fade_bottom=0, size=SIZE):
    im = Image.open(src).convert("RGB")
    w = int(round(size * zoom)); h = w
    small = im.resize((w, h), Image.LANCZOS)
    x0 = size - w; y0 = size - h + int(round(shift_y * 2))
    # crop the part of the scaled photo that is on the canvas
    cx0, cy0 = max(0, -x0), max(0, -y0)
    cx1, cy1 = min(w, size - x0), min(h, size - y0)
    vis = small.crop((cx0, cy0, cx1, cy1))
    px0, py0 = max(0, x0), max(0, y0)
    left, top = px0, py0
    right, bottom = size - (px0 + vis.width), size - (py0 + vis.height)
    arr = np.pad(np.asarray(vis), ((top, bottom), (left, right), (0, 0)), mode="edge")
    padded = Image.fromarray(arr)
    blurred = padded.filter(ImageFilter.GaussianBlur(170))     # very soft: reads as out-of-focus background, no streaks
    mask = Image.new("L", (size, size), 0)
    inset = 70                                              # feather the photo's own edge into the blurred extension
    box = [px0 + (inset if left else 0), py0 + (inset if top else 0),
           px0 + vis.width - (inset if right else 0), py0 + vis.height - (inset if bottom else 0)]
    from PIL import ImageDraw
    ImageDraw.Draw(mask).rectangle(box, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(40))
    out = Image.composite(padded, blurred, mask)
    if fade_bottom:
        a = np.asarray(out).astype(np.float32)
        n = int(fade_bottom * 2)
        ramp = np.clip((np.arange(size) - (size - n)) / n, 0, 1)[:, None, None]
        a = a * (1 - ramp) + 255 * ramp
        out = Image.fromarray(a.astype(np.uint8))
    out.save(dst, "JPEG", quality=93, optimize=True, subsampling=0)
    return dst


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--zoom", type=float, default=1.0)
    ap.add_argument("--shift-y", type=float, default=0)
    ap.add_argument("--fade-bottom", type=float, default=0)
    a = ap.parse_args()
    extend(a.src, a.dst, a.zoom, a.shift_y, a.fade_bottom)
    print(a.dst)
