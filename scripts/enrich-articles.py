#!/usr/bin/env python3
"""Background enrichment for top-scored articles (inspired by Horizon).
For articles with score >= 7, extract key entities and search web for context.
Appends enrichment to the article's summary for deeper 💡 insights.
"""

import json, sys, re, subprocess, urllib.parse, time

JINA_READER = "https://r.jina.ai"
SEARCH_API = "https://api.duckduckgo.com"  # Fallback: simple web search

def extract_entities(title, snippet):
    """Extract company/product/tech names worthy of background research."""
    entities = []

    # Known patterns: Capitalized Names, "X's Y", quoted terms
    caps = re.findall(r'\b[A-Z][a-zA-Z]+\s+(?:AI|LLM|API|ML|OS|GPU|VR|AR|SDK|CLI|MCP|IPO|CEO)\b', title)
    entities.extend(caps)

    # Product names in quotes
    quoted = re.findall(r'["“]([^"”]+)["”]', title)
    entities.extend(quoted[:2])

    # Company names (common patterns)
    companies = re.findall(r'\b(?:Anthropic|OpenAI|Google|Microsoft|Meta|Apple|Amazon|NVIDIA|DeepSeek|HuggingFace|SpaceX|Valve|Oracle|PeopleSoft|FFmpeg|CRISPR|ByteDance|Alibaba|Huawei|Tencent|Baidu)\b', title + " " + snippet)
    entities.extend(companies)

    # Dedupe, limit to 3
    seen = set()
    unique = []
    for e in entities:
        if e.lower() not in seen:
            seen.add(e.lower())
            unique.append(e)
    return unique[:3]

def search_web(query):
    """Search web for context about an entity."""
    try:
        # Use Jina Reader for search results
        r = subprocess.run([
            "curl", "-s", "--max-time", "10",
            f"{JINA_READER}/https://www.google.com/search?q={urllib.parse.quote(query)}"
        ], capture_output=True, text=True, timeout=12)
        if r.returncode == 0 and r.stdout:
            # Extract first few paragraphs
            text = r.stdout[:1500]
            # Clean Jina formatting
            text = re.sub(r'\[.*?\]\(.*?\)', '', text)
            return text[:500].strip()
    except:
        pass
    return ""

def enrich_article(article):
    """Add background context to an article."""
    title = article.get('title','')
    snippet = article.get('snippet','') or article.get('summary','') or ''
    score_obj = article.get('_score', {})
    total_score = score_obj.get('total', 0) if isinstance(score_obj, dict) else score_obj

    # Only enrich high-scored articles
    if total_score < 7:
        return article

    entities = extract_entities(title, snippet)
    if not entities:
        return article

    contexts = []
    for entity in entities[:2]:  # Max 2 entities
        ctx = search_web(f"{entity} what is background context")
        if ctx and len(ctx) > 30:
            contexts.append(f"{entity}: {ctx[:200]}")

    if contexts:
        article['_enrichment'] = contexts
        print(f"  Enriched: {title[:60]} -> {len(contexts)} entities", file=sys.stderr)

    return article

if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/td-articles-scored.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else '/tmp/td-articles-enriched.json'

    with open(input_file, 'r') as f:
        articles = json.load(f)

    print(f"Enriching top articles (score >= 7)...", file=sys.stderr)
    enriched = []
    for a in articles:
        enriched.append(enrich_article(a))

    enriched_count = sum(1 for a in enriched if '_enrichment' in a)
    print(f"Enriched: {enriched_count}/{len(enriched)} articles", file=sys.stderr)

    with open(output_file, 'w') as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)
