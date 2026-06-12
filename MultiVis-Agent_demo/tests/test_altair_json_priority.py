#!/usr/bin/env python3
"""Regression checks for Altair live-preview execution."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vis_system.code_generation_agent import CodeGenerationAgent  # noqa: E402

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" - {detail}"
    print(line)
    if not ok:
        FAILURES.append(f"{name}: {detail}")


def main() -> int:
    tmp_dir = ROOT / "test_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    output_png = tmp_dir / "altair_json_priority.png"
    output_json = tmp_dir / "altair_json_priority.vega.json"
    user_save_png = tmp_dir / "user_requested_save_should_not_run.png"
    for path in (output_png, output_json, user_save_png):
        path.unlink(missing_ok=True)

    code = f"""
import altair as alt
import pandas as pd

data = pd.DataFrame({{
    "genre": ["Rock", "Jazz", "Latin"],
    "tracks": [120, 48, 73],
}})
chart = alt.Chart(data).mark_bar().encode(
    x=alt.X("genre:N", sort="-y"),
    y="tracks:Q",
    color="genre:N",
)
chart.save(
    r"{user_save_png}"
)
chart.show(
)
"""

    agent = CodeGenerationAgent(use_log=False)
    result = agent._execute_altair_code(code, str(output_png))

    check("Altair executor succeeds", result.get("status") == "success", str(result))
    check("Executor returns Vega JSON path", result.get("json_path") == str(output_json), str(result))
    check("Vega JSON file exists", output_json.exists(), str(output_json))
    check("Live preview does not require PNG output", not output_png.exists(), str(output_png))
    check("User-authored save side effect is stripped", not user_save_png.exists(), str(user_save_png))

    if output_json.exists():
        spec = json.loads(output_json.read_text(encoding="utf-8"))
        check("Saved spec is Vega-Lite", "$schema" in spec and "mark" in spec, str(spec)[:300])
        check("Saved spec keeps the chart mark", spec.get("mark", {}).get("type") == "bar" or spec.get("mark") == "bar", str(spec.get("mark")))

    if FAILURES:
        print("\nFailures:")
        for failure in FAILURES:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
