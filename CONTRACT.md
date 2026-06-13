---
name: follow-news
version: 1
schema_version: 2
iteration: 3
last_updated: 2026-06-13T08:00:00Z
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

**This file IS the /loop prompt.** Each firing reads it, generates the daily digest, delivers it, and self-revises.

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

### Step 0 — 防重复 + 延迟检查

```bash
PROJECT_CWD="/mnt/c/Users/A2260/.claude/follow-news"
TODAY=$(date +%Y-%m-%d)

# Check if already delivered today
if [ -f "$PROJECT_CWD/.delivered-$TODAY" ]; then
    echo "STATUS: already_delivered — exiting"
    exit 0
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

# Do NOT create .generating lock here — pipeline manages its own
# Check if delayed (>8:00 AM Beijing = >00:00 UTC, i.e. >8h into the day)
HOUR_BJ=$(TZ=Asia/Shanghai date +%H)
if [ "$HOUR_BJ" -ge 8 ]; then
    DELAYED=true
else
    DELAYED=false
fi
```

If `already_delivered` → exit cleanly. If `generating_in_progress` with fresh lock → exit.
**Do NOT create .generating lock here** — the pipeline script manages its own lock internally. Creating one here would cause the pipeline to exit with code 1 (detects our lock as "another process generating").
If delayed, note for the digest title.

### Step 1 — 数据采集

```bash
# 1a. Primary pipeline: news collection (runs in background)
bash ~/.openclaw/scripts/follow-news-pipeline.sh &
PIPELINE_PID=$!

# 1b. GitHub Trending: top repositories by daily star growth
bash ~/.openclaw/scripts/fetch-github-trending.sh

# 1c. NEW: Community discussions (HN + V2EX + LinuxDo)
bash ~/.openclaw/scripts/fetch-community.sh

# 1d. NEW: AI papers (HuggingFace daily papers)
bash ~/.openclaw/scripts/fetch-papers.sh

# 1e. NEW: Products/tools (Product Hunt + new GitHub AI repos)
bash ~/.openclaw/scripts/fetch-products.sh

# Wait for pipeline
wait $PIPELINE_PID
PIPELINE_EXIT=$?

# 1f. Deduplicate articles (cross-source merge)
python3 ~/.openclaw/scripts/dedup-articles.py /tmp/td-articles.json /tmp/td-articles-deduped.json

# 1g. AI Score & filter (0-10 rating, threshold=5.0)
python3 ~/.openclaw/scripts/score-articles.py /tmp/td-articles-deduped.json /tmp/td-articles-scored.json 5.0

# 1h. Enrich top articles with web context (score >= 7)
python3 ~/.openclaw/scripts/enrich-articles.py /tmp/td-articles-scored.json /tmp/td-articles-enriched.json
```

Exit codes from pipeline:
- `0` → data ready, continue
- `1` → generating in progress, exit
- `2` → already delivered, exit
- `3` → pipeline failure, report and exit

### Step 2 — 生成日报

Read these files:
- `/tmp/td-articles-enriched.json` (scored + enriched news)
- `/mnt/c/Users/A2260/.claude/follow-news/digest-rules.md`
- `/tmp/td-github-trending.json` (🔥 GitHub)
- `/tmp/td-community.json` (💬 社区)
- `/tmp/td-papers.json` (📄 论文)
- `/tmp/td-products.json` (🆕 产品)

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
- End with `🤖 autoloop follow-news v3.18`

### Step 3 — 存档 + GitHub Pages 站点

```bash
# Main digest (latest)
cp /tmp/daily-digest-content.md "$PROJECT_CWD/daily-digest.md"
# Archive with date
mkdir -p "$PROJECT_CWD/archive/follow-news"
cp /tmp/daily-digest-content.md "$PROJECT_CWD/archive/follow-news/daily-$TODAY.md"

# Clean up generating lock
rm -f "$PROJECT_CWD/.generating"

# Build & push GitHub Pages site
export GIT_SSL_NO_VERIFY=1
python3 ~/.openclaw/scripts/build-pages-site.py
cd "$PROJECT_CWD/site"
git add .
git commit -m "daily: $TODAY" --allow-empty 2>/dev/null || true
git push origin main 2>&1 || echo "WARN: Pages push failed (non-blocking)"
cd -
```

🌐 站点地址: `https://thewher.github.io/daily/`

### Step 4 — 投递 Telegram（主通道）

Telegram 比微信稳定（标准 API，无静默截断），作为主投递通道。微信仅保留被动响应（日常 bot），不再主动维护。

**Telegram 直接投递**（合约内完成，不等用户触发）：

```bash
# Split digest into ≤3800 char chunks, send via Telegram channel
python3 << 'PYEOF'
import json, subprocess

with open("$PROJECT_CWD/daily-digest.md", "r") as f:
    digest = f.read()

# Split on logical boundaries (~3800 chars Telegram safe limit)
lines = digest.split("\n")
bullet_lines = [i for i, l in enumerate(lines) if l.startswith("• ")]
github_header = [i for i, l in enumerate(lines) if l.startswith("## 🔥")]

# Build 4 messages: header+1-4 / 5-8 / 9-13 / GitHub Trending+footer
def build_msg(from_idx, to_idx, label, include_header=False):
    start = bullet_lines[from_idx]
    end = bullet_lines[to_idx+1] - 1 if to_idx+1 < len(bullet_lines) else len(lines)
    result = [label] + ([] if not include_header else lines[:start]) + lines[start:end]
    return "\n".join(result).strip()

messages = [
    build_msg(0, 3, "(1/4)", include_header=True),
    "\n".join(["(2/4)"] + [
        "\n".join(lines[max(bullet_lines[i]-1,0):(bullet_lines[i+1]-1 if i+1<len(bullet_lines) else (github_header[0] if github_header else len(lines)))])
        for i in range(4, 8)
    ]).strip(),
    "\n".join(["(3/4)"] + [
        "\n".join(lines[max(bullet_lines[i]-1,0):(bullet_lines[i+1]-1 if i+1<len(bullet_lines) else (github_header[0] if github_header else len(lines)))])
        for i in range(8, 13)
    ]).strip(),
    ("(4/4)\n" + "\n".join(lines[github_header[0]:]).strip()) if github_header else "(4/4)",
]

# Send each chunk
for i, msg in enumerate(messages):
    if len(msg) > 3900:
        print(f"WARNING: chunk {i+1} too long ({len(msg)} chars), skip", file=sys.stderr)
        continue
    print(f"Sending chunk {i+1}/4 ({len(msg)} chars)...")
    result = subprocess.run([
        "openclaw", "agent", "--agent", "main",
        "--channel", "telegram", "--deliver",
        "--reply-to", "7683765778",
        "--message", msg,
        "--timeout", "60"
    ], capture_output=True, text=True, timeout=65)
    if result.returncode != 0:
        print(f"FAILED chunk {i+1}: {result.stderr[:200]}", file=sys.stderr)
    else:
        print(f"OK chunk {i+1}")

print("Telegram delivery complete")
PYEOF
```

**微信被动模式**（不主动投递，仅响应用户消息）：
- 微信通道 `openclaw-weixin` 保持运行作为日常 bot
- 用户主动发消息时 agent 正常回复
- 不再主动推送日报到微信
- 不再写 `PENDING-TASK.md`

### Step 5 — 标记完成

```bash
touch "$PROJECT_CWD/.delivered-$TODAY"
```

⚠️ This step is MANDATORY. Missing it causes the backup trigger to re-run unnecessarily.

---

## Dynamic Pacing

Since this is a daily task, the trigger mechanism is CronCreate (not ScheduleWakeup, which maxes at 3600s).

After completing all 5 steps:
1. **If successful**: the next firing will be triggered by tomorrow's CronCreate at 7:03 AM. No ScheduleWakeup needed.
2. **If pipeline failed** (exit 3): schedule a retry via `ScheduleWakeup(1200s)` (~20 min) to give time for transient issues to resolve. Max 3 retries, then report failure via the contract's current state.
3. **If delivery failed** (step 4 Telegram agent errors): retry once after 60s. If still failing, write to workspace for manual recovery.

---

## Current State (auto-maintained — rewrite each firing)

**Last completed iteration**: iter-3 (2026-06-13 03:21 UTC)

**Last delivered date**: 2026-06-13

**Pipeline stats**: 138 articles collected (pipeline) + 20 GitHub trending repos → 13 news + 5 GitHub trending → 9,109 byte digest

**Active monitors**: none

**Outstanding issues**:

- [x] ~~Contract Step 0 lock conflict~~ — 合约不应在 Step 0 创建 .generating 锁（管道自己管理）。已修复。
- [x] ~~messages_send MCP broken~~ — 切换 Telegram 直接投递，不再依赖微信 agent 回复路径（2026-06-13）。
- [x] ~~WeChat 主动维护~~ — 微信降级为被动日常 bot，不再主动推送。Telegram 成为主投递通道（2026-06-13）。
- [x] ~~GitHub Pages 存档站~~ — Step 3 自动构建+推送，`https://thewher.github.io/daily/`（2026-06-13）。
- [ ] Pipeline uses Windows paths under /mnt/c — fragile if drive letter changes
- [ ] CronCreate 7-day auto-expire — triggers (87d493a8, 1a3c41c8) expire 2026-06-18, need renewal or SessionStart hook auto-recreate
- [ ] WSL2 无 launchd — waker.sh 不可用，完全依赖 CronCreate 触发（非 macOS 标准路径）
- [ ] 微信备份触发 (8:57 AM) — 既然 Telegram 已直接投递，备份 trigger 是否仍需保留？

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

### Tier 2 (improvements)
- [ ] Add resilience: if pipeline returns empty, use fallback sources (RSS direct)
- [ ] Add weekly summary mode (every Sunday, summarize the week's top stories)
- [ ] Auto-detect and skip duplicate/similar stories across consecutive days

---

## Non-Obvious Learnings

- **messages_send MCP 损坏 (v2026.5.22)**: WS 层返回 messageId 但 channel 插件不生成 outbound 日志，消息永不送达。唯一可行路径是用户发消息→agent 回复→outbound。不要尝试用 messages_send 或 broadcast。
  - **How to apply**: Step 4 投递始终走 agent 回复路径，不调用 messages_send MCP。
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

---

## Revision Log

- 2026-06-13 08:00 UTC — **v3.18 板块扩展**: 新增三个板块（💬社区讨论 + 📄AI论文 + 🆕产品工具），去重引擎（URL+标题+域三层策略），GitHub Pages 存档站上线。5→8 数据源，2→6 个抓取脚本。
- 2026-06-13 03:30 UTC — **架构变更**: Telegram 成为主投递通道（4 分条直接发送）。微信降级为被动日常 bot，不再主动推送。合约 Step 4 重写为 Telegram Python 内联脚本。
- 2026-06-13 03:21 UTC — **iter-3**: Pipeline 收集 138 篇 → 精选 13 条新闻 + 5 个 GitHub 热门 → 9.1KB 日报。重磅新闻：US Government 强制 Anthropic 关闭 Fable 5/Mythos 5（AI 史上首次政府下线前沿模型），Fable 5 性价比争议（+5.7%性能双倍价格），SpaceX IPO 首日暴涨，Meta AI 部门内乱曝光，PeopleSoft 0-day 大规模数据泄露，华为发布鸿蒙 7，CRISPR 新技术精准摧毁癌细胞。投递到 workspace 等待用户微信触发。
- 2026-06-12 00:10 UTC — **iter-2**: Pipeline 收集 143 篇 → 精选 12 条新闻 + 5 个 GitHub 热门 → 6KB 日报。重点：SpaceX IPO、OpenAI 秘密递表、Claude 系统提示词泄露、Oracle 100+企业被黑、Apple Siri AI 欧盟延迟。投递到 workspace 等待用户微信触发。
- 2026-06-11 10:00 UTC — **iter-1**: 首次 autoloop 测试运行。Pipeline 收集 185 篇 → 精选 10 条新闻 + 5 个 GitHub 热门 → 79 行日报。发现并修复 Step 0 锁冲突（合约 vs 管道双重创建 .generating）。文件投递到 workspace 等用户微信触发。
- 2026-06-11 09:00 UTC — Initial contract scaffolded. Migrated from 3 CronCreate tasks (585b76ee, 3c98e860, 78fa8665) to single autoloop contract + thin CronCreate pointer trigger. Architecture: autoloop v21.89.1, v2 contract layout (.autoloop/follow-news--dc4c5f/).
