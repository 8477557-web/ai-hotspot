# AI选题助手 (AI Hotspot)

帮助AI自媒体创作者发现选题的AI热点聚合工具。
25个信源，日均抓取~400条，DeepSeek AI 自动精选+选题推荐。

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

# 测试各环节
python scripts/test_pipeline.py
```

## 项目结构

```
ai-hotspot/
├── scripts/
│   ├── config.py         # 信源配置（25源，多格式）
│   ├── fetch_news.py     # 多格式爬虫（RSS/JSON API/HTML）
│   ├── ai_pipeline.py    # AI预筛/评分/选题/日报
│   ├── main.py           # 主入口
│   ├── test_pipeline.py  # 管线测试
│   └── seed_data.py      # 初始数据生成
├── data/
│   ├── raw_news.json     # 原始抓取数据
│   ├── selected_news.json # AI精选后数据
│   └── daily_report.json  # 每日AI日报
├── web/                  # 纯静态前端（4个Tab）
├── requirements.txt
└── README.md
```
