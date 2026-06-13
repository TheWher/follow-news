#!/bin/bash
# GitHub Trending 补充采集 — 追加到 /tmp/td-articles.json
# 策略: 搜近期创建/活跃仓库，按日均涨星排序，关注新锐项目

set -e
HOURS_CREATED=168  # 7 days for new repos
HOURS_PUSHED=72    # 3 days for active repos
CUTOFF_CREATED=$(date -d "$HOURS_CREATED hours ago" -u +%Y-%m-%d)
CUTOFF_PUSHED=$(date -d "$HOURS_PUSHED hours ago" -u +%Y-%m-%d)
OUT=/tmp/td-github-trending.json
LOG=/tmp/td-github-trending.log

echo "=== GitHub Trending ($(date)) ===" > "$LOG"
echo "created cutoff: $CUTOFF_CREATED, pushed cutoff: $CUTOFF_PUSHED" >> "$LOG"

# 多维查询: created(新项目发现) + pushed(活跃项目)
declare -A QUERIES
QUERIES["AI-Agent-新项目"]="ai-agent+OR+llm+OR+agentic+created:>$CUTOFF_CREATED+stars:>20&sort=stars&order=desc&per_page=6"
QUERIES["开发者工具-新项目"]="developer-tools+OR+cli+OR+devtools+created:>$CUTOFF_CREATED+stars:>20&sort=stars&order=desc&per_page=6"
QUERIES["开源替代-新项目"]="open-source+alternative+OR+self-hosted+created:>$CUTOFF_CREATED+stars:>20&sort=stars&order=desc&per_page=6"
QUERIES["AI-ML-近期活跃"]="machine-learning+OR+deep-learning+OR+llm+pushed:>$CUTOFF_PUSHED+stars:>50&sort=stars&order=desc&per_page=6"
QUERIES["MCP-工具-近期活跃"]="mcp+OR+model-context-protocol+OR+ai-tools+pushed:>$CUTOFF_PUSHED+stars:>10&sort=stars&order=desc&per_page=6"

for label in "${!QUERIES[@]}"; do
  q="${QUERIES[$label]}"
  echo "--- $label ---" >> "$LOG"
  URL="https://api.github.com/search/repositories?q=${q}"

  RESP=$(curl -sk --noproxy '*' --connect-timeout 10 --max-time 15 \
    -H "User-Agent: FollowNews/1.0" \
    -H "Accept: application/vnd.github.v3+json" \
    "$URL" 2>> "$LOG")

  echo "$RESP" | python3 -c "
import json,sys
data=json.load(sys.stdin)
repos=[]
for item in data.get('items',[])[:5]:
    from datetime import datetime, timezone
    created = item.get('created_at','')
    stars = item['stargazers_count']
    days = 1
    if created:
        try:
            dt = datetime.fromisoformat(created.replace('Z','+00:00'))
            days = max(1, (datetime.now(timezone.utc) - dt).days)
        except: pass
    daily = stars / days
    desc = (item.get('description') or 'No description')[:120]
    topics = ','.join(item.get('topics',[])[:5])
    repos.append({
        'title': f\"⭐{stars} (+{daily:.0f}/d) | {item['full_name']}: {desc}\",
        'snippet': f\"{item['full_name']} — {desc} [Stars: {stars}, +{daily:.0f}/d, Created: {created[:10]}, Topics: {topics}]\",
        'summary': f\"GitHub: {item['full_name']} — {desc} [⭐{stars}, 日均+{daily:.0f}, 语言: {item.get('language','?')}]\",
        'link': item['html_url'],
        'source': 'github-trending',
        'stars': stars,
        'daily_growth': daily
    })
json.dump(repos, sys.stdout, ensure_ascii=False)
" 2>> "$LOG" > "/tmp/td-gt-${label// /_}.json"
  echo "  done" >> "$LOG"
done

# 合并去重，按日均涨星排序
python3 -c "
import json,glob
all_repos=[]
seen=set()
for f in sorted(glob.glob('/tmp/td-gt-*.json')):
    repos=json.load(open(f))
    for r in repos:
        key=r['link']
        if key not in seen:
            seen.add(key)
            all_repos.append(r)
all_repos.sort(key=lambda r: r.get('daily_growth',0), reverse=True)
result = all_repos[:20]
json.dump(result, open('$OUT','w'), ensure_ascii=False, indent=2)
n = len(result)
for i, r in enumerate(result[:5]):
    print(f'  {i+1}. {r[\"title\"][:120]}')
print(f'github_trending={n}')
" 2>> "$LOG" | tee -a "$LOG"

# 追加到 articles
if [ -f /tmp/td-articles.json ]; then
  python3 -c "
import json
existing=json.load(open('/tmp/td-articles.json'))
trending=json.load(open('$OUT'))
for r in trending:
    r.pop('stars',None)
    r.pop('daily_growth',None)
existing.extend(trending)
json.dump(existing, open('/tmp/td-articles.json','w'), ensure_ascii=False)
print(f'merged: {len(existing)} total articles')
" 2>&1 | tee -a "$LOG"
fi

echo "=== Done ===" >> "$LOG"
