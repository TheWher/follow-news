#!/bin/bash
# 检查今日日报是否存在，不存在则标记错过
TODAY=$(date +%Y-%m-%d)
DIGEST="/mnt/c/Users/A2260/.claude/follow-news/daily-digest.md"
FLAG="/mnt/c/Users/A2260/.claude/follow-news/.missed"

if [ -f "$DIGEST" ] && grep -q "$TODAY" "$DIGEST" 2>/dev/null; then
    rm -f "$FLAG"
else
    echo "$TODAY" > "$FLAG"
fi
