#!/usr/bin/env python3
"""Fast browser checks for result-page failure states."""
from __future__ import annotations

import os
import sys
import time
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("MULTIVIS_BASE_URL", "http://127.0.0.1:8765")
FAILURES: list[str] = []
BENCH_REF_CODE = (
    ROOT.parent
    / "MultiVis-Bench"
    / "vis_modify"
    / "Advanced Calculations___gantt_chart___chinook_1.py"
).read_text(encoding="utf-8")
ACTIVITY_BASENAME_REF_CODE = """\
import altair as alt
import pandas as pd
import sqlite3

con = sqlite3.connect('activity_1.sqlite')
df = pd.read_sql_query(
    \"\"\"
    SELECT a.activity_name, AVG(s.age) AS avg_age
    FROM Participates_in p
    JOIN Student s ON s.StuID = p.StuID
    JOIN Activity a ON a.actid = p.actid
    GROUP BY a.activity_name
    \"\"\",
    con,
)

chart = (
    alt.Chart(df)
    .mark_point(size=140, filled=False)
    .encode(
        x=alt.X('activity_name:N', title='Activity'),
        y=alt.Y('avg_age:Q', title='Average age'),
        tooltip=['activity_name', 'avg_age'],
    )
    .properties(title='Reference code with basename sqlite path')
)
chart
"""


def packaged_app_root() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "MultiVisAgent"
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home())) / "MultiVisAgent"
    return Path.home() / ".local" / "share" / "MultiVisAgent"


def write_test_tmp_fixture(filename: str, content: str) -> None:
    """Write a static-route fixture for both dev and packaged app roots."""
    targets = [
        ROOT / "test_tmp" / filename,
        packaged_app_root() / "test_tmp" / filename,
    ]
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


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
            with urlopen(f"{BASE}/", timeout=2) as response:
                if response.status == 200:
                    print(f"Server ready ({i + 1}s)")
                    return
        except Exception:
            time.sleep(1)
    raise RuntimeError(f"Server not reachable at {BASE}")


def run_tests() -> int:
    wait_server()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 820})
        page = context.new_page()

        page.goto(
            f"{BASE}/result?session_id=manual_error_state&db_name=chinook_1.sqlite&nl_query={quote('Manual error-state check')}",
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#chartArea", timeout=15000)

        page.evaluate(
            """() => {
                window.handleProgressUpdate({
                    step: 'error',
                    status: 'error',
                    data: 'Forced backend failure for UI regression test'
                });
            }"""
        )
        chart_text = page.locator("#chartArea").inner_text(timeout=5000)
        code_text = page.locator("#codeArea").inner_text(timeout=5000)
        chart_style = page.locator("#chartArea").evaluate(
            """el => ({
                color: getComputedStyle(el).color,
                background: getComputedStyle(el).backgroundColor,
                whiteSpace: getComputedStyle(el).whiteSpace,
            })"""
        )
        check("Error event renders visible chart error", "Forced backend failure" in chart_text, chart_text[:220])
        check(
            "Error event uses readable chart error styling",
            chart_style["background"] != "rgb(255, 255, 255)" and chart_style["color"] != "rgb(243, 244, 246)",
            str(chart_style),
        )
        check("Error event clears code loading placeholder", "Generating visualization code" not in code_text, code_text[:220])

        page.goto(
            f"{BASE}/result?session_id=manual_complete_empty&db_name=chinook_1.sqlite&nl_query={quote('Manual empty result check')}",
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#chartArea", timeout=15000)
        page.evaluate("() => window.updateFinalResults({})")
        chart_text = page.locator("#chartArea").inner_text(timeout=5000)
        code_text = page.locator("#codeArea").inner_text(timeout=5000)
        check("Empty final result renders visible chart error", "No chart was generated" in chart_text, chart_text[:220])
        check("Empty final result renders visible code message", "No visualization code generated" in code_text, code_text[:220])

        page.evaluate(
            """() => window.updateFinalResults({
                vis_code: "import altair as alt\\nchart = alt.Chart(data).mark_bar()",
                chart_img: "/test_tmp/should_not_render_generated_png.png"
            })"""
        )
        image_only_state = page.locator("#chartArea").evaluate(
            """el => ({
                className: el.className,
                imageCount: el.querySelectorAll('img[src]').length,
                text: el.innerText,
            })"""
        )
        check(
            "Generated chart refuses PNG-only fallback",
            "result-error-state" in image_only_state["className"]
            and image_only_state["imageCount"] == 0
            and "Vega JSON" in image_only_state["text"],
            str(image_only_state),
        )

        page.goto(
            f"{BASE}/result?session_id=manual_pending_after_code&db_name=chinook_1.sqlite&nl_query={quote('Manual pending after code check')}",
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#chartArea", timeout=15000)
        page.evaluate(
            """() => {
                window.handleProgressUpdate({
                    step: 'code_update',
                    status: 'info',
                    data: "import sqlite3\\nimport pandas as pd\\nimport altair as alt\\n# stage code exists"
                });
            }"""
        )
        pending_after_code = page.locator("#chartArea").evaluate(
            """el => ({
                className: el.className,
                imageCount: el.querySelectorAll('img[src]').length,
                vegaCount: el.querySelectorAll('.vega-embed svg, .vega-embed canvas').length,
                text: el.innerText,
            })"""
        )
        check(
            "Code update shows chart execution pending state",
            "chart-pending-state" in pending_after_code["className"]
            and pending_after_code["imageCount"] == 0
            and pending_after_code["vegaCount"] == 0
            and "Executing" in pending_after_code["text"],
            str(pending_after_code),
        )
        page.evaluate(
            """() => {
                window.handleProgressUpdate({
                    step: 'iteration_execution',
                    status: 'error',
                    data: "sqlite database path could not be opened"
                });
            }"""
        )
        execution_error_state = page.locator("#chartArea").evaluate(
            """el => ({
                className: el.className,
                imageCount: el.querySelectorAll('img[src]').length,
                text: el.innerText,
            })"""
        )
        check(
            "Execution error replaces chart loading state",
            "result-error-state" in execution_error_state["className"]
            and execution_error_state["imageCount"] == 0
            and "sqlite database path could not be opened" in execution_error_state["text"],
            str(execution_error_state),
        )

        page.goto(
            f"{BASE}/result?session_id=manual_png_only_update&db_name=chinook_1.sqlite&nl_query={quote('Manual PNG-only live update check')}",
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#chartArea", timeout=15000)
        page.evaluate(
            """() => {
                window.handleProgressUpdate({
                    step: 'chart_update',
                    status: 'info',
                    data: {
                        iteration: 1,
                        code: "import matplotlib.pyplot as plt",
                        chart_path: "/test_tmp/png_only_live_preview.png",
                        chart_type: "image"
                    }
                });
            }"""
        )
        png_only_update_state = page.locator("#chartArea").evaluate(
            """el => ({
                className: el.className,
                imageCount: el.querySelectorAll('img[src]').length,
                text: el.innerText,
            })"""
        )
        check(
            "PNG-only live update reports missing Vega JSON",
            "result-error-state" in png_only_update_state["className"]
            and png_only_update_state["imageCount"] == 0
            and "no Vega JSON" in png_only_update_state["text"],
            str(png_only_update_state),
        )

        write_test_tmp_fixture(
            "live_iteration_test.vega.json",
            json.dumps(
                {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "data": {"values": [{"kind": "Draft", "value": 3}, {"kind": "Refined", "value": 7}]},
                    "mark": "bar",
                    "encoding": {
                        "x": {"field": "kind", "type": "nominal"},
                        "y": {"field": "value", "type": "quantitative"},
                    },
                }
            ),
        )
        page.evaluate(
            """() => {
                window.handleProgressUpdate({
                    step: 'code_iteration',
                    status: 'info',
                    data: {
                        iteration: 2,
                        code: "import altair as alt\\nchart = alt.Chart(data).mark_bar()\\n# live iteration marker",
                        chart_json_path: '/test_tmp/live_iteration_test.vega.json',
                        timestamp: '12:00:00'
                    }
                });
            }"""
        )
        page.wait_for_selector("#chartArea .vega-embed svg", timeout=10000)
        live_code = page.locator("#codeArea").inner_text(timeout=5000)
        live_chart_state = page.locator("#chartArea").evaluate(
            """el => ({
                className: el.className,
                jsonPath: el.getAttribute('data-json-path'),
                svgCount: el.querySelectorAll('.vega-embed svg').length,
                imageCount: el.querySelectorAll('img[src]').length,
            })"""
        )
        check("Realtime iteration updates code", "live iteration marker" in live_code, live_code[:220])
        check(
            "Realtime iteration renders latest chart JSON",
            live_chart_state["jsonPath"] == "/test_tmp/live_iteration_test.vega.json"
            and live_chart_state["svgCount"] > 0
            and live_chart_state["imageCount"] == 0,
            str(live_chart_state),
        )

        page.evaluate(
            """() => {
                window.__mainVegaEmbedTargets = [];
                if (!window.__originalVegaEmbedForTest) {
                    window.__originalVegaEmbedForTest = window.vegaEmbed;
                }
                window.vegaEmbed = function(target, spec, options) {
                    window.__mainVegaEmbedTargets.push({
                        targetType: typeof target,
                        targetId: target && target.id ? target.id : ''
                    });
                    return window.__originalVegaEmbedForTest(target, spec, options);
                };
                window.updateChartDisplay('/test_tmp/live_iteration_test.vega.json');
            }"""
        )
        page.wait_for_selector("#chartArea .vega-embed svg", timeout=10000)
        embed_target_state = page.evaluate(
            """() => {
                const targets = window.__mainVegaEmbedTargets || [];
                window.vegaEmbed = window.__originalVegaEmbedForTest || window.vegaEmbed;
                return targets[targets.length - 1] || {};
            }"""
        )
        check(
            "Main chart embeds into scoped DOM node",
            embed_target_state.get("targetType") == "object"
            and str(embed_target_state.get("targetId", "")).startswith("vis-"),
            str(embed_target_state),
        )

        write_test_tmp_fixture(
            "layered_selection_collision.vega.json",
            json.dumps(
                {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "data": {
                        "values": [
                            {"GenreName": "Rock", "TrackCount": 1297},
                            {"GenreName": "Latin", "TrackCount": 579},
                            {"GenreName": "Metal", "TrackCount": 374},
                        ]
                    },
                    "layer": [
                        {
                            "mark": "bar",
                            "encoding": {
                                "x": {"field": "TrackCount", "type": "quantitative"},
                                "y": {"field": "GenreName", "type": "nominal", "sort": "-x"},
                            },
                        },
                        {
                            "mark": {"type": "text", "align": "left", "baseline": "middle", "dx": 3},
                            "encoding": {
                                "x": {"field": "TrackCount", "type": "quantitative"},
                                "y": {"field": "GenreName", "type": "nominal", "sort": "-x"},
                                "text": {"field": "TrackCount", "type": "quantitative"},
                            },
                        },
                    ],
                    "params": [
                        {"name": "select", "select": {"type": "point", "on": "click"}},
                        {"name": "highlight", "select": {"type": "point", "on": "pointerover"}},
                    ],
                }
            ),
        )
        page.evaluate("() => window.updateChartDisplay('/test_tmp/layered_selection_collision.vega.json')")
        page.wait_for_selector("#chartArea .vega-embed svg", timeout=10000)
        layered_chart_state = page.locator("#chartArea").evaluate(
            """el => ({
                className: el.className,
                svgCount: el.querySelectorAll('.vega-embed svg').length,
                imageCount: el.querySelectorAll('img[src]').length,
                text: el.innerText,
            })"""
        )
        check(
            "Layered Vega chart strips collision-prone generic selections",
            "result-error-state" not in layered_chart_state["className"]
            and layered_chart_state["svgCount"] > 0
            and layered_chart_state["imageCount"] == 0
            and "Duplicate signal" not in layered_chart_state["text"],
            str(layered_chart_state)[:320],
        )

        page.goto(
            f"{BASE}/result?session_id=manual_reference_preview&db_name=chinook_1.sqlite&nl_query={quote('Manual reference preview check')}",
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#refArea", state="attached", timeout=15000)
        page.evaluate(
            """() => {
                document.getElementById('tmpl_uploaded_code').textContent = JSON.stringify(
                    "import matplotlib.pyplot as plt\\nplt.plot([1, 2, 3], [3, 1, 4])\\nplt.title('Reference Preview')\\nplt.show()"
                );
                document.dispatchEvent(new Event('DOMContentLoaded'));
            }"""
        )
        page.wait_for_selector("#refArea img[src], #refArea .vega-embed canvas, #refArea .vega-embed svg", timeout=20000)
        ref_state = page.locator("#refPreviewWrapper").evaluate(
            """el => ({
                display: getComputedStyle(el).display,
                imageCount: el.querySelectorAll('#refArea img[src]').length,
                vegaCount: el.querySelectorAll('#refArea .vega-embed canvas, #refArea .vega-embed svg').length,
            })"""
        )
        check(
            "Reference Preview renders before final result",
            ref_state["display"] != "none" and (ref_state["imageCount"] > 0 or ref_state["vegaCount"] > 0),
            str(ref_state),
        )

        page.goto(
            f"{BASE}/result?session_id=manual_bench_reference_preview&db_name=chinook_1.sqlite&nl_query={quote('Manual benchmark reference preview check')}",
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#refArea", state="attached", timeout=15000)
        page.evaluate(
            """(code) => {
                document.getElementById('tmpl_uploaded_code').textContent = JSON.stringify(code);
                document.dispatchEvent(new Event('DOMContentLoaded'));
            }""",
            BENCH_REF_CODE,
        )
        page.wait_for_selector("#refArea .vega-embed svg", timeout=25000)
        bench_ref_state = page.locator("#refPreviewWrapper").evaluate(
            """el => ({
                display: getComputedStyle(el).display,
                fallback: el.querySelector('#refArea.reference-preview-fallback') !== null,
                imageCount: el.querySelectorAll('#refArea img[src]').length,
                svgCount: el.querySelectorAll('#refArea .vega-embed svg').length,
            })"""
        )
        check(
            "MultiVis-Bench Altair reference code renders",
            bench_ref_state["display"] != "none"
            and not bench_ref_state["fallback"]
            and bench_ref_state["imageCount"] == 0
            and bench_ref_state["svgCount"] > 0,
            str(bench_ref_state),
        )

        page.goto(
            f"{BASE}/result?session_id=manual_activity_basename_reference&db_name=activity_1.sqlite&nl_query={quote('Manual activity basename reference preview check')}",
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#refArea", state="attached", timeout=15000)
        page.evaluate(
            """(code) => {
                document.getElementById('tmpl_uploaded_code').textContent = JSON.stringify(code);
                document.dispatchEvent(new Event('DOMContentLoaded'));
            }""",
            ACTIVITY_BASENAME_REF_CODE,
        )
        page.wait_for_selector("#refArea .vega-embed svg", timeout=25000)
        activity_ref_state = page.locator("#refPreviewWrapper").evaluate(
            """el => ({
                display: getComputedStyle(el).display,
                fallback: el.querySelector('#refArea.reference-preview-fallback') !== null,
                imageCount: el.querySelectorAll('#refArea img[src]').length,
                svgCount: el.querySelectorAll('#refArea .vega-embed svg').length,
                text: el.innerText,
            })"""
        )
        check(
            "Activity reference code resolves packaged database basename",
            activity_ref_state["display"] != "none"
            and not activity_ref_state["fallback"]
            and activity_ref_state["imageCount"] == 0
            and activity_ref_state["svgCount"] > 0,
            str(activity_ref_state)[:320],
        )

        page.goto(
            f"{BASE}/result?session_id=manual_reference_failure_preview&db_name=chinook_1.sqlite&nl_query={quote('Manual reference failure preview check')}",
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#refArea", state="attached", timeout=15000)
        page.evaluate(
            """() => {
                document.getElementById('tmpl_uploaded_code').textContent = JSON.stringify(
                    "import altair as alt\\nraise RuntimeError('reference preview forced failure')"
                );
                document.dispatchEvent(new Event('DOMContentLoaded'));
            }"""
        )
        page.wait_for_selector("#refArea.reference-preview-fallback", timeout=20000)
        fallback_state = page.locator("#refArea").evaluate(
            """el => ({
                background: getComputedStyle(el).backgroundColor,
                color: getComputedStyle(el).color,
                text: el.innerText,
            })"""
        )
        check(
            "Reference Preview failure uses readable fallback",
            fallback_state["background"] == "rgb(255, 255, 255)"
            and "Reference preview unavailable" in fallback_state["text"]
            and "reference preview forced failure" in fallback_state["text"],
            str(fallback_state)[:320],
        )

        progress_state = page.locator("#progressOverlay").evaluate(
            """el => ({
                bottom: getComputedStyle(el).bottom,
                top: getComputedStyle(el).top,
                right: getComputedStyle(el).right,
                position: getComputedStyle(el).position,
                marginTop: getComputedStyle(el).marginTop,
                containerTop: document.querySelector('.container').getBoundingClientRect().top,
                overlayTop: el.getBoundingClientRect().top,
            })"""
        )
        check(
            "Processing status is a floating overlay",
            progress_state["position"] == "fixed"
            and progress_state["marginTop"] == "0px"
            and progress_state["containerTop"] < 130,
            str(progress_state),
        )

        page.evaluate(
            """async () => {
                const chartArea = document.querySelector('#chartArea');
                chartArea.className = 'generated-code has-interactive-chart';
                chartArea.style.backgroundColor = '#ffffff';
                chartArea.innerHTML = '<div id="vis" style="width: 360px; height: 260px;"></div>';
                if (window.ensureVegaEmbedReady) {
                    await window.ensureVegaEmbedReady();
                }
                await window.vegaEmbed('#vis', {
                    '$schema': 'https://vega.github.io/schema/vega-lite/v5.json',
                    data: { values: [{ category: 'A', value: 2 }, { category: 'B', value: 4 }] },
                    mark: 'bar',
                    encoding: {
                        x: { field: 'category', type: 'nominal' },
                        y: { field: 'value', type: 'quantitative' }
                    }
                }, { actions: true, renderer: 'svg' });
                const details = document.querySelector('.vega-embed details');
                if (details) details.open = true;
            }"""
        )
        page.wait_for_selector(".vega-embed details[open] .vega-actions", timeout=10000)
        action_style = page.locator(".vega-embed details[open]").evaluate(
            """el => {
                const actions = el.querySelector('.vega-actions');
                const link = actions.querySelector('a');
                const summary = el.querySelector('summary');
                const summarySvg = summary.querySelector('svg');
                const rect = node => {
                    const box = node.getBoundingClientRect();
                    return { width: box.width, height: box.height };
                };
                return {
                    detailsBackground: getComputedStyle(el).backgroundColor,
                    detailsOpacity: getComputedStyle(el).opacity,
                    actionsBackground: getComputedStyle(actions).backgroundColor,
                    linkBackground: getComputedStyle(link).backgroundColor,
                    linkColor: getComputedStyle(link).color,
                    detailsRect: rect(el),
                    summaryRect: rect(summary),
                    summarySvgRect: rect(summarySvg),
                };
            }"""
        )
        check(
            "Vega actions menu is opaque",
            action_style["detailsBackground"] == "rgb(255, 255, 255)"
            and action_style["actionsBackground"] == "rgb(255, 255, 255)"
            and action_style["detailsOpacity"] == "1",
            str(action_style),
        )
        check(
            "Vega actions button stays compact",
            action_style["summaryRect"]["width"] <= 40
            and action_style["summaryRect"]["height"] <= 40
            and action_style["summarySvgRect"]["width"] <= 18
            and action_style["summarySvgRect"]["height"] <= 18
            and action_style["detailsRect"]["width"] <= 280,
            str(action_style),
        )

        page.goto(
            f"{BASE}/result?session_id=manual_clean_reference_preview&db_name=chinook_1.sqlite&nl_query={quote('Clean reference preview screenshot')}",
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#refArea", state="attached", timeout=15000)
        page.evaluate(
            """async (code) => {
                document.getElementById('tmpl_uploaded_code').textContent = JSON.stringify(code);
                document.dispatchEvent(new Event('DOMContentLoaded'));
                window.updateFinalResults({
                    vis_code_iter: "import altair as alt\\nchart = alt.Chart(data).mark_bar()\\n# clean reference screenshot",
                    chart_json: "/test_tmp/live_iteration_test.vega.json",
                    eval_result: "Clean screenshot state"
                });
                const overlay = document.getElementById('progressOverlay');
                if (overlay) overlay.style.display = 'none';
            }""",
            BENCH_REF_CODE,
        )
        page.wait_for_selector("#chartArea .vega-embed svg", timeout=10000)
        page.wait_for_selector("#refArea .vega-embed svg", timeout=25000)
        clean_chart_state = page.locator("#chartArea").evaluate(
            """el => ({
                imageCount: el.querySelectorAll('img[src]').length,
                svgCount: el.querySelectorAll('.vega-embed svg').length,
                jsonPath: el.getAttribute('data-json-path'),
            })"""
        )
        clean_screenshot_state = page.locator("#refArea").evaluate(
            """el => ({
                fallback: el.classList.contains('reference-preview-fallback'),
                text: el.innerText,
                imageCount: el.querySelectorAll('img[src]').length,
                svgCount: el.querySelectorAll('.vega-embed svg').length,
                bottomGap: (() => {
                    const svg = el.querySelector('.vega-embed svg');
                    if (!svg) return -1;
                    return Math.round(el.getBoundingClientRect().bottom - svg.getBoundingClientRect().bottom);
                })(),
            })"""
        )
        check(
            "Clean screenshot generated chart is Vega, not image",
            clean_chart_state["jsonPath"] == "/test_tmp/live_iteration_test.vega.json"
            and clean_chart_state["svgCount"] > 0
            and clean_chart_state["imageCount"] == 0,
            str(clean_chart_state),
        )
        check(
            "Clean screenshot Reference Preview is Vega, not image",
            not clean_screenshot_state["fallback"]
            and clean_screenshot_state["svgCount"] > 0
            and clean_screenshot_state["imageCount"] == 0
            and clean_screenshot_state["bottomGap"] >= 48
            and "Reference preview unavailable" not in clean_screenshot_state["text"],
            str(clean_screenshot_state)[:320],
        )

        page.screenshot(path="/tmp/multivis_result_error_states.png", full_page=True)
        print("Screenshot: /tmp/multivis_result_error_states.png")
        browser.close()

    if FAILURES:
        print("\nFAILURES:")
        for failure in FAILURES:
            print(f"- {failure}")
        return 1
    print("\nALL RESULT ERROR STATE TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
