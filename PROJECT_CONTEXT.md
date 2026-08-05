# AI选题助手 — 项目上下文

## 基本信息
- **项目路径**: f:/claude code/ai-hotspot
- **仓库**: Private（仅个人使用）
- **定位**: 个人AI热点精选 + 自媒体选题发现工具
- **输出**: Obsidian Markdown 日报 + JSON 数据 + 本地 HTML 预览

## 技术架构
- **爬虫**: Python feedparser + requests + BeautifulSoup，支持RSS/JSON API/HTML三种格式，25个信源，约400条/天
- **AI处理**: DeepSeek API (V3.2预筛 + V4 Pro评分)，批量+5线程并行
- **人群验证**: 百度/B站热搜匹配，crowd_heat 作为第六评分维度
- **输出**: Markdown 日报写入 Obsidian 知识库（`资源/AI日报/` 目录）
- **前端**: 纯静态 HTML+CSS+JS（本地 `python -m http.server` 预览）
- **数据**: JSON文件，无需数据库
- **自动化**: GitHub Actions 定时（每天 UTC 0:00）+ 本地 `git pull` 同步
- **成本**: 约¥1-3/月（仅DeepSeek API）

## AI管线流程
1. 多格式爬虫抓取（RSS/JSON API/HTML）→ raw_news.json
2. DeepSeek V3.2批量预筛(10条/批) → 过滤AI无关
3. DeepSeek V4 Pro批量评分(5条/批) → 5维打分
4. 代码公式重算质量分 → 排序取Top 20
5. 人群验证(默认开启): 百度/B站热搜匹配 → crowd_heat第6维
6. DeepSeek批量选题推荐(5条/批) → 每条1-2个自媒体角度
7. DeepSeek日报摘要生成 → 4版块(模型/产品/行业/研究/观点)
8. Markdown输出到Obsidian知识库
9. 历史追踪: 每日聚合摘要归档 → trends.json + daily_items.json

## 关键配置
- **API Key**: 环境变量 `DEEPSEEK_API_KEY`，GitHub Secrets 已配置
- **数据目录**: data/（不入库）、web/data/（历史数据入库）
- **Obsidian输出**: `F:\zhi_shi_ku\claude code\资源\AI日报\`
- **GitHub Actions**: .github/workflows/deploy.yml

## 可用信源(25个)

### T1 一手官方 (9个)
OpenAI Blog, Google DeepMind, Anthropic (Claude+Engineering), Facebook Engineering,
Microsoft Research, NVIDIA Technical Blog, Hugging Face Blog, Apple ML Research

### T2 中文媒体 (8个)
36氪, 少数派, 雷锋网, InfoQ中国, 量子位, 极客公园, 爱范儿, IT之家

### T2 热搜/搜索 (4个)
百度热搜(JSON API), B站热搜(JSON API), Google News AI, Google News AI 中文

### T2 技术社区 (4个)
Hacker News, Reddit ML, GitHub Trending(HTML爬虫), GitHub AI新项目(JSON API)

## 已关闭信源(2个)
Mistral AI Blog (JS渲染), 机器之心 (JS渲染+API付费)

## 日常使用

**自动模式**（推荐）：
1. GitHub Actions 每天北京时间8:00自动抓取+AI处理，提交数据回仓库
2. 晚上开工前双击运行 `generate_report.bat`（git pull + 生成Markdown）
3. Obsidian 里直接阅读当日日报

**手动模式**：
```bash
$env:DEEPSEEK_API_KEY='sk-xxx'
python scripts/main.py    # 完整管线 → JSON + Markdown → Obsidian
```
