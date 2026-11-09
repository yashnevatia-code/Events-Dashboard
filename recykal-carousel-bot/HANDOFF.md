# Recykal LinkedIn carousel bot: complete handoff

Written 2026-11-09 for a new session (or person) to carry on exactly where the last session stopped.
Read this first, then `.claude/skills/recykal-carousel/SKILL.md` (the bot's own instructions) and `recykal-carousel-bot/README.md`.

---

## 1. What this is

A spec-driven tool that turns slide-by-slide copy into a **LinkedIn carousel**: a PDF for LinkedIn's document upload, 1080x1080 PNG per slide, a caption with hashtags, and (optionally) a design-rationale PDF. The user (Recykal marketing, marketing@recykal.com) supplies the copy slide by slide; the bot delivers every post in the same Recykal template.

* Repository: `yashnevatia-code/events-dashboard` (GitHub). The tool lives in the folder `recykal-carousel-bot/`; the bot's instructions are in `.claude/skills/recykal-carousel/SKILL.md`.
* Working branch: `claude/intelligent-newton-tcpb5o` (everything is committed and pushed; the last commit is "PDF export: flatten photo slide backgrounds"). No pull request has been opened (the user has not asked for one).
* The events dashboard that shares this repository is unrelated to this work.

## 2. Files and where things are

```
.claude/skills/recykal-carousel/SKILL.md   the bot's instructions (workflow, spec format, brand rules, photo rules)
recykal-carousel-bot/
  README.md                                how to run, PDF export notes
  HANDOFF.md                               this file
  engine/
    build.py                               the builder: spec JSON -> HTML -> PDF + PNGs + caption + QA
    theme.css                              the design system (type, colours, layouts, template chrome, bg-photo layout)
    library.py, scenes.py                  vector icons/objects/scenes (only used when the user asks for vectors)
    photo_prepare.py                       mild colour grade + JPEG export for generated photos
    rationale.py                           builds the design-rationale PDF from posts/<slug>/rationale.json
    measure.py                             measures vertical spacing on every slide (use instead of judging by eye)
    fetch_fonts.py, assets/                Poppins fonts (vendored), logo.svg (no longer used), template.svg (official template)
  posts/<slug>/post.json                   one spec per post (copy, layout, image placement, caption, hashtags)
  posts/<slug>/images/slide-N.jpg          the graded final photos (committed)
  posts/<slug>/rationale.json              slide-by-slide rationale (optional)
  dist/<slug>/                             outputs: <slug>-linkedin-carousel.pdf, slide-N.png, caption.txt, qa.json (committed)
```

**Not in the repository:** `posts/<slug>/images/_candidates/` (git-ignored) held the raw OpenArt downloads and all unused variants. That folder was lost when the working container was replaced. The final graded photos (`slide-1..4.jpg`) are safe, but the original downloads and rejected variants are gone. To change a photo, regenerate it (see section 7).

## 3. How to run it

Needs: Python 3, Pillow, Chromium (found under `/opt/pw-browsers/chromium-*`, or set `CHROME=/path/to/chrome`), and `pdftoppm` (poppler-utils). Poppins fonts are vendored, so builds work offline.

```bash
cd recykal-carousel-bot
python3 -I engine/build.py posts/<slug>/post.json      # builds dist/<slug>/ (PDF, PNGs, caption, qa.json)
python3 -I engine/build.py --all                        # every post
python3 -I engine/measure.py $PWD/dist/<slug>/index.html   # spacing numbers per slide
python3 -I engine/photo_prepare.py in.png out.jpg --sat 1.1 --contrast 1.07 --warm 0.04 --max 2160
```

The build prints per slide: layout, headline size and lines, body size, callout size. Any `<-- CHECK` line or entry in `qa.json` `problems` means text still overflows after the automatic shrink: shorten the copy or adjust sizes. `index.html` is git-ignored.

## 4. The template (mandatory for all posts)

The user supplied the official Recykal social media template (`engine/assets/template.svg`, 1080x1080). The engine inlines it on every slide:

* logo block with tagline: top-left, x=50, y=50, about 229 px wide (ends at y=134)
* `www.recykal.com` footer text: x=50, about y 987-1012 (drawn as paths, so the `footer` field in specs is ignored)
* black bar 227x10: x=50, on the bottom edge
* content margin is **50 px** (aligned with the logo); everything old and new was rebuilt on it

The swipe arrow (bottom right) and the progress dots are **additions of ours**, not in the template. They were kept on the carousels and aligned to the footer; remove them if the user wants only what is in the template.

## 5. Design system (what the user approved, and why)

Brand: Poppins; DRS green `#049769`; black and white. Headlines are **uppercase** in the DRS carousels; green highlight phrases mark the key idea.

**Current preferred look: photo-base layout (`"kind": "bg"`)**, used by `waste-collection-value-recovery-photo`:

* a realistic full-bleed square photo is the base layer; the copy sits on a white fade on the left (logo, headline and body are never on the photo itself)
* DRS styling stays: green accents, uppercase headline, solid green callout box (`fill`), template footer
* it was inspired by Recykal's **EPR posts** (Bulk Waste Generator, E-waste Q1 filing, RDF target). The user later clarified the EPR posts were **only a reference for the photographic look**. Do NOT use the EPR blue, a contact-details CTA bar, or title-case headlines
* spacing standard (measured with `engine/measure.py`): headline top y=202 on every slide (68 px under the logo block), headline to rule 30, rule to body 28, paragraph gap 26, callout box top y=782, headline 40-44 px, body 24-26 px. Slide 4 was the user's reference ("perfect"); slides 1-3 were made to match it
* slide fields for the bg layout: `visual.zoom/origin/shift_x/shift_y` (pan/zoom the photo), `text_width` (copy column width), `heading_width` (let a short headline run wider), `veil_end` (where the white fade ends, % of width), `veil_low` + `veil_low_from/to` (ease the fade below the copy), `ground` (soft floor shadow). All are documented in the skill

Older layouts still work: contained rounded photos (`tall`/`card`/`col`), vector scenes (`scene`), and the layouts `cover`, `split`, `statement`, `journey`, `text`. Do not use `top`/`bottom` (full-bleed strips above/below the copy; the user disliked them).

**PDF export:** photo slides are flattened (see `README.md`, "PDF export notes"). The user reported pixelated and sometimes blank pages in Edge; the cause was CSS masks, filters and blurred shadows turning into stacks of transparency layers. The fix: photo, fade and shadows are baked into one 2160 px JPEG per slide, with text and logo kept as vector. **The user has not yet confirmed the fix in Edge**; ask them to open the latest PDF and report.

## 6. The user's standing preferences (collected over the whole project)

Content
* Keep the user's copy word for word; tell them if a sentence moves between body and callout. They edit copy themselves (e.g. the slide 4 goal line, below).
* Do not add claims or statistics. Put green highlights at the **start of a line** (manual `\n` breaks).
* Prefer 2-4 line headlines; they objected to a short headline split over three lines (reading flow). Avoid single-word last lines.

Visual
* Photography over vector illustration for new work; each image must come from the exact meaning of its slide, with a connected narrative and consistent lighting/grade. No repeated compositions across slides.
* Avoid repetition with earlier posts; avoid clutter and clumsy slides. Icons (when used) must look accurate: landfill = dump truck tipping onto a heap with gulls; recycling = the standard three chasing arrows in a single DRS green with lighter-tint folds; a globe at the centre of loop diagrams.
* No logo on a photo; no full-bleed horizontal strips; text must not overlap the photo's subject; white space should look even (not too much above the headline, not an empty corner). The user checks these closely.
* The used bottle must look like a bottle **returned straight from a consumer under a DRS**: crushed is fine, dirty is not.
* Clear plastic needs a darker backdrop behind it, or it disappears into the white fade.
* The user asked for the **Indian context** (Indian customer, Indian street and settings) and for **hyper-realistic** images. A machine with DRS lettering is acceptable (they asked for it), but no real brands; the "Return. Earn. Recycle." text was removed from the machine on request.

Process
* Show a representative slide before applying a new direction to all slides; show options for design choices; give concrete before/after for polish passes; measure spacing.
* Deliver PDFs, PNGs and caption with `SendUserFile`; commit and push each change (a stop hook flags uncommitted or untracked files).

## 7. Image generation (OpenArt)

* Tool: OpenArt MCP, model `nano-banana-2-1`, mode `text2image`, params `prompt`, `aspectRatio` ("1:1" for bg slides), `resolution` "2K", `imageCount` (1-2). About 30 credits per image; the account is on the Pro plan (5,290 credits at last check). Generation is asynchronous (about 40-70 s): poll with `openart_creation_get` and download the CDN URL with `curl`.
* The cloud environment must allow `cdn.openart.ai` (it does, in the environment named "website verification"). If curl returns 403, stop and ask the user to allow the host; do not generate blind.
* Grade every photo with `photo_prepare.py` using the same flags per carousel so the series matches (the photo carousel used `--sat 1.05-1.1 --contrast 1.05-1.07 --warm 0.03-0.05 --max 2160`).
* Prompt pattern that worked for the bg layout: "Photorealistic high-key editorial photograph, square 1:1, <lens/light>, true-to-life muted colours, not stylised, not CGI. <subject and action>. Plain unbranded packaging, no labels/logos/text. COMPOSITION: the subject sits in the right half; the left 45% of the frame is a very bright, soft, hazy, out-of-focus area fading to near-white, empty, for text." Add "behind the objects a darker blurred backdrop" for clear plastic. Keep subjects out of y 782-914 on slides with a callout (the box covers it) by panning with `shift_y`.
* Always look at each image (Read it): realism, warped hands, gibberish text, accuracy, composition. Re-prompt rather than accept a generic or misleading image.
* The prompts behind the current photos: slide 1 low kerbside view of an Indian street with a modest scatter of empty bottles/cans beside a storm drain; slide 2 an Indian woman (blue block-print kurta top) putting a bottle into the round aperture of a modern green-and-charcoal reverse vending machine with only "DRS" and "Deposit Refund Scheme" lettering; slide 3 gloved hands at a collection-centre sorting table between a crate of clean bottles and a crate of soiled bottles; slide 4 on a dark slate bench, a clean crushed bottle with a teal cap, a mound of clean PET flakes and a new bottle, against a blurred dark plant backdrop.

Accuracy rules (the content explains DRS and material recovery): do not invent scheme-specific infrastructure; do not imply that collecting or returning packaging means it was recycled; keep collection, sorting, processing and recycling visually distinct; show litter modestly; no misleading depictions of how a DRS works.

## 8. The posts and their status

| slug | what it is | state |
|---|---|---|
| `waste-collection-value-recovery-photo` | **Current focus.** "From waste collection to value recovery": 4 slides, photo-base layout, template applied | Final candidate; all changes pushed. Latest PDF: `dist/waste-collection-value-recovery-photo/waste-collection-value-recovery-photo-linkedin-carousel.pdf` |
| `waste-collection-to-value-recovery` | Same copy, earlier version with contained portrait photos | Kept for comparison; rebuilt on the template; slide 4 wording updated |
| `drs-knowing-vs-doing` | First post, "Knowing is not the same as doing", vector illustrations | Approved earlier; rebuilt on the template |
| `circularity-shared-responsibility` | "Circularity is a shared responsibility", vector illustrations | Approved earlier; rebuilt on the template |

Photo carousel slide by slide (copy is in `post.json`; headlines uppercase):
1. "FROM WASTE COLLECTION / TO VALUE RECOVERY: / **BUILDING A BETTER / PATHWAY**". Kerbside litter photo. Green callout: "Recovering that value requires a more organised collection system and **a clear pathway to material recovery.**"
2. "A DEPOSIT REFUND SCHEME CREATES **A STRUCTURED RETURN PATHWAY.**" RVM photo. Two paragraphs, no callout.
3. "MATERIAL QUALITY MATTERS / **FOR RECOVERY.**" (two lines, by request). Sorting table photo with a soft floor shadow and an eased fade in the lower left. Two paragraphs, no callout.
4. "BUILDING A BETTER PATHWAY MEANS **KEEPING MATERIAL VALUE IN CIRCULATION.**" Bottles-and-flakes photo. Callout (the user's own wording, changed from "help packaging's material value find its way back into the economy"): "The goal: help packaging waste / **find its way back into the value chain.**" The caption was updated to match.

Caption and hashtags are in `post.json` (`#CircularEconomy #DepositRefundScheme #DRS #EPR #Recycling #Recykal`).

## 9. Open items and ideas (nothing here has been approved yet)

1. **Confirm the PDF in Edge** (see section 5). If pages are still slow or soft, last resort: export each slide as a full image into the PDF (loads fastest, text no longer selectable).
2. **Slide 2 photo:** the machine's left edge sits close to the body copy and the woman is cropped at the hip. Offered: regenerate with more room around her.
3. **Slide 4 "new bottle"** could be read as bottle-to-bottle recycling, which the copy does not claim. Offered: swap for another product made from recycled material if that is a concern. (The rationale notes this.)
4. **Continuity device:** a thin green line growing along the bottom from slide to slide, instead of the dots. Offered, not requested.
5. **Headlines on slides 2 and 4** are 4 and 5 lines. Offered: re-break into fewer, longer lines as was done on slide 3 (the photo behind limits the width).
6. **Rationale PDF** for the photo post was written before the template and spacing passes; refresh `rationale.json` if it is going to be shared.
7. The other three posts still use their own look (vectors or contained photos). If the user wants them re-done in the photo-base style, each needs new photography.
8. The user wanted to link a **desktop folder ("recykal linkedin")** to the chat. A cloud chat can only use a folder the desktop app serves through Remote Control (Settings > Claude Code > Remote Control); none was listed. The reliable route is a new session on the user's computer in that folder, cloning the repository and branch above.

## 10. Environment notes

* The chat ran in the cloud environment "website verification" (personal, network limited: package registries, MCP servers and `cdn.openart.ai`; no setup script). The only other environment is "Default".
* Tools used: OpenArt MCP for images; `SendUserFile` to deliver files; git for saving work. Adobe, Figma, Notion and Drive connectors were available but not used.
* Compaction of the long chat failed once on the weekly usage limit (resets 09:00 UTC); starting a fresh session from this handoff avoids a very long context.

## 11. Recreate the current state on a new computer

```bash
git clone https://github.com/yashnevatia-code/events-dashboard.git
cd events-dashboard && git checkout claude/intelligent-newton-tcpb5o
cd recykal-carousel-bot
python3 -I engine/build.py posts/waste-collection-value-recovery-photo/post.json
```

Then open `dist/waste-collection-value-recovery-photo/` for the PDF, PNGs and caption.
