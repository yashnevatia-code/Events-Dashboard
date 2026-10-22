---
name: recykal-carousel
description: Builds a Recykal LinkedIn carousel (1080x1080 slides as a PDF + PNGs + caption) in the Recykal social design system from slide-by-slide copy. Use whenever the user gives content for a Recykal / LinkedIn / Instagram carousel or post ("make a post for this copy", "here is slide 1...", "same template as the DRS post"), or asks to edit a post already built.
---

# Recykal carousel bot

Turns the user's slide-by-slide copy into a finished carousel using the engine in `recykal-carousel-bot/`
(Poppins, DRS green `#049769`, logo top-left, footer + arrow, original illustrations per slide).
The first post, `posts/drs-knowing-vs-doing/post.json`, is the reference for tone, layout and visuals. Read it before building a new one.

## Workflow

1. **Read the copy.** Keep the user's words exactly. Do not rewrite, shorten or "improve" it. If something cannot fit, say so and offer a trimmed version instead of silently editing.
2. **Plan each slide**: pick a `scene` from the idea the slide expresses (table below). Slides should *flow*: reuse the same objects/icons across slides and let a later visual answer an earlier one (e.g. slide 1 shows a gap, the last slide bridges it; or a circle of stakeholders that is broken on slide 2 and complete on slide 4).
3. **Write `recykal-carousel-bot/posts/<slug>/post.json`** (format below). Pick `slug` as short-kebab-case.
4. **Build**: `python3 -I recykal-carousel-bot/engine/build.py recykal-carousel-bot/posts/<slug>/post.json`
   Output goes to `recykal-carousel-bot/dist/<slug>/`. The console prints per-slide QA; any `<-- CHECK` line means text still overflows after auto-shrink: fix it (shorter callout text is the user's call; you can lower `heading_size`/`body_size` or split the slide).
5. **Look at it.** Make a contact sheet (`montage dist/<slug>/slide-*.png -tile 4x1 -geometry 500x500+4+4 sheet.png`) and Read it, then zoom into anything small (icons, text). Check: no clipped/overlapping elements, highlights on sensible phrases, icons recognisable, visuals match the slide's meaning, white space feels balanced (not empty, not crowded).
6. **Caption**: if the user did not supply one, write it into the spec (`caption`, `hashtags`): hook line, 2-4 short paragraphs built only from the slide content, a line inviting people to swipe, 4-6 hashtags. Plain text, no emojis unless asked, under 3000 characters.
7. **Deliver**: send `<slug>-linkedin-carousel.pdf` (this is the file to upload as a LinkedIn document), the `slide-N.png` files and `caption.txt` with SendUserFile, and give the caption in the reply so it can be pasted. Commit `posts/<slug>` and `dist/<slug>` and push to the session branch.
8. **Revisions**: edit the spec (or the engine, if a new icon/scene is needed), rebuild, re-check, re-send. Never hand-edit files in `dist/`.

## Choosing a scene

| Slide idea | scene | panel | params |
|---|---|---|---|
| intention vs action, a missing step, "knowing is not doing" | `gap` | tall | `idea`, `waypoint` (icons), `from`, `to` (objects) |
| one subject in focus + 1-3 supporting ideas | `hero` | tall | `object`, `badges` (up to 3 icons) |
| a moment of choice, several possible outcomes | `fork` | card | `object`, `options` (2-4; `{"icon":"machine","state":"go"}` highlights one, `"state":"lost"` fades one) |
| a repeating cycle (3-4 stages) | `loop` | card | `nodes`, `center` |
| an ordered process, top to bottom | `steps` | card | `steps` (3-4), optional `labels` |
| one number / percentage | `stat` | card | `value` (0-100), `text`, `caption`, `icon` |
| stakeholders / roles sharing a system (closed circle; one can be missing `"state":"lost"` or highlighted `"state":"go"`) | `ring` | tall | `nodes` (3-6), `center` |
| the same circle inside a card slide (e.g. "circle broken without X", "X restored") | `ring_card` | card | `nodes` (3-6), `center` |
| a journey / route through 3-5 stages ("pathway", "return route") | `pathway` | col | `nodes` (3-5) |
| two outcomes side by side (done well vs done badly; before / after) | `compare` | col | `good`, `bad` (3 items each; the `bad` column is shown faded with an x) |
| **journey band** (full-width road that continues from slide to slide; best for a story told as a pathway): start of the journey with leaks / gaps | `trail` | band | `start`, `leaks` (3), `end` |
| journey band: things converging onto a structured route | `converge` | band | `nodes` (3-4), `object` |
| journey band: the route splits into done well vs done badly | `lanes` | band | `start`, `good`, `bad` (2 items each) |
| journey band: the finished circuit that loops back | `circuit` | band | `nodes` (3-5), `end` |
| from A to B with enablers in between | `bridge` | wide | `from`, `to`, `stops` (2-4) |
| the closed circle as a wide oval ("the loop is complete") | `track` | wide | `nodes` (3-6), `center` |
| a left-to-right sequence | `flow` | wide | `steps` (3-5), optional `labels` |
| no visual needed (list, quote, closing) | omit `visual` | none | use `bullets` / big `heading` |
| the user supplies a real photo | `{"image": "path.jpg", "kind": "card"}` | card/tall | |

Panel decides the layout: **tall** = cover-style (text centred on the left, no callout), **card** = text + panel + callout box, **band** = *journey layout* (heading on top, full-bleed road in the middle, copy under it, optional callout; the road enters and leaves every slide at the same height, so use band scenes on consecutive slides and the carousel reads as one continuous pathway), **col** = tall card with no callout box (text centred beside a 390x700 panel), **wide** = heading, wide panel, callout box.
A closing/bold line from the user's copy usually becomes the `fill` callout box; use `col` scenes when a slide has two paragraphs and nothing to put in a box.
Line breaks: put `\n` in a heading to control where it breaks. Break so the green phrase starts at the beginning of a line (a colour change mid-line looks accidental).
Slide items are objects (`bottle can glass machine coin crate bag kiosk`, full colour) or icons (`python3 engine/build.py --library` renders the catalogue to `dist/_library.png`; look at it).
In a `{"icon": "machine"}` entry the line icon is used; a bare `"machine"` gives the illustration; `{"obj": "machine"}` forces the illustration.
Icons not in the catalogue? Add one to `engine/library.py` (48x48 grid centred on 0,0, stroke-only), re-render the catalogue and check it. Same for a new object or scene. Keep new work in the same language: thin green outlines, mint halos, circular nodes, chevron arrows.

## Visual direction: realistic photography (standing instruction from the user)

Carousels are **photography-led**. Do not use the flat vector scenes (gap, fork, ring, journey bands...) unless the user explicitly asks for them. If a photographic image does not work for a slide, try a different photographic composition first.

**Principle: the visual is derived from the meaning of the slide, not the other way round.**

Workflow for every carousel:
1. Read ALL the copy. Write the core message of each slide in one line, and how the slides connect.
2. Write an art direction that is shared by the whole carousel (light, colour grade, lens, setting, how people appear) and a shot list: one specific, different, realistic image per slide. No repeated subject, composition or metaphor; the images should progress with the narrative (e.g. problem -> return -> quality -> recovery). Save it as `posts/<slug>/art-direction.md` and show it to the user before generating if they have not approved a shot list.
3. Generate each image with OpenArt (`openart_model_form_get` then `openart_generate_image`; `nano-banana-2-1` text2image, 2K, about 30 credits per image). Aspect ratio per layout below. Poll with `openart_creation_get`.
4. Download the image into `posts/<slug>/images/slide-N.png` (the URL is in the result; it is on `cdn.openart.ai`), then **look at it** (Read the file). Check: realism (no AI look, no warped hands/objects, no gibberish text), contextual accuracy, composition for the layout, consistency with the other images. Re-prompt (max 2-3 attempts) if generic, artificial, repetitive, misleading or disconnected from the copy.
5. Harmonise the series with `python3 engine/photo_prepare.py in.png posts/<slug>/images/slide-N.jpg --sat 0.8-0.92 [--warm -6..6]`: a mild grade only (mute oversaturated or colour-cast images so all slides share one palette) plus a sensible JPEG size. Keep raw downloads in `posts/<slug>/images/_candidates/` (git-ignored).
6. Put it in the spec as `"visual": {"image": "images/slide-N.jpg", "kind": "tall|card|col", "position": "50% 40%"}` (`position` sets the crop focus)` and build as usual.

**Current preferred photo treatment: the photo-base layout (`"kind": "bg"`), see the next section.** The contained rounded photos below (`tall`/`card`/`col`) still work and are used by older posts. Do not use `top`/`bottom` (full-bleed strips above/below the copy; the user disliked them).

### Photo-base layout (`kind: "bg"`)

A realistic square photo is the base layer of the slide (the look of Recykal's EPR posts), but the brand system stays DRS: DRS green `#049769`, uppercase Poppins headings, solid green callout, the template footer. Do NOT use the EPR blue, a contact-details CTA bar or title-case headings.

* Copy sits on a white fade (the "veil") on the left; logo, headline and body are never on the image itself. The photo subject sits in the right ~45-55%.
* Generate each image **1:1, 2K**, with the subject confined to the right half and a very bright, hazy, near-white, empty left side (ask for it in the prompt). Keep subjects out of y 782-914 on slides with a callout (the box covers it): pan the photo up with `shift_y`.
* Clear plastic needs a **darker backdrop** behind it or it disappears into the white fade; transparent objects against a pale background are invisible.
* Slide fields: `"visual": {"image": "images/slide-N.jpg", "kind": "bg", "zoom": 1.14, "origin": "100% 100%", "shift_x": 148, "shift_y": -150}` (pan/zoom the photo; a panned photo's bottom edge fades out automatically); `"text_width": 410` (copy column width, keep it clear of the subject), `"heading_width": 720` (let a short two-line headline run wider than the body), `"veil_end": 56` (where the white fade ends, % of width; smaller keeps more of the photo clear), `"veil_low": 0.2` (+ optional `veil_low_from`/`veil_low_to`) eases the fade off below the copy, `"ground": 1` adds a soft floor shadow where the photo is blown out.
* Spacing standard (agreed with the user): headline starts at y=202 on every slide (68 px under the logo block), heading to rule 30 px, rule to body 28 px, gap between body paragraphs 26 px, headline 40-44 px, body 24-26 px. Text left edge = 50 px = the logo's left edge. Callout box top y=782. Check with a measurement, not by eye.
* Headlines: prefer 2-4 lines; do not split a short headline over three lines if two fit (reading flow). Green highlight phrases start at the beginning of a line (use `\n`).
* Callout text can be broken with `\n` so the underlined phrase starts a line.

### Contained photos (`tall` / `card` / `col`)

| kind | layout | image area | generate | note |
|---|---|---|---|---|
| `tall` | text left, tall photo right (cover style, no callout) | 460x660 | 3:4 portrait | the default for slides without a callout box |
| `card` | text left, photo right, callout box below | 390x536 | 3:4 portrait | use when the slide has a bold closing line; simple, bold subject |
| `col` | text left, taller narrow photo right, no callout | 390x700 | 3:4 portrait (crops sides slightly) | when two paragraphs need the room |
| `top` / `bottom` | full-bleed photo above / below the copy | 1080x520 / 1080x392 | 21:9 | avoid (see above) |

Always compose for **portrait** (3:4) so the photo is generated for its frame: stack the story vertically (foreground / midground / background) instead of side-by-side wide scenes.

Copy always sits on white, outside the photo, so the photo needs no empty area for text. Never ask for text, labels, logos, brand marks or watermarks in the image; ask for plain unbranded packaging.

Prompt shape: `Documentary editorial photograph, <specific scene and action>, <Indian urban/retail/industrial setting>, soft natural daylight, 35mm lens, shallow depth of field, natural muted colour grade, realistic skin, hands and materials, unbranded plain packaging, no text, no logos, no watermark.` Keep the same style sentence in every prompt of a carousel so the series matches.

Accuracy rules (the content explains DRS and material recovery):
* Show only processes, equipment and activities that fit the slide. Do not invent scheme-specific infrastructure or imply a process is universal; prefer generic return points / collection counters over branded kiosks.
* Never suggest that returning or collecting packaging means it has been recycled. Keep collection, sorting, processing and recycling visually distinct.
* Show contamination or littering realistically and modestly (a handful of items, not apocalyptic piles).
* No misleading depictions of how a Deposit Refund Scheme works.

If the images cannot be downloaded (`cdn.openart.ai` blocked by the environment: curl returns 403), STOP. Tell the user the host must be allowed (cloud environment menu in the title bar > Edit > Network access > add `cdn.openart.ai` under Allowed domains, or a broader level). Do not generate images you cannot review, and do not silently fall back to vector scenes or mocked images.

## Spec format

```json
{
  "slug": "short-kebab-name",
  "title": "browser title (optional)",
  "footer": "www.recykal.com",
  "slides": [
    {
      "heading": "Plain text with **green highlight** markers",
      "body": ["paragraph one", "paragraph two with **a highlighted phrase**"],
      "bullets": ["optional list, **highlights** allowed"],
      "visual": {"scene": "fork", "...": "scene params"},
      "callout": {"style": "line|fill", "icon": "arrow", "text": "box text with **highlight**"},
      "heading_size": 36, "body_size": 23, "align": "top"
    }
  ],
  "caption": "LinkedIn post text",
  "hashtags": ["#Recykal"]
}
```

* Variety: if a previous post used card/callout layouts on every slide, change the composition (journey band, tall cover, wide statement) rather than repeating it. Keep one visual idea running through the whole carousel. Add `"progress": true` at the top of the spec for slide-progress dots in the footer.
* Text next to a card panel is vertically centred on the panel (like cover slides). Add `"align": "top"` to a slide to pin it to the top instead.
* Highlight with `**...**`. If the user already marks emphasis, keep it. If not, highlight one key phrase per heading and the phrase that carries the idea in the body/callout. Don't highlight whole sentences.
* `callout` style: `line` (white box, green outline) for a reflective point; `fill` (solid green) for the payoff/CTA. Tall (cover) slides have no callout.
* Wide-scene slides take heading + callout only (body text ignored). Put the sentence in the callout. Long copy can be split between `body` and `callout` without changing a word; tell the user which sentence went where.
* Last slide has no next-arrow automatically. The logo block, the `www.recykal.com` footer and the bottom bar come from the official Recykal social template (`engine/assets/template.svg`, applied to every slide automatically; the `footer` field is no longer used).
* The engine auto-shrinks text to fit (heading min 28/40 px, body 19 px, callout 22 px) and reports what it did.

## Brand rules (from the Recykal social guidelines)

Canvas 1080x1080, **follow the Recykal social template (`engine/assets/template.svg`): logo block top-left at x=50 y=50 (229 px wide), `www.recykal.com` footer at x=50 (about y 987-1012), black 227x10 bar at x=50 on the bottom edge. Content margin is 50 px, aligned with the logo. All posts, old and new, use it.** Poppins only (max 3 weights). Core palette green/black/white; DRS green `#049769` is the accent for highlights, icons, arrows, outlines and CTA boxes. No extra colours, no shadows or effects on the logo, no photos with heavy filters. White space is part of the design: do not fill it just to fill it. Same system, different layouts.

## Never

* Invent statistics, claims or quotes. Numbers appear only if the user gave them.
* Change the user's wording without telling them.
* Post to LinkedIn or any external service. Deliver files and caption; the user publishes.
* Use network image generators unless the user explicitly asks: the sandbox may block their CDN, and some tools spend the user's paid credits. The engine's own vector scenes are the default.
