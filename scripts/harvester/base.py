"""Shared utilities for the follow-news harvester.

Replaces curl+inline-Python patterns from the legacy shell scripts
with native Python requests, configurable proxy, logging, and output.
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

import urllib.request
import urllib.error

logger = logging.getLogger('harvester')


# ── Proxy ─────────────────────────────────────────────────
def get_proxy() -> dict:
    """Return requests-compatible proxy dict, reading env or defaulting to local."""
    proxy_url = os.environ.get('FN_PROXY', 'http://127.0.0.1:7890')
    return {'http': proxy_url, 'https': proxy_url} if proxy_url else {}


# ── HTTP fetch ─────────────────────────────────────────────
def fetch_json(url: str, timeout: int = 15, headers: Optional[dict] = None) -> Any:
    """Fetch a URL and parse JSON response.

    Uses system curl via subprocess as fallback when urllib fails
    (matches the legacy shell scripts' behavior with proxy).
    """
    all_headers = {'User-Agent': 'FollowNews/1.0', 'Accept': 'application/json'}
    if headers:
        all_headers.update(headers)

    try:
        req = urllib.request.Request(url, headers=all_headers)
        proxy_url = os.environ.get('FN_PROXY', 'http://127.0.0.1:7890')
        if proxy_url:
            proxy_support = urllib.request.ProxyHandler({
                'http': proxy_url, 'https': proxy_url
            })
            opener = urllib.request.build_opener(proxy_support)
            with opener.open(req, timeout=timeout) as resp:
                text = resp.read().decode('utf-8')
        else:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                text = resp.read().decode('utf-8')
        return json.loads(text)
    except Exception as e:
        logger.debug("fetch_json failed with urllib: %s, trying curl fallback", e)
        return _curl_fetch_json(url, timeout)


def fetch_text(url: str, timeout: int = 15, headers: Optional[dict] = None) -> str:
    """Fetch a URL and return raw text. Uses curl fallback."""
    all_headers = {'User-Agent': 'FollowNews/1.0'}
    if headers:
        all_headers.update(headers)

    try:
        req = urllib.request.Request(url, headers=all_headers)
        proxy_url = os.environ.get('FN_PROXY', 'http://127.0.0.1:7890')
        if proxy_url:
            proxy_support = urllib.request.ProxyHandler({
                'http': proxy_url, 'https': proxy_url
            })
            opener = urllib.request.build_opener(proxy_support)
            with opener.open(req, timeout=timeout) as resp:
                return resp.read().decode('utf-8')
        else:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode('utf-8')
    except Exception as e:
        logger.debug("fetch_text failed with urllib: %s, trying curl fallback", e)
        return _curl_fetch_text(url, timeout)


def _curl_fetch_json(url: str, timeout: int = 15) -> Any:
    """Fallback: use system curl, same as legacy shell scripts."""
    text = _curl_fetch_text(url, timeout)
    if text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    return None


def _curl_fetch_text(url: str, timeout: int = 15) -> str:
    proxy_url = os.environ.get('FN_PROXY', 'http://127.0.0.1:7890')
    try:
        cmd = ['curl', '-s', '--proxy', proxy_url, '--max-time', str(timeout), url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    except Exception as e:
        logger.debug("curl fallback also failed: %s", e)
    return ""


# ── Output writer ──────────────────────────────────────────
def write_output(path: str, data: Any):
    """Write JSON to output file, creating parent dirs if needed."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_to_articles(articles_path: str, new_items: list):
    """Append items to the master articles file (merge step)."""
    existing = []
    try:
        with open(articles_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    seen = set()
    for a in existing:
        k = a.get('title', '')[:80].lower().strip()
        if k:
            seen.add(k)

    for item in new_items:
        item.pop('stars', None)
        item.pop('daily_growth', None)
        k = item.get('title', '')[:80].lower().strip()
        if k and k not in seen:
            seen.add(k)
            existing.append(item)

    with open(articles_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    return len(existing)
