"""
历史趋势追踪 — 记录每日精选数据的聚合指标，支持趋势对比
"""
import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from config import DATA_DIR, WEB_DATA_DIR, SELECTED_FILE

BJT = timezone(timedelta(hours=8))
HISTORY_DIR = os.path.join(DATA_DIR, "history")
TRENDS_FILE = os.path.join(HISTORY_DIR, "trends.json")
ITEMS_FILE = os.path.join(HISTORY_DIR, "daily_items.json")
WEB_HISTORY_DIR = os.path.join(WEB_DATA_DIR, "history")

MAX_DAYS_MAIN = 90
MAX_DAYS_WEB = 30


def load_json(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_keywords_brief(title: str, top_n: int = 3) -> list[str]:
    """从标题提取代表性关键词（2-4字中文词 + 英文实体）"""
    keywords = []
    # 英文实体
    eng = re.findall(r'[A-Z][a-zA-Z0-9.+-]{2,}(?:\s+[A-Z][a-zA-Z0-9.+-]+)*', title)
    keywords.extend(eng)
    # 中文2-4gram，取频率最高
    chinese = re.findall(r'[一-鿿]+', title)
    for chunk in chinese:
        for wlen in (4, 3, 2):
            for i in range(len(chunk) - wlen + 1):
                gram = chunk[i:i + wlen]
                if len(gram) >= 2:
                    keywords.append(gram)
    counter = Counter(keywords)
    return [kw for kw, _ in counter.most_common(top_n)]


def compute_aggregate(items: list[dict], date_str: str) -> dict:
    """计算当日聚合指标"""
    if not items:
        return {"date": date_str, "total_items": 0}

    scores = [it.get("quality_score", 0) for it in items]
    crowd_heats = [it.get("scores", {}).get("crowd_heat", 0) for it in items]
    crowd_hot = sum(1 for ch in crowd_heats if ch >= 2)

    # 选题分布
    topic_dist = Counter()
    for it in items:
        for tp in it.get("topics", []):
            tag = tp.get("tag", "other")
            topic_dist[tag] += 1

    # 信源分布
    source_dist = Counter()
    for it in items:
        source_dist[it.get("source_tier", "T2")] += 1

    # Top关键词
    all_kw = Counter()
    for it in items:
        for kw in extract_keywords_brief(it.get("title", "")):
            all_kw[kw] += 1

    return {
        "date": date_str,
        "total_items": len(items),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "crowd_hot_count": crowd_hot,
        "avg_crowd_heat": round(sum(crowd_heats) / len(crowd_heats), 1) if crowd_heats else 0,
        "topic_distribution": dict(topic_dist.most_common()),
        "source_distribution": dict(source_dist),
        "top_keywords": all_kw.most_common(5),
    }


def compute_daily_items(items: list[dict]) -> list[dict]:
    """提取当日逐条摘要"""
    return [{
        "title": it.get("title", ""),
        "quality_score": it.get("quality_score", 0),
        "source_name": it.get("source_name", ""),
        "crowd_heat": it.get("scores", {}).get("crowd_heat", 0),
        "topic_tags": [tp.get("tag", "") for tp in it.get("topics", [])],
    } for it in items]


def trim_days(days: list[dict], max_days: int) -> list[dict]:
    """按日期修剪，保留最近 max_days 天"""
    days.sort(key=lambda d: d.get("date", ""), reverse=True)
    return days[:max_days]


def append_today(items: list[dict], date_str: str = None):
    """追加今日数据到历史文件"""
    if date_str is None:
        date_str = datetime.now(BJT).strftime("%Y-%m-%d")

    # trends
    trends = load_json(TRENDS_FILE)
    days = trends.get("days", [])
    days = [d for d in days if d.get("date") != date_str]
    days.append(compute_aggregate(items, date_str))
    days = trim_days(days, MAX_DAYS_MAIN)
    save_json(TRENDS_FILE, {
        "updated_at": datetime.now(BJT).isoformat(),
        "total_days": len(days),
        "days": sorted(days, key=lambda d: d["date"], reverse=True),
    })

    # daily items
    items_data = load_json(ITEMS_FILE)
    item_days = items_data.get("days", [])
    item_days = [d for d in item_days if d.get("date") != date_str]
    item_days.append({"date": date_str, "items": compute_daily_items(items)})
    item_days = trim_days(item_days, MAX_DAYS_MAIN)
    save_json(ITEMS_FILE, {
        "updated_at": datetime.now(BJT).isoformat(),
        "days": sorted(item_days, key=lambda d: d["date"], reverse=True),
    })


def export_for_web():
    """导出最近30天数据到web目录"""
    os.makedirs(WEB_HISTORY_DIR, exist_ok=True)

    for src, dst_name in [(TRENDS_FILE, "trends.json"), (ITEMS_FILE, "daily_items.json")]:
        data = load_json(src)
        days = data.get("days", [])
        data["days"] = trim_days(days, MAX_DAYS_WEB)
        save_json(os.path.join(WEB_HISTORY_DIR, dst_name), data)


def main():
    if not os.path.exists(SELECTED_FILE):
        print("selected_news.json 不存在，跳过历史追踪")
        return

    with open(SELECTED_FILE, "r", encoding="utf-8") as f:
        selected = json.load(f)

    items = selected.get("items", [])
    date_str = datetime.now(BJT).strftime("%Y-%m-%d")
    print(f"历史追踪: {date_str} — {len(items)}条精选新闻")

    append_today(items, date_str)
    export_for_web()
    print(f"已追加到 {HISTORY_DIR}/")
    print(f"已导出到 {WEB_HISTORY_DIR}/ (最近{MAX_DAYS_WEB}天)")


if __name__ == "__main__":
    main()
