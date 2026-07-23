"""Run all follow-news tests.

Usage:
    python tests/run_all.py
"""

from __future__ import annotations

import subprocess
import sys
import os

TESTS = [
    "tests/test_parser.py",
    "tests/test_dedup.py",
]

if __name__ == '__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)

    total_pass = 0
    total_fail = 0

    for test_file in TESTS:
        test_path = os.path.join(project_root, test_file)
        print(f"\n{'=' * 60}")
        print(f"Running: {test_file}")
        print(f"{'=' * 60}")

        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=False,  # stream to stdout
            text=True,
            cwd=project_root,
        )

        if result.returncode == 0:
            total_pass += 1
        else:
            total_fail += 1

    print(f"\n{'=' * 60}")
    print(f"Summary: {total_pass} test files passed, {total_fail} failed")
    if total_fail > 0:
        sys.exit(1)
