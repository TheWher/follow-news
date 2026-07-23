"""follow-news harvester — configuration-driven multi-source news collector.

Replaces 4 legacy shell scripts:
  - scripts/fetch-community.sh
  - scripts/fetch-github-trending.sh
  - scripts/fetch-papers.sh
  - scripts/fetch-products.sh

Usage:
    python -m scripts.harvester                    # auto: collect all sources
    python -m scripts.harvester --sources community,github  # subset
    python -m scripts.harvester --list-sources              # list available

Output files (overridable via env FN_DATA_DIR):
  - data/td-community.json
  - data/td-github-trending.json
  - data/td-papers.json
  - data/td-products.json
"""

import argparse
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from . import handlers
from .base import logger

# Import handlers so they register
from . import handlers  # noqa: F811
from .handlers import community, github, papers, products  # noqa: F401


def _resolve_output(source_type: str) -> str:
    """Resolve output path for a source type.

    Priority: env var > data/ directory > ./data/ fallback.
    """
    data_dir = os.environ.get('FN_DATA_DIR', os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'
    ))
    filenames = {
        'community': 'td-community.json',
        'github': 'td-github-trending.json',
        'papers': 'td-papers.json',
        'products': 'td-products.json',
    }
    fname = filenames.get(source_type, f'td-{source_type}.json')
    # Allow env-level override per source
    env_key = f'FN_OUTPUT_{source_type.upper()}'
    return os.environ.get(env_key, os.path.join(data_dir, fname))


def collect_sources(source_types: list[str] | None = None,
                    parallel: bool = True,
                    max_workers: int = 4) -> dict[str, list[dict]]:
    """Collect news from specified sources (or all registered).

    Returns:
        dict mapping source_type -> list of collected items
    """
    if source_types is None:
        source_types = handlers.list_types()

    results: dict[str, list[dict]] = {}
    logger.info("Harvester: collecting %d source(s): %s",
                len(source_types), source_types)

    if parallel and len(source_types) > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {}
            for st in source_types:
                handler = handlers.get_handler(st)
                if not handler:
                    logger.warning("  No handler registered for '%s'", st)
                    continue
                output_path = _resolve_output(st)
                future = executor.submit(handler, output_path)
                future_map[future] = st

            for future in as_completed(future_map):
                st = future_map[future]
                try:
                    results[st] = future.result()
                except Exception as e:
                    logger.error("  Source '%s' failed: %s", st, e)
                    results[st] = []
    else:
        for st in source_types:
            handler = handlers.get_handler(st)
            if not handler:
                logger.warning("  No handler registered for '%s'", st)
                continue
            output_path = _resolve_output(st)
            try:
                results[st] = handler(output_path)
            except Exception as e:
                logger.error("  Source '%s' failed: %s", st, e)
                results[st] = []

    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='follow-news harvester — collect news from multiple sources'
    )
    parser.add_argument(
        '--sources', '-s',
        help='Comma-separated source types (default: all registered)'
    )
    parser.add_argument(
        '--list-sources', action='store_true',
        help='List available source types and exit'
    )
    parser.add_argument(
        '--sequential', action='store_true',
        help='Run sources sequentially (default: parallel)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose logging'
    )

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stderr,
    )

    if args.list_sources:
        print("Available sources:")
        for st in handlers.list_types():
            print(f"  - {st}")
        return

    source_types = None
    if args.sources:
        source_types = [s.strip() for s in args.sources.split(',')]

    t0 = time.time()
    results = collect_sources(source_types, parallel=not args.sequential)
    elapsed = time.time() - t0

    print(f"\nHarvester done in {elapsed:.1f}s:")
    for st, items in results.items():
        print(f"  {st}: {len(items)} items")


if __name__ == '__main__':
    main()
