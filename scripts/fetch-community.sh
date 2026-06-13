#!/bin/bash
# Fetch community discussions: Hacker News + V2EX + LinuxDo
# Output: /tmp/td-community.json

OUTPUT="/tmp/td-community.json"
PROXY="http://127.0.0.1:7890"

echo "[community] Fetching..."

python3 << 'PYEOF'
import json, subprocess, sys

PROXY = "http://127.0.0.1:7890"
results = []

def curl(url, timeout=10):
    try:
        r = subprocess.run(["curl", "-s", "--proxy", PROXY, "--max-time", str(timeout), url],
                          capture_output=True, text=True, timeout=timeout+3)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout
    except:
        pass
    return ""

# --- Hacker News Top ---
print("[community] HN...", file=sys.stderr)
hn_ids = curl("https://hacker-news.firebaseio.com/v0/topstories.json")
if hn_ids:
    try:
        ids = json.loads(hn_ids)[:30]
    except:
        ids = []
    count = 0
    for item_id in ids:
        if count >= 5:
            break
        story_raw = curl(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", 5)
        if not story_raw:
            continue
        try:
            story = json.loads(story_raw)
            score = story.get('score', 0)
            if score >= 30 and story.get('title'):
                results.append({
                    'title': story['title'],
                    'link': story.get('url', f"https://news.ycombinator.com/item?id={item_id}"),
                    'source': 'Hacker News',
                    'score': score,
                    'comments': story.get('descendants', 0)
                })
                count += 1
        except:
            pass
    print(f"  HN: {count}", file=sys.stderr)

# --- V2EX Hot ---
print("[community] V2EX...", file=sys.stderr)
v2ex_raw = curl("https://www.v2ex.com/api/topics/hot.json")
if v2ex_raw:
    try:
        topics = json.loads(v2ex_raw)
        for t in topics[:10]:
            if len([r for r in results if r['source'].startswith('V2EX')]) >= 3:
                break
            title = t.get('title','')
            if not title:
                continue
            results.append({
                'title': title,
                'link': t.get('url', f"https://www.v2ex.com/t/{t.get('id','')}"),
                'source': f"V2EX {t.get('node',{}).get('title','')}",
                'score': t.get('replies', 0),
                'comments': t.get('replies', 0)
            })
    except:
        pass
    v2ex_count = len([r for r in results if r['source'].startswith('V2EX')])
    print(f"  V2EX: {v2ex_count}", file=sys.stderr)

# --- LinuxDo Hot ---
print("[community] LinuxDo...", file=sys.stderr)
linuxdo_raw = curl("https://linux.do/top/daily.json")
if linuxdo_raw:
    try:
        data = json.loads(linuxdo_raw)
        topics = data.get('topic_list',{}).get('topics',[])
        ld_count = 0
        for t in topics[:5]:
            if ld_count >= 3:
                break
            title = t.get('title','')
            if not title:
                continue
            slug = t.get('slug','')
            tid = t.get('id','')
            results.append({
                'title': title,
                'link': f"https://linux.do/t/{slug}/{tid}" if slug else f"https://linux.do/t/topic/{tid}",
                'source': 'LinuxDo',
                'score': t.get('like_count', 0),
                'comments': t.get('posts_count', 0)
            })
            ld_count += 1
        print(f"  LinuxDo: {ld_count}", file=sys.stderr)
    except:
        pass

# Write output
with open('/tmp/td-community.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"[community] Done: {len(results)} items", file=sys.stderr)
PYEOF
