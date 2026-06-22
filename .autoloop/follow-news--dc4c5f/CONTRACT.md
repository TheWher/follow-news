---
name: follow-news
version: 1
schema_version: 2
iteration: 10
last_updated: 2026-06-22T07:00:00Z
exit_condition: "user-stop OR explicit DONE section"
max_iterations: 3650
trigger: "/loop — reads this file verbatim each firing"
dispatch_policy:
  enabled: false
  require_experimental_teams: false
# === IMMUTABLE BIRTH RECORD ===
loop_id: c7f2c27b949b
campaign_slug: follow-news
created_at_utc: 2026-06-11T09:00:00Z
created_in_session: pending-bind
created_at_cwd: /mnt/c/Users/A2260/.claude/follow-news
created_at_git_branch: N/A
created_at_git_commit: N/A
# === MUTABLE OWNERSHIP MIRROR ===
owner_session_id: pending-bind
owner_pid: 0
owner_started_us: 0
generation: 0
last_heartbeat_us: 0
last_heartbeat_session_id: ""
# === CROSS-LINKS ===
state_dir: /mnt/c/Users/A2260/.claude/follow-news/.autoloop/follow-news--dc4c5f/state
revision_log_path: /mnt/c/Users/A2260/.claude/follow-news/.autoloop/follow-news--dc4c5f/state/revision-log
# === STALENESS HINT ===
expected_cadence: "daily"
status: "active"
---

# 每日 AI 科技日报

**This file IS the /loop prompt.** Each firing reads it, generates the daily digest, delivers it, and self-revises. **v3.20** — multi-source rotation + cross-day URL dedup + weekly summary.

## How to invoke this loop

The daily trigger is a thin CronCreate job (7:03 AM Beijing = 23:03 UTC previous day). Its prompt is stable — the contract below holds all the logic:

```
/loop

Read and execute the latest autonomous work contract at:
  /mnt/c/Users/A2260/.claude/follow-news/.autoloop/follow-news--dc4c5f/CONTRACT.md

Follow its instructions verbatim. That file self-updates; this trigger stays fixed.
```

Backup trigger at 8:57 AM Beijing (00:57 UTC) uses the same pointer trigger.

---

## Core Directive

每日自动采集过去 24-48 小时的 AI/科技新闻，按重要性排序撰写 8-15 条中文日报，包含 🔥 GitHub Trending 板块，投递到微信。每条新闻包含 Unicode bold 标题 + 1 句摘要 + 💡 1 句解读（做什么+影响+怎么用）+ 🔗 链接。宁缺毋滥。

---

## Provenance & Ownership

**Loop ID**: `c7f2c27b949b` · **Campaign**: `follow-news`
**Created**: `2026-06-11T09:00:00Z` in session `pending-bind` at `/mnt/c/Users/A2260/.claude/follow-news`
**State**: `.autoloop/follow-news--dc4c5f/state/` · **Revision log**: `.autoloop/follow-news--dc4c5f/state/revision-log/`
**Registry**: `jq '.loops[] | select(.loop_id == "c7f2c27b949b")' ~/.claude/loops/registry.json`

---

## Execution Contract

Each firing MUST complete all 5 steps below. A firing that skips a step is a regression.

### Step 0 — 防重复 + 延迟检查 + 多源轮换

```bash
PROJECT_CWD="/mnt/c/Users/A2260/.claude/follow-news"
TODAY=$(date +%Y-%m-%d)
RERUN_TRACKER="$PROJECT_CWD/.rerun-count-$TODAY"
USED_URLS="$PROJECT_CWD/.used-urls.json"  # persisted to Git, cross-day dedup
CACHE_DIR="$PROJECT_CWD/cache"
mkdir -p "$CACHE_DIR"
export CACHE_DIR  # subprocesses (shell scripts) inherit this
USED_URLS_TMP="$CACHE_DIR/ai-daily-used-urls-$TODAY.txt"

# Detect: auto (cron) or manual (user request)
# AUTO_RUN is set to "1" by cron trigger, empty for manual
if [ -z "$AUTO_RUN" ]; then
    RUN_MODE="manual"
else
    RUN_MODE="auto"
fi

# === AUTO mode: skip if already delivered ===
if [ "$RUN_MODE" = "auto" ] && [ -f "$PROJECT_CWD/.delivered-$TODAY" ]; then
    echo "STATUS: already_delivered — exiting"
    exit 0
fi

# === MANUAL mode: increment rerun counter, ALWAYS proceed ===
if [ "$RUN_MODE" = "manual" ]; then
    if [ -f "$RERUN_TRACKER" ]; then
        RERUN_COUNT=$(($(cat "$RERUN_TRACKER") + 1))
    else
        RERUN_COUNT=1
    fi
    echo "$RERUN_COUNT" > "$RERUN_TRACKER"
    echo "STATUS: manual_rerun count=$RERUN_COUNT"
    # Don't exit — always proceed. Use rotation to get fresh data.
fi

# Check if another process is generating
if [ -f "$PROJECT_CWD/.generating" ]; then
    AGE=$(($(date +%s) - $(stat -c %Y "$PROJECT_CWD/.generating" 2>/dev/null || echo 0)))
    if [ "$AGE" -lt 5400 ]; then
        echo "STATUS: generating_in_progress age=${AGE}s — exiting"
        exit 0
    fi
    echo "STATUS: stale_lock_cleaned age=${AGE}s"
    rm -f "$PROJECT_CWD/.generating"
fi

# Check if delayed (>8:00 AM Beijing)
HOUR_BJ=$(TZ=Asia/Shanghai date +%H)
if [ "$HOUR_BJ" -ge 8 ]; then
    DELAYED=true
else
    DELAYED=false
fi

# Init used URLs tracker (persisted + session)
touch "$USED_URLS_TMP"
# Init persisted URL state if missing
if [ ! -f "$USED_URLS" ]; then
    echo '{"urls":{},"last_prune":"'"$TODAY"'"}' > "$USED_URLS"
fi

# === Multi-source rotation for manual reruns ===
# Rotation order (cycles through different real-time sources each run):
#   run 1: follow-news MCP pipeline (default, broad coverage)
#   run 2: TechCrunch AI + The Decoder (English first-hand)
#   run 3: Techmeme + Google News 24h (aggregator breadth)
#   run 4+: combo of 2-3 randomly selected from pool
#
# This ensures each rerun within a single day gets DIFFERENT fresh data.
case ${RERUN_COUNT:-0} in
    0) ROTATION="default" ;;     # auto cron — use pipeline
    1) ROTATION="default" ;;     # first manual — use pipeline (broad)
    2) ROTATION="techcrunch_decoder" ;;  # second — English first-hand
    3) ROTATION="techmeme_google" ;;     # third — aggregators
    *) ROTATION="random_pool" ;;         # fourth+ — random combo
esac
echo "STATUS: rotation=$ROTATION mode=$RUN_MODE"
```

**Logic summary:**
- **Auto (cron)**: `.delivered-$TODAY` exists → skip. Standard pipeline.
- **Manual (user)**: ALWAYS proceed. Increment counter. Pick rotation.
- **Rotation**: each manual rerun uses different sources → fresh content guaranteed.
- **Lock**: shared between auto and manual — only one generation at a time.

**Same-day dedup (v3.21)**: Each run appends its URLs to `$USED_URLS_TMP`. Before writing digest, filter ALL candidate articles against this file — skip any URL already seen in today's earlier runs. This prevents the 4th rerun from repeating news the 1st run already covered.

```bash
# === Same-day dedup — append mode, survives across reruns ===
# Before generating digest, filter out URLs already seen today
if [ -s "$USED_URLS_TMP" ]; then
    ALREADY_TODAY=$(wc -l < "$USED_URLS_TMP")
    echo "STATUS: $ALREADY_TODAY URLs already used in earlier runs today"
else
    echo "STATUS: first run today — no same-day dedup needed"
fi
```

**RERUN_COUNT ≥ 3 → skip fixed-layer in digest**: GitHub trending, community, papers, products are same-day stable. After 2 editions, they're stale. The digest should be NEWS-ONLY — skip sections 2-5 (GitHub/Community/Papers/Products). Just deliver fresh news from the rotated source pool.

### Step 1 — 数据采集（多源轮换）

**If rotation is `default`** (auto cron or first manual run):

```bash
# 1a. Primary pipeline: news collection (runs in background)
bash ~/.openclaw/scripts/follow-news-pipeline.sh &
PIPELINE_PID=$!

# 1b-1e. Fixed-layer sources (always run, same-day stable)
bash ~/.openclaw/scripts/fetch-github-trending.sh
bash ~/.openclaw/scripts/fetch-community.sh
bash ~/.openclaw/scripts/fetch-papers.sh
bash ~/.openclaw/scripts/fetch-products.sh

wait $PIPELINE_PID
PIPELINE_EXIT=$?

case $PIPELINE_EXIT in
    0) echo "Pipeline: data ready" ;;
    1) echo "Pipeline: generating in progress — exiting"; exit 0 ;;
    2) echo "Pipeline: already delivered — exiting"; exit 0 ;;
    3) echo "Pipeline: FAILED — reporting and exiting"; exit 3 ;;
    *) echo "Pipeline: unexpected exit $PIPELINE_EXIT — exiting"; exit 3 ;;
esac

# 1f-1h. Process
python3 ~/.openclaw/scripts/dedup-articles.py $CACHE_DIR/td-articles.json $CACHE_DIR/td-articles-deduped.json
python3 ~/.openclaw/scripts/score-articles.py $CACHE_DIR/td-articles-deduped.json $CACHE_DIR/td-articles-scored.json 5.0
python3 ~/.openclaw/scripts/enrich-articles.py $CACHE_DIR/td-articles-scored.json $CACHE_DIR/td-articles-enriched.json

# 1i. Same-day dedup — filter out URLs already seen in today's earlier runs
if [ -s "$USED_URLS_TMP" ]; then
    python3 -c "
import json
seen = set(open('$USED_URLS_TMP').read().strip().split('\n'))
for f in ['$CACHE_DIR/td-articles-enriched.json', '$CACHE_DIR/td-articles-scored.json']:
    articles = json.load(open(f))
    fresh = [a for a in articles if a.get('link','') not in seen]
    json.dump(fresh, open(f,'w'), ensure_ascii=False)
    print(f'same-day-filtered {f}: {len(fresh)}/{len(articles)} fresh')
"
fi
```

**If rotation is NOT `default`** (manual rerun — use real-time web sources):

The AI agent (Claude Code) directly scrapes live sources using `mcp__hyperbrowser__scrape_webpage`. No shell pipeline needed — the agent orchestrates data collection inline.

**⚠️ Same-day dedup for agent-scraped sources**: Before selecting news to include in the digest, the agent MUST:
1. Read `$USED_URLS_TMP` to get all URLs already used in today's earlier runs
2. Skip any article whose URL appears in that file
3. After writing the digest, append all new URLs to `$USED_URLS_TMP`

**Fixed-layer at RERUN_COUNT >= 2**: Still fetch (or reuse cached) fixed-layer data. But in the digest, diff against the previous edition — only show items that are new or changed. See Step 2 diff mode rules.

**Data source rotation table**:

| Rotation | News Sources | Method |
|----------|-------------|--------|
| `techcrunch_decoder` | TechCrunch AI + The Decoder | `scrape_webpage` x2 |
| `techmeme_google` | Techmeme + Google News 24h | `scrape_webpage` x2 |
| `random_pool` | Pick 2-3 from pool: [TechCrunch, Decoder, Techmeme, HN 24h, Bing News] | `scrape_webpage` x3 |

**Deduplication (cross-day, persisted to Git)**: Before writing the digest, check each article URL against `$USED_URLS` (persisted JSON). Skip any URL already seen in the last 7 days. After delivery, append new URLs and prune old entries.

```bash
# Filter out already-used URLs (persisted cross-day)
if [ -f "$USED_URLS" ]; then
    python3 -c "
import json, sys
from datetime import datetime, timedelta
cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
with open('$USED_URLS') as f:
    state = json.load(f)
urls = state.get('urls', {})
# prune old entries
state['urls'] = {u:d for u,d in urls.items() if d >= cutoff}
# load articles
with open('$CACHE_DIR/td-articles-enriched.json') as f:
    articles = json.load(f)
fresh = [a for a in articles if a.get('link','') not in state['urls']]
json.dump(fresh, open('$CACHE_DIR/td-articles-enriched.json','w'), ensure_ascii=False)
# also filter td-articles-scored.json for downstream
with open('$CACHE_DIR/td-articles-scored.json') as f:
    scored = json.load(f)
scored_fresh = [a for a in scored if a.get('link','') not in state['urls']]
json.dump(scored_fresh, open('$CACHE_DIR/td-articles-scored.json','w'), ensure_ascii=False)
print(f'cross-day-filtered: {len(fresh)}/{len(articles)} fresh, {len(state[\"urls\"])} tracked URLs')
"
fi
```

**Fixed-layer reuse**: GitHub trending, community, papers, and products JSONs are same-day stable. If they already exist from a previous run today, reuse them directly (no need to re-fetch). Only re-fetch if files are missing or older than 12h.

```bash
# Reuse fixed-layer if already fetched today (saves API calls)
for f in td-github-trending td-community td-papers td-products; do
    if [ -f "$CACHE_DIR/${f}.json" ]; then
        AGE=$(($(date +%s) - $(stat -c %Y "$CACHE_DIR/${f}.json" 2>/dev/null || echo 0)))
        if [ "$AGE" -lt 43200 ]; then  # <12h old → reuse
            echo "Reusing $CACHE_DIR/${f}.json (${AGE}s old)"
            continue
        fi
    fi
    # Re-fetch if missing or stale
    echo "Re-fetching ${f}..."
    bash ~/.openclaw/scripts/${f//-/}.sh 2>/dev/null || true
done
```

Exit codes from pipeline (default rotation only):
- `0` → data ready, continue
- `1` → generating in progress, exit
- `2` → already delivered, exit
- `3` → pipeline failure, fall back to direct web scraping instead of exiting

### Step 2 — 生成日报

Read these files:
- `$CACHE_DIR/td-articles-enriched.json` (scored + enriched news)
- `/mnt/c/Users/A2260/.claude/follow-news/digest-rules.md`
- `$CACHE_DIR/td-github-trending.json` (🔥 GitHub)
- `$CACHE_DIR/td-community.json` (💬 社区)
- `$CACHE_DIR/td-papers.json` (📄 论文)
- `$CACHE_DIR/td-products.json` (🆕 产品)

**Scoring aid**: articles sorted by `_score.total` desc. Verdicts: MUST_INCLUDE (8+) > GOOD (6-7.9) > MAYBE (4-5.9). Use verdicts as sorting guide.

**Sections** (in order):
1. **AI/科技新闻** (8-15 条) — 按 AI 评分排序，MUST_INCLUDE 优先
2. **🔥 GitHub Trending** (3-5 个) — 日增星最快
3. **💬 社区讨论** (2-3 条) — HN/V2EX/LinuxDo 热帖
4. **📄 AI 热门论文** (2-3 篇) — HuggingFace 日榜
5. **🆕 产品/工具** (1-2 个) — 新 AI 产品

**Section separator**: `---` between each section

**Enrichment**: If article has `_enrichment` field, use it to write more specific 💡 insights.

**Rules**:
- 8-15 news items, quality over quantity
- Chinese output, technical terms in English (LLM, API, Agent, etc.)
- If `$DELAYED` is true, add `⏰ 今日延迟发送，请见谅。` below the title
- If `$RERUN_COUNT` >= 1, title format: `# 🌐 每日 AI 科技日报 — 2026年6月22日 第N版 🆕`
- End with `🤖 autoloop follow-news v3.20`
- **Output markdown only** — do NOT generate HTML.
- **v3.21 diff mode (RERUN_COUNT >= 2)**: Before writing each section, compare against the previous edition's items (saved in `$CACHE_DIR/td-prev-edition-items-$TODAY.json`). For fixed-layer (GitHub/Community/Papers/Products): only show items that are NEW or whose ranking changed significantly (≥2 positions for GitHub, different title/URL for others). For sections with zero new items: output `⚠️ 与上版相同，无新增` instead of repeating. This gives readers incremental value — they see what changed, not what they already read. The AI agent reads the previous edition's item file and diffs inline — no shell script needed.

### Step 2.5 — 保存本版条目（供下一版 diff）

After writing the digest, save the item list so the next rerun can diff against it:

```bash
python3 -c "
import json
today = '$(date +%Y-%m-%d)'
items = {
    'github': ['affaan-m/ECC', 'NousResearch/hermes-agent', 'vercel/eve', 'Forsy-AI/agent-apprenticeship', 'overflowy/make-look-scanned'],
    'news_urls': open('$CACHE_DIR/ai-daily-used-urls-$TODAY.txt').read().strip().split('\n') if __import__('os').path.exists('$CACHE_DIR/ai-daily-used-urls-{}.txt'.format(today)) else [],
}
# Fill in actual items from the digest just generated — the AI agent updates this
json.dump(items, open('$CACHE_DIR/td-prev-edition-items-{}.json'.format(today), 'w'), ensure_ascii=False)
print('saved edition items for next diff')
"
```

> ⚠️ The AI agent MUST update the above JSON with the actual list of items shown in this edition (GitHub repos, community titles, paper titles, product names). The next rerun reads this file to know what to skip.

### Step 3 — 存档 + GitHub Pages 站点 (v5.0 Enhanced)

```bash
# Main digest (latest)
cp $CACHE_DIR/daily-digest-content.md "$PROJECT_CWD/daily-digest.md"
# Archive with date
mkdir -p "$PROJECT_CWD/archive/follow-news"
cp $CACHE_DIR/daily-digest-content.md "$PROJECT_CWD/archive/follow-news/daily-$TODAY.md"

# Clean up generating lock
rm -f "$PROJECT_CWD/.generating"

# Build enhanced v5.0 HTML pages (search, bookmarks, category filters, read tracking)
python3 "$PROJECT_CWD/scripts/build-enhanced-site.py"
# Copy to WSL2 side for execution from either environment
cp "$PROJECT_CWD/scripts/build-enhanced-site.py" ~/.openclaw/scripts/build-enhanced-site.py

# Push to GitHub Pages (SSH over 443 — WSL2 GnuTLS breaks HTTPS)
cd "$PROJECT_CWD/site"
git add .
git commit -m "daily: $TODAY" --allow-empty 2>/dev/null || true
git pull origin main --no-rebase 2>&1 || true
git push origin main 2>&1 || echo "WARN: Pages push failed (non-blocking)"
cd -
```

> **v5.0 Enhanced Pages** (2026-06-16): `build-enhanced-site.py` replaces the old `build-pages-site.py` and LLM-generated HTML. Features: 🔍 full-text search, ⭐ bookmarks (localStorage), ✓ read-progress tracking, 🏷 category filter chips, 📱 mobile horizontal-scroll archive bar. All pure client-side — no backend needed.

### Step 4 — 投递 Telegram（主通道）⚠️ 已验证可用

Telegram 主通道。微信仅保留被动响应，不再主动推送。

**方式**：`mcp__openclaw__messages_send` MCP 直接投递。**2026-06-22 验证：4/4 成功（msg #221-226）**。

**Session key**：`agent:main:telegram:direct:7683765778`

**分条规则**：每条 ≤3500 字符，分 4 条：(1/4) 标题+新闻1-4 → (2/4) 新闻5-8 → (3/4) 新闻9-13 → (4/4) GitHub+社区+论文+产品+footer。

**每次 firing 直接调用 4 次 `mcp__openclaw__messages_send`，无需 shell 脚本。**

### Step 5 — 标记完成 + URL 持久化

```bash
touch "$PROJECT_CWD/.delivered-$TODAY"

# Persist today's URLs to cross-day state
python3 -c "
import json
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
# read new URLs from this run's articles
try:
    with open('$CACHE_DIR/td-articles-enriched.json') as f:
        articles = json.load(f)
    with open('$USED_URLS') as f:
        state = json.load(f)
    for a in articles:
        link = a.get('link','')
        if link:
            state['urls'][link] = today
    state['last_prune'] = today
    with open('$USED_URLS','w') as f:
        json.dump(state, f, ensure_ascii=False)
    print(f'urls-persisted: {len(state[\"urls\"])} total tracked')
except Exception as e:
    print(f'urls-persist-skipped: {e}')
"
```

⚠️ This step is MANDATORY. Missing it causes the backup trigger to re-run unnecessarily AND cross-day dedup to fail.

### Step 6 — 周报汇总（仅周日）

```bash
DOW=$(date +%u)  # 1=Mon ... 7=Sun
if [ "$DOW" -eq 7 ]; then
    echo "STATUS: sunday — generating weekly summary"
    WEEK_START=$(date -d "6 days ago" +%Y-%m-%d)
    WEEK_END=$TODAY
    
    # Collect all articles from this week's archive files
    python3 -c "
import json, glob, os
week_articles = []
archive_dir = '$PROJECT_CWD/archive/follow-news'
for i in range(7):
    d = __import__('datetime').date.today() - __import__('datetime').timedelta(days=6-i)
    f = f'{archive_dir}/daily-{d.strftime(\"%Y-%m-%d\")}.md'
    if os.path.exists(f):
        with open(f) as fh:
            content = fh.read()
        week_articles.append({'date': d.strftime('%Y-%m-%d'), 'content': content})
with open('$CACHE_DIR/td-weekly-articles.json', 'w') as f:
    json.dump(week_articles, f, ensure_ascii=False, indent=2)
print(f'week-articles: {len(week_articles)} days collected')
"
else
    echo "STATUS: not_sunday — skipping weekly"
fi
```

**If Sunday**: After daily digest delivery, the AI agent generates a weekly summary:
- **Title**: `# 📅 AI 科技周报 — $WEEK_START ~ $WEEK_END`
- **Content**: Top 10 stories of the week (from daily archives), notable trends, key GitHub projects
- **Delivery**: Same Telegram channel, labeled `[周报]`
- **Archive**: `$PROJECT_CWD/archive/follow-news/weekly-$WEEK_END.md`
- **No extra LLM calls** — the AI agent synthesizes from existing daily digests

---

## Dynamic Pacing

Since this is a daily task, the trigger mechanism is CronCreate (not ScheduleWakeup, which maxes at 3600s).

After completing all 5 steps:
1. **If successful**: the next firing will be triggered by tomorrow's CronCreate at 7:03 AM. No ScheduleWakeup needed.
2. **If pipeline failed** (exit 3): schedule a retry via `ScheduleWakeup(1200s)` (~20 min) to give time for transient issues to resolve. Max 3 retries, then report failure via the contract's current state.
3. **If delivery failed** (step 4 Telegram agent errors): retry once after 60s. If still failing, write to workspace for manual recovery.

---

## Current State (auto-maintained — rewrite each firing)

**Last completed iteration**: iter-14 (2026-06-22, v3.21 random_pool #2 — NEWS-ONLY mode)

**Last delivered date**: 2026-06-22 (manual ×4 verified: v1 pipeline + v2 TechCrunch + v3 random_pool + v5 random_pool NEWS-ONLY, 13/13 Telegram OK — msg #225-237)

**v3.21 validated**: 同天内 diff 模式 + RERUN_COUNT≥3 → NEWS-ONLY 生效。第 5 版仅含 12 条实时新闻（TechCrunch AI + Decoder + Bing News），跳过固定层。

**URL 持久化**: 22 total tracked in `.used-urls.json`，same-day dedup 12 URLs

**Multi-source rotation**: ✅ all 4 levels verified + random_pool 二次验证 — 5 manual reruns, 4 different source combos, zero duplicate headlines

**Active monitors**: none

**Outstanding issues**:

- [x] ~~messages_send MCP broken~~ — Telegram 13/13 全部成功 (2026-06-22)
- [x] ~~一天多次跑数据重复~~ — v3.19 多源轮换 + v3.20 URL 持久化 — 5 版 0 重复
- [x] ~~agents-radar 32次 LLM 调用 ¥1.4/次~~ — 放弃，经验已应用到 follow-news
- [ ] CronCreate 7-day auto-expire — check via `/autoloop:muster`

---

## Implementation Queue

### Tier 1 (daily operations)

- [x] Pipeline data collection (follow-news-pipeline.sh + fetch-github-trending.sh)
- [x] Digest generation with 💡 interpretation
- [x] Dual archival (daily-digest.md + archive/)
- [x] ~~WeChat delivery via agent reply path~~ → Telegram 直接投递 (2026-06-13)
- [x] Delivered marker (.delivered-YYYY-MM-DD)
- [x] Telegram 4-chunk delivery with (1/4)-(4/4) labels
- [x] GitHub Pages 存档站 (https://thewher.github.io/daily/)
- [x] 去重 (dedup-articles.py — URL + 标题相似度 + 同域关键词)
- [x] 💬 社区讨论板块 (fetch-community.sh — HN + V2EX + LinuxDo)
- [x] 📄 AI 论文板块 (fetch-papers.sh — HuggingFace daily papers)
- [x] 🆕 产品工具板块 (fetch-products.sh — Product Hunt + GitHub new repos)
- [x] AI 评分 (score-articles.py — 4维度 0-10 评分 + MUST_INCLUDE/GOOD/MAYBE/SKIP)
- [x] 背景增强 (enrich-articles.py — 高评分文章实体提取 + web 搜索上下文)
- [x] MCP Server (follow-news-mcp.py — 8 tools: search/get trending/papers/community/products/digest)
- [x] **v5.0 增强站点** (build-enhanced-site.py — 搜索+书签+已读+分类筛选+移动端, 替代 LLM HTML 生成) (2026-06-16)

### Tier 2 (improvements)
- [x] **多源轮换** (v3.19, 2026-06-22): 手动重跑自动切换数据源（default→TechCrunch→Techmeme→random），去重 URL 追踪
- [x] **URL 持久化去重** (v3.20, 2026-06-22): `.used-urls.json` 存 Git，跨天 7 天去重，每步自动过滤
- [x] **同天内去重** (v3.21, 2026-06-22): `/tmp/ai-daily-used-urls-$TODAY.txt` 追踪当天所有 run 的 URL，每版过滤已发。RERUN_COUNT ≥3 → NEWS-ONLY（跳过 GitHub/社区/论文/产品固定层）。防止第 4 版重复前面内容。
- [x] **周报汇总** (v3.20, 2026-06-22): 每周日自动从 7 天存档生成 Top 10 周报，零额外 LLM 成本
- [ ] Auto-detect and skip duplicate/similar stories across consecutive days (已由 URL 持久化覆盖)

---

## Non-Obvious Learnings

- **messages_send MCP 微信损坏但 Telegram 可用 (v2026.6.20)**: `messages_send` 对微信超时但对 Telegram 秒到（messageId 206-209，4/4 成功）。`openclaw agent --deliver` 走网关排队（96s+），且多余一次模型调用。日报投递直接用 `messages_send` MCP → Telegram session。
  - **How to apply**: Step 4 直接用 `mcp__openclaw__messages_send` 发到 `agent:main:telegram:direct:7683765778`，分 4 条。不用 `openclaw agent --deliver`。
- **微信文本上限 ~2048 字符**: 超长消息被微信静默丢弃。每条消息控制在 1800 字符以内，超长时分条。
  - **How to apply**: 日报超过 1800 字符时必须分条，每条约 2-3 条新闻。
- **CronCreate prompt 内联存储**: 编辑外部 prompt 文件不会更新 cron。修改触发逻辑需 CronDelete + CronCreate 重建。
  - **How to apply**: 迁移到 autoloop 后，CronCreate 只存稳定的 pointer trigger，SOP 在合约中独立管理。
- **.delivered 标记不可跳过**: 2026-06-10 漏标导致备份触发重复运行。
  - **How to apply**: Step 5 必须在 Step 4 完成后立即执行。
- **管道 exit code 含义**: 0=数据就绪, 1=生成中, 2=已投递, 3=失败。不要用 set -e（exit 1/2 是正常跳过）。
  - **How to apply**: Step 1 中分别处理每个 exit code，不要一律报错。
- **CronCreate 7 天自动过期 (v2026.6.11)**: 新建的 CronCreate 任务在 7 天后自动过期删除。需要定期检查并续期，或由 SessionStart hook 自动重建。
  - **How to apply**: 每周执行 `/autoloop:muster` 检查 cron 状态。若 expired，用 CronCreate 重建相同 trigger。autoloop heal-self.sh 每小时自动扫描并修复孤儿 registry entries。
- **md_to_html 内联标签检测必须在顶层 (v2026.6.16)**: `💡`/`🔗`/`⭐` 等行是一级独立行，不是 bullet 子元素。把检测逻辑嵌套在 `if startsWith('• ')` 内会导致它们全部掉入兜底 `<p>` 段落，链接永远不可点击。
  - **How to apply**: `build-pages-site.py` 中内联标签（💡🔗⭐📄💬🆕）的检测必须是顶层 `elif`，且在 `• ` 检测之前。
- **v5.0 增强站点生成器 (v2026.6.16)**: LLM 不再生成 HTML — 只输出 MD → `build-enhanced-site.py` 统一生成增强版 HTML。包含搜索、书签（localStorage）、已读跟踪、分类筛选、移动端优化。所有页面纯客户端，无需后端。
  - **How to apply**: Step 2 只输出 markdown。Step 3 调用 `build-enhanced-site.py`（不是 `build-pages-site.py`）。脚本自动处理 3 种历史 MD 格式（v1 `【section】` + v2 `**title**` 无 bullet + v3 `## section` + `• **title**`）。
- **MD 格式三版本兼容**: 06-08/06-09 用 `【section】` + `• title`，06-11 用 `## GitHub` + `**title**` 无 bullet，06-12+ 用 `## section` + `• **title**`。解析器需从标题提取日期（支持 `2026年6月8日` + `2026-06-08` 两种格式），自动归类 section 到 category。
  - **How to apply**: `build-enhanced-site.py` 的 `parse_digest_md()` 已处理全部三种格式。新增格式时测试所有历史日期。

---

## Revision Log

- 2026-06-22 ~15:45 UTC — **iter-14 (v3.21 NEWS-ONLY)**: RERUN_COUNT=5, rotation=random_pool #2。TechCrunch AI + The Decoder + Bing News 实时抓取。精选 12 条新闻（Samsung ChatGPT 全员部署 · Sakana Fugu 多 LLM 编排 · Altman scaling 路线辩护 · Codex Record & Replay · John Jumper 跳槽 Anthropic · Trump 禁令受益分析 · iOS 27 AI 功能 · AWS Agent 安全 · Damodaran AI 崩盘警告 · Amazon 自研芯片外销 · AI 数据中心绿色通道 · Ambani AI 基建）。NEWS-ONLY 模式——跳过固定层。Telegram 4/4 成功（msg #234-237）。URL 持久化 22 total。
- 2026-06-22 ~08:30 UTC — **v3.21 同天内 diff 模式**: iter-13 用户反馈第 4 版重复了前面的 GitHub trending 和新闻。修复：Step 0 新增 `USED_URLS_TMP` 同天 URL 追踪（追加模式）。Step 2 新增 diff mode（RERUN_COUNT ≥2 时对比上一版条目，仅展示新上榜/排名变化项，无新增则标注「⚠️ 与上版相同」）。Step 2.5 新增保存本版条目 JSON 供下一版 diff。策略从「跳过固定层」改为「增量 diff」——每版都有增量价值。
- 2026-06-22 07:00 UTC — **v3.20 周报+URL 持久化**: Step 5 新增 URL 持久化（`.used-urls.json`，跨天 7 天去重，自动剪枝）。新增 Step 6 周报汇总（周日自动从 7 天存档合成 Top 10，零额外 LLM 成本）。评估 agents-radar 后放弃（32 次 LLM 调用 ¥1.4/次），取其精华（周报/URL 持久化/配置驱动）融入 follow-news。
- 2026-06-22 06:00 UTC — **v3.19 多源轮换**: 新增手动重跑支持——Step 0 引入 `RUN_MODE`（auto/manual）+ `RERUN_COUNT` 计数器 + 4 级数据源轮换（default→techcrunch_decoder→techmeme_google→random_pool）。Step 1 分支：auto/首次走 pipeline，手动重跑走 hyperbrowser 实时抓取。URL 去重追踪（`/tmp/ai-daily-used-urls-$TODAY.txt`）。固定层复用（<12h 不重新抓取）。手动重跑标题标注「第N版」。iter-11 手动触发 2 次验证轮换生效（v1 default + v2 techcrunch_decoder）。Telegram 6/6 条全部成功。
- 2026-06-21 04:45 UTC — **iter-10**: Pipeline 收集 128 篇 → 去重 121 篇 → 评分 74 篇过线（18 MUST_INCLUDE + 39 GOOD）→ 精选 13 条新闻 + 5 GitHub + 3 社区 + 3 论文 + 2 产品 → 11.1KB 日报。头条：Anthropic Project Fetch Phase Two · LLM 瓶颈声称突破 · OpenAI Codex「观察学习」能力 · AI 系统提示词第四轮泄露 · AI 数据样本效率黑洞（Dwarkesh Patel）· NVIDIA 机器人自我研究 · Signal CEO 警告 AI 聊天机器人风险 · NYU 教授 AI 泡沫警告 · Nobel 奖得主转投 Anthropic · Atlantic 发布 AI 训练音乐数据库。GitHub：affaan-m/ECC 日增 1.4K star 继续屠榜，NousResearch/hermes-agent +596/d，vercel/eve +472/d。Telegram 4 分条全部成功投递（messageId 217-220）。延迟发送（12:00 BJT）。Cron IDs 已刷新: 0bb3a9db / c0010082。
- 2026-06-19 04:25 UTC — **iter-8**: Pipeline 收集 164 篇 → 去重 151 篇 → 评分 100 篇过线（23 MUST_INCLUDE）→ 精选 13 条新闻 + 4 GitHub + 3 社区 + 3 论文 + 2 产品。头条：SpaceX 600 亿美元收购 Cursor（AI 工具最大并购）。SK 电信疑与中国关联触发 Anthropic 危机。Trump 向 Anthropic 提出"不可能的要求"。白宫"实时编造"AI 规则。三大 AI 公司系统提示词再次泄露。Microsoft 发现新型加密币窃取后门。以色列上市公司被指运营僵尸网络。Adobe Creative Cloud 全系加入 AI Agent。OpenAI 辅助诊断儿童罕见遗传病。Google AMIE 可管理慢性病。GLM-5.2 发布。印度封禁 Telegram。GitHub：affaan-m/ECC 日增 1.4K star 继续屠榜，vercel/eve 3 天 1.4K star，junction 首日 510 star。Telegram 4 分条全部成功投递。延迟发送（12:00 BJT）。: Pipeline 收集 160 篇 → 去重 150 篇 → 评分 112 篇过线（29 MUST_INCLUDE）→ 精选 15 条新闻 + 5 GitHub + 3 社区 + 3 论文 + 2 产品 → 11.9KB 日报。头条：AI 系统提示词第三轮大规模泄露（Anthropic Fable 5/Opus 4.8 + OpenAI GPT-5.5/Codex + Google Gemini 3.5）。Trump 向 Anthropic 提出"不可能的要求"，SK 电信卷入 Mythos 出口管制。Gary Marcus 分析 OpenAI 领先优势快速缩小。GLM-5.2 被 Simon Willison 评为最强纯文本开源 LLM。US 暂缓 DeepSeek 黑名单但 100+ 中企列入风险名单。Chrome WebMCP 标准提案——浏览器原生 Agent 协议。NVIDIA XR AI 将 Agent 带入 AR 眼镜。北京建 10 万 P 算力 AI 工厂。Midjourney Medical 进军医疗影像。GitHub：ponytail 6 天 32K star 继续屠榜，Vercel eve 首日 794 star，Junction VS Code AI 侧边栏首日 501 star。Telegram 4 分条全部成功投递。
- 2026-06-17 03:37 UTC — **iter-6**: Pipeline 收集 140 篇 → 去重 137 篇 → 评分 99 篇过线（30 MUST_INCLUDE）→ 精选 13 条新闻 + 5 GitHub + 3 社区 + 3 论文 + 1 产品 → 5.7KB 日报。头条：SpaceX 600 亿美元收购 Cursor（AI 工具领域最大并购）+ SpaceX 估值 2.6 万亿美元超越 Amazon。三大 AI 公司系统提示词再次大规模泄露（Claude Fable 5/Opus 4.8/GPT 5.5/Gemini 3.5）。DeepSeek 完成 500 亿元融资。Microsoft Copilot Cowork 转向按量计费并可能接入 DeepSeek。智谱 GLM-5.2 开源编程能力超越 Fable 5。Meta 工程组织内乱曝光。GitHub：ponytail 5 天狂揽 25.9K star 继续屠榜。Telegram 4 分条全部成功投递。
- 2026-06-15 02:10 UTC — **iter-4**: Pipeline 收集 125 篇 → 去重 120 篇 → 评分 74 篇过线（17 MUST_INCLUDE）→ 精选 13 条新闻 + 5 GitHub + 3 社区 + 3 论文 + 1 产品 → 5.8KB 日报。重磅：US 政府强制 Anthropic 关闭 Fable 5/Mythos 5（AI 史上首次政府下线前沿模型），Amazon 等六公司被指触发禁令，中国可能已获取 Mythos 权重。WWDC 2026 Apple Siri 引入 Gemini 1.2T。鸿蒙 HDC 宣告系统级 Agent 演进。三大 AI 公司系统提示词大规模泄露。OpenAI 推出合作伙伴网络。KPMG 被曝编造 AI 案例研究。Telegram 2 分条成功投递。发现 WSL2 GnuTLS 导致 GitHub Pages push 失败（非阻塞）。
- 2026-06-13 08:00 UTC — **v3.18 板块扩展**: 新增三个板块（💬社区讨论 + 📄AI论文 + 🆕产品工具），去重引擎（URL+标题+域三层策略），GitHub Pages 存档站上线。5→8 数据源，2→6 个抓取脚本。
- 2026-06-13 03:30 UTC — **架构变更**: Telegram 成为主投递通道（4 分条直接发送）。微信降级为被动日常 bot，不再主动推送。合约 Step 4 重写为 Telegram Python 内联脚本。
- 2026-06-13 03:21 UTC — **iter-3**: Pipeline 收集 138 篇 → 精选 13 条新闻 + 5 个 GitHub 热门 → 9.1KB 日报。重磅新闻：US Government 强制 Anthropic 关闭 Fable 5/Mythos 5（AI 史上首次政府下线前沿模型），Fable 5 性价比争议（+5.7%性能双倍价格），SpaceX IPO 首日暴涨，Meta AI 部门内乱曝光，PeopleSoft 0-day 大规模数据泄露，华为发布鸿蒙 7，CRISPR 新技术精准摧毁癌细胞。投递到 workspace 等待用户微信触发。
- 2026-06-12 00:10 UTC — **iter-2**: Pipeline 收集 143 篇 → 精选 12 条新闻 + 5 个 GitHub 热门 → 6KB 日报。重点：SpaceX IPO、OpenAI 秘密递表、Claude 系统提示词泄露、Oracle 100+企业被黑、Apple Siri AI 欧盟延迟。投递到 workspace 等待用户微信触发。
- 2026-06-11 10:00 UTC — **iter-1**: 首次 autoloop 测试运行。Pipeline 收集 185 篇 → 精选 10 条新闻 + 5 个 GitHub 热门 → 79 行日报。发现并修复 Step 0 锁冲突（合约 vs 管道双重创建 .generating）。文件投递到 workspace 等用户微信触发。
- 2026-06-11 09:00 UTC — Initial contract scaffolded. Migrated from 3 CronCreate tasks (585b76ee, 3c98e860, 78fa8665) to single autoloop contract + thin CronCreate pointer trigger. Architecture: autoloop v21.89.1, v2 contract layout (.autoloop/follow-news--dc4c5f/).
