# 05 — Fix MIPL v2 design flaws (Antigravity prompt)

You are editing the static site in this folder (MIPL website v2 / v2.1). There is no build step: edit `assets/css/v2.css`, `assets/js/v2.js` and the HTML directly. If you use `_source/build_v2.py`, mirror each change there as well. Keep every fact, page, the real logo, the vendored libraries and the relative paths. Don't add new claims.

**Test viewports:** real Chromium/Edge at 1024×575, 1280×720, 1440×900 and 390×844. Serve with `python -m http.server 8000` and also open via file://. For each fix: apply it, reload, scroll slowly through the section, and check the acceptance criterion.

Items marked **[DONE in v2.1]** are already fixed in MIPL-website-v2.1.zip. Verify them and don't redo them. Items marked **[TODO]** still need fixing.

---

## P0: 3D carousel "One from every line." (`index.html #lineup`)

1. **[DONE in v2.1] The ring never rotated visually, and the caption showed the wrong card.**
   - **Cause:** in `assets/js/v2.js`, the carousel stored `.ring` in `var rg`, and the custom-cursor block later re-declared `var rg=$('.c-ring')` in the same function scope. So `apply()` rotated the cursor ring, not the carousel. That produced the white half-circle stuck in the top-left corner, and a caption like "4 of 8: VR Simulators" while Telescopic Manipulator sat in front.
   - **Fix:** rename the carousel variable to `ringEl` everywhere (`apply`, `setup`, the flat-mode `scrollBy`).
   - **Accept:** click → three times. The card in front matches the `.ring-live` caption every time, and there's no stray white circle at the top-left of the viewport.
2. **[DONE in v2.1] Mirrored text on back faces.**
   - **Fix:** add `.ring3d.is3d .rc{backface-visibility:hidden;-webkit-backface-visibility:hidden}`.
   - **Accept:** no reversed text is visible at any rotation.
3. **[DONE in v2.1] Muddy, see-through cards.**
   - **Cause:** side cards used `opacity:.55`, so the cards behind showed through the front card.
   - **Fix:** remove the opacity and use `.rc:not(.front){filter:saturate(.7) brightness(.55)}` instead. Cards stay opaque.
   - **Accept:** the front card is crisp, and no other card's text shows through it.
4. **[DONE in v2.1] Broken images showing alt text (Edge).**
   - **Cause:** the images were `loading="lazy"` inside 3D-transformed or translated containers (`.ring`, `.htl` pinned track, `.explode`, `.stack`). Chromium/Edge lazy-load often never fires for images moved into view by transforms; our sweep found the timeline images still "pending" while on screen.
   - **Ruled out:** the files are byte-identical on the PC (MD5 checked) and all paths are lowercase. Windows Python 3.12 serves `.webp` as `application/octet-stream` (no registry MIME type), but Chromium still decodes that, so it's not the cause.
   - **Fix:** in `v2.js`, add `$$('.ring img,.htl img,.explode img,.stack img').forEach(i=>i.loading='eager')`, or better, set `loading="eager"` in the HTML for those images.
   - **Extra hardening [TODO]:** add an `onerror` on `.rc img` that removes the sibling `<source>` and falls back to the `.jpg`. Give `.rph` a neutral `background:#1c1c22` instead of the blue radial gradient, so a failed image never shows as an "empty dark blue panel".
   - **Accept:** in Edge at 1024×575, all 8 cards show photos straight after scrolling to the section, and `[...document.querySelectorAll('.rc img')].every(i=>i.complete&&i.naturalWidth>0)` is true.
5. **[DONE in v2.1] Cards overflowed the section on short screens.**
   - **Cause:** cards were a fixed 280×400 while the stage was 64vh (368 px at 575 high), so cards spilled over the heading and caption.
   - **Fix:** in `setup()`, compute `hh = clamp(300, innerHeight-260, 520)` and `w = hh*0.7`, and set `--ch` and `--cw` on `.ring3d`. In CSS, size `.ring` from those variables (width, height, negative margins) and set `.ring3d.is3d{height:calc(var(--ch) + 40px)}`. The radius comes from `w`.
   - **Accept:** at 1024×575 the whole front card fits between the heading and the caption.
6. **[DONE in v2.1] The heading sat tight under the nav, and the sticky CTA covered "4 of 8".**
   - **Fix:** `#lineup{padding-top:clamp(110px,16vh,160px);padding-bottom:clamp(120px,18vh,180px)}` and `.ring-live{margin-bottom:40px}`.
   - **Remaining [TODO]:** hide the sticky CTA while `#lineup` is in view. In `v2.js` next to the footer check, use an IntersectionObserver on `#lineup, .ending, .explode` that toggles `.stickycta.hide`, with CSS `.stickycta.hide{transform:translate(-50%,160%)}`.
   - **Accept:** the caption is never covered.
7. **[TODO] The scroll-driven spin fights the buttons and drag.**
   - **Fix:** remove `r3.__scroll` and its ScrollTrigger in `generic()`, or limit it to ±1 card. Rotation should come only from the buttons, drag, arrow keys and an optional slow autoplay that pauses on hover or focus.
   - **Accept:** scrolling past the section doesn't change which card is in front.

## P1: Other sections (home)

8. **[DONE in v2.1] Stacked cards showed "ghost" text from the card underneath** (seen at 1024×575 and 390). `.scard` faded to opacity .55 while still on top, so the previous card showed through.
   - **Fix:** in the `generic()` stacked-cards tween, replace `opacity:.55` with `filter:'brightness(.9)'`. Add `z-index:calc(var(--i) + 1)` to `.scard`.
   - **Accept:** no text from another card is ever visible inside the top card.
9. **[DONE in v2.1] Stacked cards were taller than short viewports**, so the chips and the "Explore" button were cut off at 575 px.
   - **Fix:** `height:min(76vh,700px,calc(100svh - 130px))`.
   - **[TODO]:** at heights of 650 px or less, reduce the `.scard .num` size and hide the chips row.
10. **[TODO] Exploder at 1024×575 and 1280×720:**
    - The spec callouts (5 m, 25 kg, 6 h) overlap the split photos.
    - The top-right layer touches the nav.
    - "Telescopic *Manipulator*" overlaps the left half at the start.

    **Fix:**
    - Under `@media (max-height:760px)`, set `.ex-anim .ex-main{width:40vw;top:60%}`, shrink `.ex-layer` to `clamp(120px,12vw,200px)`, and move the top layer to `top:20%`.
    - Give `.ex-callout` a dark pill background (`background:#0a0a0dcc;padding:10px 14px;border-radius:12px`).
    - Make `.ex-head` sit above the photos at `z-index:5` and fade it out as the split starts.

    **Accept:** at 1024×575 there's no text-on-photo overlap at any scroll point inside the pin.
11. **[TODO] Counters (blue section):**
    - At 1024 wide they fall into a 2×2 grid (the `max-width:1100px` rule), so labels such as "CLIENTS" sit at the very bottom of the screen and the captions misalign.
    - The particle canvas runs behind the captions and lowers contrast.

    **Fix:**
    - Keep 4 columns down to 901 px: change `.counts` in the 1100 px media query to `repeat(4,1fr)` with `.counts .n{font-size:clamp(48px,6.4vw,110px)}`.
    - Set `.counts>div{display:flex;flex-direction:column}` with captions at a fixed `min-height:3lh`, so the captions line up.
    - Make `.p3d{opacity:.45}` and add `mask-image:linear-gradient(transparent,#000 40%)` so the dots stay behind the numbers and not behind the text.
    - Check the final values are exactly 2014 / 8 / 15 / 12, and that the captions match ("Ahmedabad, Gujarat." under FOUNDED, and so on).

    **Accept:** at 1024×575 all four counters and their captions sit on one baseline, with caption contrast of at least 4.5:1.
12. **[TODO] The theme switches too early at the exploder → counters boundary.** The blue theme turns on while the end of the dark exploder pin is still visible, so the photos sit on blue.
    - **Fix:** in `themes()`, use `start:'top 35%'` for `[data-theme=blue]`, or trigger on the pin-spacer end.
13. **[TODO] Timeline:**
    - Several nodes share the same year (2024 ×7), which reads as repetition.
    - Captions sit under the sticky CTA.
    - At the pin end, the year row has scrolled off before the last card.

    **Fix:**
    - Show the year only on the first node of each year; later nodes show a small "· 2024" mono label.
    - Add `padding-bottom:110px` to `.htl` while pinned.
    - End the pin at `tr.scrollWidth - innerWidth + 80`.
14. **[DONE in v2.1] Logo wall:** the client names peeked half out of each tile (cut text).
    - **Fix:** `.lw .nm{opacity:0}`, then `opacity:1` on hover and focus.
    - **Accept:** no half-visible labels.
15. **[TODO] Ending at 1024:** "Navnirmit" runs into the 3D logo, and the sticky CTA covers "Bharat.".
    - **Fix:** between 901 and 1200 px, make `.logo3d{width:30vw;top:-80px;opacity:.9}` and `.ending .big{font-size:clamp(64px,11vw,200px)}`. Hide the sticky CTA over `.ending` (see 6).
    - **Mobile:** reduce the empty gap above the logo by setting `.logo3d{width:min(220px,56vw);margin:0 auto 10px}`.

## P1: Inner pages

16. **[TODO] Product pages, sticky `.subnav`** (top 76px): its background gradient is translucent, so headings slide visibly behind the chips.
    - **Fix:** `background:var(--bg)` and `border-bottom:1px solid var(--line)`. Give the section anchors `scroll-margin-top:150px`.
17. **[TODO] Product pages, clip-path wipe on `.prod2 .media`:** it takes 1.4 s, so while scrolling it shows a thin dark sliver.
    - **Fix:** duration .9, `start:'top 92%'`. If the media has no image (CROT), skip the wipe.
18. **[TODO] Sticky "Talk to MIPL" bar** covers body text and buttons on every page at 1024×575 and 390 (probe hits on about, product and timeline pages).
    - **Fix:** show it only when scrolling up (hide on scroll down) and only after the hero. Hide it over forms, `.band`, `.ending` and `.foot`.
    - **Mobile:** use a compact single button at bottom-right, next to back-to-top.
    - **Accept:** no automated probe hits; see the self-test.
19. **[TODO] Headings under the nav:** the H2s on product pages reach y<78 when jumped to via the subnav or `#hash`.
    - **Fix:** `[id]{scroll-margin-top:120px}`, and pass a Lenis `scrollTo` offset of −110 for hash links.
20. **[TODO] Contact page:** the honeypot label sits at x=−9999. Fine for bots, but use `.hp{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}` instead, to avoid horizontal-overflow risk.
21. **[TODO] Cursor:** the "OPEN" cursor label covers card text on product cards. Use the `.label` cursor only over images (`.ph`, `.rph`), not whole cards.
22. **[TODO] Mobile 390:**
    - The ring row peeks only 10% of the next card; make cards 78vw with 12px padding-inline so the next card shows about 18%.
    - The exploder static layout repeats the heading under the ring caption, so add 60px top margin.
    - Check the mobile menu covers the sticky CTA (`.menu-open .stickycta{display:none}`).

---

## Final visual self-test (must pass before you finish)

Write `qa/visual.py` (Playwright, Chromium, plus Edge via `channel="msedge"` if available). For each of the 4 viewports and all 15 pages:

1. Load the page, wait for `window.__ready`, then scroll in steps of 0.6× the viewport height, waiting 500 ms per step, and screenshot each step.
2. At each step, assert:
   - every on-screen `<img>` is `complete && naturalWidth>0`;
   - no visible text element intersects `.stickycta.show`;
   - no H1/H2 has `top<80` unless it is scrolling past;
   - `document.documentElement.scrollWidth<=innerWidth`;
   - no console errors.
3. Carousel: at each viewport, click → 8 times. After each click, assert that `.rc.front b` matches `.ring-live`, and that the screenshot has no mirrored text (visual check).
4. Reduced motion (`reduced_motion='reduce'`): no pins, flat carousel, static logo. No WebGL (`--disable-webgl`): static logo, no errors.
5. Build a contact sheet of all the screenshots, open it, and look at every frame for overlaps, cut text, empty dark panels and low contrast. Fix anything you find and re-run until the probes are clean.
