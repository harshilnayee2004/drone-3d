# MIPL website v2: open items (TODO)

The facts are the same as in v1, all taken from `content.json` (crawled from miplsolns.com). Nothing new was invented for v2.

## Needs MIPL input
1. **Contact form endpoint.** `contact.html` uses `data-endpoint="https://formspree.io/f/YOUR_FORM_ID"`. Replace `YOUR_FORM_ID`. Until then, and always over file://, the form shows a toast and opens the visitor's email app with the message pre-filled.
2. **Domain.** Canonical, OG and sitemap URLs assume `https://miplsolns.com/` (`DOMAIN` in `_source/data.py`).
3. **Careers.** No openings exist. The "Disciplines" accordion uses generic copy derived from the product lines, not a real org chart.
4. **Client logo 13** is labelled "Army Service Corps" (identified from the emblem). Please confirm.
5. **Leadership, certifications and awards** aren't in the content, so they aren't shown.
6. **Unverified claims, deliberately left out:** CISF / New Parliament House, the 39 GTC kamikaze drone, and Divya Chakshu.

## New in v2: please review
- **Sector tags in the product finder** are derived automatically, by keyword matching on each product's own text (for example, "nuclear" → Nuclear). Spot-check them and edit `SECT` in `_source/build_v2.py` if needed.
- **Timeline** uses only dated facts: founded in 2014, the dated deliveries and events, the 10th anniversary in 2024, and the 2025 CSMT delivery.
- **Exploder callouts** (5 m reach / 900 mm collapsed, 25 kg lift, 6 h battery) are the Telescopic Manipulator specs from the live site.
- **The before/after slider** pairs a workshop capability photo with the DRDO-INMAS delivery photo. Swap the pair if you'd prefer a different one.
- **Neutral copy I wrote:** section headings and leads such as "Eight lines. One standard.", "One from every line.", "From the workshop to the field." and "Navnirmit Bharat.", plus the counter captions.

## Missing photos / media (same as v1)
- Underwater ROV has 2 photos, IoBT has 1, and Smart Health Monitoring has none.
- Some VR & AR products have no local photo, so they show a typographic panel.
- The hero uses `home.mp4` (re-encoded). The newer `Home-Page-Updated.mp4` on the live site wasn't downloaded.

## Numbers used
Since 2014 · 10 years in 2024 · 8 product lines · 15 client logos · 12 sectors served (the live site's sectors list). No other statistics.
