"""Booru tag autocompletion data source (a1111-sd-webui-tagcomplete compatible).

Serves the tag database used by the frontend autocomplete (javascript/
tag_autocomplete.js) over two small HTTP endpoints registered in interface.py:

    GET /dte/tagcomplete/config    -> JSON options (from settings)
    GET /dte/tagcomplete/tags.csv  -> the raw tagcomplete-format CSV

The CSV format is the one used by DominikDoom/a1111-sd-webui-tagcomplete:

    <name>,<type>,<postCount>,"<alias1,alias2,...>"

so any tag file from an existing tagcomplete installation (danbooru.csv,
e621.csv, a custom or translation file, ...) can be pointed to via the
"Tag autocomplete CSV file" setting. A bundled tags/danbooru.csv is the
default so the feature works out of the box.
"""
from __future__ import annotations

from pathlib import Path

import settings
from utilities import base_dir_path

DEFAULT_TAG_FILE = "tags/danbooru.csv"


def resolve_tag_file() -> Path:
    """Resolve the configured tag CSV to an absolute path (relative paths are
    taken against the repo root). Falls back to the bundled default."""
    raw = (settings.current.tagcomplete_tag_file or "").strip() or DEFAULT_TAG_FILE
    p = Path(raw)
    if not p.is_absolute():
        p = base_dir_path() / p
    return p


def get_config() -> dict:
    s = settings.current
    return {
        "enabled": bool(s.tagcomplete_enabled),
        "maxResults": int(s.tagcomplete_max_results),
        "searchAlias": bool(s.tagcomplete_search_alias),
        "replaceUnderscores": bool(s.tagcomplete_replace_underscores),
        "appendComma": bool(s.tagcomplete_append_comma),
        "tagFile": str(resolve_tag_file()),
    }


def get_tags_csv() -> str:
    """Return the raw CSV text, or an empty string when disabled / missing so
    the frontend simply stays inactive."""
    if not settings.current.tagcomplete_enabled:
        return ""
    p = resolve_tag_file()
    try:
        if p.is_file():
            return p.read_text("utf-8", errors="replace")
    except OSError:
        pass
    return ""
