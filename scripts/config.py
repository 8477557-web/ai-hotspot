"""
信源配置 — 所有RSS源和分类标签定义
"""
import os

# ── DeepSeek API ──────────────────────────────────────────
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_PRE_FILTER_MODEL = "deepseek-chat"       # V3.2, 便宜, 预筛
DEEPSEEK_SCORE_MODEL = "deepseek-chat"             # V4 Pro, 评分+选题

# ── 采集设置 ──────────────────────────────────────────────
MAX_ITEMS_PER_SOURCE = 20      # 每个源最多取N条
REQUEST_TIMEOUT = 30           # 请求超时(秒)
TOP_N_SELECTED = 20            # 最终精选条数

# ── 选题标签 ──────────────────────────────────────────────
TOPIC_TAGS = [
    {"id": "tutorial",  "label": "教程向", "emoji": "🎬", "desc": "可以做教程/实测视频"},
    {"id": "money",     "label": "搞钱向", "emoji": "💰", "desc": "能讲商业机会/变现思路"},
    {"id": "science",   "label": "科普向", "emoji": "🧠", "desc": "适合通俗科普讲解"},
    {"id": "product",   "label": "产品向", "emoji": "📦", "desc": "新产品/新功能推荐评测"},
    {"id": "hotspot",   "label": "热点向", "emoji": "🔥", "desc": "蹭热点/快速追流量"},
]

# ── RSS信源列表 ───────────────────────────────────────────
# 等级: T1=一手官方, T1.5=官方社媒, T2=媒体/KOL
SOURCES = [
    # ===== T1: 一手官方（用RSSHub/第三方Feed替代） =====
    {
        "id": "openai-blog",
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": True,   # 官方RSS，已验证
    },
    {
        "id": "deepmind-blog",
        "name": "Google DeepMind",
        "url": "https://deepmind.google/blog/rss.xml",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": True,   # 官方RSS，已验证
    },
    {
        "id": "anthropic-blog",
        "name": "Anthropic (Claude Blog)",
        "url": "https://tim-hilde.github.io/anthropic-rss/rss.xml",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": True,   # 第三方RSS(GitHub Pages)，已验证
    },
    {
        "id": "anthropic-engineering",
        "name": "Anthropic Engineering",
        "url": "https://raw.githubusercontent.com/conoro/anthropic-engineering-rss-feed/main/anthropic_engineering_rss.xml",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": True,   # 第三方RSS(GitHub Raw)，已验证
    },
    {
        "id": "fb-engineering",
        "name": "Facebook Engineering",
        "url": "https://engineering.fb.com/feed/",
        "tier": "T1.5",
        "lang": "en",
        "category": "official",
        "enabled": True,   # 替代Meta AI Blog，含AI/ML内容
    },
    {
        "id": "microsoft-research",
        "name": "Microsoft Research",
        "url": "https://www.microsoft.com/en-us/research/feed/",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": True,   # ✓ 可用
    },
    {
        "id": "nvidia-blog",
        "name": "NVIDIA Technical Blog",
        "url": "https://developer.nvidia.com/blog/feed/",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": True,   # ✓ 可用
    },
    {
        "id": "huggingface-blog",
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": True,   # 新增，官方RSS
    },
    {
        "id": "apple-ml",
        "name": "Apple ML Research",
        "url": "https://machinelearning.apple.com/rss.xml",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": True,   # 新增，官方RSS
    },
    {
        "id": "mistral-blog",
        "name": "Mistral AI Blog",
        "url": "https://mistral.ai/news/feed.xml",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": False,  # 网站改为纯JS渲染，RSS Feed已不存在
    },

    # ===== T2: 中文媒体 =====
    {
        "id": "36kr",
        "name": "36氪",
        "url": "https://36kr.com/feed",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": True,   # ✓ 可用
    },
    {
        "id": "sspai",
        "name": "少数派",
        "url": "https://sspai.com/feed",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": True,   # ✓ 可用
    },
    {
        "id": "leiphone",
        "name": "雷锋网",
        "url": "https://www.leiphone.com/feed",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": True,   # 替代机器之心，需Googlebot UA
        "ua": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    },
    {
        "id": "infoq-cn",
        "name": "InfoQ中国",
        "url": "https://www.infoq.cn/feed",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": True,   # 官方RSS，已验证
    },
    {
        "id": "qbitai",
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": True,   # 官方RSS，已验证
    },
    {
        "id": "geekpark",
        "name": "极客公园",
        "url": "https://www.geekpark.net/rss",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": True,   # 新增
    },
    {
        "id": "ifanr",
        "name": "爱范儿",
        "url": "https://www.ifanr.com/feed",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": True,   # 新增
    },
    {
        "id": "ithome-ai",
        "name": "IT之家",
        "url": "https://www.ithome.com/rss/",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": True,   # 官方RSS，已验证（全站，AI内容由DeepSeek筛选）
    },

    # ===== T2: 热搜/搜索平台 =====
    {
        "id": "baidu-hot",
        "name": "百度热搜",
        "url": "https://top.baidu.com/api/board?tab=realtime",
        "type": "json_api",
        "item_path": ["data", "cards", 0, "content"],
        "field_map": {"title": "word", "summary": "desc"},
        "link_template": "https://www.baidu.com/s?wd={word}",
        "tier": "T2",
        "lang": "zh",
        "category": "hotlist",
        "enabled": True,
    },
    {
        "id": "bilibili-hot",
        "name": "B站热搜",
        "url": "https://api.bilibili.com/x/web-interface/search/square?limit=10",
        "type": "json_api",
        "item_path": ["data", "trending", "list"],
        "field_map": {"title": "keyword"},
        "link_template": "https://search.bilibili.com/all?keyword={keyword}",
        "tier": "T2",
        "lang": "zh",
        "category": "hotlist",
        "enabled": True,
    },
    {
        "id": "google-news-ai",
        "name": "Google News (AI)",
        "url": "https://news.google.com/rss/search?q=AI+artificial+intelligence+LLM+GPT&hl=en-US&gl=US&ceid=US:en",
        "tier": "T2",
        "lang": "en",
        "category": "search",
        "enabled": True,
    },
    {
        "id": "google-news-ai-zh",
        "name": "Google News (AI 中文)",
        "url": "https://news.google.com/rss/search?q=人工智能+AI+大模型&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "tier": "T2",
        "lang": "zh",
        "category": "search",
        "enabled": True,
    },

    # ===== T2: 技术社区 =====
    {
        "id": "hn-ai",
        "name": "Hacker News (AI)",
        "url": "https://hnrss.org/frontpage?q=AI+OR+LLM+OR+GPT+OR+OpenAI+OR+Claude+OR+Gemini",
        "tier": "T2",
        "lang": "en",
        "category": "community",
        "enabled": True,
    },
    {
        "id": "reddit-ml",
        "name": "Reddit r/MachineLearning",
        "url": "https://www.reddit.com/r/MachineLearning/.rss",
        "tier": "T2",
        "lang": "en",
        "category": "community",
        "enabled": True,
    },
    {
        "id": "github-trending",
        "name": "GitHub Trending",
        "url": "https://github.com/trending?since=daily",
        "type": "html_scrape",
        "item_selector": "article.Box-row",
        "field_map": {
            "title": "h2 a",
            "link": "h2 a[href]",
            "summary": "p",
        },
        "base_url": "https://github.com",
        "tier": "T2",
        "lang": "en",
        "category": "community",
        "enabled": True,
    },
    {
        "id": "github-ai-repos",
        "name": "GitHub AI 新项目",
        "url": "https://api.github.com/search/repositories?q=topic:ai+stars:>50&sort=updated&per_page=10",
        "type": "json_api",
        "item_path": ["items"],
        "field_map": {"title": "full_name", "summary": "description", "link": "html_url"},
        "tier": "T2",
        "lang": "en",
        "category": "community",
        "enabled": True,
    },
]

# ── 输出路径 ──────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RAW_FILE = os.path.join(DATA_DIR, "raw_news.json")
SELECTED_FILE = os.path.join(DATA_DIR, "selected_news.json")
DAILY_FILE = os.path.join(DATA_DIR, "daily_report.json")

# Web前端数据目录（与DATA_DIR同步输出）
WEB_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "data")
WEB_SELECTED_FILE = os.path.join(WEB_DATA_DIR, "selected_news.json")
WEB_DAILY_FILE = os.path.join(WEB_DATA_DIR, "daily_report.json")
