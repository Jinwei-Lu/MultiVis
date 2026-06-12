#!/usr/bin/env python3
"""Regression check for benchmark reference-image submission fallback."""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app as app_module

FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    if not ok:
        FAILURES.append(f"{name}: {detail}")


class NoopThread:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def start(self) -> None:
        return None


def restore_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    if src.exists():
        shutil.copytree(src, dst)


def run_tests() -> int:
    history_dir = ROOT / "history"
    uploads_dir = ROOT / "static" / "uploads"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        history_backup = tmp_path / "history"
        uploads_backup = tmp_path / "uploads"
        if history_dir.exists():
            shutil.copytree(history_dir, history_backup)
        if uploads_dir.exists():
            shutil.copytree(uploads_dir, uploads_backup)

        original_thread = app_module.threading.Thread
        original_clear = app_module.clear_folders
        try:
            app_module.threading.Thread = NoopThread
            app_module.clear_folders = lambda: None

            client = app_module.app.test_client()
            response = client.post(
                "/",
                data={
                    "db_name": "activity_1.sqlite",
                    "nl_query": "Reference image fallback submission check",
                    "model_type": "gemini-3-flash-preview",
                    "benchmark_ref_image_url": "/static/bench_examples/img/stacked_bar_chart.png",
                    "benchmark_ref_image_name": "Bar Charts___stacked_bar_chart.png",
                },
                follow_redirects=False,
            )

            check("Benchmark image form redirects to result", response.status_code == 302, str(response.status_code))
            history = app_module.get_history()
            item = next(
                (
                    entry
                    for entry in history
                    if entry.get("query") == "Reference image fallback submission check"
                ),
                {},
            )
            uploaded_name = item.get("uploaded_image_name") or ""
            original_name = item.get("original_image_name") or ""
            check("History records benchmark image", bool(uploaded_name), str(item))
            check("History preserves original benchmark image name", "stacked_bar_chart" in original_name, original_name)
            check("History input image exists", (history_dir / "input" / uploaded_name).exists(), uploaded_name)
            check(
                "Benchmark image copied into upload area",
                (uploads_dir / "Bar Charts___stacked_bar_chart.png").exists(),
                str(uploads_dir / "Bar Charts___stacked_bar_chart.png"),
            )
        finally:
            app_module.threading.Thread = original_thread
            app_module.clear_folders = original_clear
            restore_dir(history_backup, history_dir)
            restore_dir(uploads_backup, uploads_dir)

    if FAILURES:
        print("\nFAILURES:")
        for failure in FAILURES:
            print(f" - {failure}")
        return 1

    print("\nALL BENCHMARK REFERENCE IMAGE SUBMISSION TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_tests())
