import concurrent.futures
import http.server
import pathlib
import socketserver
import sys
import threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = ROOT / "qa" / "shots"
SHOTS.mkdir(parents=True, exist_ok=True)

PAGES = [
    "index.html",
    "products.html",
    "about.html",
    "clients.html",
    "careers.html",
    "contact.html",
    "404.html",
    "products/robotics.html",
    "products/bomb-detection-disposal.html",
    "products/underwater-rov.html",
    "products/vr-ar.html",
    "products/ai-ml.html",
    "products/iobt.html",
    "products/industrial-automation.html",
    "products/special-purpose-machinery.html",
]

VIEWPORTS = [
    ("1024x575", 1024, 575, False),
    ("1280x720", 1280, 720, False),
    ("1440x900", 1440, 900, False),
    ("390x844", 390, 844, True),
]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        pass


def start_server():
    socketserver.ThreadingTCPServer.request_queue_size = 64
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), QuietHandler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, port


PROBE_JS = """() => {
  const vw = window.innerWidth, vh = window.innerHeight;
  const imgs = [...document.querySelectorAll('img')].filter(im => {
    const r = im.getBoundingClientRect();
    const cs = getComputedStyle(im);
    return cs.display !== 'none' && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < vh && r.right > 0 && r.left < vw;
  });
  const brokenImgs = imgs.filter(im => !im.complete || im.naturalWidth === 0).map(im => im.getAttribute('src') || im.alt);

  const cta = document.querySelector('.stickycta.show');
  let ctaHits = [];
  if (cta) {
    const cr = cta.getBoundingClientRect();
    const csCta = getComputedStyle(cta);
    if (csCta.visibility !== 'hidden' && cr.height > 0 && cr.top < vh && cr.bottom > 0) {
      const els = [...document.querySelectorAll('main p, main h1, main h2, main h3, main h4, main a.btn, main button.btn, main .chip, main li')];
      for (const el of els) {
        if (el.closest('.stickycta')) continue;
        const cs = getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.05) continue;
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) continue;
        const ix = Math.max(0, Math.min(cr.right, r.right) - Math.max(cr.left, r.left));
        const iy = Math.max(0, Math.min(cr.bottom, r.bottom) - Math.max(cr.top, r.top));
        if (ix > 4 && iy > 4) {
          ctaHits.push((el.textContent || '').trim().slice(0, 40));
        }
      }
    }
  }

  const hIssues = [];
  const y = window.scrollY;
  for (const h of document.querySelectorAll('h1, h2')) {
    const cs = getComputedStyle(h);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.1) continue;
    const r = h.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const pinEl = h.closest('.explode, .hmask, .htl');
    const isFixed = pinEl && getComputedStyle(pinEl).position === 'fixed';
    if ((y < 5 || isFixed) && r.top < 80 && r.bottom > 0) {
      hIssues.push(`${h.tagName}:${Math.round(r.top)}:${h.textContent.trim().slice(0, 30)}`);
    }
  }

  const overflow = document.documentElement.scrollWidth > vw;
  return { brokenImgs, ctaHits, hIssues, overflow, scrollWidth: document.documentElement.scrollWidth, vw };
}"""


def test_viewport(base, bname, channel, vname, vw, vh, is_mob):
    errors = []
    shots = []
    with sync_playwright() as p:
        kwargs = {"channel": channel} if channel else {}
        browser = p.chromium.launch(**kwargs)
        ctx = browser.new_context(
            viewport={"width": vw, "height": vh},
            has_touch=is_mob,
            is_mobile=is_mob,
        )
        page = ctx.new_page()
        page.add_init_script("sessionStorage.setItem('miplIntro','1');")
        console_errs = []
        page.on("pageerror", lambda e: console_errs.append(f"pageerror: {e}"))
        page.on("console", lambda m: console_errs.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)

        for pg in PAGES:
            console_errs.clear()
            url = f"{base}/{pg}"
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function("() => window.__ready === true", timeout=15000)
            page.wait_for_timeout(350)

            step_px = max(120, int(vh * 0.6))
            doc_h = page.evaluate("() => document.documentElement.scrollHeight")
            steps = min(40, max(1, int((doc_h - vh) / step_px) + 1))

            pg_slug = pg.replace("/", "_").replace(".html", "")
            for s in range(steps + 1):
                target_y = min(s * step_px, max(0, doc_h - vh))
                page.evaluate(f"window.scrollTo(0, {target_y})")
                page.wait_for_timeout(500)
                res = page.evaluate(PROBE_JS)
                if res["brokenImgs"]:
                    errors.append(f"[{bname} {vname} {pg} y={target_y}] brokenImgs: {res['brokenImgs']}")
                if res["ctaHits"]:
                    errors.append(f"[{bname} {vname} {pg} y={target_y}] ctaHits: {res['ctaHits']}")
                if res["hIssues"]:
                    errors.append(f"[{bname} {vname} {pg} y={target_y}] hIssues: {res['hIssues']}")
                if res["overflow"]:
                    errors.append(f"[{bname} {vname} {pg} y={target_y}] overflow: {res['scrollWidth']}>{res['vw']}")

                if bname == "chromium" and (pg == "index.html" or s in (0, steps // 2)):
                    sp = SHOTS / f"{vname}_{pg_slug}_s{s:02d}.png"
                    page.screenshot(path=str(sp))
                    shots.append(sp)

                if target_y >= doc_h - vh:
                    break

            if pg.startswith("products/") and bname == "chromium":
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(200)
                chips = page.locator(".subnav a.chip")
                if chips.count() > 1:
                    chips.nth(1).click()
                    page.wait_for_timeout(1400)
                    href = chips.nth(1).get_attribute("href")
                    if href and href.startswith("#"):
                        h2_top = page.evaluate(f"() => {{ const el = document.querySelector('{href} h2'); return el ? el.getBoundingClientRect().top : 999; }}")
                        if h2_top < 78:
                            errors.append(f"[{bname} {vname} {pg}] subnav anchor {href} h2 top={h2_top:.1f} < 78")

            if console_errs:
                errors.append(f"[{bname} {vname} {pg}] console errors: {list(console_errs)}")

        if bname == "chromium":
            page.goto(f"{base}/index.html", wait_until="domcontentloaded")
            page.wait_for_function("() => window.__ready === true", timeout=15000)
            page.locator("#lineup").scroll_into_view_if_needed()
            page.wait_for_timeout(450)
            if not is_mob:
                nxt = page.locator('[data-ring="1"]')
                for k in range(8):
                    nxt.click()
                    page.wait_for_timeout(850)
                    front_b = page.locator(".rc.front b").text_content().strip()
                    live_t = page.locator(".ring-live").text_content().strip()
                    if front_b not in live_t:
                        errors.append(f"[{bname} {vname}] carousel click {k+1}: front='{front_b}' not in live='{live_t}'")
            sp_c = SHOTS / f"{vname}_carousel.png"
            page.screenshot(path=str(sp_c))
            shots.append(sp_c)

        ctx.close()
        browser.close()
    print(f"Finished {bname} {vname}: {len(errors)} issue(s)", flush=True)
    for err in errors:
        print("  !", err, flush=True)
    return errors, shots


def run_suite():
    chromium_only = "--chromium-only" in sys.argv
    httpd, port = start_server()
    base = f"http://127.0.0.1:{port}"
    errors = []
    shot_paths = []

    browsers = [("chromium", None)]
    if not chromium_only:
        try:
            with sync_playwright() as p:
                b = p.chromium.launch(channel="msedge")
                b.close()
                browsers.append(("msedge", "msedge"))
        except Exception as exc:
            print(f"[info] Edge channel unavailable, skipping: {exc}", flush=True)

    for bname, channel in browsers:
        print(f"\n=== Browser: {bname} ===", flush=True)
        workers = 4 if bname == "chromium" else 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [
                ex.submit(test_viewport, base, bname, channel, vname, vw, vh, is_mob)
                for vname, vw, vh, is_mob in VIEWPORTS
            ]
            for f in concurrent.futures.as_completed(futs):
                e_list, s_list = f.result()
                errors.extend(e_list)
                shot_paths.extend(s_list)

    with sync_playwright() as p:
        # Reduced motion check
        b_rm = p.chromium.launch()
        ctx_rm = b_rm.new_context(viewport={"width": 1280, "height": 720}, reduced_motion="reduce")
        p_rm = ctx_rm.new_page()
        p_rm.goto(f"{base}/index.html", wait_until="domcontentloaded")
        p_rm.wait_for_function("() => window.__ready === true", timeout=15000)
        rm_state = p_rm.evaluate("() => ({ pins: document.querySelectorAll('.pin-spacer').length, is3d: document.querySelector('.ring3d').classList.contains('is3d'), d3: window.__3d && window.__3d.status })")
        if rm_state["pins"] != 0 or rm_state["is3d"]:
            errors.append(f"[reduced-motion] unexpected state: {rm_state}")
        print(f"[reduced-motion] {rm_state}", flush=True)
        b_rm.close()

        # No-WebGL check
        b_nw = p.chromium.launch(args=["--disable-webgl"])
        ctx_nw = b_nw.new_context(viewport={"width": 1280, "height": 720})
        p_nw = ctx_nw.new_page()
        p_nw.add_init_script("sessionStorage.setItem('miplIntro','1');")
        nw_errs = []
        p_nw.on("pageerror", lambda e: nw_errs.append(str(e)))
        p_nw.goto(f"{base}/index.html", wait_until="domcontentloaded")
        p_nw.wait_for_function("() => window.__ready === true", timeout=15000)
        p_nw.locator(".ending").scroll_into_view_if_needed()
        p_nw.wait_for_timeout(400)
        nw_status = p_nw.evaluate("() => window.__3d ? window.__3d.status : 'none'")
        if nw_errs:
            errors.append(f"[no-webgl] errors: {nw_errs}")
        print(f"[no-webgl] status={nw_status}, errors={len(nw_errs)}", flush=True)
        b_nw.close()

        # file:// smoke check
        b_file = p.chromium.launch()
        ctx_f = b_file.new_context(viewport={"width": 1280, "height": 720})
        p_f = ctx_f.new_page()
        p_f.add_init_script("sessionStorage.setItem('miplIntro','1');")
        f_errs = []
        p_f.on("pageerror", lambda e: f_errs.append(str(e)))
        p_f.goto((ROOT / "index.html").as_uri(), wait_until="domcontentloaded")
        p_f.wait_for_function("() => window.__ready === true", timeout=15000)
        if f_errs:
            errors.append(f"[file://] errors: {f_errs}")
        print(f"[file://] ready=True, errors={len(f_errs)}", flush=True)
        b_file.close()

    httpd.shutdown()

    # Build contact sheets if Pillow is available
    try:
        from PIL import Image
        shot_paths = sorted(set(shot_paths))
        if shot_paths:
            cols = 4
            thumb_w, thumb_h = 360, 220
            chunks = [shot_paths[i:i + 24] for i in range(0, len(shot_paths), 24)]
            for idx, chunk in enumerate(chunks):
                rows = (len(chunk) + cols - 1) // cols
                sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h), (18, 18, 22))
                for j, sp in enumerate(chunk):
                    im = Image.open(sp).convert("RGB")
                    im.thumbnail((thumb_w - 8, thumb_h - 8))
                    x = (j % cols) * thumb_w + (thumb_w - im.width) // 2
                    y = (j // cols) * thumb_h + (thumb_h - im.height) // 2
                    sheet.paste(im, (x, y))
                out_sheet = ROOT / "qa" / f"contact-sheet-{idx + 1}.png"
                sheet.save(out_sheet)
                print(f"Saved {out_sheet}", flush=True)
    except Exception as exc:
        print(f"[info] Contact sheet skipped: {exc}", flush=True)

    if errors:
        print(f"\nFAILED with {len(errors)} issue(s):", flush=True)
        for err in errors[:50]:
            print(" -", err, flush=True)
        sys.exit(1)
    else:
        print("\nALL PROBES CLEAN!", flush=True)


if __name__ == "__main__":
    run_suite()
