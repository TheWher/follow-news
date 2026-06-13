#!/usr/bin/env python3
"""Build a static HTML site from follow-news daily digest archives."""

import os, re, json, glob
from datetime import datetime

ARCHIVE_DIR = "/mnt/c/Users/A2260/.claude/follow-news/archive/follow-news"
OUTPUT_DIR = "/mnt/c/Users/A2260/.claude/follow-news/site"
LATEST_DIGEST = "/mnt/c/Users/A2260/.claude/follow-news/daily-digest.md"

def md_to_html(text):
    """Simple markdown to HTML converter for digest format."""
    lines = text.split('\n')
    html_lines = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()

        # Title
        if stripped.startswith('# ') and not stripped.startswith('## '):
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            html_lines.append(f'<h1>{stripped[2:]}</h1>')
            continue

        # GitHub Trending header
        if stripped.startswith('## '):
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            html_lines.append(f'<h2>{stripped[3:]}</h2>')
            continue

        # Horizontal rule
        if stripped == '---':
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            html_lines.append('<hr>')
            continue

        # Bullet items (news entries)
        if stripped.startswith('• '):
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            content = stripped[2:]
            # Bold title detection
            content = re.sub(r'\*\*(.+?)\*\*', r'<strong class="title">\1</strong>', content)
            # Detect special lines
            if content.startswith('💡'):
                html_lines.append(f'<p class="insight">{content}</p>')
            elif content.startswith('🔗'):
                url = content[2:].strip()
                html_lines.append(f'<p class="link"><a href="{url}" target="_blank">{url}</a></p>')
            elif content.startswith('⭐'):
                html_lines.append(f'<p class="github-item">{content}</p>')
            else:
                html_lines.append(f'<p class="news-item">{content}</p>')
            continue

        # Delayed notice
        if stripped.startswith('⏰'):
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            html_lines.append(f'<p class="delayed-notice">{stripped}</p>')
            continue

        # Footer
        if stripped.startswith('🤖'):
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            html_lines.append(f'<p class="footer-tag">{stripped}</p>')
            continue

        # Empty line
        if not stripped:
            if in_paragraph:
                html_lines.append('</p>')
                in_paragraph = False
            continue

        # Regular paragraph
        if not in_paragraph:
            html_lines.append('<p>')
            in_paragraph = True
        html_lines.append(line)

    if in_paragraph:
        html_lines.append('</p>')

    return '\n'.join(html_lines)

def get_archive_dates():
    """Get all archive dates sorted descending."""
    files = glob.glob(os.path.join(ARCHIVE_DIR, "daily-*.md"))
    dates = []
    for f in files:
        basename = os.path.basename(f)
        date_str = basename.replace("daily-", "").replace(".md", "")
        dates.append((date_str, f))
    dates.sort(reverse=True)
    return dates

def build_page(title, content, archive_links, current_date=None):
    """Wrap content in full HTML page template."""
    archive_html = '\n'.join([
        f'<li><a href="{d}.html">{d}</a></li>' if d != current_date
        else f'<li class="current">{d}</li>'
        for d, _ in archive_links
    ])

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — AI 科技日报</title>
<style>
:root {{
    --bg: #faf9f6;
    --card: #ffffff;
    --text: #1a1a2e;
    --muted: #6b7280;
    --accent: #2563eb;
    --border: #e5e7eb;
    --insight-bg: #eff6ff;
    --insight-border: #bfdbfe;
    --github-bg: #f0fdf4;
}}
@media (prefers-color-scheme: dark) {{
    :root {{
        --bg: #0f172a;
        --card: #1e293b;
        --text: #e2e8f0;
        --muted: #94a3b8;
        --accent: #60a5fa;
        --border: #334155;
        --insight-bg: #1e3a5f;
        --insight-border: #2563eb;
        --github-bg: #14532d;
    }}
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
}}
.container {{
    display: flex;
    max-width: 1100px;
    margin: 0 auto;
    min-height: 100vh;
}}
.sidebar {{
    width: 220px;
    padding: 2rem 1.5rem;
    border-right: 1px solid var(--border);
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    background: var(--card);
}}
.sidebar h3 {{
    font-size: 0.9rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
}}
.sidebar ul {{ list-style: none; }}
.sidebar li {{
    margin-bottom: 0.4rem;
    font-size: 0.9rem;
}}
.sidebar a {{
    color: var(--accent);
    text-decoration: none;
}}
.sidebar a:hover {{ text-decoration: underline; }}
.sidebar li.current {{
    font-weight: 600;
    color: var(--text);
}}
.main {{
    flex: 1;
    padding: 2rem;
    max-width: 780px;
}}
h1 {{
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}}
h2 {{
    font-size: 1.3rem;
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--border);
}}
hr {{ border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }}
.delayed-notice {{ color: var(--muted); font-style: italic; margin-bottom: 1rem; }}
.news-item {{
    margin-bottom: 0.3rem;
    padding-left: 0;
}}
.news-item strong.title {{
    font-size: 1.05rem;
    color: var(--text);
}}
.insight {{
    background: var(--insight-bg);
    border-left: 3px solid var(--insight-border);
    padding: 0.5rem 1rem;
    margin: 0.3rem 0 1rem;
    border-radius: 0 6px 6px 0;
    font-size: 0.95rem;
}}
.link {{
    font-size: 0.85rem;
    margin-bottom: 1.2rem;
    word-break: break-all;
}}
.link a {{ color: var(--accent); }}
.github-item {{
    background: var(--github-bg);
    padding: 0.4rem 0.8rem;
    margin-bottom: 0.3rem;
    border-radius: 6px;
    font-size: 0.95rem;
}}
.footer-tag {{
    text-align: center;
    color: var(--muted);
    font-size: 0.85rem;
    margin-top: 2rem;
}}
@media (max-width: 768px) {{
    .container {{ flex-direction: column; }}
    .sidebar {{
        width: 100%;
        height: auto;
        position: static;
        border-right: none;
        border-bottom: 1px solid var(--border);
        padding: 1rem;
    }}
    .sidebar ul {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
    }}
    .sidebar li {{ margin-bottom: 0; }}
    .main {{ padding: 1rem; }}
}}
</style>
</head>
<body>
<div class="container">
<nav class="sidebar">
    <h3>📰 历史日报</h3>
    <ul>
        {archive_html}
    </ul>
</nav>
<main class="main">
{content}
</main>
</div>
</body>
</html>'''

def build_site():
    """Main build function."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    archives = get_archive_dates()
    if not archives:
        print("No archives found!")
        return

    print(f"Found {len(archives)} archive files")

    # Build individual archive pages
    for date_str, filepath in archives:
        with open(filepath, 'r') as f:
            md_content = f.read()

        # Extract title from first line
        first_line = md_content.split('\n')[0]
        title = first_line.replace('# ', '').strip()

        html_content = md_to_html(md_content)
        page = build_page(title, html_content, archives, current_date=date_str)

        output_path = os.path.join(OUTPUT_DIR, f"{date_str}.html")
        with open(output_path, 'w') as f:
            f.write(page)
        print(f"  Built {date_str}.html")

    # Build index page (redirects to latest)
    latest_date, _ = archives[0]
    with open(os.path.join(OUTPUT_DIR, f"{latest_date}.html"), 'r') as f:
        latest_html = f.read()

    # Copy latest as index
    with open(os.path.join(OUTPUT_DIR, "index.html"), 'w') as f:
        f.write(latest_html)
    print(f"  Built index.html → {latest_date}.html")

    print(f"\nSite built in {OUTPUT_DIR}/")
    print(f"Open: file://{OUTPUT_DIR}/index.html")

if __name__ == '__main__':
    build_site()
