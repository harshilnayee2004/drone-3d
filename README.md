# MIPL website, version 2

Version 2 is a separate static site with 15 pages. It has a new look, a new scroll sequence, interactive components and a few light 3D touches. Version 1 (`MIPL-website`) hasn't been changed.

## How to open it
- **Quickest:** double-click `index.html`. Everything works from file://, including fonts, animations and 3D.
- **Like a real server:** in this folder, run `python -m http.server 8000`, then open http://localhost:8000.
- **To deploy:** upload the folder as-is to any static host (Netlify, Vercel, cPanel, S3). All paths are relative and there's no build step.

## What's inside
- 15 pages: `index`, `products` (product finder), 8 product-line pages in `products/`, `about`, `clients`, `careers`, `contact` and `404`.
- `assets/vendor/`: vendored GSAP 3.13 + ScrollTrigger, Lenis 1.1.13, and three.js r147 (`three.min.js` + `SVGLoader.js`). three.js is lazy-loaded, and only on the home page.
- `assets/js/v2.js`: all the scroll choreography and components. `v2-3d.js` holds the WebGL logo and particles. `search-index.js` is the Ctrl/Cmd+K index.
- `assets/css/v2.css`: Geist, Geist Mono and Instrument Serif are embedded so they load over file://.
- `_source/`: the Python generator (`build_v2.py`). Edit the data or templates there and re-run it to regenerate the pages.
- `_preview/`: the contact sheet and a 25-second preview video.

## Scroll choreography
Scroll-fill text, sticky stacked cards, clip-path wipes, a horizontal company timeline pinned from 2014 onward, a pinned product "exploder" (Telescopic Manipulator photo split with parallax layers and spec callouts), a velocity-skewed marquee, section colour shifts (paper, ink, blue), a progress bar, a hero video mask, and four-column curtain page transitions.

## Components
Custom cursor, magnetic buttons, tilt/spotlight cards, the product finder (sector, line and text filters, deep links such as `products.html?sector=Nuclear`), ARIA tabs and specs accordions, animated counters, a before/after slider, hover image reveal, a lightbox, a client logo wall, a sticky CTA, Ctrl/Cmd+K search (or press `/`), back-to-top with a progress ring, and a toast on form submit.

## 3D (light)
- **Extruded 3D MIPL logo** at the end of the home page. It's built live from the traced logo SVG paths using three.js SVGLoader and ExtrudeGeometry, in the brand blue and red, and it follows the mouse.
- **3D product carousel** ("The lineup"), built with CSS 3D: a ring of 8 real product photos. Rotate it with the arrows, drag, arrow keys or scrolling.
- **Particle wave** behind the blue numbers section, using a WebGL shader.
- three.js loads only when a 3D section comes near the viewport. Each scene pauses offscreen and when the tab is hidden, and the pixel ratio is capped.
- With reduced motion turned on, or without WebGL, the static logo image and a flat carousel are shown instead. On phones and tablets (900 px and narrower) the carousel becomes a swipeable row, and the 3D scenes run lighter.

## Accessibility
All controls work from the keyboard: the menu has a focus trap, the tabs support arrow keys and Home/End, and Escape closes the lightbox, search and menu. Visible focus styles are kept. `prefers-reduced-motion` turns off the intro, pins and 3D. Touch devices don't get the cursor, magnetic or tilt effects.

Note: `_source/build_v2.py` uses absolute paths from the build machine (`SRC`, `OUT`, and the `sys.path` line at the top). Point them at your own folders before re-running it. The original images live in `assets/img`.
