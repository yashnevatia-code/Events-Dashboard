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
2. **Plan each slide**: pick a `scene` from the idea the slide expresses (table below). Slides should *flow*: reuse the same objects (bottle, machine...) across slides and let a later visual answer an earlier one (e.g. slide 1 shows a gap, the last slide bridges it).
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
| from A to B with enablers in between | `bridge` | wide | `from`, `to`, `stops` (2-4) |
| a left-to-right sequence | `flow` | wide | `steps` (3-5), optional `labels` |
| no visual needed (list, quote, closing) | omit `visual` | none | use `bullets` / big `heading` |
| the user supplies a real photo | `{"image": "path.jpg", "kind": "card"}` | card/tall | |

Panel decides the layout: **tall** = cover-style (text centred on the left, no callout), **card** = text + panel + callout box, **wide** = heading, wide panel, callout box.
Slide items are objects (`bottle can glass machine coin crate bag kiosk`, full colour) or icons (`python3 engine/build.py --library` renders the catalogue to `dist/_library.png`; look at it).
In a `{"icon": "machine"}` entry the line icon is used; a bare `"machine"` gives the illustration; `{"obj": "machine"}` forces the illustration.
Icons not in the catalogue? Add one to `engine/library.py` (48x48 grid centred on 0,0, stroke-only), re-render the catalogue and check it. Same for a new object or scene. Keep new work in the same language: thin green outlines, mint halos, circular nodes, chevron arrows.

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
      "heading_size": 36, "body_size": 23
    }
  ],
  "caption": "LinkedIn post text",
  "hashtags": ["#Recykal"]
}
```

* Highlight with `**...**`. If the user already marks emphasis, keep it. If not, highlight one key phrase per heading and the phrase that carries the idea in the body/callout. Don't highlight whole sentences.
* `callout` style: `line` (white box, green outline) for a reflective point; `fill` (solid green) for the payoff/CTA. Tall (cover) slides have no callout.
* Wide-scene slides take heading + callout only (body text ignored). Put the sentence in the callout.
* Last slide has no next-arrow automatically. Footer URL is the same on every slide.
* The engine auto-shrinks text to fit (heading min 28/40 px, body 19 px, callout 22 px) and reports what it did.

## Brand rules (from the Recykal social guidelines)

Canvas 1080x1080, safe margins 70 px. Poppins only (max 3 weights). Core palette green/black/white; DRS green `#049769` is the accent for highlights, icons, arrows, outlines and CTA boxes. No extra colours, no shadows or effects on the logo, no photos with heavy filters. White space is part of the design: do not fill it just to fill it. Same system, different layouts.

## Never

* Invent statistics, claims or quotes. Numbers appear only if the user gave them.
* Change the user's wording without telling them.
* Post to LinkedIn or any external service. Deliver files and caption; the user publishes.
* Use network image generators unless the user explicitly asks: the sandbox may block their CDN, and some tools spend the user's paid credits. The engine's own vector scenes are the default.
