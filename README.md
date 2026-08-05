# AI选题助手

个人AI热点聚合 + 自媒体选题发现工具。25个信源，日均~400条，DeepSeek AI 自动精选 + 选题推荐 + 人群验证。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置 DeepSeek API Key
$env:DEEPSEEK_API_KEY='sk-xxx'   # PowerShell

# 3. 运行完整管线（抓取 + AI处理 + Markdown输出到Obsidian）
python scripts/main.py

# 仅抓取新闻（不需API Key）
python scripts/main.py --fetch-only

# 仅AI处理 + 生成Markdown（使用已有数据）
python scripts/main.py --ai-only

# 关闭人群验证
python scripts/main.py --no-crowd

# 不输出Markdown
python scripts/main.py --no-markdown

# 从已有JSON生成Markdown日报（秒级，适合git pull后使用）
python scripts/markdown_reporter.py

# 管线测试
python scripts/test_pipeline.py
```

## 输出位置

- **Obsidian 日报**: `F:\zhi_shi_ku\claude code\资源\AI日报\YYYY-MM-DD.md`
- **JSON 数据**: `data/`（原始数据）、`web/data/`（前端数据）
- **本地预览**: `cd web && python -m http.server 8080`

## AI 管线

```
25信源抓取 → DeepSeek预筛 → 五维评分 → 人群验证 → 选题推荐 → AI日报 → Markdown输出
```

## 项目结构

```
ai-hotspot/
├── scripts/
│   ├── config.py           # 信源配置（25源）+ 评分公式 + Obsidian路径
│   ├── fetch_news.py       # 多格式爬虫（RSS/JSON API/HTML）
│   ├── ai_pipeline.py      # AI管线：预筛→评分→选题→日报
│   ├── crowd_verify.py     # 人群验证（百度/B站热搜匹配）
│   ├── markdown_reporter.py # Markdown日报生成（→Obsidian）
│   ├── history_tracker.py  # 历史趋势追踪
│   ├── main.py             # 主入口
│   ├── test_pipeline.py    # 管线测试
│   └── seed_data.py        # 示例数据生成
├── data/
│   ├── raw_news.json       # 原始抓取
│   ├── selected_news.json  # AI精选Top20
│   ├── daily_report.json   # AI日报
│   └── history/            # 历史趋势（90天）
├── web/                    # 本地HTML预览
├── .github/workflows/      # CI自动化（每日数据采集）
├── generate_report.bat     # 一键生成本地Markdown日报
└── requirements.txt
```

## 自动化

GitHub Actions 每天北京时间 8:00 自动运行：
1. 抓取25信源 → AI管线处理 → 历史归档
2. 数据提交回 main 分支
3. 晚上本地 `git pull && python scripts/markdown_reporter.py` 秒出日报
