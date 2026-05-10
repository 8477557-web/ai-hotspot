# AI选题助手 — 项目上下文

## 基本信息
- **项目路径**: f:/claude code/ai-hotspot
- **GitHub仓库**: https://github.com/8477557-web/ai-hotspot
- **在线网址**: https://8477557-web.github.io/ai-hotspot/
- **定位**: AI热点精选聚合 + 自媒体选题推荐工具
- **变现**: 网站免费引流 → 付费社群(¥29.9/月)，不靠订阅制

## 技术架构
- **爬虫**: Python feedparser + requests + BeautifulSoup，支持RSS/JSON API/HTML三种格式，25个信源，约400条/天
- **AI处理**: DeepSeek API (V3.2预筛 + V4 Pro评分)，批量+5线程并行，约10秒完成
- **前端**: 纯静态 HTML+CSS+JS，4个Tab(日报/精选/选题/信源)
- **数据**: JSON文件，无需数据库
- **托管**: GitHub Pages (gh-pages分支) + GitHub Actions定时(每天8:00 UTC)
- **成本**: 约¥1-3/月(仅DeepSeek API)
- **日均产量**: ~400条（25个活跃信源）

## AI管线流水线
1. 多格式爬虫抓取（RSS/JSON API/HTML）→ raw_news.json
2. DeepSeek V3.2批量预筛(10条/批) → 过滤AI无关
3. DeepSeek V4 Pro批量评分(5条/批) → 5维打分
4. 代码公式重算质量分 → 排序取Top 20
5. DeepSeek批量选题推荐(5条/批) → 每条1-2个自媒体角度
6. DeepSeek日报摘要生成 → 4版块(模型/产品/行业/研究/观点)

## 关键配置
- **API Key**: 环境变量`DEEPSEEK_API_KEY`，GitHub Secrets已配置
- **数据目录**: data/(不入库)、web/data/(入库，初始数据)
- **GitHub Actions**: .github/workflows/deploy.yml
- **安全**: CSP已设、全局XSS转义、API Key无明文

## 可用信源(25个，2026-05-10全部修复+扩展)

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
Mistral AI Blog (网站改为纯JS渲染), 机器之心 (JS渲染+API付费)

## 下一步
- 持续监控信源可用性
- 优化评分策略（400条/天需更精准筛选）
- 趋势预测/热度指数功能
- 个人域名配置
