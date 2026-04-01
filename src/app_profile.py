"""
Application profile and content-pack loading.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_PACK_ID = "legal"
_CACHE: dict[str, "AppProfile"] = {}


@dataclass(frozen=True)
class AppProfile:
    pack_id: str
    app_name: str
    app_dir_name: str
    db_filename: str
    source_db_path: str
    terms_path: str
    backup_filename: str
    github_repo: str
    update_user_agent: str
    hero_eyebrow: str
    hero_guest_title: str
    hero_subtitle: str
    activation_product_name: str
    activation_key_prompt: str
    easter_caption: str
    reminder_message: str
    backup_invalid_message: str
    category_styles: dict[str, dict[str, list[str]]] = field(default_factory=dict)


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def get_current_pack_id() -> str:
    return os.environ.get("LET_APP_PACK", DEFAULT_PACK_ID).strip() or DEFAULT_PACK_ID


def load_profile(pack_id: str | None = None) -> AppProfile:
    resolved_pack = pack_id or get_current_pack_id()
    if resolved_pack not in _CACHE:
        profile_path = project_root() / "packs" / resolved_pack / "profile.json"
        data = json.loads(profile_path.read_text(encoding="utf-8"))
        _CACHE[resolved_pack] = AppProfile(
            pack_id=data["pack_id"],
            app_name=data["app_name"],
            app_dir_name=data["app_dir_name"],
            db_filename=data["db_filename"],
            source_db_path=data["source_db_path"],
            terms_path=data["terms_path"],
            backup_filename=data["backup_filename"],
            github_repo=data["github_repo"],
            update_user_agent=data["update_user_agent"],
            hero_eyebrow=data["hero_eyebrow"],
            hero_guest_title=data["hero_guest_title"],
            hero_subtitle=data["hero_subtitle"],
            activation_product_name=data["activation_product_name"],
            activation_key_prompt=data["activation_key_prompt"],
            easter_caption=data["easter_caption"],
            reminder_message=data["reminder_message"],
            backup_invalid_message=data["backup_invalid_message"],
            category_styles=data.get("category_styles", {}),
        )
    return _CACHE[resolved_pack]


def get_current_profile() -> AppProfile:
    return load_profile()
