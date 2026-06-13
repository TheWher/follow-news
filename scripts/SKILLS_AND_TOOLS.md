# Skills & Tools 行为边界（借鉴 Fable 5 Claude Code 架构）

`<skill_architecture>`

OpenClaw Agent 的能力来自三层：

| 层 | 来源 | 示例 |
|----|------|------|
| **内置工具** | OpenClaw 网关 | `memory_search`, `web_search`, `exec`, `messages_send` |
| **ClawHub 技能** | clawhub 注册表 | `weather`, `stock-price-query`, `parallel` |
| **本地 Agent** | `~/.claude/agents/` | `nature-polishing`, `nature-figure` |

技能 = 专用知识 + 工具的集合。Agent 在匹配到触发条件时自动加载对应技能。

`</skill_architecture>`

---

`<when_to_use_skills>`

| 用户需求 | 路由到 |
|----------|--------|
| 天气查询 | `weather` |
| 网页深度搜索 | `parallel` |
| 浏览器自动化 | `browser-automation` |
| 股票查询 | `stock-price-query` |
| 学术写作 | `nature-polishing` / `nature-writing` |
| 搜索安装技能 | `find-skills` → `skillhub` 优先 |
| 技能创建 | `skill-creator` |
| 代码编写/编辑 | Claude Code 原生（不经过 OpenClaw） |
| 文件操作 | Claude Code 原生 |

**判断原则**：用户请求如果能被 OpenClaw 技能更好地完成 → 走网关调度。Claude Code 原生能力（代码编辑、文件操作、git）→ 不走网关。

`</when_to_use_skills>`

---

`<skill_behavior_patterns>`

`<pattern>`
**先检查是否已安装**：
- 用户提到某种需求 → 先 `clawhub list` / `skillhub list` 检查是否已有对应技能
- 不要直接提供通用方案，如果已有专用技能
`</pattern>`

`<pattern>`
**Skill 模板需要本地化覆盖**：
- Skill 安装后默认是通用模板
- 需要根据项目具体环境（路径/API/时区）覆盖默认值
- 不要直接用模板——先读模板，再写覆盖
`</pattern>`

`<pattern>`
**安全审查**：
- 新安装的 skill → review 其代码 → 确认无恶意
- 不要对未知来源的 skill 盲目信任
`</pattern>`

`</skill_behavior_patterns>`

---

`<computer_use_boundaries>`

借鉴 Fable 5 的 computer_use 设计，Agent 操作计算机的边界：

`<can_do>`
- ✅ 读写项目文件
- ✅ 运行非破坏性命令（ls, grep, git status, npm test）
- ✅ 执行数据抓取脚本
- ✅ 发送 Telegram 消息（通过 Bot API）
- ✅ 读写 `/tmp/` 临时文件
`</can_do>`

`<requires_confirmation>`
- ⚠️ 运行可能修改系统状态的命令（systemctl, apt install）
- ⚠️ 删除文件（rm, git reset --hard）
- ⚠️ 推送代码到 GitHub
- ⚠️ 修改网关配置（openclaw config set）
`</requires_confirmation>`

`<cannot_do>`
- ❌ 重启/停止网关（从 agent session 内操作会自杀）
- ❌ 运行重型管道（>30s, >500MB 内存）——改用独立脚本
- ❌ 访问 Windows 侧文件系统（除非通过 `/mnt/c/` 明确路径）
`</cannot_do>`

`</computer_use_boundaries>`

---

`<tool_usage_essentials>`

`<essential_practice>`
**代理回退**：
- `gh` CLI TLS 不通 → 用 `curl` + GitHub API + proxy
- `git push` HTTPS 不通 → 走 HTTP proxy + sslVerify=false
- SSH 22 端口不通 → 用 HTTPS + token 认证
`</essential_practice>`

`<essential_practice>`
**执行模式选择**：
- 轻量命令（<10s）→ Bash 直接执行
- 中等任务（10-60s）→ Bash background + TaskOutput 轮询
- 重型采集（>60s）→ 预写脚本 + 独立进程
`</essential_practice>`

`<essential_practice>`
**API 调用规范**：
- 外部 API → 必须走 `http://127.0.0.1:7890` 代理
- DeepSeek → `https://api.deepseek.com/anthropic` + `ANTHROPIC_AUTH_TOKEN`
- Telegram → `https://api.telegram.org/bot<TOKEN>/` + proxy
- GitHub → `https://api.github.com/` + token + proxy
`</essential_practice>`

`</tool_usage_essentials>`
