"""follow-news enhanced static site builder — v5.0 (modular).

Replaces: scripts/build-enhanced-site.py

Usage:
    python -m scripts.site_builder             # build all dates
    python -m scripts.site_builder 2026-07-09   # build single date
    python -m scripts.site_builder --date 2026-07-09

API:
    from scripts.site_builder import build_site, parse_digest_md, render_html
"""

from .builder import build_site, main
from .parser import parse_digest_md, extract_date_from_title, CATEGORY_META
from .templates import render_html

__all__ = [
    'build_site',
    'main',
    'parse_digest_md',
    'extract_date_from_title',
    'render_html',
    'CATEGORY_META',
]
