"""
Filesystem paths derived from the active application profile.
"""

from __future__ import annotations

from pathlib import Path

try:
    from .app_profile import get_current_profile, project_root
except ImportError:
    from app_profile import get_current_profile, project_root


def get_app_dir() -> Path:
    return Path.home() / get_current_profile().app_dir_name


def ensure_app_dir() -> Path:
    app_dir = get_app_dir()
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_user_file(filename: str) -> Path:
    return get_app_dir() / filename


def get_runtime_db_path(frozen: bool = False) -> Path:
    profile = get_current_profile()
    if frozen:
        return ensure_app_dir() / profile.db_filename
    return project_root() / profile.source_db_path


def get_terms_seed_path() -> Path:
    return project_root() / get_current_profile().terms_path
