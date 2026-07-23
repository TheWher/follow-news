"""Markdown parser for follow-news daily digest.

Handles 3 historical formats:
  v1 (06-08, 06-09): bare title, 【section】, • articles
  v2 (06-11):        # title, no sections, **articles** without bullets, ## GitHub later
  v3 (06-12+):       # title, ## sections, • **articles**

Extracted from build-enhanced-site.py for modularity.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

# Article dict type alias for clarity
Article = dict[str, Any]
Section = tuple[str, str, list[Article]]
ParsedDigest = dict[str, Any]


# ── Category registry ──────────────────────────────────────
CATEGORY_META = {
    "news":       {"icon": "🌐", "label": "AI/科技新闻", "id": "news"},
    "github":     {"icon": "🔥", "label": "GitHub Trending", "id": "github"},
    "community":  {"icon": "💬", "label": "社区讨论", "id": "community"},
    "papers":     {"icon": "📄", "label": "AI 热门论文", "id": "papers"},
    "products":   {"icon": "🆕", "label": "产品/工具", "id": "products"},
}

SECTION_HEADER_MAP = {
    "🌐": "news",
    "🔥": "github",
    "💬": "community",
    "📄": "papers",
    "🆕": "products",
    "💡": "products",  # 值得关注的新项目 → products category
}


def extract_date_from_title(title: str) -> str | None:
    """Extract date from various title formats.

    Formats:
      - '# 每日 AI 科技日报 — 2026-06-16'
      - 'AI 科技日报 — 2026-06-09'
      - '🗞️ AI 日报 — 2026年6月11日'
      - '📰 科技日报 — 2026年6月8日'
    """
    m = re.search(r'(\d{4}-\d{2}-\d{2})', title)
    if m:
        return m.group(1)
    m = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', title)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return None


def _classify_section(header_text: str) -> str:
    """Map a section header (any format) to a category id."""
    """Map a section header (any format) to a category id."""
    for icon_prefix, cid in SECTION_HEADER_MAP.items():
        if icon_prefix in header_text:
            return cid
    if 'AI Agent' in header_text or 'Agent' in header_text:
        return 'news'
    if 'LLM' in header_text or '大模型' in header_text:
        return 'news'
    if 'GitHub' in header_text:
        return 'github'
    if 'Hacker News' in header_text or 'HN' in header_text:
        return 'community'
    if '论文' in header_text or 'paper' in header_text.lower():
        return 'papers'
    if '产品' in header_text or '工具' in header_text:
        return 'products'
    if '博客' in header_text or 'blog' in header_text.lower():
        return 'community'
    if '前沿' in header_text or '科技' in header_text:
        return 'news'
    return 'news'


def parse_digest_md(text: str) -> ParsedDigest:
    """Parse a follow-news markdown digest into structured data.

    Returns:
        {
            "date": "2026-06-16",
            "title": "...",
            "delayed": False,
            "sections": [("cat_id", "Section Title", [Article, ...]), ...]
        }
        Each Article: {"title", "summary", "insight", "url", "stars", "domain"}
    """
    lines = text.split('\n')
    result = {
        "date": None,
        "title": "",
        "delayed": False,
        "sections": [],
    }
    current_section = None       # (cat_id, section_title)
    current_article = None       # dict
    articles = []                # list for current section
    title_found = False

    def flush_article():
        nonlocal current_article
        if current_article and current_article.get("url"):
            summary_text = ' '.join(current_article.get("summary_lines", [])).strip()
            articles.append({
                "title":   current_article.get("title", ""),
                "summary": summary_text,
                "insight": current_article.get("insight", ""),
                "url":     current_article.get("url", ""),
                "stars":   current_article.get("stars", ""),
                "domain":  urlparse(current_article.get("url", "")).netloc,
            })
        current_article = None

    def flush_section():
        nonlocal articles, current_section
        flush_article()
        if articles:
            if current_section:
                result["sections"].append(
                    (current_section[0], current_section[1], articles)
                )
            else:
                result["sections"].append(("news", "🌐 AI/科技新闻", articles))
        articles = []
        current_section = None

    def start_article(title_text, rest_text=""):
        nonlocal current_article
        flush_article()
        insight = ""
        url = ""
        stars = ""
        summary = rest_text
        if rest_text:
            # Extract inline 💡 insight
            im = re.search(r'💡\s*(.+?)(?=🔗|⭐|$)', rest_text)
            if im:
                insight = im.group(1).strip()
                summary = summary.replace(im.group(0), '').strip()
            # Extract inline 🔗 URL
            um = re.search(r'🔗\s*(?:\((https?://[^\)]+)\)|(https?://\S+))', summary)
            if um:
                url = um.group(1) or um.group(2)
                summary = summary[:um.start()].strip()
            # Extract inline ⭐ stars
            sm = re.search(r'⭐\s*(.+?)(?:·|🔗|$)', summary)
            if sm:
                stars = sm.group(1).strip()
                summary = summary[:sm.start()].strip()
        current_article = {
            "title": title_text,
            "summary_lines": [summary] if summary else [],
            "insight": insight,
            "url": url,
            "stars": stars,
        }

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Footer
        if stripped.startswith('🤖'):
            flush_section()
            break

        # Page title (v2/v3: '# ...')
        if stripped.startswith('# ') and not stripped.startswith('## '):
            result["title"] = stripped[2:]
            result["date"] = extract_date_from_title(result["title"])
            title_found = True
            continue

        # Bare title (v1)
        if (not title_found
            and not stripped.startswith('•')
            and not stripped.startswith('【')
            and not stripped.startswith('##')
            and not stripped.startswith('⏰')
            and not stripped.startswith('💡')
            and not stripped.startswith('🔗')
            and not stripped.startswith('**')
            and not stripped.startswith('⭐')
            and '—' in stripped
            and ('日报' in stripped or '科技' in stripped)):
            result["title"] = stripped.lstrip('#').strip()
            result["date"] = extract_date_from_title(result["title"])
            title_found = True
            continue

        # Delayed notice
        if stripped.startswith('⏰'):
            result["delayed"] = True
            continue

        # Horizontal rule (v2 article separator)
        if stripped == '---':
            flush_section()
            continue

        # Section header: v3 (## or ###)
        if stripped.startswith('### '):
            flush_section()
            header_text = stripped[4:]
            current_section = (_classify_section(header_text), header_text)
            continue
        if stripped.startswith('## '):
            flush_section()
            header_text = stripped[3:]
            current_section = (_classify_section(header_text), header_text)
            continue

        # Section header: v1 【Category】
        if stripped.startswith('【') and stripped.endswith('】'):
            flush_section()
            inner = stripped[1:-1]
            inner_clean = re.sub(r'^[^\w一-鿿#]+', '', inner).strip()
            current_section = (_classify_section(inner_clean), inner)
            continue

        # Article: v1/v3 bullet '• ...'
        if stripped.startswith('• '):
            content = stripped[2:]
            title_match = re.match(r'\*\*(.+?)\*\*', content)
            if title_match:
                article_title = title_match.group(1)
                rest = content[title_match.end():].strip()
                rest = re.sub(r'^[—\-]\s*', '', rest)
            else:
                article_title = content
                rest = ""
            start_article(article_title, rest)
            continue

        # Article: numbered list (06-09 format)
        if re.match(r'^\d{1,2}\.\s', stripped):
            content = re.sub(r'^\d{1,2}\.\s', '', stripped)
            title_match = re.match(r'\*\*(.+?)\*\*', content)
            if title_match:
                article_title = title_match.group(1)
                rest = content[title_match.end():].strip()
                rest = re.sub(r'^[—\-]\s*', '', rest)
            else:
                article_title = content
                rest = ""
            start_article(article_title, rest)
            continue

        # Article: v2 bold-only
        if stripped.startswith('**'):
            title_match = re.match(r'\*\*(.+?)\*\*', stripped)
            if title_match:
                article_title = title_match.group(1)
                rest = stripped[title_match.end():].strip()
                rest = re.sub(r'^[—\-]\s*', '', rest)
                start_article(article_title, rest)
                url_match = re.search(r'(https?://\S+)', rest)
                if url_match and current_article:
                    current_article["url"] = url_match.group(1)
                continue

        # Content lines (continuation of current article)
        if current_article is not None:
            if stripped.startswith('💡'):
                current_article["insight"] = stripped[2:].strip()
                continue
            if stripped.startswith('🔗'):
                url = stripped[2:].strip()
                link_match = re.search(r'\((https?://[^\)]+)\)', url)
                if link_match:
                    url = link_match.group(1)
                else:
                    url = url.strip()
                current_article["url"] = url
                continue
            if stripped.startswith('⭐'):
                stars_line = stripped[2:].strip()
                link_match = re.search(
                    r'🔗\s*(?:\((https?://[^\)]+)\)|(https?://\S+))', stars_line
                )
                if link_match:
                    url = link_match.group(1) or link_match.group(2)
                    current_article["url"] = url
                    stars_line = stars_line[:link_match.start()].strip()
                current_article["stars"] = stars_line.rstrip('·').strip()
                continue
            if any(stripped.startswith(p) for p in ['💬', '📄', '🆕']):
                current_article["summary_lines"].append(stripped[2:].strip())
                continue
            if re.match(r'^\(\d+↑', stripped):
                continue
            current_article["summary_lines"].append(stripped)
            continue

    flush_section()
    return result
