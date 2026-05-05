from __future__ import annotations

import sys
from pathlib import Path


def app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def app_data_dir() -> Path:
    p = app_base_dir() / "app_data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def sessions_dir() -> Path:
    p = app_data_dir() / "sessions"
    p.mkdir(parents=True, exist_ok=True)
    return p
