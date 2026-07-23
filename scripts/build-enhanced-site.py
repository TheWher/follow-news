#!/usr/bin/env python3
"""Enhanced static site builder for follow-news daily digest — v5.0.

Thin wrapper delegating to the modular scripts/site_builder/ package.
Keeping this file for backward compatibility with existing scripts and README.

Usage:
  python3 build-enhanced-site.py [--date YYYY-MM-DD]
  python3 build-enhanced-site.py 2026-07-09
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.site_builder import main

if __name__ == '__main__':
    main()
