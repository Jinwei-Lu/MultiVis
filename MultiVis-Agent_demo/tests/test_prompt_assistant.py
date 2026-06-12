#!/usr/bin/env python3
"""Prompt assistant browser checks for the demo homepage."""
from __future__ import annotations

import os
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import expect, sync_playwright

BASE = os.environ.get("MULTIVIS_BASE_URL", "http://127.0.0.1:8765")
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    if not ok:
        FAILURES.append(f"{name}: {detail}")


def wait_server(timeout: int = 30) -> None:
    for _ in range(timeout):
        try:
            with urlopen(f"{BASE}/", timeout=2) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(1)
    raise RuntimeError(f"Server not reachable at {BASE}")


def main() -> int:
    wait_server()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1360, "height": 860})
        page = context.new_page()
        page.goto(BASE, wait_until="networkidle", timeout=60000)
        page.evaluate("() => localStorage.removeItem('mv_recent_prompts')")
        page.reload(wait_until="networkidle", timeout=60000)

        assistant = page.locator("#promptAssistant")
        expect(assistant).to_be_visible()
        check("Prompt assistant visible", True)

        history_summary = page.locator("#historySummary").inner_text(timeout=5000)
        check(
            "History summary labels sessions accurately",
            "demo samples" not in history_summary and "sessions" in history_summary,
            history_summary,
        )

        bench_sources = page.locator("[data-bench-source]")
        check(
            "Prompt cards expose MultiVis-Bench sources",
            bench_sources.count() == 8,
            f"count={bench_sources.count()}",
        )
        prompt_sources = page.evaluate(
            """() => (window.DEMO_PROMPT_IDEAS || []).map(item => ({
                id: item.id,
                sourceFile: item.sourceFile,
                sourceIndex: item.sourceIndex,
                sourceType: item.sourceType,
                scenario: item.scenario
            }))"""
        )
        check("Prompt data has 8 benchmark entries", len(prompt_sources) == 8, str(prompt_sources))
        check(
            "Prompt data is sourced from MultiVis-Bench",
            all((item.get("sourceFile") or "").startswith("MultiVis-Bench/") for item in prompt_sources),
            str(prompt_sources),
        )
        check(
            "Prompt data records benchmark row indexes",
            all(isinstance(item.get("sourceIndex"), int) for item in prompt_sources),
            str(prompt_sources),
        )
        scenarios = {item.get("scenario") for item in prompt_sources}
        check(
            "Prompt data covers four MultiVis scenarios",
            scenarios == {"Text2Vis", "Image-guided", "Code-guided", "Vis Modify"},
            str(sorted(scenarios)),
        )

        stacked = page.locator("[data-prompt-id='activity-stacked']")
        expect(stacked).to_be_visible()
        stacked.click()
        page.wait_for_timeout(300)
        query_value = page.locator("textarea[name='nl_query']").input_value()
        db_value = page.locator("#db_name").input_value()
        check("Curated prompt fills query", "students" in query_value.lower() and "faculty" in query_value.lower(), query_value)
        check("Curated prompt switches database", db_value == "activity_1.sqlite", db_value)

        page.locator("[data-prompt-id='image-campus-stacked']").click()
        page.wait_for_timeout(500)
        image_state = page.evaluate(
            """() => ({
                files: document.querySelector('#ref_image')?.files?.length || 0,
                name: document.querySelector('#file-name')?.textContent || '',
                infoDisplay: getComputedStyle(document.querySelector('#image-info')).display,
                benchmarkUrl: document.querySelector('#benchmark_ref_image_url')?.value || '',
                benchmarkName: document.querySelector('#benchmark_ref_image_name')?.value || '',
                badge: document.querySelector('#image-source-badge')?.textContent || ''
            })"""
        )
        check(
            "Image-guided prompt attaches benchmark image",
            image_state["files"] == 1 or image_state["benchmarkUrl"].endswith("/stacked_bar_chart.png"),
            str(image_state),
        )
        check("Image-guided prompt labels image source", "stacked_bar_chart" in image_state["name"], str(image_state))
        check("Image-guided prompt marks benchmark source", image_state["badge"] == "Benchmark", str(image_state))
        image_overflow_state = page.evaluate(
            """() => {
                const longName = 'Very_Long_MultiVis_Bench_Image_File_Name___With_Many_Chart_Details___stacked_bar_chart_reference_preview.png';
                document.querySelector('#file-name').innerHTML = `<a href="#">${longName}</a>`;
                const info = document.querySelector('#image-info');
                const name = document.querySelector('#file-name');
                const link = name.querySelector('a');
                return {
                    infoOverflow: getComputedStyle(info).overflow,
                    nameOverflow: getComputedStyle(name).overflow,
                    linkOverflow: getComputedStyle(link).overflow,
                    linkTextOverflow: getComputedStyle(link).textOverflow,
                    linkWhiteSpace: getComputedStyle(link).whiteSpace,
                    infoFits: info.scrollWidth <= info.clientWidth + 1
                };
            }"""
        )
        check(
            "Uploaded image filename stays inside its chip",
            image_overflow_state["infoFits"]
            and image_overflow_state["linkOverflow"] == "hidden"
            and image_overflow_state["linkTextOverflow"] == "ellipsis"
            and image_overflow_state["linkWhiteSpace"] == "nowrap",
            str(image_overflow_state),
        )

        page.locator("[data-prompt-id='code-chinook-pie']").click()
        page.wait_for_timeout(300)
        code_state = page.evaluate(
            """() => ({
                code: document.querySelector('#code')?.value || '',
                name: document.querySelector('#code-file-name')?.textContent || '',
                isDatabaseCode: document.querySelector('#is_database_code')?.checked || false,
                infoDisplay: getComputedStyle(document.querySelector('#code-info')).display,
                badge: document.querySelector('#code-source-badge')?.textContent || ''
            })"""
        )
        check("Code-guided prompt attaches benchmark reference code", "ax.pie" in code_state["code"], code_state["code"][:160])
        check("Code-guided prompt marks code as external reference", code_state["isDatabaseCode"] is False, str(code_state))
        check("Code-guided prompt marks benchmark source", code_state["badge"] == "Benchmark", str(code_state))

        page.locator("[data-prompt-id='modify-activity-stacked']").click()
        page.wait_for_timeout(300)
        modify_state = page.evaluate(
            """() => ({
                code: document.querySelector('#code')?.value || '',
                name: document.querySelector('#code-file-name')?.textContent || '',
                isDatabaseCode: document.querySelector('#is_database_code')?.checked || false,
                badge: document.querySelector('#code-source-badge')?.textContent || ''
            })"""
        )
        check("Vis Modify prompt attaches original chart code", "sqlite3.connect('database/activity_1.sqlite')" in modify_state["code"], modify_state["code"][:160])
        check("Vis Modify prompt marks code as database-based", modify_state["isDatabaseCode"] is True, str(modify_state))
        check("Vis Modify prompt shows DB code badge", modify_state["badge"] == "DB Code", str(modify_state))

        stacked.click()
        page.wait_for_timeout(300)
        cleared_state = page.evaluate(
            """() => ({
                imageFiles: document.querySelector('#ref_image')?.files?.length || 0,
                code: document.querySelector('#code')?.value || '',
                isDatabaseCode: document.querySelector('#is_database_code')?.checked || false,
                benchmarkUrl: document.querySelector('#benchmark_ref_image_url')?.value || '',
                imageBadge: document.querySelector('#image-source-badge')?.textContent || '',
                codeBadge: document.querySelector('#code-source-badge')?.textContent || ''
            })"""
        )
        check(
            "Text2Vis prompt clears stale image/code context",
            cleared_state == {
                "imageFiles": 0,
                "code": "",
                "isDatabaseCode": False,
                "benchmarkUrl": "",
                "imageBadge": "",
                "codeBadge": "",
            },
            str(cleared_state),
        )

        page.locator("#promptInspireBtn").click()
        page.wait_for_timeout(300)
        inspired_query = page.locator("textarea[name='nl_query']").input_value()
        inspired_db = page.locator("#db_name").input_value()
        check("Inspire Me fills a prompt", len(inspired_query.strip()) > 20, inspired_query)
        check("Inspire Me selects a demo database", inspired_db in {"chinook_1.sqlite", "activity_1.sqlite"}, inspired_db)

        custom_prompt = "Audience request: show a compact comparison of activity participation by role."
        page.locator("textarea[name='nl_query']").fill(custom_prompt)
        page.locator("textarea[name='nl_query']").blur()
        page.wait_for_timeout(400)
        recent = page.locator("[data-recent-prompt]").filter(has_text="Audience request")
        expect(recent).to_be_visible()
        check("Recent input appears after blur", True)

        page.locator("textarea[name='nl_query']").fill("")
        recent.click()
        page.wait_for_timeout(300)
        restored_query = page.locator("textarea[name='nl_query']").input_value()
        check("Recent input restores query", restored_query == custom_prompt, restored_query)

        page.locator("#clearRecentPromptsBtn").click()
        page.wait_for_timeout(300)
        has_recent = page.locator("[data-recent-prompt]").count() > 0
        check("Recent inputs can be cleared", not has_recent, f"count={page.locator('[data-recent-prompt]').count()}")

        page.screenshot(path="/tmp/multivis_prompt_assistant.png", full_page=True)
        print("Screenshot: /tmp/multivis_prompt_assistant.png")
        browser.close()

    if FAILURES:
        print("\nFAILED")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print("\nALL PROMPT ASSISTANT TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
