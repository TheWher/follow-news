#!/bin/bash
# Fetch new AI products/tools: Product Hunt + GitHub trending AI tools
# Output: /tmp/td-products.json

OUTPUT="/tmp/td-products.json"
PROXY="http://127.0.0.1:7890"
TMPDIR="/tmp/td-products-$$"
mkdir -p "$TMPDIR"

echo "[products] Fetching Product Hunt + new AI repos..."

# --- Product Hunt via RSS ---
PH_RSS=$(curl -s --proxy "$PROXY" --max-time 15 \
  "https://www.producthunt.com/feed?category=ai" 2>/dev/null)

echo "$PH_RSS" | python3 -c "
import sys, json, re, html

text = sys.stdin.read()
results = []

# Parse RSS items
items = re.findall(r'<item>(.*?)</item>', text, re.DOTALL)
for item in items[:10]:
    title = re.search(r'<title>(.*?)</title>', item)
    link = re.search(r'<link>(.*?)</link>', item)
    desc = re.search(r'<description>(.*?)</description>', item)

    t = html.unescape(title.group(1)) if title else ''
    l = link.group(1).strip() if link else ''
    d = html.unescape(desc.group(1)) if desc else ''

    # Clean description (strip HTML tags)
    d_clean = re.sub(r'<[^>]+>', '', d)[:200]

    if t and 'AI' in (t + d_clean).upper()[:200]:
        results.append({
            'title': t,
            'link': l,
            'source': 'Product Hunt',
            'score': 0,
            'summary': d_clean
        })

print(json.dumps(results[:5], ensure_ascii=False))
" 2>/dev/null > "$TMPDIR/ph.json"

PH_COUNT=$(python3 -c "import json; print(len(json.load(open('$TMPDIR/ph.json'))))" 2>/dev/null || echo 0)
echo "  Product Hunt: $PH_COUNT AI products"

# --- New AI repos from GitHub (created last 24h, 10+ stars) ---
echo "[products] Fetching new GitHub AI repos..."
GH_NEW=$(curl -s --proxy "$PROXY" --max-time 10 \
  "https://api.github.com/search/repositories?q=AI+agent+tools+created:>$(date -d '2 days ago' +%Y-%m-%d)&sort=stars&order=desc&per_page=10" 2>/dev/null)

echo "$GH_NEW" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    results = []
    for repo in data.get('items', [])[:5]:
        results.append({
            'title': f'{repo[\"full_name\"]}: {repo.get(\"description\",\"\") or \"\"}',
            'link': repo['html_url'],
            'source': 'GitHub New',
            'score': repo.get('stargazers_count', 0),
            'summary': f'⭐ {repo[\"stargazers_count\"]} · Language: {repo.get(\"language\",\"?\")}'
        })
    print(json.dumps(results[:3], ensure_ascii=False))
except:
    print('[]')
" 2>/dev/null > "$TMPDIR/gh_new.json"

GH_COUNT=$(python3 -c "import json; print(len(json.load(open('$TMPDIR/gh_new.json'))))" 2>/dev/null || echo 0)
echo "  GitHub new: $GH_COUNT repos"

# --- Merge ---
python3 -c "
import json

items = []
for f in ['$TMPDIR/ph.json', '$TMPDIR/gh_new.json']:
    try:
        data = json.load(open(f))
        items.extend(data)
    except: pass

# Dedupe by title similarity
seen = set()
unique = []
for item in items:
    key = item['title'][:50].lower()
    if key not in seen:
        seen.add(key)
        unique.append(item)

print(json.dumps(unique[:6], ensure_ascii=False, indent=2))
" > "$OUTPUT"

COUNT=$(python3 -c "import json; print(len(json.load(open('$OUTPUT'))))" 2>/dev/null || echo 0)
echo "[products] Done: $COUNT items → $OUTPUT"
rm -rf "$TMPDIR"
