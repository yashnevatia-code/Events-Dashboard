#!/usr/bin/env bash
# Rebuild PDF + PNG slides from carousel.html (needs Chromium + poppler-utils)
set -euo pipefail
cd "$(dirname "$0")"
CH="${CHROME:-$(ls /opt/pw-browsers/chromium-*/chrome-linux/chrome | head -1)}"
"$CH" --headless --no-sandbox --disable-gpu --virtual-time-budget=10000 --no-pdf-header-footer \
  --print-to-pdf=recykal-drs-knowing-vs-doing-linkedin-carousel.pdf "file://$PWD/carousel.html"
rm -f slide-*.png
pdftoppm -r 96 -png recykal-drs-knowing-vs-doing-linkedin-carousel.pdf slide   # 810pt @96dpi = 1080px
