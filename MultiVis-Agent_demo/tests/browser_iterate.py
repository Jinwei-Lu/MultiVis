#!/usr/bin/env python3
"""Browser iteration helper — screenshots + interaction checks."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

BASE = "http://127.0.0.1:8765"
OUT = Path("/tmp/multivis_browser_iter")
OUT.mkdir(exist_ok=True)
issues: list[str] = []


def shot(page, name: str) -> None:
    path = OUT / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"  screenshot: {path}")


def run() -> int:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_demo_history.py")],
        check=True,
        cwd=ROOT,
    )
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        logs: list[str] = []
        page.on("console", lambda m: logs.append(f"{m.type}: {m.text}") if m.type == "error" else None)

        # --- Homepage ---
        page.goto(BASE, wait_until="networkidle", timeout=60000)
        page.wait_for_selector("img.history-thumb", timeout=15000)
        shot(page, "01_home")
        if not page.locator(".mv-demo-banner").is_visible():
            issues.append("Demo banner not visible")
        n_hist = page.locator(".history-list .history-item").count()
        if n_hist != 4:
            issues.append(f"Expected 4 history items, got {n_hist}")
        thumb_count = page.locator("img.history-thumb").count()
        if thumb_count < 3:
            issues.append(f"Expected history thumbnails, got {thumb_count}")
        if not page.locator("#db-file-name").inner_text().strip():
            issues.append("Default database name not shown")

        # Quick chip
        page.locator(".mv-chip", has_text="Stacked bar").click()
        page.wait_for_timeout(400)
        q = page.locator("textarea[name='nl_query']").input_value()
        if "Stacked bar" not in q:
            issues.append("Quick query chip did not fill textarea")
        shot(page, "02_quick_chip")

        # Schema visible
        if not page.locator("#dbStructureSection").is_visible():
            issues.append("DB schema section not visible after default db load")
        shot(page, "03_schema")

        # Schema collapse toggle
        page.locator("#schemaToggleBtn").click()
        page.wait_for_timeout(300)
        collapsed = page.locator("#dbStructureSection.schema-collapsed").count() > 0
        if not collapsed:
            issues.append("Schema toggle did not collapse panel")
        page.locator("#schemaToggleBtn").click()
        shot(page, "03b_schema_toggle")

        # Click first history item
        page.locator(".history-item").first.click()
        page.wait_for_timeout(800)
        # History mode may open result in new tab
        if len(ctx.pages) > 1:
            rp = ctx.pages[-1]
            rp.wait_for_load_state("domcontentloaded")
            shot(rp, "04_history_result_tab")
            if "/result" not in rp.url:
                issues.append(f"History click did not open result: {rp.url}")
            body = rp.locator("body").inner_text()
            if "Generating" in body and "chart" not in body.lower():
                pass  # may still be loading demo
            # Check chart area
            has_img = rp.locator("img").count() > 0 or rp.locator("#vis").count() > 0
            if not has_img and "stacked" not in body.lower():
                issues.append("History result page may lack chart content")
        else:
            issues.append("History click did not open new tab")

        # Fresh generate flow (skip if demo history should stay pristine)
        page.goto(BASE, wait_until="networkidle")
        page.locator("textarea[name='nl_query']").fill("Top 5 genres by track count as a bar chart")
        page.evaluate("document.getElementById('db_name').value='chinook_1.sqlite'")
        with ctx.expect_page(timeout=90000) as pinfo:
            page.locator("button.generate-btn").click()
        np = pinfo.value
        np.wait_for_load_state("domcontentloaded")
        np.wait_for_timeout(2500)
        shot(np, "05_generate_result")
        if "/result" not in np.url:
            issues.append("Generate did not open result page")

        # Mobile viewport + history drawer
        page.set_viewport_size({"width": 390, "height": 844})
        page.goto(BASE, wait_until="networkidle")
        page.wait_for_selector("#openSidebarBtn", timeout=10000)
        page.locator("#openSidebarBtn").click()
        page.wait_for_timeout(400)
        if page.locator(".layout.sidebar-drawer-open").count() == 0:
            issues.append("Mobile history drawer did not open")
        shot(page, "06_mobile_drawer_open")
        page.evaluate("() => { if (typeof setSidebarOpen === 'function') setSidebarOpen(false); }")
        page.wait_for_timeout(300)
        if page.locator(".layout.sidebar-drawer-open").count() > 0:
            issues.append("Mobile drawer did not close")
        shot(page, "06b_mobile_drawer_closed")

        # Result page theme (from history tab if available)
        if len(ctx.pages) > 1:
            rp = ctx.pages[1]
            if "/result" in rp.url:
                if not rp.locator("body.result-page").count():
                    issues.append("Result page missing result-page body class")
                shot(rp, "07_result_theme")

        err_logs = [l for l in logs if l and "favicon" not in l.lower()]
        if err_logs:
            issues.append(f"Console errors: {err_logs[:5]}")

        browser.close()

    # Restore the canonical 4-item demo history (the fresh-generate flow above
    # appends a 5th entry; reset it so the shipped state is always pristine).
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_demo_history.py")],
        check=True,
        cwd=ROOT,
    )

    print("\n=== Browser iteration ===")
    if issues:
        print("ISSUES:")
        for i in issues:
            print(f"  - {i}")
        return 1
    print("No issues found.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
