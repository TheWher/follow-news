"""Unit tests for the article deduplication engine."""

from __future__ import annotations

import importlib.util
import os
import sys

# dedup-articles.py has a hyphen in its name (cannot import directly)
_DEDUP_PATH = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'dedup-articles.py')
if not os.path.exists(_DEDUP_PATH):
    raise FileNotFoundError(f"Cannot find dedup-articles.py at {_DEDUP_PATH}")

spec = importlib.util.spec_from_file_location("dedup_articles", _DEDUP_PATH)
_dedup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_dedup)

deduplicate = _dedup.deduplicate
normalize_url = _dedup.normalize_url
extract_domain = _dedup.extract_domain
word_overlap = _dedup.word_overlap
title_words = _dedup.title_words

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

def test_normalize_url():
    print("\n── URL normalization ──")
    cases = [
        ("https://www.example.com/path?utm=1#anchor", "example.com/path"),
        ("http://EXAMPLE.COM/", "example.com"),
        ("https://github.com/user/repo", "github.com/user/repo"),
        ("https://www.google.com/search?q=test", "google.com/search"),
    ]
    for inp, expected in cases:
        result = normalize_url(inp)
        check(result == expected, f"normalize({inp[:40]}) = '{result}' (expected '{expected}')")


def test_extract_domain():
    print("\n── Domain extraction ──")
    cases = [
        ("https://www.example.com/path", "example.com"),
        ("https://github.com/user/repo", "github.com"),
        ("https://sub.domain.co.uk/page", "sub.domain.co.uk"),
    ]
    for inp, expected in cases:
        result = extract_domain(inp)
        check(result == expected, f"domain('{inp}') = '{result}'")


def test_title_words():
    print("\n── Title word extraction ──")
    words = title_words("The New AI Model from OpenAI beats benchmarks")
    check("openai" in words, "extracts 'openai' from title")
    check("the" not in words, "filters stopword 'the'")
    check("from" not in words, "filters stopword 'from'")
    check(len(words) > 0, "returns non-empty word list")


def test_word_overlap():
    print("\n── Word overlap ──")
    w1 = ["openai", "release", "new", "model"]
    w2 = ["openai", "model", "gpt", "launch"]
    overlap = word_overlap(w1, w2)
    check(0.4 <= overlap <= 0.7, f"partial overlap: {overlap:.2f}")

    w3 = ["gpt", "benchmark"]
    overlap2 = word_overlap(w1, w3)
    check(overlap2 == 0.0, f"zero overlap: {overlap2:.2f}")

    w4 = ["openai", "release", "new", "model"]
    overlap3 = word_overlap(w1, w4)
    check(overlap3 == 1.0, f"full overlap: {overlap3:.2f}")


def test_deduplicate():
    print("\n── Deduplication ──")

    # Exact URL match
    articles = [
        {"title": "OpenAI releases GPT-5", "link": "https://example.com/gpt5", "source": "Source A"},
        {"title": "GPT-5 is out!", "link": "https://example.com/gpt5", "source": "Source B"},
    ]
    merged = deduplicate(articles, threshold=0.55)
    check(len(merged) == 1, f"exact URL: {len(merged)} merged (expected 1)")

    # Different articles, no dedup
    articles2 = [
        {"title": "AI news story", "link": "https://example.com/ai-news", "source": "A"},
        {"title": "Completely different topic", "link": "https://other.com/different", "source": "B"},
    ]
    merged2 = deduplicate(articles2, threshold=0.55)
    check(len(merged2) == 2, f"different articles: {len(merged2)} (expected 2)")

    # Empty input
    merged3 = deduplicate([], threshold=0.55)
    check(len(merged3) == 0, "empty: returns empty")


if __name__ == '__main__':
    print("=" * 50)
    print("dedup engine tests")
    print("=" * 50)

    test_normalize_url()
    test_extract_domain()
    test_title_words()
    test_word_overlap()
    test_deduplicate()

    print(f"\n{'='*50}")
    print(f"Results: {PASS} passed, {FAIL} failed, {PASS+FAIL} total")
    if FAIL > 0:
        sys.exit(1)
    else:
        print("All tests passed!")
