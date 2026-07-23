#!/usr/bin/env python3
"""AI Scoring engine for news articles (inspired by Horizon).
Rates each article 0-10 on: 影响范围/时效性/新颖性/可信度.
Batch processing via DeepSeek API.
"""

import json, os, sys, time

API_URL = "https://api.deepseek.com/anthropic/v1/messages"
PROXY = "http://127.0.0.1:7890"

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
if not API_KEY:
    # Read from Claude Code settings (ANTHROPIC_AUTH_TOKEN used with DeepSeek endpoint)
    try:
        cfg = json.load(open(os.path.expanduser("~/.claude/settings.json")))
        API_KEY = cfg.get("env",{}).get("ANTHROPIC_AUTH_TOKEN","") or \
                  cfg.get("env",{}).get("DEEPSEEK_API_KEY","")
    except:
        pass

SCORING_PROMPT = """You are a tech news editor evaluating article newsworthiness for an AI/tech daily digest aimed at developers and tech professionals.

Score each article below on these 4 dimensions (each 0-10):

1. **影响范围 (Impact scope)**: How many people/companies does this affect? Industry-wide=8-10, niche=3-5, personal=0-2
2. **时效性 (Timeliness)**: Is this breaking/current news? Today's news=8-10, ongoing=5-7, history=0-3
3. **新颖性 (Novelty)**: Is this surprising/new? Breakthrough=9-10, incremental=4-6, rehash=0-3
4. **可信度 (Credibility)**: Based on source authority. Major outlet/official=8-10, blog=5-7, rumor=0-3

Then calculate: **total_score = round(impact*0.35 + timeliness*0.25 + novelty*0.25 + credibility*0.15, 1)**

Output ONLY valid JSON array, no markdown, no code fences. Each object: {"index": <original_index>, "impact": int, "timeliness": int, "novelty": int, "credibility": int, "total": float, "verdict": "MUST_INCLUDE"|"GOOD"|"MAYBE"|"SKIP"}

Articles to score:
"""

VERDICT_RULES = {
    "MUST_INCLUDE": "总分 8+ — 必选，放日报最前面",
    "GOOD": "总分 6-7.9 — 推荐，视篇幅决定",
    "MAYBE": "总分 4-5.9 — 候补，只选最有代表性的",
    "SKIP": "总分 <4 — 跳过（纯营销/无实质内容/重复）"
}

def score_batch(articles, batch_size=15):
    """Score articles in batches to stay within token limits."""
    scored = []

    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        batch_text = "\n".join([
            f"[{i+j}] {a.get('title','')[:200]}\n  Source: {a.get('source','?')} | Link: {a.get('link','')[:150]}"
            for j, a in enumerate(batch)
        ])

        print(f"  Scoring batch {i//batch_size + 1} ({len(batch)} articles)...", file=sys.stderr)

        try:
            import subprocess

            body = json.dumps({
                "model": "deepseek-v4-pro",
                "max_tokens": 4096,
                "thinking": {"type": "disabled"},
                "messages": [
                    {"role": "user", "content": SCORING_PROMPT + batch_text}
                ]
            })

            r = subprocess.run([
                "curl", "-s", "--proxy", PROXY,
                "-H", "Content-Type: application/json",
                "-H", f"Authorization: Bearer {API_KEY}",
                "-H", f"x-api-key: {API_KEY}",
                API_URL, "-d", body
            ], capture_output=True, text=True, timeout=65)

            data = json.loads(r.stdout)
            content = data.get("content", [{}])
            # Skip thinking blocks
            text_parts = [c.get("text","") for c in content if c.get("type") == "text"]
            content_text = "\n".join(text_parts) if text_parts else ""

            # Strip code fences if present
            if content_text.startswith("```"):
                content_text = content_text.split("\n", 1)[1]
                if content_text.endswith("```"):
                    content_text = content_text[:-3]

            results = json.loads(content_text)
            for r in results:
                r["_idx"] = r["index"]
                scored.append(r)

        except Exception as e:
            print(f"  Score error: {e}", file=sys.stderr)
            # Fallback: assign default scores
            for j, a in enumerate(batch):
                scored.append({
                    "index": i+j, "_idx": i+j,
                    "impact": 5, "timeliness": 5, "novelty": 5, "credibility": 5,
                    "total": 5.0, "verdict": "MAYBE",
                    "_fallback": True
                })

        time.sleep(0.5)  # Rate limit

    # Sort back by original index
    scored.sort(key=lambda x: x["_idx"])
    return scored

def filter_by_threshold(articles, scores, threshold=5.0):
    """Filter articles below threshold."""
    filtered = []
    for a, s in zip(articles, scores):
        if s.get("total", 0) >= threshold:
            a["_score"] = s
            filtered.append(a)

    # Sort by score desc
    filtered.sort(key=lambda x: x.get("_score", {}).get("total", 0), reverse=True)
    return filtered

if __name__ == '__main__':
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from config.project_paths import FN_ARTICLES_DEDUPED, FN_ARTICLES_SCORED
    input_file = sys.argv[1] if len(sys.argv) > 1 else FN_ARTICLES_DEDUPED
    output_file = sys.argv[2] if len(sys.argv) > 2 else FN_ARTICLES_SCORED
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0

    with open(input_file, 'r') as f:
        articles = json.load(f)

    print(f"Scoring {len(articles)} articles (threshold={threshold})...", file=sys.stderr)

    if not API_KEY:
        print("WARNING: No API key, using default scores", file=sys.stderr)
        scores = [{
            "index": i, "_idx": i,
            "impact": 5, "timeliness": 5, "novelty": 5, "credibility": 5,
            "total": 5.0, "verdict": "MAYBE", "_fallback": True
        } for i in range(len(articles))]
    else:
        scores = score_batch(articles)

    scored_articles = filter_by_threshold(articles, scores, threshold)

    verdicts = {}
    for a in scored_articles:
        v = a.get("_score", {}).get("verdict", "?")
        verdicts[v] = verdicts.get(v, 0) + 1

    print(f"Scored: {len(scored_articles)}/{len(articles)} above threshold ({verdicts})", file=sys.stderr)

    with open(output_file, 'w') as f:
        json.dump(scored_articles, f, ensure_ascii=False, indent=2)
