"""Centralized path resolution for follow-news.

All paths computed from project root, with env var overrides.
Every Python script in this project should import paths from here,
not hardcode absolute paths.

Usage:
    from config.project_paths import (
        ARCHIVE_DIR, OUTPUT_DIR, CACHE_DIR, DATA_DIR,
        LATEST_DIGEST, data_file, ensure_dirs
    )
"""

from __future__ import annotations

import os
from pathlib import Path


# ── Project root detection ─────────────────────────────────
# config/project_paths.py  →  parent = project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ── Directory paths (env overridable) ──────────────────────
ARCHIVE_DIR = os.environ.get(
    'FN_ARCHIVE_DIR',
    str(_PROJECT_ROOT / 'archive' / 'follow-news')
)
OUTPUT_DIR = os.environ.get(
    'FN_OUTPUT_DIR',
    str(_PROJECT_ROOT / 'site')
)
CACHE_DIR = os.environ.get(
    'FN_CACHE_DIR',
    str(_PROJECT_ROOT / 'cache')
)
DATA_DIR = os.environ.get(
    'FN_DATA_DIR',
    str(_PROJECT_ROOT / 'data')
)
CONFIG_DIR = os.environ.get(
    'FN_CONFIG_DIR',
    str(_PROJECT_ROOT / 'config')
)
SCRIPTS_DIR = os.environ.get(
    'FN_SCRIPTS_DIR',
    str(_PROJECT_ROOT / 'scripts')
)
ARCHIVE_ROOT = os.environ.get(
    'FN_ARCHIVE_ROOT',
    str(_PROJECT_ROOT / 'archive')
)


# ── Key file paths ─────────────────────────────────────────
LATEST_DIGEST = os.environ.get(
    'FN_DIGEST',
    str(_PROJECT_ROOT / 'daily-digest.md')
)
USED_URLS = os.environ.get(
    'FN_USED_URLS',
    str(_PROJECT_ROOT / '.used-urls.json')
)


# ── Intermediate data files (in data/ instead of /tmp/) ────
def data_file(name: str) -> str:
    """Resolve a filename to the data directory.

    Replaces legacy /tmp/td-*.json patterns with
    project-local data/ files, portable across platforms.
    """
    return str(_PROJECT_ROOT / 'data' / name)


# Standard intermediate file names (matching legacy pipeline)
FN_MERGED        = data_file('td-merged.json')
FN_ARTICLES      = data_file('td-articles.json')
FN_ARTICLES_DEDUPED = data_file('td-articles-deduped.json')
FN_ARTICLES_SCORED  = data_file('td-articles-scored.json')
FN_ARTICLES_ENRICHED = data_file('td-articles-enriched.json')
FN_GITHUB        = data_file('td-github-trending.json')
FN_COMMUNITY     = data_file('td-community.json')
FN_PAPERS        = data_file('td-papers.json')
FN_PRODUCTS      = data_file('td-products.json')
FN_PIPELINE_LOG  = data_file('td-pipeline.log')


# ── Ensure directories exist ───────────────────────────────
def ensure_dirs() -> None:
    """Create all data directories if they don't exist."""
    for d in [ARCHIVE_DIR, OUTPUT_DIR, CACHE_DIR, DATA_DIR]:
        Path(d).mkdir(parents=True, exist_ok=True)


# ── Quick test ─────────────────────────────────────────────
if __name__ == '__main__':
    ensure_dirs()
    print(f"Project root  : {_PROJECT_ROOT}")
    print(f"Archive dir   : {ARCHIVE_DIR}")
    print(f"Output dir    : {OUTPUT_DIR}")
    print(f"Cache dir     : {CACHE_DIR}")
    print(f"Data dir      : {DATA_DIR}")
    print(f"Latest digest : {LATEST_DIGEST}")
    print(f"Merged        : {FN_MERGED}")
