"""
RSS新闻爬虫 — 从所有启用的信源抓取最新消息
"""
import json
import os
import sys
import hashlib
from datetime import datetime, timezone, timedelta
from dateutil import parser as dateparser

import feedparser
import requests

# 项目路径处理
sys.path.insert(0, os.path.dirname(__file__))
from config import SOURCES, RAW_FILE, REQUEST_TIMEOUT, MAX_ITEMS_PER_SOURCE, DATA_DIR

# 北京时间
BJT = timezone(timedelta(hours=8))


def safe_fetch(url: str) -> str:
    """安全请求，带UA和超时"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }
    r = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
    r.raise_for_status()
    return r.content


def parse_date(entry) -> str:
    """尽可能从feed条目中提取时间，返回ISO格式字符串"""
    for field in ("published_parsed", "updated_parsed"):
        tp = getattr(entry, field, None)
        if tp:
            try:
                from time import mktime
                dt = datetime.fromtimestamp(mktime(tp), tz=BJT)
                return dt.isoformat()
            except Exception:
                pass
    for field in ("published", "updated"):
        raw = getattr(entry, field, None)
        if raw:
            try:
                return dateparser.parse(raw).astimezone(BJT).isoformat()
            except Exception:
                pass
    return datetime.now(BJT).isoformat()


def item_id(source_id: str, link: str) -> str:
    """生成稳定去重ID"""
    raw = f"{source_id}:{link}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def fetch_all() -> list[dict]:
    """遍历所有信源，返回原始新闻列表"""
    all_items = []
    stats = {"success": 0, "fail": 0, "skipped": 0}

    for src in SOURCES:
        if not src.get("enabled", True):
            continue

        print(f"[{src['name']}] 抓取中... ", end="", flush=True)

        try:
            content = safe_fetch(src["url"])
            feed = feedparser.parse(content)

            if feed.bozo and not feed.entries:
                raise Exception(f"RSS解析失败: {feed.bozo_exception}")

            count = 0
            for entry in feed.entries[:MAX_ITEMS_PER_SOURCE]:
                link = entry.get("link", "")
                if not link:
                    continue

                item = {
                    "id": item_id(src["id"], link),
                    "source_id": src["id"],
                    "source_name": src["name"],
                    "source_tier": src["tier"],
                    "source_lang": src["lang"],
                    "source_category": src["category"],
                    "title": entry.get("title", "").strip(),
                    "link": link,
                    "summary": (entry.get("summary", "") or entry.get("description", "")).strip(),
                    "published": parse_date(entry),
                    "fetched_at": datetime.now(BJT).isoformat(),
                }
                all_items.append(item)
                count += 1

            stats["success"] += 1
            print(f"{count}条")

        except Exception as e:
            stats["fail"] += 1
            print(f"失败: {e}")

    print(f"\n总计: {len(all_items)}条 | 成功{stats['success']}个源 | 失败{stats['fail']}个源")
    return all_items


def deduplicate(items: list[dict]) -> list[dict]:
    """按ID去重，保留最早的"""
    seen = {}
    for item in items:
        uid = item["id"]
        if uid not in seen or item["published"] < seen[uid]["published"]:
            seen[uid] = item
    return list(seen.values())


def save_raw(items: list[dict]):
    """保存原始数据"""
    os.makedirs(DATA_DIR, exist_ok=True)
    output = {
        "updated_at": datetime.now(BJT).isoformat(),
        "total": len(items),
        "items": sorted(items, key=lambda x: x["published"], reverse=True),
    }
    with open(RAW_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"已保存到 {RAW_FILE}")


def main():
    print("=" * 50)
    print(f"AI选题助手 — RSS爬虫启动 {datetime.now(BJT).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    items = fetch_all()
    items = deduplicate(items)
    save_raw(items)

    print(f"\n去重后: {len(items)}条")
    return items


if __name__ == "__main__":
    main()
