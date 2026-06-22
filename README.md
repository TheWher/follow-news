<p align="center">
  <img src="https://img.shields.io/github/stars/TheWher/follow-news?style=for-the-badge&color=3b82f6" alt="Stars">
  <img src="https://img.shields.io/github/license/TheWher/follow-news?style=for-the-badge&color=10b981" alt="License">
  <img src="https://img.shields.io/badge/days-14%20archived-8b5cf6?style=for-the-badge" alt="Archive">
  <img src="https://img.shields.io/badge/version-v3.22-f59e0b?style=for-the-badge" alt="Version">
</p>

<h1 align="center">📰 每日 AI 科技日报</h1>

<p align="center">
  <strong>全自动 AI 新闻采集 → 中文日报撰写 → Telegram 投递 → 站点存档</strong><br>
  每天 7:03 AM 自动运行，零人工干预。5 源轮换 + 4 维评分 + 同天内去重。<br>
  <a href="https://thewher.github.io/daily/"><strong>🌐 在线站点 »</strong></a>
</p>

---

## ⚡ 产出样例

```
📰 每日 AI 科技日报 — 2026年6月22日

• Samsung 全员部署 ChatGPT Enterprise + Codex — OpenAI 史上最大企业交易
  💡 韩企 AI 军备竞赛全面加速
  🔗 https://the-decoder.com/samsung-rolls-out-chatgpt...

• Sakana AI 的 Fugu 多 LLM 编排达到 Fable/Mythos 基准
  💡 scaling 护城河面临「组合式竞争」侵蚀

• OpenAI Codex「Record & Replay」— 录一次，AI 替你做一辈子
  💡 白领自动化从事务级下降到操作级

🔥 GitHub Trending: affaan-m/ECC (+1,417/d) · vercel/eve (+368/d)
💬 社区: HN · V2EX · LinuxDo
📄 论文: HuggingFace Daily Papers
🆕 产品: Product Hunt AI

🤖 autoloop follow-news v3.22
```

---

## 🏗️ 架构

```mermaid
graph TD
    A[CronCreate<br/>7:03 + 8:57 AM] -->|pointer trigger| B[/loop]
    B --> C[CONTRACT.md<br/>autoloop v2 合约]
    C --> D[Step 1: 数据采集]
    D --> E1[pipeline.sh<br/>多源采集]
    D --> E2[hyperbrowser<br/>实时抓取]
    E1 --> F[去重 + 评分 + 增强]
    E2 --> F
    F --> G[Step 2: 生成日报<br/>8-15 条 + 💡 解读]
    G --> H[Step 3: 存档<br/>build-enhanced-site.py]
    H --> I[Step 4: Telegram 投递<br/>4 分条 / 3500 字符]
    I --> J[Step 5: URL 持久化<br/>跨天 7 天去重]
    J --> K[Step 6: 周报<br/>仅周日]
    I --> L[📱 Telegram]
    H --> M[🌐 GitHub Pages]
```

**合约自修订**：CONTRACT.md 每次执行后更新 Current State + Revision Log，无需改 CronCreate。

---

## 🚀 快速开始

```bash
# 1. 克隆
git clone https://github.com/TheWher/follow-news.git
cd follow-news

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行当日日报
bash scripts/follow-news-pipeline.sh
bash scripts/fetch-github-trending.sh
bash scripts/fetch-community.sh
bash scripts/fetch-papers.sh
bash scripts/fetch-products.sh

# 4. 生成站点
python3 scripts/build-enhanced-site.py
# → site/index.html 可直接浏览
```

---

## ✨ 特性

| 特性 | 说明 |
|------|------|
| 🔄 **多源轮换** | 4 级数据源自动轮换（pipeline → TechCrunch → Techmeme → random pool），同天重跑不重复 |
| 🧠 **AI 评分** | 4 维度 0-10 自动评分（MUST_INCLUDE / GOOD / MAYBE / SKIP），宁缺毋滥 |
| 🔗 **URL 去重** | 三层去重：URL 精确匹配 + 标题相似度 + 同域关键词。跨天 7 天持久化 |
| 📊 **diff 模式** | 同天内第 N 版仅展示新增/排名变化的条目，无新增则标注「与上版相同」 |
| 📡 **Telegram 投递** | `messages_send` MCP 直发，4 分条（≤3500 字符/条），秒到 |
| 🌐 **增强站点** | 纯客户端搜索 + 书签（localStorage）+ 已读跟踪 + 分类筛选 + 移动端适配 |
| 🗄️ **日/周归档** | 每日存档 + 周日自动合成 Top 10 周报（零额外 LLM 成本） |
| 💾 **持久化缓存** | `cache/` 目录跨会话保留，12 小时内固定层直接复用，免重复抓取 |

---

## 📂 项目结构

```
.
├── CONTRACT.md              # autoloop 合约（SSoT，自修订）
├── scripts/
│   ├── follow-news-pipeline.sh    # 新闻采集主流程
│   ├── fetch-github-trending.sh   # GitHub Trending
│   ├── fetch-community.sh         # HN + V2EX + LinuxDo
│   ├── fetch-papers.sh            # HuggingFace 论文
│   ├── fetch-products.sh          # Product Hunt 新品
│   ├── dedup-articles.py          # 去重引擎
│   ├── score-articles.py          # AI 评分
│   ├── enrich-articles.py         # 背景增强
│   └── build-enhanced-site.py     # v5.0 站点生成器
├── cache/                   # 持久化缓存（跨会话）
├── archive/follow-news/     # 历史日报（14 天+）
├── site/                    # GitHub Pages 站点
├── .used-urls.json          # 跨天 URL 去重状态
└── .autoloop/               # autoloop 运行时
```

---

## 🔧 数据源

| 层级 | 来源 | 采集方式 |
|------|------|----------|
| 新闻 (主) | pipeline 多源 / TechCrunch / Decoder / Techmeme / Bing News | shell pipeline + hyperbrowser 实时 |
| GitHub | GitHub REST API（5 维查询） | `fetch-github-trending.sh` |
| 社区 | Hacker News / V2EX / LinuxDo | `fetch-community.sh` |
| 论文 | HuggingFace Daily Papers | `fetch-papers.sh` |
| 产品 | Product Hunt RSS + GitHub 新仓库 | `fetch-products.sh` |

---

## 🤝 贡献

```bash
1. Fork → Branch（`feature/your-feature`）
2. 改动合约逻辑 → 改 CONTRACT.md 的 Execution Contract 部分
3. 添加数据源 → 新增 fetch-*.sh 脚本 + 合约 Step 1 注册
4. 提交 PR（描述改动 + 影响）
```

---

## 📜 License

MIT

---

<p align="center">
  <a href="https://star-history.com/#TheWher/follow-news&Date">
    <img src="https://api.star-history.com/svg?repos=TheWher/follow-news&type=Date" width="500">
  </a>
</p>
