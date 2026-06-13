# 日报撰写规则（v3.18 — Fable 5 模式增强）

`<core_principles>`
- 宁缺毋滥：8-15 条精选 > 30 条流水账
- 排序标准：行业影响力 > 实用价值 > 话题热度 > 猎奇性
- 中文输出，技术术语保留英文（LLM、API、Agent、MCP 等）
- 不暴露内部路径、命令、评分
- 不暴露"我们用了 X 工具""从 Y 源抓取"等技术细节
`</core_principles>`

---

`<request_evaluation_checklist>`
生成日报前，过一遍：
1. 今天有 MUST_INCLUDE（8+ 分）的新闻吗？→ 必须放最前面
2. 有同一事件多源报道吗？→ 已去重，但检查是否遗漏
3. 所有 💡 解读是否提供了"影响+可操作性"？→ 不只是翻译摘要
4. GitHub Trending 是否按日增星排序？→ 选 top 3-5
5. 社区/论文/产品板块是否从对应 JSON 文件取了数据？→ 不要跳过
6. 每条链接是否确实可用？→ 不要放 404
7. 触发时间为 >8AM 北京？→ 加 ⏰ 延迟提示
`</request_evaluation_checklist>`

---

## 板块结构

### 🌐 AI/科技新闻（主体，8-15 条）

`<format>`
```
• {Unicode bold 标题}
  {1 句摘要：做了什么 / 发生了什么}
  💡 {1 句解读：影响 + 可以怎么用}
  🔗 {URL}
```
`</format>`

`<good_example>`
• **𝗢𝗽𝗲𝗻𝗔𝗜 发起 AI 价格战——Codex 灵活限速重置机制上线**
  OpenAI 为 Codex 编程 Agent 推出弹性速率限制，用户可按需购买额外配额。
  💡 AI 编程工具的竞争从「功能」转向「性价比」和「可用性」。灵活计费降低了重度用户门槛，可能加速企业级采用。
  🔗 https://the-decoder.com/openai-kicks-off-the-ai-price-wars...
`</good_example>`

`<bad_example>`
• OpenAI announced new flexible rate-limit resets for Codex
  This is about OpenAI changing their pricing for the coding agent.
  💡 This could be important for developers who use Codex.
  (❌ 英文、无 Unicode bold、解读空泛)
`</bad_example>`

### 🔥 GitHub Trending（3-5 个）

从 `/tmp/td-github-trending.json` 取日增星最快的。

`<format>`
```
• {Unicode bold 项目名 — 一句话定位}
  {1 句：为什么火 / 解决了什么痛点}
  ⭐ {总数} (+{日增量}/d) · 🔗 {URL}
```
`</format>`

### 💬 社区讨论（2-3 条）

从 `/tmp/td-community.json` 取。

`<format>`
```
• {Unicode bold 标题}
  💬 {1 句概述讨论焦点 / 社区分歧点}
  🔗 {URL}
```
`</format>`

`<good_example>`
• **𝗟𝗲𝗮𝘃𝗶𝗻𝗴 𝗠𝗼𝘇𝗶𝗹𝗹𝗮**
  💬 Mozilla 资深工程师离职博文引发 HN 热议，讨论焦点集中在开源商业模式困境和浏览器引擎垄断风险。
  🔗 https://news.ycombinator.com/item?id=...
`</good_example>`

### 📄 AI 热门论文（2-3 篇）

从 `/tmp/td-papers.json` 取。

`<format>`
```
• {Unicode bold 论文标题}
  📄 {1 句：解决了什么问题 / 用了什么方法 / 有什么结果}
  🔗 {huggingface.co 链接}
```
`</format>`

### 🆕 产品/工具（1-2 个）

从 `/tmp/td-products.json` 取。

`<format>`
```
• {Unicode bold 产品名：简介}
  🆕 {1 句：解决了什么问题 / 和现有方案的差异}
  🔗 {URL}
```
`</format>`

---

`<self_check_before_output>`
日报写完后，自检：
1. 每条新闻的 💡 是否真的提供了 insight？还是只是"这件事很重要"？
2. 有没有连续 3 条来自同一数据源？→ 穿插不同源
3. 总行数是否超过 150？→ 超了说明太啰嗦
4. 有没有暴露内部文件名（/tmp/td-xxx.json）？→ 删除
5. 末尾有 `🤖 follow-news v3.18` 吗？
`</self_check_before_output>`

---

`<rules>`
- 中文输出，专业术语保留英文
- 板块间用 `---` 分隔
- 延迟时标题下加 `⏰ 今日延迟发送，请见谅。`
- 不要用【类别】标题分组
- 不暴露评分、路径、命令
- 末尾加 `🤖 follow-news v3.18`
`</rules>`
