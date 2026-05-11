# AI选题助手 (AI Hotspot)

帮助AI自媒体创作者发现选题的AI热点聚合工具。
25个信源，日均抓取~400条，DeepSeek AI 自动精选+选题推荐。
可选社交舆情验证（基于 [last30days-skill](https://github.com/mvanhorn/last30days-skill)）。

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

# 启用社交舆情验证（需先安装 last30days skill）
git clone https://github.com/mvanhorn/last30days-skill.git ../skills/last30days
python scripts/main.py --ai-only --social-verify --social-top-n 5

# 测试各环节
python scripts/test_pipeline.py
```

## AI 管线

```
25信源抓取 → DeepSeek预筛 → 五维评分 → 选题推荐 → [社交验证] → AI日报
```

### 社交验证（可选）

基于 [last30days-skill](https://github.com/mvanhorn/last30days-skill)（25K+ Stars），
对 Top N 精选新闻自动搜索 Reddit、Hacker News、GitHub、YouTube 的社区讨论，
提取热度指标和关键讨论，增强选题决策依据。

- **评分维度扩展**: 在原有五维评分基础上增加"社交热度"第六维度
- **前端展示**: 新闻卡片显示社区讨论数和热度评分
- **免配置**: Reddit、HN、GitHub、YouTube 免费即可使用

```bash
# 启用社交验证（Top 5 精选新闻）
python scripts/main.py --social-verify

# 验证前 10 条
python scripts/main.py --social-verify --social-top-n 10
```

## 项目结构

```
ai-hotspot/
├── scripts/
│   ├── config.py         # 信源配置（25源，多格式）
│   ├── fetch_news.py     # 多格式爬虫（RSS/JSON API/HTML）
│   ├── ai_pipeline.py    # AI预筛/评分/选题/日报 + 社交验证
│   ├── social_verify.py  # last30days 社交舆情引擎封装
│   ├── main.py           # 主入口
│   ├── test_pipeline.py  # 管线测试
│   └── seed_data.py      # 初始数据生成
├── data/
│   ├── raw_news.json     # 原始抓取数据
│   ├── selected_news.json # AI精选后数据（含social_metrics）
│   └── daily_report.json  # 每日AI日报
├── web/                  # 纯静态前端（4个Tab + 社交讨论展示）
├── requirements.txt
└── README.md
```
