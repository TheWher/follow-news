#!/bin/bash
# Fetch AI trending papers from HuggingFace daily papers
# Output: /tmp/td-papers.json

OUTPUT="/tmp/td-papers.json"
PROXY="http://127.0.0.1:7890"

echo "[papers] Fetching HuggingFace daily papers..."

# Use HuggingFace daily papers API
PAPERS=$(curl -s --proxy "$PROXY" --max-time 15 \
  "https://huggingface.co/api/daily_papers" 2>/dev/null)

if [ -z "$PAPERS" ]; then
  echo "[papers] API failed, trying PapersWithCode trending..."
  PAPERS=$(curl -s --proxy "$PROXY" --max-time 15 \
    "https://paperswithcode.com/api/v1/papers/?ordering=-github_stars" 2>/dev/null)
fi

echo "$PAPERS" | python3 -c "
import json, sys

try:
    data = json.load(sys.stdin)
except:
    print('[]')
    sys.exit(0)

results = []

# HuggingFace format
if isinstance(data, list):
    for paper in data[:20]:
        title = paper.get('title', '') or paper.get('paper',{}).get('title','')
        if not title:
            continue
        paper_id = paper.get('paper',{}).get('id','') or paper.get('id','')
        upvotes = paper.get('upvotes', 0) or paper.get('votes', 0)
        url = f'https://huggingface.co/papers/{paper_id}' if paper_id else ''
        summary = paper.get('paper',{}).get('summary','') or paper.get('summary','') or ''
        # Truncate summary
        summary = summary[:300]

        results.append({
            'title': title,
            'link': url,
            'source': 'HuggingFace Papers',
            'score': upvotes,
            'summary': summary
        })

# PapersWithCode format
elif isinstance(data, dict) and 'results' in data:
    for paper in data['results'][:20]:
        title = paper.get('title','')
        if not title:
            continue
        url = paper.get('url_abs','') or paper.get('url_pdf','') or ''
        stars = paper.get('github_stars', 0) or 0
        summary = paper.get('abstract','')[:300] or ''

        results.append({
            'title': title,
            'link': url,
            'source': 'PapersWithCode',
            'score': stars,
            'summary': summary
        })

# Sort by score desc, take top 10
results.sort(key=lambda x: x['score'], reverse=True)
top = results[:10]

print(json.dumps(top, ensure_ascii=False, indent=2))
" > "$OUTPUT"

COUNT=$(python3 -c "import json; print(len(json.load(open('$OUTPUT'))))" 2>/dev/null || echo 0)
echo "[papers] Done: $COUNT papers → $OUTPUT"
