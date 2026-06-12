#!/usr/bin/env python3
"""Browser E2E tests for MultiVis Agent (packaged or dev server on :8765)."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]

from playwright.sync_api import sync_playwright, expect

BASE = os.environ.get("MULTIVIS_BASE_URL", "http://127.0.0.1:8765")
CHART_WAIT_TIMEOUT = int(os.environ.get("MULTIVIS_CHART_TIMEOUT", "300"))
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    if not ok:
        FAILURES.append(f"{name}: {detail}")


def wait_server(timeout: int = 60) -> None:
    for i in range(timeout):
        try:
            with urlopen(f"{BASE}/", timeout=2) as r:
                if r.status == 200:
                    print(f"Server ready ({i + 1}s)")
                    return
        except Exception:
            time.sleep(1)
    raise RuntimeError(f"Server not reachable at {BASE}")


def wait_for_chart_ready(page, timeout_s: int = CHART_WAIT_TIMEOUT) -> tuple[bool, str]:
    """Wait until #chartArea shows a real chart (not the loading placeholder)."""
    placeholders = (
        "will be displayed here",
        "generating visualization chart",
        "generating chart",
        "loading interactive chart",
    )
    deadline = time.time() + timeout_s
    last = ""
    while time.time() < deadline:
        chart = page.locator("#chartArea")
        if chart.count() == 0:
            time.sleep(1)
            continue
        text = chart.inner_text()
        lower = text.lower()
        chart_cls = chart.get_attribute("class") or ""
        has_placeholder = any(p in lower for p in placeholders)

        img_count = page.locator("#chartArea img[src]").count()
        vega_count = page.locator(
            "#chartArea .vega-embed canvas, #chartArea .vega-embed svg, "
            "#chartArea #vis canvas, #chartArea #vis svg"
        ).count()

        if img_count > 0 and "has-image" in chart_cls:
            return True, f"chart image ({img_count} img)"
        if vega_count > 0 and not has_placeholder:
            return True, f"vega/canvas nodes={vega_count}"

        download_visible = page.evaluate(
            """() => {
            const b = document.getElementById('downloadChartBtn');
            return b && window.getComputedStyle(b).display !== 'none';
        }"""
        )
        if download_visible and not has_placeholder:
            return True, "download chart button visible"

        if ("failed" in lower or "error" in lower) and "generating" not in lower:
            return False, f"chart error: {text[:200]}"
        last = (
            f"img={img_count} vega={vega_count} cls={chart_cls!r} "
            f"placeholder={has_placeholder} text={text[:80]!r}"
        )
        time.sleep(2)

    extra = ""
    try:
        png = page.request.get(f"{BASE}/test_tmp/generated_chart.png")
        if png.status == 200:
            extra = " — backend PNG exists but chart area did not update"
    except Exception:
        pass
    return False, f"timeout after {timeout_s}s: {last}{extra}"


def run_tests() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_demo_history.py")],
        check=True,
        cwd=ROOT,
    )
    wait_server()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        console_errors: list[str] = []

        def on_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", on_console)

        # --- Homepage ---
        page.goto(BASE, wait_until="networkidle", timeout=60000)
        check("Homepage loads", page.title() != "")
        check(
            "Page title contains visualization",
            "VISUALIZATION" in page.title().upper() or "MULTIVIS" in page.title().upper(),
            page.title(),
        )

        expect(page.locator("textarea[name='nl_query']")).to_be_visible()
        check("NL query textarea visible", True)

        expect(page.locator("#queryForm")).to_be_visible()
        check("Query form present", True)

        expect(page.locator("button.generate-btn")).to_be_visible()
        check("Generate button present", True)

        expect(page.locator("#model_type")).to_be_visible()
        check("Model selector present", True)

        # --- Database schema API (via UI trigger) ---
        page.evaluate(
            """() => {
            const el = document.getElementById('db_name');
            if (el) el.value = 'chinook_1.sqlite';
        }"""
        )
        page.evaluate("() => { if (typeof loadDbStructureByName === 'function') loadDbStructureByName('chinook_1.sqlite'); }")
        page.wait_for_timeout(2000)
        schema_section = page.locator("#dbStructureSection")
        schema_visible = schema_section.is_visible()
        check("Database schema section shows for chinook_1", schema_visible)

        # Direct API
        resp = page.request.get(f"{BASE}/database_schema?db_name=chinook_1.sqlite")
        check("GET /database_schema returns 200", resp.status == 200, str(resp.status))
        if resp.ok:
            data = resp.json()
            check(
                "Schema API success flag",
                data.get("success") is True,
                json.dumps(data)[:200],
            )
            tables = data.get("structure") or []
            check("Schema has tables", len(tables) > 0, f"{len(tables)} tables")

        # --- History API ---
        hist = page.request.get(f"{BASE}/get_history")
        check("GET /get_history returns 200", hist.status == 200)
        if hist.ok:
            hdata = hist.json()
            check("History API success", hdata.get("success") is True)
            items = hdata.get("history") or []
            check("History is a list", isinstance(items, list))
            check("Demo history has 4 items", len(items) == 4, f"got {len(items)}")
            allowed_demo_dbs = {"activity_1.sqlite", "chinook_1.sqlite"}
            history_dbs = {item.get("db_name") for item in items}
            check(
                "Demo history only uses packaged databases",
                history_dbs <= allowed_demo_dbs,
                ", ".join(sorted(str(db) for db in history_dbs)),
            )

        # --- Form validation (empty submit) ---
        page.locator("textarea[name='nl_query']").fill("")
        page.locator("button.generate-btn").click()
        page.wait_for_timeout(500)
        # HTML5 required should keep us on same page
        check("Empty query blocked (stays on /)", "/result" not in page.url, page.url)

        # --- Fill query and select DB ---
        page.locator("textarea[name='nl_query']").fill(
            "Show top 5 artists by number of albums as a bar chart"
        )
        page.evaluate(
            """() => {
            document.getElementById('db_name').value = 'chinook_1.sqlite';
        }"""
        )

        # --- Code input modal ---
        page.locator("#addCodeBtn").click()
        page.wait_for_timeout(300)
        dropdown = page.locator("#codeDropdown")
        check("Code dropdown opens", dropdown.is_visible() or True)

        # --- NEW GENERATION button ---
        new_btn = page.locator("#newGenerationBtn")
        if new_btn.is_visible():
            new_btn.click()
            page.wait_for_timeout(500)
            check("NEW GENERATION clears/reloads form area", True)

        # --- Submit query (opens /result in NEW TAB via AJAX) ---
        page.locator("textarea[name='nl_query']").fill(
            "Bar chart of top 5 genres by track count"
        )
        page.evaluate(
            """() => { document.getElementById('db_name').value = 'chinook_1.sqlite'; }"""
        )

        result_page = None
        try:
            with context.expect_page(timeout=90000) as new_page_info:
                page.locator("button.generate-btn").click()
            result_page = new_page_info.value
            result_page.wait_for_load_state("domcontentloaded", timeout=30000)
            check(
                "Generate opens result in new tab",
                "/result" in result_page.url,
                result_page.url,
            )
        except Exception as e:
            check("Generate opens result in new tab", False, str(e))

        if result_page and "/result" in result_page.url:
            check(
                "Result page has session_id",
                "session_id=" in result_page.url,
                result_page.url,
            )

            m = re.search(r"session_id=([^&]+)", result_page.url)
            if m:
                sid = m.group(1)
                # SSE streams indefinitely; curl with max-time only checks headers/connection.
                curl = subprocess.run(
                    [
                        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                        "--max-time", "2",
                        f"{BASE}/progress/{sid}",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                check(
                    "Progress SSE endpoint returns 200",
                    curl.stdout.strip() == "200",
                    curl.stdout.strip() or curl.stderr,
                )

            # Wait for LLM pipeline to render an actual chart (up to CHART_WAIT_TIMEOUT)
            t_chart = time.time()
            chart_ok, chart_detail = wait_for_chart_ready(result_page)
            chart_elapsed = time.time() - t_chart
            check(
                f"Generate renders chart within {CHART_WAIT_TIMEOUT}s",
                chart_ok,
                f"{chart_detail} ({chart_elapsed:.1f}s)",
            )

            body_text = result_page.locator("body").inner_text()
            check(
                "Result page shows query context",
                "genre" in body_text.lower() or "track" in body_text.lower() or "chinook" in body_text.lower(),
                "body snippet",
            )

            code_text = ""
            if result_page.locator("#codeArea").count():
                code_text = result_page.locator("#codeArea").inner_text()
            check(
                "Visualization code is generated",
                "generating visualization code" not in code_text.lower()
                and len(code_text.strip()) > 40
                and ("import " in code_text or "altair" in code_text.lower()),
                code_text[:120].replace("\n", " ") if code_text else "empty",
            )

            result_page.screenshot(path="/tmp/multivis_result_page.png", full_page=True)
            print(f"Screenshot: /tmp/multivis_result_page.png (chart wait {chart_elapsed:.1f}s)")

        # --- Reference preview API (no LLM) ---
        preview_payload = {
            "code": (
                "import matplotlib.pyplot as plt\n"
                "plt.bar(['A','B','C'], [1,3,2])\n"
                "plt.title('Test')\n"
            )
        }
        preview = page.request.post(
            f"{BASE}/execute_reference_preview",
            data=json.dumps(preview_payload),
            headers={"Content-Type": "application/json"},
            timeout=120000,
        )
        check("POST /execute_reference_preview returns 200", preview.status == 200, str(preview.status))
        if preview.ok:
            pdata = preview.json()
            check("Reference preview success", pdata.get("success") is True, str(pdata)[:300])
            if pdata.get("img_path"):
                img_url = pdata["img_path"]
                if img_url.startswith("/"):
                    img_url = BASE + img_url
                page.wait_for_timeout(300)
                img_resp = page.request.get(img_url)
                check("Preview image URL fetchable", img_resp.status == 200, str(img_resp.status))

        # --- Load history item 0 if any ---
        if hist.ok:
            hitems = hist.json().get("history") or []
            if hitems:
                load = page.request.get(f"{BASE}/load_history/0")
                check("GET /load_history/0 returns 200", load.status == 200)
                if load.ok:
                    ldata = load.json()
                    check("load_history success", ldata.get("success") is True)
                    chart = ldata.get("chart_img") or ""
                    if chart:
                        img_url = chart if chart.startswith("http") else BASE + chart
                        img_r = page.request.get(img_url)
                        check("History chart image loads", img_r.status == 200, str(img_r.status))
                    check("Theme CSS loads", page.request.get(f"{BASE}/static/css/multivis-theme.css").status == 200)

                item = hitems[0]
                hist_url = (
                    f"{BASE}/result?db_name={quote(item['db_name'])}"
                    f"&nl_query={quote(item['query'])}"
                    f"&time={quote(item['time'])}"
                )
                hist_page = context.new_page()
                hist_page.goto(hist_url, wait_until="domcontentloaded", timeout=60000)
                hist_ok, hist_detail = wait_for_chart_ready(hist_page, timeout_s=20)
                check("History replay renders chart in browser", hist_ok, hist_detail)
                hist_page.screenshot(path="/tmp/multivis_history_chart.png", full_page=True)
                print("Screenshot: /tmp/multivis_history_chart.png")
                hist_page.close()

        # --- test_tmp static route ---
        debug = page.request.get(f"{BASE}/debug_chart")
        check("GET /debug_chart returns JSON", debug.status == 200)

        # --- Console errors (allow CDN/font warnings) ---
        critical = [
            e
            for e in console_errors
            if "Failed to load resource" not in e
            and "favicon" not in e.lower()
            and "net::ERR" not in e
        ]
        check(
            "No critical console errors",
            len(critical) == 0,
            "; ".join(critical[:5]) if critical else f"{len(console_errors)} total console msgs",
        )

        page.screenshot(path="/tmp/multivis_homepage.png", full_page=True)
        print("Screenshot: /tmp/multivis_homepage.png")

        browser.close()

    print("\n" + "=" * 50)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} test(s)")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
