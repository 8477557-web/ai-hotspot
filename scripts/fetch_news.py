"""
多格式新闻爬虫 — 从RSS、JSON API、HTML页面抓取最新消息
"""
import json
import os
import sys
import hashlib
import re
from time import mktime
from datetime import datetime, timezone, timedelta
from dateutil import parser as dateparser

import feedparser
import requests
from bs4 import BeautifulSoup

# 项目路径处理
sys.path.insert(0, os.path.dirname(__file__))
from config import SOURCES, RAW_FILE, REQUEST_TIMEOUT, MAX_ITEMS_PER_SOURCE, DATA_DIR

# 北京时间
BJT = timezone(timedelta(hours=8))


def safe_fetch(url: str, ua: str = None) -> str:
    """安全请求，带UA和超时，支持按源定制UA"""
    headers = {
        "User-Agent": ua or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }
    r = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
    r.raise_for_status()
    return r.content


def safe_fetch_json(url: str, ua: str = None) -> dict:
    """请求JSON API，返回解析后的dict/list"""
    content = safe_fetch(url, ua=ua)
    return json.loads(content)


def safe_fetch_html(url: str, ua: str = None) -> BeautifulSoup:
    """请求HTML页面，返回BeautifulSoup对象"""
    content = safe_fetch(url, ua=ua)
    return BeautifulSoup(content, "html.parser")


def parse_date(entry) -> str:
    """尽可能从feed条目中提取时间，返回ISO格式字符串"""
    for field in ("published_parsed", "updated_parsed"):
        tp = getattr(entry, field, None)
        if tp:
            try:
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


def resolve_json_path(data, path: list):
    """按路径从JSON中提取数据"""
    for key in path:
        if isinstance(data, dict):
            data = data.get(key, {})
        elif isinstance(data, list) and isinstance(key, int):
            data = data[key] if key < len(data) else {}
        else:
            return []
    return data if isinstance(data, list) else []


def build_item(source: dict, title: str, link: str, summary: str) -> dict:
    """构建标准item格式"""
    return {
        "id": item_id(source["id"], link or title),
        "source_id": source["id"],
        "source_name": source["name"],
        "source_tier": source["tier"],
        "source_lang": source["lang"],
        "source_category": source["category"],
        "title": title.strip() if title else "",
        "link": link,
        "summary": summary.strip() if summary else "",
        "published": datetime.now(BJT).isoformat(),
        "fetched_at": datetime.now(BJT).isoformat(),
    }


def get_field(raw_item: dict, field_map: dict, key: str, default: str = "") -> str:
    """从原始条目中按映射提取字段值"""
    mapped = field_map.get(key, key)
    if not mapped:
        return default
    return str(raw_item.get(mapped, default))


def format_link(raw_item: dict, template: str) -> str:
    """用模板 + 条目数据生成链接"""
    try:
        return template.format(**raw_item)
    except Exception:
        return ""


def fetch_rss(src: dict, content: bytes) -> list[dict]:
    """抓取RSS/Atom源"""
    items = []
    feed = feedparser.parse(content)

    if feed.bozo and not feed.entries:
        raise Exception(f"RSS解析失败: {feed.bozo_exception}")

    for entry in feed.entries[:MAX_ITEMS_PER_SOURCE]:
        link = entry.get("link", "")
        if not link:
            continue

        item = build_item(
            src,
            title=entry.get("title", ""),
            link=link,
            summary=(entry.get("summary", "") or entry.get("description", "")),
        )
        item["published"] = parse_date(entry)
        items.append(item)
    return items


def fetch_json_api(src: dict) -> list[dict]:
    """抓取JSON API源"""
    items = []
    data = safe_fetch_json(src["url"], ua=src.get("ua"))
    raw_items = resolve_json_path(data, src.get("item_path", []))

    field_map = src.get("field_map", {})
    link_tpl = src.get("link_template", "")

    for raw in raw_items[:MAX_ITEMS_PER_SOURCE]:
        title = get_field(raw, field_map, "title")
        link = get_field(raw, field_map, "link")
        if not link and link_tpl:
            link = format_link(raw, link_tpl)
        summary = get_field(raw, field_map, "summary")
        if not title and not link:
            continue

        items.append(build_item(src, title, link, summary))
    return items


def fetch_html_scrape(src: dict) -> list[dict]:
    """抓取HTML页面（CSS选择器）"""
    items = []
    soup = safe_fetch_html(src["url"], ua=src.get("ua"))
    elements = soup.select(src.get("item_selector", ""))

    field_map = src.get("field_map", {})

    for el in elements[:MAX_ITEMS_PER_SOURCE]:
        title = extract_html_field(el, field_map, "title")
        link = extract_html_field(el, field_map, "link")
        summary = extract_html_field(el, field_map, "summary")
        if not title and not link:
            continue

        # 补全相对URL
        if link and link.startswith("/"):
            link = src.get("base_url", "") + link

        items.append(build_item(src, title, link, summary))
    return items


def extract_html_field(element, field_map: dict, key: str) -> str:
    """从HTML元素中提取字段（支持 attr[href] 语法）"""
    selector = field_map.get(key, "")
    if not selector:
        return ""

    attr_match = re.match(r'(.+)\[([\w-]+)\]$', selector)
    if attr_match:
        el = element.select_one(attr_match.group(1))
        return el.get(attr_match.group(2), "") if el else ""
    else:
        el = element.select_one(selector)
        return el.get_text(strip=True) if el else ""


_FETCH_DISPATCH = {
    "json_api": fetch_json_api,
    "html_scrape": fetch_html_scrape,
}


def fetch_all() -> list[dict]:
    """遍历所有信源，按类型分发抓取逻辑"""
    all_items = []
    stats = {"success": 0, "fail": 0}

    for src in SOURCES:
        if not src.get("enabled", True):
            continue

        src_type = src.get("type", "rss")
        print(f"[{src['name']}] 抓取中... ", end="", flush=True)

        try:
            handler = _FETCH_DISPATCH.get(src_type)
            if handler:
                items = handler(src)
            else:
                content = safe_fetch(src["url"], ua=src.get("ua"))
                items = fetch_rss(src, content)

            all_items.extend(items)
            stats["success"] += 1
            print(f"{len(items)}条")

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
    print(f"AI选题助手 — 多格式爬虫启动 {datetime.now(BJT).strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    items = fetch_all()
    items = deduplicate(items)
    save_raw(items)

    print(f"\n去重后: {len(items)}条")
    return items


if __name__ == "__main__":
    main()
