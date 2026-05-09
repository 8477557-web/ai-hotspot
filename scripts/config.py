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
        "url": "https://rsshub.app/openai/blog",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": False,  # RSSHub 403, 待修复
    },
    {
        "id": "deepmind-blog",
        "name": "Google DeepMind",
        "url": "https://deepmind.google/blog/rss.xml",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": False,  # SSL问题, 待修复
    },
    {
        "id": "anthropic-blog",
        "name": "Anthropic News",
        "url": "https://rsshub.app/anthropic/news",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": False,  # RSSHub 403, 待修复
    },
    {
        "id": "meta-ai",
        "name": "Meta AI Blog",
        "url": "https://ai.meta.com/blog/rss/",
        "tier": "T1",
        "lang": "en",
        "category": "official",
        "enabled": False,  # 400, 待修复
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
        "enabled": True,   # 新增，官方RSS
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
        "id": "jiqizhixin",
        "name": "机器之心",
        "url": "https://rsshub.app/jiqizhixin",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": False,  # RSSHub 403, 待用直爬替代
    },
    {
        "id": "qbitai",
        "name": "量子位",
        "url": "https://rsshub.app/qbitai",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": False,  # RSSHub 403, 待用直爬替代
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
        "name": "IT之家 (AI)",
        "url": "https://rsshub.app/ithome/tag/ai",
        "tier": "T2",
        "lang": "zh",
        "category": "media",
        "enabled": False,  # RSSHub受限, 待开启
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
