#!/usr/bin/env python3
"""Unit checks for live code/chart progress events without calling an LLM."""
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

app_module = importlib.import_module("app")
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    if not ok:
        FAILURES.append(f"{name}: {detail}")


class FakeCoordinatorAgent:
    def __init__(self, *args, **kwargs):
        self.visualization_code = None
        self.chart_json_path = None

    def _generate_visualization_code_tool(self):
        self.visualization_code = (
            "import altair as alt\n"
            "chart = alt.Chart(data).mark_bar()\n"
            "# fake live preview"
        )
        return {"status": True, "message": "generated"}

    def _execute_visualization_code(self, code: str, iteration: int) -> str:
        os.makedirs("test_tmp", exist_ok=True)
        json_path = Path("test_tmp") / f"fake_live_preview_{iteration}.vega.json"
        json_path.write_text(
            json.dumps(
                {
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "data": {"values": [{"label": "A", "value": 1}]},
                    "mark": "bar",
                    "encoding": {
                        "x": {"field": "label", "type": "nominal"},
                        "y": {"field": "value", "type": "quantitative"},
                    },
                }
            ),
            encoding="utf-8",
        )
        self.chart_json_path = str(json_path)
        return f"./test_tmp/fake_live_preview_{iteration}.png"

    def process(self, **kwargs):
        self._generate_visualization_code_tool()
        return {
            "vis_code": self.visualization_code,
            "vis_code_iter": self.visualization_code,
            "chart_img": "/test_tmp/fake_live_preview_1.png",
            "chart_json": "/test_tmp/fake_live_preview_1.vega.json",
            "sql": "select 1",
            "sql_iter": "select 1",
            "eval_result": "fake pass",
        }


def run_tests() -> int:
    original = app_module.CoordinatorAgent
    session_id = "unit_live_progress"
    try:
        app_module.CoordinatorAgent = FakeCoordinatorAgent
        app_module.clear_progress(session_id)
        app_module.process_async(session_id, "", "", None, "", "", None, "fake@fake")
        events = app_module.get_progress(session_id)
    finally:
        app_module.CoordinatorAgent = original

    steps = [event["step"] for event in events]
    check("Progress includes code update", "code_update" in steps, str(steps))
    check("Progress includes live code iteration", "code_iteration" in steps, str(steps))
    check("Progress includes chart update", "chart_update" in steps, str(steps))

    code_iteration = next((event for event in events if event["step"] == "code_iteration"), {})
    chart_update = next((event for event in events if event["step"] == "chart_update"), {})
    complete = next((event for event in events if event["step"] == "complete"), {})

    check(
        "Code iteration carries latest code",
        "fake live preview" in (code_iteration.get("data", {}).get("code") or ""),
        str(code_iteration.get("data")),
    )
    check(
        "Chart update prefers Vega JSON path",
        chart_update.get("data", {}).get("chart_json_path") == "/test_tmp/fake_live_preview_1.vega.json",
        str(chart_update.get("data")),
    )
    check("Complete event still emitted", bool(complete), str(steps))

    if FAILURES:
        print("\nFAILURES:")
        for failure in FAILURES:
            print(f"- {failure}")
        return 1
    print("\nALL LIVE PROGRESS EVENT TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
