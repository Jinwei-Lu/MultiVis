"""Runtime path helpers for development and PyInstaller bundles."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

_FROZEN = getattr(sys, "frozen", False)
_APP_NAME = "MultiVisAgent"


def is_frozen() -> bool:
    return _FROZEN


def _is_macos_app_bundle() -> bool:
    return _FROZEN and sys.platform == "darwin" and ".app/Contents/MacOS" in Path(sys.executable).as_posix()


def app_root() -> Path:
    """Writable per-user data directory when packaged; project dir in development."""
    if not _FROZEN:
        return Path(__file__).resolve().parent

    if sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support" / _APP_NAME
    elif sys.platform == "win32":
        root = Path(os.environ.get("APPDATA", Path.home())) / _APP_NAME
    else:
        root = Path.home() / ".local" / "share" / _APP_NAME

    root.mkdir(parents=True, exist_ok=True)
    return root


def bundle_root() -> Path:
    """Read-only bundled resources (_MEIPASS when frozen)."""
    if _FROZEN and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def resource_path(*parts: str) -> Path:
    return bundle_root().joinpath(*parts)


def runtime_path(*parts: str) -> Path:
    return app_root().joinpath(*parts)


def resolve_runtime(*parts: str) -> str:
    return str(runtime_path(*parts))


def resolve_resource(*parts: str) -> str:
    return str(resource_path(*parts))


def desktop_log_path() -> Path:
    return runtime_path("logs", "desktop.log")


_WRITABLE_DIRS = (
    "logs",
    "test_tmp",
    "temp",
    "history",
    "history/input",
    "history/chart_result",
    "history/chart_json",
    "database",
    "static/uploads",
    "static/vendor",
)

_SEED_DIRS = ("database",)


def _seed_demo_history() -> None:
    """Copy bundled demo history.

    Packaged demo launches should always start from the curated four-item
    history so an older App Support directory cannot leak into a live demo.
    Development runs keep the previous first-launch behavior.
    """
    src_history = resource_path("history")
    if not src_history.is_dir():
        return
    dst_history = runtime_path("history")

    if _FROZEN:
        try:
            if src_history.resolve() == dst_history.resolve():
                return
        except FileNotFoundError:
            pass
        if dst_history.exists():
            shutil.rmtree(dst_history)
        shutil.copytree(src_history, dst_history)
        return

    dst_json = dst_history / "history.json"
    if dst_json.exists():
        return

    dst_history.mkdir(parents=True, exist_ok=True)
    for item in src_history.iterdir():
        if item.is_file():
            shutil.copy2(item, dst_history / item.name)
        elif item.is_dir():
            shutil.copytree(item, dst_history / item.name, dirs_exist_ok=True)


def _seed_from_bundle(rel_dir: str) -> None:
    src_dir = resource_path(rel_dir)
    dst_dir = runtime_path(rel_dir)
    if not src_dir.is_dir():
        return
    dst_dir.mkdir(parents=True, exist_ok=True)
    for item in src_dir.iterdir():
        if not item.is_file():
            continue
        target = dst_dir / item.name
        if not target.exists():
            shutil.copy2(item, target)


def _seed_static_subdir(name: str) -> None:
    """Mirror a read-only static subdir (e.g. vendor, css) into the user data dir.

    Always refreshes from the bundle so theme/CSS updates ship with each build
    instead of being shadowed by an older copy in the user's data directory.
    """
    src = resource_path("static", name)
    dst = runtime_path("static", name)
    if not src.is_dir():
        return
    try:
        if src.resolve() == dst.resolve():
            return
    except FileNotFoundError:
        pass
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def _seed_tree_from_bundle(rel_dir: str, refresh: bool = False) -> None:
    src = resource_path(rel_dir)
    dst = runtime_path(rel_dir)
    if not src.is_dir():
        return
    try:
        if src.resolve() == dst.resolve():
            return
    except FileNotFoundError:
        pass
    if refresh and dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, dirs_exist_ok=True)


def init_runtime() -> Path:
    """Prepare cwd and writable folders; seed bundled assets on first run."""
    root = app_root()
    os.chdir(root)

    for rel in _WRITABLE_DIRS:
        runtime_path(rel).mkdir(parents=True, exist_ok=True)

    for rel in _SEED_DIRS:
        _seed_from_bundle(rel)

    _seed_tree_from_bundle("chart_example", refresh=_FROZEN)

    for static_subdir in ("vendor", "css", "bench_examples"):
        _seed_static_subdir(static_subdir)
    _seed_demo_history()
    return root
