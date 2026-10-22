# Recykal carousel bot

Give it content slide by slide; it returns a LinkedIn-ready carousel in the Recykal design system:

* `dist/<slug>/<slug>-linkedin-carousel.pdf`  (upload as a LinkedIn *document* post)
* `dist/<slug>/slide-1.png … slide-N.png`      (1080×1080)
* `dist/<slug>/caption.txt`                    (post text + hashtags)
* `dist/<slug>/qa.json`                        (what the auto-fit did)

## Use it from Claude Code

Open this repo and just paste the slide content ("slide 1: … slide 2: …"), or invoke the skill: `/recykal-carousel`.
The skill (`.claude/skills/recykal-carousel/SKILL.md`) tells Claude how to pick visuals, write the spec, build, review and deliver.

## Use it by hand

```bash
python3 engine/build.py posts/drs-knowing-vs-doing/post.json   # one post
python3 engine/build.py --all                                  # every post in posts/
python3 engine/build.py --library                              # catalogue of objects, icons, scenes -> dist/_library.png
```

Requirements: Python 3, Chromium (found under `$PLAYWRIGHT_BROWSERS_PATH`, or set `CHROME=/path/to/chrome`) and `pdftoppm` (poppler-utils).
Fonts and the logo are vendored in `engine/assets`, so builds work offline and look identical everywhere.

## How it fits together

```
posts/<slug>/post.json      content + visuals for each slide (the only thing you write)
engine/build.py             spec -> HTML -> PDF + PNGs + caption, with layout QA and text auto-fit
engine/theme.css            the design system (type scale, colours, layouts, footer)
engine/scenes.py            illustration compositions: gap, hero, fork, loop, steps, stat, ring, ring_card, pathway, compare, bridge, flow, track, trail, converge, lanes, circuit (journey bands)
engine/library.py           objects (bottle, can, machine, coin ...) and line icons
engine/assets/              Poppins + logo
```

A slide's visual decides its layout: **tall** scene → cover layout, **card** scene → split layout with callout box, **wide** scene → statement layout, no visual → text layout.
See `.claude/skills/recykal-carousel/SKILL.md` for the full spec reference and scene table.

## Extending

* New icon / object: add it to `engine/library.py`, run `--library`, look at the sheet.
* New scene: add a function to `engine/scenes.py` with `@scene("tall"|"card"|"wide")`; it is picked up automatically.
* Tweak the look (spacing, sizes): `engine/theme.css`. Change it once and every post built afterwards follows. Rebuild old posts with `--all`.

## Photography-led carousels

The default visual direction is realistic photography generated with OpenArt (see `.claude/skills/recykal-carousel/SKILL.md`, section *Visual direction*). Image slots: `kind` top / bottom / tall / card (`visual.image`, optional `visual.position`). Vector scenes are still available for when they are asked for. Downloading generated images needs `cdn.openart.ai` to be reachable.

## Known limits

* Vector scenes are available but photography is the default; see above.
* The logo block, `www.recykal.com` footer and bottom bar come from the official Recykal social template, `engine/assets/template.svg` (1080x1080, 50 px margin). The engine inlines it on every slide; replace that file if the template changes. `engine/assets/logo.svg` is no longer used by the slides.

## PDF export notes

Photo slides (`"kind": "bg"`) are flattened for the PDF: the photo, white fade, ground shadow and callout shadow are rendered by Chromium at 2x into one 2160 px JPEG per slide, and only the text, logo block and callout stay vector on top. CSS masks, filters and blurred shadows otherwise turn into stacks of transparency groups that browser PDF viewers (Edge, Chrome) draw slowly and at low resolution, which showed up as soft, pixelated or blank pages. Check with `pdfimages -list <pdf>`: one 2160 px image per photo page and no `smask` entries is correct. Needs Pillow.
