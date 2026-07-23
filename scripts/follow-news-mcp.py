#!/usr/bin/env python3
"""MCP Server for follow-news — expose daily AI news pipeline as tools.
Standards: Model Context Protocol (MCP) via stdio JSON-RPC.
Tools: search_news, get_trending, get_papers, get_products, get_community, get_digest
"""

import json, sys, os, glob
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.project_paths import (
    ARCHIVE_DIR, LATEST_DIGEST,
    FN_ARTICLES, FN_ARTICLES_ENRICHED,
    FN_GITHUB, FN_PAPERS, FN_COMMUNITY, FN_PRODUCTS,
)

DIGEST_FILE = LATEST_DIGEST

def read_json(path, default=None):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return default if default is not None else []

def format_article(a):
    title = a.get('title','')
    link = a.get('link','')
    source = a.get('source','?')
    score = a.get('_score',{}).get('total','-') if isinstance(a.get('_score'), dict) else '-'
    return f"• {title}\n  [{source}] score={score}\n  {link}"

# Tool definitions
TOOLS = [
    {
        "name": "search_news",
        "description": "Search today's AI/tech news articles. Returns scored and filtered news items.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keyword to filter articles (title match)"},
                "limit": {"type": "integer", "default": 10, "description": "Max results"},
                "min_score": {"type": "number", "default": 5.0, "description": "Minimum AI score threshold"}
            }
        }
    },
    {
        "name": "get_trending_repos",
        "description": "Get trending GitHub repositories (daily star growth).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "get_trending_papers",
        "description": "Get trending AI/ML papers from HuggingFace daily papers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 10}
            }
        }
    },
    {
        "name": "get_community_discussions",
        "description": "Get hot community discussions from Hacker News, V2EX, and LinuxDo.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 8}
            }
        }
    },
    {
        "name": "get_new_products",
        "description": "Get new AI products and tools.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 5}
            }
        }
    },
    {
        "name": "get_latest_digest",
        "description": "Get the latest daily AI/tech digest in Chinese.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_archive_digest",
        "description": "Get a specific date's daily digest from the archive.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format (e.g., 2026-06-13)"}
            },
            "required": ["date"]
        }
    },
    {
        "name": "list_archives",
        "description": "List all available archive dates.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

def handle_tool(name, args):
    if name == "search_news":
        query = args.get("query", "").lower()
        limit = args.get("limit", 10)
        min_score = args.get("min_score", 5.0)

        articles = read_json(FN_ARTICLES_ENRICHED) or read_json(FN_ARTICLES)

        results = []
        for a in articles:
            score = a.get('_score',{}).get('total', 5.0) if isinstance(a.get('_score'), dict) else 5.0
            if score < min_score:
                continue
            if query and query not in a.get('title','').lower():
                continue
            results.append(format_article(a))
            if len(results) >= limit:
                break

        return {"content": [{"type": "text", "text": f"🔍 Found {len(results)} articles matching '{query}':\n\n" + "\n\n".join(results) if results else "No articles found."}]}

    elif name == "get_trending_repos":
        limit = args.get("limit", 10)
        repos = read_json(FN_GITHUB)
        lines = []
        for r in repos[:limit]:
            lines.append(f"• {r['title'].split('|')[0].strip()} ⭐{r.get('stars','?')} (+{r.get('daily_growth',0):.0f}/d)\n  {r['link']}")
        return {"content": [{"type": "text", "text": f"🔥 GitHub Trending ({len(repos[:limit])} repos):\n\n" + "\n\n".join(lines)}]}

    elif name == "get_trending_papers":
        limit = args.get("limit", 10)
        papers = read_json(FN_PAPERS)
        lines = []
        for p in papers[:limit]:
            lines.append(f"• {p['title']}\n  📄 {p.get('summary','')[:150]}\n  {p.get('link','')}")
        return {"content": [{"type": "text", "text": f"📄 AI Papers ({len(papers[:limit])}):\n\n" + "\n\n".join(lines)}]}

    elif name == "get_community_discussions":
        limit = args.get("limit", 8)
        discussions = read_json(FN_COMMUNITY)
        lines = []
        for d in discussions[:limit]:
            lines.append(f"• [{d['source']}] {d['title']}\n  💬 {d.get('comments',0)} comments · {d.get('score',0)} pts\n  {d['link']}")
        return {"content": [{"type": "text", "text": f"💬 Community Discussions ({len(discussions[:limit])}):\n\n" + "\n\n".join(lines)}]}

    elif name == "get_new_products":
        limit = args.get("limit", 5)
        products = read_json(FN_PRODUCTS)
        lines = []
        for p in products[:limit]:
            lines.append(f"• [{p['source']}] {p['title']}\n  🆕 {p.get('summary','')[:150]}\n  {p['link']}")
        return {"content": [{"type": "text", "text": f"🆕 New AI Products ({len(products[:limit])}):\n\n" + "\n\n".join(lines)}]}

    elif name == "get_latest_digest":
        try:
            with open(DIGEST_FILE, 'r') as f:
                digest = f.read()
        except:
            digest = "Digest not available yet."
        return {"content": [{"type": "text", "text": digest}]}

    elif name == "get_archive_digest":
        date_str = args["date"]
        filepath = os.path.join(ARCHIVE_DIR, f"daily-{date_str}.md")
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return {"content": [{"type": "text", "text": content}]}
        except:
            return {"content": [{"type": "text", "text": f"No digest found for {date_str}"}]}

    elif name == "list_archives":
        files = sorted(glob.glob(os.path.join(ARCHIVE_DIR, "daily-*.md")), reverse=True)
        dates = [os.path.basename(f).replace("daily-","").replace(".md","") for f in files]
        return {"content": [{"type": "text", "text": f"📅 {len(dates)} archives:\n" + "\n".join(f"  - {d}" for d in dates)}]}

    return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}]}

def main():
    # MCP stdio protocol
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            request = json.loads(line.strip())

            req_id = request.get("id")
            method = request.get("method")

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "follow-news-mcp",
                            "version": "3.18"
                        }
                    }
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": TOOLS}
                }
            elif method == "tools/call":
                tool_name = request.get("params",{}).get("name","")
                tool_args = request.get("params",{}).get("arguments",{})
                result = handle_tool(tool_name, tool_args)
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": result
                }
            elif method == "notifications/initialized":
                continue  # Don't respond to notifications
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }

            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError:
            continue
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": req_id if req_id else None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()

if __name__ == '__main__':
    main()
