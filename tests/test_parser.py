"""Smoke tests for the digest markdown parser.

Covers:
  - Real archive parsing (all 23 files, v1/v2/v3 formats)
  - Edge cases (empty input, minimal valid digest, non-standard titles)
  - Structural invariants (every article has url/title, sections aren't empty)
"""

from __future__ import annotations

import os
import sys
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.site_builder.parser import (
    parse_digest_md,
    extract_date_from_title,
    _classify_section,
    CATEGORY_META,
)

ARCHIVE_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'archive', 'follow-news'
)

PASS = 0
FAIL = 0


def ok(msg: str):
    global PASS
    PASS += 1
    print(f"  ✓ {msg}")


def bad(msg: str):
    global FAIL
    FAIL += 1
    print(f"  ✗ FAIL: {msg}")


def check(cond, msg: str):
    if cond:
        ok(msg)
    else:
        bad(msg)


# ═══════════════════════════════════════════════════════════
#  1. Date extraction
# ═══════════════════════════════════════════════════════════

def test_date_extraction():
    print("\n── Date extraction ──")

    cases = [
        ("🌐 每日 AI 科技日报 — 2026年7月9日", "2026-07-09"),
        ("# 每日 AI 科技日报 — 2026-06-16", "2026-06-16"),
        ("📰 科技日报 — 2026年6月8日", "2026-06-08"),
        ("🗞️ AI 日报 — 2026年12月31日", "2026-12-31"),
        ("Random text with no date", None),
        ("", None),
    ]
    for title, expected in cases:
        result = extract_date_from_title(title)
        check(result == expected, f"extract('{title[:30]}...') = {result}")


# ═══════════════════════════════════════════════════════════
#  2. Section classification
# ═══════════════════════════════════════════════════════════

def test_section_classification():
    print("\n── Section classification ──")

    cases = [
        ("🌐 AI/科技新闻", "news"),
        ("🔥 GitHub Trending", "github"),
        ("💬 社区讨论", "community"),
        ("📄 AI 热门论文", "papers"),
        ("🆕 产品/工具", "products"),
        ("💡 值得关注的新项目", "products"),
        ("【🤖 AI Agent】", "news"),
        ("【🧠 LLM / 大模型】", "news"),
        ("Unknown section", "news"),
    ]
    for header, expected in cases:
        result = _classify_section(header)
        check(result == expected, f"classify('{header}') = {result}")


# ═══════════════════════════════════════════════════════════
#  3. Full archive parsing (regression)
# ═══════════════════════════════════════════════════════════

def test_archive_parsing():
    print("\n── Archive parsing (regression) ──")

    files = sorted(glob.glob(os.path.join(ARCHIVE_DIR, "daily-*.md")))
    if not files:
        print("  (no archive files found, skipping)")
        return

    print(f"  Parsing {len(files)} archive files...")

    for f in files:
        basename = os.path.basename(f)
        with open(f, 'r', encoding='utf-8') as fh:
            data = parse_digest_md(fh.read())

        # Structural invariants
        check(data["title"] != "", f"{basename}: has title")
        check(data["date"] is not None, f"{basename}: has date ({data['date']})")
        check(isinstance(data["sections"], list), f"{basename}: sections is list")

        total = sum(len(arts) for _, _, arts in data["sections"])
        check(total > 0, f"{basename}: {total} articles")

        # Every article must have url and title
        for cat_id, sec_title, arts in data["sections"]:
            for a in arts:
                check(a["url"] != "", f"{basename}: [{cat_id}] article has url")
                check(a["title"] != "", f"{basename}: [{cat_id}] article has title")

    # Cross-file consistency: all dates unique (after dedup by content_date)
    dates = []
    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            data = parse_digest_md(fh.read())
        if data["date"]:
            dates.append(data["date"])
    check(len(dates) == len(files), f"all {len(files)} files have dates")


# ═══════════════════════════════════════════════════════════
#  4. Edge cases
# ═══════════════════════════════════════════════════════════

def test_edge_cases():
    print("\n── Edge cases ──")

    # Empty input
    data = parse_digest_md("")
    check(data["title"] == "", "empty: title is empty")
    check(data["date"] is None, "empty: date is None")
    check(data["sections"] == [], "empty: no sections")

    # Minimal valid digest (v3 format)
    minimal = """# 每日 AI 科技日报 — 2026-01-01

## 🌐 Test Section

• **Test Article** — Test summary 💡 Test insight 🔗 https://example.com
"""
    data = parse_digest_md(minimal)
    check(data["date"] == "2026-01-01", "minimal: date parsed")
    check(len(data["sections"]) == 1, "minimal: one section")
    cat_id, sec_title, arts = data["sections"][0]
    check(cat_id == "news", "minimal: categorized as news")
    check(len(arts) == 1, "minimal: one article")
    check(arts[0]["url"] == "https://example.com", "minimal: url extracted")
    check("Test insight" in arts[0]["insight"], "minimal: insight extracted")

    # Delayed flag
    delayed = """# 每日 AI 科技日报 — 2026-01-01
⏰ 今日延迟发送，请见谅。

## 🌐 News
• **Something** — Something 💡 Something 🔗 https://x.com
"""
    data = parse_digest_md(delayed)
    check(data["delayed"] is True, "delayed: flag set")

    # v1 format (no #, bare title)
    v1 = """📰 科技日报 — 2026年6月8日

【🤖 AI Agent】
• **DeepSeek something** Something happened 💡 Interesting 🔗 https://example.com/ds
"""
    data = parse_digest_md(v1)
    check(data["date"] == "2026-06-08", "v1: date parsed")
    check(data["title"] != "", "v1: title found")

    # v2 format (bold articles without bullets)
    v2 = """# 每日 AI 科技日报 — 2026-06-11

**Analysis of AI benchmarks** https://example.com/benchmarks
"""
    data = parse_digest_md(v2)
    check(data["date"] == "2026-06-11", "v2: date parsed")
    check(len(data["sections"]) >= 1, "v2: at least default section")


# ═══════════════════════════════════════════════════════════
#  5. Site builder integration (lightweight)
# ═══════════════════════════════════════════════════════════

def test_site_builder_imports():
    """Verify all site_builder modules import cleanly."""
    print("\n── Site builder imports ──")

    from scripts.site_builder import parse_digest_md, render_html, build_site
    from scripts.site_builder.templates import escape_html, escape_attr
    from scripts.site_builder.assets import CSS, JS

    check(len(CSS) > 100, "CSS: asset loaded (>100 chars)")
    check(len(JS) > 100, "JS: asset loaded (>100 chars)")
    check(escape_html("<script>") == "&lt;script&gt;", "escape_html works")
    check(escape_attr('test"quote') == "test&quot;quote", "escape_attr works")
    check(callable(build_site), "build_site is callable")
    check(callable(render_html), "render_html is callable")


# ═══════════════════════════════════════════════════════════
#  6. Harvester module imports
# ═══════════════════════════════════════════════════════════

def test_harvester_imports():
    """Verify all harvester modules import cleanly."""
    print("\n── Harvester imports ──")

    from scripts.harvester import collect_sources
    from scripts.harvester.handlers import list_types, get_handler

    types = list_types()
    check(len(types) == 4, f"harvester: 4 handlers registered ({types})")
    for t in types:
        h = get_handler(t)
        check(callable(h), f"harvester: handler for '{t}' is callable")


# ═══════════════════════════════════════════════════════════
#  7. Path resolution
# ═══════════════════════════════════════════════════════════

def test_paths():
    """Verify project paths resolve correctly."""
    print("\n── Path resolution ──")

    from config.project_paths import (
        ARCHIVE_DIR, OUTPUT_DIR, DATA_DIR,
        LATEST_DIGEST, data_file, FN_MERGED, FN_ARTICLES,
    )

    check(os.path.exists(ARCHIVE_DIR), f"ARCHIVE_DIR exists: {ARCHIVE_DIR}")
    check(os.path.exists(OUTPUT_DIR), f"OUTPUT_DIR exists: {OUTPUT_DIR}")
    check(ARCHIVE_DIR.endswith("archive\\follow-news") or
          ARCHIVE_DIR.endswith("archive/follow-news"),
          f"ARCHIVE_DIR has correct structure")
    check("follow-news" in LATEST_DIGEST, "LATEST_DIGEST in project root")
    check(FN_MERGED == data_file("td-merged.json"), "data_file resolves correctly")
    check(FN_ARTICLES == data_file("td-articles.json"), "data_file resolves correctly")


# ═══════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 50)
    print("follow-news smoke tests")
    print("=" * 50)

    test_date_extraction()
    test_section_classification()
    test_archive_parsing()
    test_edge_cases()
    test_site_builder_imports()
    test_harvester_imports()
    test_paths()

    print(f"\n{'='*50}")
    print(f"Results: {PASS} passed, {FAIL} failed, {PASS+FAIL} total")
    if FAIL > 0:
        sys.exit(1)
    else:
        print("All tests passed!")
