# AI选题助手 (AI Hotspot)

帮助AI自媒体创作者发现选题的AI热点聚合工具。

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

# 仅抓取RSS（不需API Key）
python scripts/main.py --fetch-only

# 仅AI处理（使用已有数据）
python scripts/main.py --ai-only
```

## 项目结构

```
ai-hotspot/
├── scripts/
│   ├── config.py         # 信源配置 + AI参数
│   ├── fetch_news.py     # RSS爬虫
│   ├── ai_pipeline.py    # AI预筛/评分/选题/日报
│   └── main.py           # 主入口
├── data/
│   ├── raw_news.json     # 原始抓取数据
│   ├── selected_news.json # AI精选后数据
│   └── daily_report.json  # 每日AI日报
├── web/                  # 前端页面（待搭建）
├── requirements.txt
└── README.md
```
