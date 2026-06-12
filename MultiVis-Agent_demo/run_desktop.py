#!/usr/bin/env python3
"""Desktop entry point for MultiVis Agent — double-click / zero-config demo."""
from __future__ import annotations

import argparse
import logging
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from urllib.error import URLError
from urllib.request import urlopen


def _pick_port(host: str, preferred: int) -> int:
    for port in (preferred, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
                return sock.getsockname()[1]
            except OSError:
                continue
    raise RuntimeError("Could not bind to a local port")


def _setup_logging(frozen: bool) -> None:
    from multivis_paths import desktop_log_path, init_runtime

    init_runtime()
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if frozen:
        log_file = desktop_log_path()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )


def _notify(title: str, message: str) -> None:
    if sys.platform == "darwin":
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script], check=False)
    elif sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
        except Exception:
            pass


def _show_fatal_error(message: str) -> None:
    logging.exception(message)
    if sys.platform == "darwin":
        safe = message.replace("\\", "\\\\").replace('"', '\\"')[:500]
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display dialog "{safe}" with title "MultiVis Agent" buttons {{"OK"}} '
                'default button "OK" with icon stop',
            ],
            check=False,
        )
    else:
        print(f"ERROR: {message}", file=sys.stderr)


def _wait_for_server(url: str, timeout: float = 120.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (URLError, OSError, TimeoutError):
            pass
        time.sleep(0.4)
    return False


def _open_browser_when_ready(url: str) -> None:
    def _worker() -> None:
        if _wait_for_server(url):
            webbrowser.open(url)
            _notify("MultiVis Agent", "Demo is ready in your browser.")
        else:
            _show_fatal_error(f"Server did not start in time.\nOpen manually: {url}")

    threading.Thread(target=_worker, daemon=True).start()


def _prewarm_matplotlib() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.figure()
    plt.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="MultiVis Agent desktop demo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    from multivis_paths import is_frozen, resolve_resource

    frozen = is_frozen()
    _setup_logging(frozen)

    host = args.host
    port = _pick_port(host, args.port)
    url = f"http://{host}:{port}/"

    from multivis_paths import app_root

    logging.info("MultiVis Agent — SIGMOD Demo (%s)", "packaged" if frozen else "development")
    logging.info("Data directory: %s", app_root())
    logging.info("URL: %s", url)

    open_browser = not args.no_browser and (frozen or True)
    if open_browser:
        _open_browser_when_ready(url)

    _prewarm_matplotlib()

    from app import app

    app.template_folder = resolve_resource("templates")

    app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        _show_fatal_error(str(exc))
        raise SystemExit(1) from exc
    except KeyboardInterrupt:
        logging.info("Server stopped.")
        raise SystemExit(0)
