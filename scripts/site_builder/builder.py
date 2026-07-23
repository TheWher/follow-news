"""Site builder orchestrator — reads archives, parses, renders, writes files.

The main entry point for building the enhanced static site from
daily digest markdown archives.

Extracted from build-enhanced-site.py for modularity.

Usage:
    python -m scripts.site_builder             # build all
    python -m scripts.site_builder 2026-07-09   # build single date
"""

from __future__ import annotations

import glob
import os
import sys
from datetime import datetime
from typing import Any

from .parser import parse_digest_md
from .templates import render_html


def get_archive_dates(archive_dir: str) -> list[str]:
    """Get archive date list sorted descending."""
    files = glob.glob(os.path.join(archive_dir, "daily-*.md"))
    dates = []
    for f in files:
        basename = os.path.basename(f)
        date_str = basename.replace("daily-", "").replace(".md", "")
        dates.append(date_str)
    dates.sort(reverse=True)
    return dates


def build_site(target_date: str | None = None,
               archive_dir: str | None = None,
               output_dir: str | None = None) -> None:
    """Build all (or single) enhanced HTML pages.

    Args:
        target_date: specific date to build (None = all)
        archive_dir: path to archive directory
        output_dir: path to output (site) directory
    """
    if archive_dir is None or output_dir is None:
        from config.project_paths import ARCHIVE_DIR, OUTPUT_DIR
        archive_dir = archive_dir or ARCHIVE_DIR
        output_dir = output_dir or OUTPUT_DIR

    os.makedirs(output_dir, exist_ok=True)

    all_dates = get_archive_dates(archive_dir)
    if not all_dates:
        print("No archives found!")
        return

    print(f"Found {len(all_dates)} archive dates: {', '.join(all_dates)}")

    if target_date:
        if target_date not in all_dates:
            print(f"Date {target_date} not in archives. Available: {all_dates}")
            sys.exit(1)
        build_dates = [target_date]
    else:
        build_dates = all_dates

    built = []
    errors = []
    total_articles = 0

    # First pass: parse all, collect content dates
    parsed_pages = []
    for date_str in build_dates:
        filepath = os.path.join(archive_dir, f"daily-{date_str}.md")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                md_text = f.read()
            data: dict[str, Any] = parse_digest_md(md_text)
            content_date = data["date"] or date_str
            parsed_pages.append((content_date, date_str, data))
        except Exception as e:
            print(f"  ✗ daily-{date_str}.md  PARSE ERROR: {e}")
            errors.append((date_str, str(e)))

    # Deduplicate by content date — latest file_date wins
    seen = {}
    for content_date, file_date, data in parsed_pages:
        if content_date not in seen or file_date > seen[content_date][0]:
            seen[content_date] = (file_date, data)
    content_dates = sorted(seen.keys(), reverse=True)

    for content_date in content_dates:
        file_date, data = seen[content_date]
        try:
            n_articles = sum(len(arts) for _, _, arts in data["sections"])
            total_articles += n_articles

            html = render_html(data, content_dates, page_date=content_date)

            output_path = os.path.join(output_dir, f"{content_date}.html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

            print(f"  ✓ {content_date}.html  ({n_articles} articles, "
                  f"{len(html):,} bytes)  ← daily-{file_date}.md")
            built.append(content_date)

            # Guard: today's page must not be empty
            today = datetime.now().strftime('%Y-%m-%d')
            if content_date == today and n_articles == 0:
                print(f"  ⛔ FATAL: today's page ({content_date}) has 0 articles "
                      f"— parser may have failed. Aborting.")
                sys.exit(1)

        except Exception as e:
            print(f"  ✗ {content_date}.html  ERROR: {e}")
            errors.append((content_date, str(e)))

    # Build index (copy latest)
    if built:
        latest_date = content_dates[0]
        latest_path = os.path.join(output_dir, f"{latest_date}.html")
        index_path = os.path.join(output_dir, "index.html")
        if os.path.exists(latest_path):
            with open(latest_path, 'r', encoding='utf-8') as f:
                index_html = f.read()
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(index_html)
            print(f"  ✓ index.html  → {latest_date}.html")

    # Clean up orphaned date HTML files
    if target_date is None:
        for f in glob.glob(os.path.join(output_dir,
                                        "20[0-9][0-9]-[0-9][0-9]-[0-9][0-9].html")):
            fname = os.path.basename(f).replace(".html", "")
            if fname not in built:
                os.remove(f)
                print(f"  🗑 removed orphan: {os.path.basename(f)}")

    print(f"\n{'─'*50}")
    print(f"Built {len(built)} pages, {total_articles} total articles")
    if errors:
        print(f"Errors: {len(errors)}")
        for d, e in errors:
            print(f"  {d}: {e}")
    print(f"Output: {output_dir}/")
    print(f"Open:  file://{output_dir}/index.html")


def main():
    """CLI entry point."""
    target = None
    if len(sys.argv) > 2 and sys.argv[1] == '--date':
        target = sys.argv[2]
    elif len(sys.argv) > 1:
        target = sys.argv[1]
    build_site(target)


if __name__ == '__main__':
    main()
