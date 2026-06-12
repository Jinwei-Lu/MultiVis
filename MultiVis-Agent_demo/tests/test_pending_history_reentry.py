#!/usr/bin/env python3
"""Regression checks for reopening an in-progress generation from history."""
from __future__ import annotations

import importlib
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" - {detail}"
    print(line)
    if not ok:
        FAILURES.append(f"{name}: {detail}")


def run_tests() -> int:
    original_cwd = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="multivis_pending_history_") as tmp:
        os.chdir(tmp)
        try:
            app_module = importlib.import_module("app")

            session_id = "session_pending_reentry"
            history_time = app_module.add_history(
                "chinook_1.sqlite",
                "Create a chart while I leave the page",
                results=None,
                uploaded_image_name="1.png",
                original_image_name="reference.png",
                session_id=session_id,
                uploaded_code="import matplotlib.pyplot as plt\nplt.plot([1, 2], [2, 1])",
                is_database_code=False,
            )

            history = app_module.get_history()
            check("Pending history stores session id", history[0].get("session_id") == session_id, str(history[0]))
            check("Pending history stores reference code", bool(history[0].get("uploaded_code")), str(history[0]))

            with app_module.app.test_client() as client:
                load_response = client.get("/load_history/0")
                payload = load_response.get_json()
                check("load_history succeeds for pending item", bool(payload and payload.get("success")), str(payload))
                check("load_history exposes pending session id", payload.get("session_id") == session_id, str(payload))
                check("load_history marks item as working", payload.get("is_working") is True, str(payload))

                result_response = client.get(
                    f"/result?session_id={session_id}&db_name=chinook_1.sqlite"
                    f"&nl_query=Create+a+chart+while+I+leave+the+page&time={history_time}"
                )
                html = result_response.get_data(as_text=True)
                check("Result page reopens for pending history", result_response.status_code == 200, str(result_response.status_code))
                check("Result page receives reference code from history", "plt.plot" in html, html[:300])
        finally:
            os.chdir(original_cwd)

    if FAILURES:
        print("\nFAILURES:")
        for failure in FAILURES:
            print(f"- {failure}")
        return 1
    print("\nALL PENDING HISTORY REENTRY TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
