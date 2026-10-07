#!/usr/bin/env bash
# Downloads the 4 AI-generated slide images (OpenArt, Nano Banana 2.1) into assets/
set -euo pipefail
cd "$(dirname "$0")/assets"
B=https://cdn.openart.ai/openart-ai/production/2026-10/create-image/cuGEg6oynx5k0Obrocis
curl -fsS -o gen-1.png $B/image_1791370871045_3b9c6721_1791370871643_f75a9c8a.png   # slide 1: knowing vs doing
curl -fsS -o gen-2.png $B/image_1791370875400_0ca153ba_1791370876344_3bd573f4.png   # slide 2: forgotten bottle
curl -fsS -o gen-3.png $B/image_1791370881371_0aebcbd2_1791370881917_59fcd2c2.png   # slide 3: return point
curl -fsS -o gen-4.png $B/image_1791370882853_b319abb0_1791370883639_875035fa.png   # slide 4: wide scene
