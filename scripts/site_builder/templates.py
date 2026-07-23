"""HTML template renderer for the follow-news enhanced site.

Takes parsed digest data and produces a self-contained HTML page
with embedded CSS, JS, and structured article data.

Extracted from build-enhanced-site.py for modularity.
"""

from __future__ import annotations

import json
from typing import Any

from .assets import CSS, JS
from .parser import CATEGORY_META, ParsedDigest


# ═══════════════════════════════════════════════════════════
#  Helpers
# ═══════════════════════════════════════════════════════════

def escape_html(text: str) -> str:
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))


def escape_attr(text: str) -> str:
    return (text
            .replace('&', '&amp;')
            .replace('"', '&quot;')
            .replace("'", '&#39;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


# ═══════════════════════════════════════════════════════════
#  Render
# ═══════════════════════════════════════════════════════════

def render_html(data: ParsedDigest, archive_dates: list[str], page_date: str = "") -> str:
    """Render a single enhanced HTML page from parsed digest data."""

    date_str = data["date"] or "????-??-??"
    title    = data["title"]
    delayed  = data["delayed"]
    sections = data["sections"]
    nav_date = page_date or date_str

    # ── Build archive nav links ──
    archive_links_html = []
    for d in archive_dates:
        cls = 'active' if d == nav_date else ''
        archive_links_html.append(
            f'<a href="{d}.html" class="{cls}">{d[5:]}</a>'
        )

    # ── Embed article data as JSON for client-side search ──
    articles_json_parts = []
    for cat_id, sec_title, arts in sections:
        for a in arts:
            articles_json_parts.append(json.dumps({
                "title": a["title"],
                "summary": a["summary"],
                "insight": a["insight"],
                "url": a["url"],
                "category": cat_id,
                "stars": a["stars"],
                "domain": a["domain"],
            }, ensure_ascii=False))
    articles_json = "[\n" + ",\n".join(articles_json_parts) + "\n]"

    # ── Render sections ──
    sections_html_parts = []
    for cat_id, sec_title, arts in sections:
        meta = CATEGORY_META.get(cat_id, CATEGORY_META["news"])
        cards_html = []
        for a in arts:
            insight_html = ""
            if a["insight"]:
                insight_html = (
                    f'<div class="card-insight">💡 {escape_html(a["insight"])}</div>'
                )

            stars_html = ""
            if a["stars"]:
                stars_html = f'<span class="card-stars">⭐ {escape_html(a["stars"])}</span>'

            domain_html = ""
            if a["domain"]:
                domain_html = f'<span class="card-domain">{escape_html(a["domain"])}</span>'

            cards_html.append(
                f'<article class="card" data-href="{escape_attr(a["url"])}" '
                f'data-url="{escape_attr(a["url"])}">\n'
                f'    <div class="card-header">\n'
                f'        <h3 class="card-title">{a["title"]}</h3>\n'
                f'        <button class="card-bookmark" data-url="{escape_attr(a["url"])}" '
                f'title="收藏" aria-label="收藏文章">\n'
                f'            <span class="bm-icon">☆</span>\n'
                f'        </button>\n'
                f'    </div>\n'
                f'    <p class="card-body">{escape_html(a["summary"])}</p>\n'
                f'    {insight_html}\n'
                f'    <div class="card-actions">\n'
                f'        <a href="{escape_attr(a["url"])}" target="_blank" '
                f'rel="noopener" class="card-btn card-btn-primary" '
                f'onclick="event.stopPropagation()">\n'
                f'            🔗 阅读原文\n'
                f'        </a>\n'
                f'        {stars_html}\n'
                f'        {domain_html}\n'
                f'        <span class="card-read-badge" '
                f'data-url="{escape_attr(a["url"])}">✓ 已读</span>\n'
                f'    </div>\n'
                f'</article>'
            )

        sections_html_parts.append(
            f'<section class="section" data-category="{cat_id}">\n'
            f'    <h2 class="section-title">{sec_title} '
            f'<span class="section-count">({len(arts)})</span></h2>\n'
            f'    <div class="cards">\n'
            f'        {"".join(cards_html)}\n'
            f'    </div>\n'
            f'</section>'
        )

    sections_html = '\n'.join(sections_html_parts)

    # ── Delayed banner ──
    delayed_html = (
        f'<p class="delayed">⏰ 今日延迟发送，请见谅。</p>' if delayed else ''
    )

    # ── Inject JS with date + articles data ──
    js_injected = JS.replace("{date_str}", date_str).replace(
        "{articles_json}", articles_json
    )

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>{escape_html(title)} — AI 科技日报</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>
{CSS}
</style>
</head>
<body>

<!-- ═══ Top Bar ═══ -->
<div class="top-bar">
<div class="top-bar-inner">
    <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input type="search" id="search-input" placeholder="搜索标题、摘要..." autocomplete="off">
        <button class="search-clear" id="search-clear" title="清除">✕</button>
    </div>
    <span class="search-info" id="search-info"></span>
    <div class="chips" id="filter-chips">
        <button class="chip active" data-filter="all">全部</button>
        <button class="chip" data-filter="news">🌐 新闻</button>
        <button class="chip" data-filter="github">🔥 GitHub</button>
        <button class="chip" data-filter="community">💬 社区</button>
        <button class="chip" data-filter="papers">📄 论文</button>
        <button class="chip" data-filter="products">🆕 产品</button>
        <button class="chip" data-filter="bookmarks">📌 书签</button>
        <button class="chip" data-filter="unread">👁 未读</button>
    </div>
</div>
</div>

<!-- ═══ Content ═══ -->
<div class="container">
    <h1>{escape_html(title)}</h1>
    {delayed_html}
    <div class="date-summary">
        <span id="total-count"><strong>共 0 篇</strong></span>
        <span id="visible-count"></span>
        <span id="bookmark-count"></span>
        <span id="unread-count"></span>
    </div>
    <nav class="archive-bar">{''.join(archive_links_html)}</nav>

    {sections_html}

    <div class="no-results" id="no-results">
        <div class="no-results-icon">🔍</div>
        <p>没有匹配的文章</p>
    </div>

    <footer>🤖 follow-news v5.0 · <span id="footer-stats"></span></footer>
</div>

<button id="back-top" title="回到顶部" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>
<div class="toast" id="toast"></div>

<script>
{js_injected}
</script>
</body>
</html>'''
