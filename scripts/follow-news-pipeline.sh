#!/bin/bash
# follow-news pipeline — 机械工作：锁检查、数据采集、提取去重
# Exit codes: 0=数据就绪, 1=正在生成, 2=今日已投递, 3=管道失败

set -e
WORK=/mnt/c/Users/A2260/.claude/follow-news
SKILL=/mnt/c/Users/A2260/skills/follow-news
TODAY=$(date +%Y-%m-%d)

# --- 检查是否已投递 ---
if [ -f "$WORK/.delivered-$TODAY" ]; then
    echo "STATUS:already_delivered"
    exit 2
fi

# --- 检查是否正在生成 ---
if [ -f "$WORK/.generating" ]; then
    # 检查锁文件年龄（秒）
    AGE=$(($(date +%s) - $(stat -c %Y "$WORK/.generating" 2>/dev/null || echo 0)))
    if [ "$AGE" -lt 5400 ]; then
        echo "STATUS:generating_in_progress age=${AGE}s"
        exit 1
    fi
    echo "STATUS:stale_lock_cleaned age=${AGE}s"
    rm -f "$WORK/.generating"
fi

# --- 创建生成锁 ---
touch "$WORK/.generating"

# --- 数据采集管道 ---
echo "STATUS:pipeline_start"
cd "$SKILL"
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python3 scripts/run-pipeline.py \
    --defaults config/defaults \
    --config "$WORK/config" \
    --hours 48 \
    --freshness pd \
    --archive-dir "$WORK/archive/follow-news" \
    --output /tmp/td-merged.json \
    --force \
    > /tmp/td-pipeline.log 2>&1

if [ $? -ne 0 ]; then
    echo "STATUS:pipeline_failed"
    rm -f "$WORK/.generating"
    exit 3
fi

echo "STATUS:pipeline_done"

# --- 提取去重 ---
PYTHONIOENCODING=utf-8 python3 -c "
import json
with open('/tmp/td-merged.json') as f:
    data = json.load(f)
topics = data.get('topics', {})
articles = []
for tid, td in topics.items():
    for a in td.get('articles', []):
        articles.append({
            'title': a.get('title', '')[:200],
            'snippet': (a.get('snippet') or '')[:300],
            'summary': (a.get('summary') or '')[:400],
            'link': a.get('link', '') or '',
        })
seen = set()
unique = []
for a in articles:
    k = a['title'][:80].lower().strip()
    if k and k not in seen:
        seen.add(k)
        unique.append(a)
with open('/tmp/td-articles.json', 'w') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print(f'articles={len(unique)}')
"

echo "STATUS:ready"
exit 0
