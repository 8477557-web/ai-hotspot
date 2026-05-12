# AI选题助手 (AI Hotspot)

帮助AI自媒体创作者发现选题的AI热点聚合工具。
25个信源，日均抓取~400条，DeepSeek AI 自动精选+选题推荐。
人群验证（百度/B站热搜匹配）+ 历史趋势追踪 + 可选社交舆情验证。

🌐 **在线访问**: https://8477557-web.github.io/ai-hotspot/

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置DeepSeek API Key
# PowerShell:
$env:DEEPSEEK_API_KEY='sk-xxx'
# Bash:
export DEEPSEEK_API_KEY='sk-xxx'

# 3. 运行完整管线（抓取 + AI处理）
python scripts/main.py

# 仅抓取新闻（不需API Key）
python scripts/main.py --fetch-only

# 仅AI处理（使用已有数据）
python scripts/main.py --ai-only

# 启用人群验证（百度/B站热搜匹配，CI默认开启）
python scripts/main.py --ai-only --crowd-verify

# 启用社交舆情验证（需先安装 last30days skill）
git clone https://github.com/mvanhorn/last30days-skill.git ../skills/last30days
python scripts/main.py --ai-only --social-verify --social-top-n 5

# 测试各环节
python scripts/test_pipeline.py
```

## AI 管线

```
25信源抓取 → DeepSeek预筛 → 五维评分 → [人群验证] → 选题推荐 → [社交验证] → AI日报 → 历史追踪
```

### 人群验证（CI 默认开启）

自动匹配百度热搜(50条)和B站热搜(10条)与Top 20精选新闻的关键词，
判断AI话题在普通网民中的关注度，提升 virality 评分。

```bash
python scripts/main.py --ai-only --crowd-verify
```

### 社交验证（可选）

基于 [last30days-skill](https://github.com/mvanhorn/last30days-skill)，
对 Top N 精选新闻搜索 Reddit、HN、GitHub、YouTube 社区讨论。

```bash
git clone https://github.com/mvanhorn/last30days-skill.git ../skills/last30days
python scripts/main.py --ai-only --social-verify --social-top-n 5
```

## 项目结构

```
ai-hotspot/
├── scripts/
│   ├── config.py         # 信源配置（25源，多格式）
│   ├── fetch_news.py     # 多格式爬虫（RSS/JSON API/HTML）
│   ├── crowd_verify.py   # 人群验证引擎（百度/B站热搜匹配）
│   ├── history_tracker.py # 历史趋势追踪（每日摘要归档）
│   ├── ai_pipeline.py    # AI预筛/评分/人群验证/选题/日报
│   ├── social_verify.py  # last30days 社交舆情引擎封装
│   ├── main.py           # 主入口
│   ├── test_pipeline.py  # 管线测试
│   └── seed_data.py      # 初始数据生成
├── data/
│   ├── raw_news.json     # 原始抓取数据
│   ├── selected_news.json # AI精选后数据
│   ├── daily_report.json  # 每日AI日报
│   └── history/          # 历史趋势数据（90天）
├── web/                  # 纯静态前端（5个Tab + 趋势页）
├── requirements.txt
└── README.md
```
