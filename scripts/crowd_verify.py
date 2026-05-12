"""
人群验证引擎 — 百度/B站热搜匹配，判断AI选题的公众关注度
"""
import json
import re
import math
import sys
import os
from datetime import datetime, timezone, timedelta

import requests

sys.path.insert(0, os.path.dirname(__file__))
from config import REQUEST_TIMEOUT

BJT = timezone(timedelta(hours=8))

BAIDU_HOT_URL = "https://top.baidu.com/api/board?tab=realtime"
BILIBILI_HOT_URL = "https://api.bilibili.com/x/web-interface/search/square?limit=10"

STOP_WORDS = {"的", "了", "是", "在", "和", "也", "就", "都", "而", "及", "与",
              "着", "或", "一个", "没有", "我们", "你们", "他们", "它们", "这个",
              "那个", "哪些", "什么", "怎么", "如何", "为什么", "可以", "已经",
              "还", "要", "会", "能", "被", "把", "从", "到", "对", "让", "给"}


def safe_get_json(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}
    r = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
    r.raise_for_status()
    return r.json()


def normalize(s: str) -> str:
    result = []
    for c in s:
        code = ord(c)
        if 0xFF01 <= code <= 0xFF5E:
            result.append(chr(code - 0xFEE0))
        elif code == 0x3000:
            result.append(" ")
        else:
            result.append(c)
    return "".join(result).strip().lower()


def extract_keywords(title: str) -> list[str]:
    """从标题提取关键词：英文实体 + 中文n-gram"""
    keywords = []
    normalized = normalize(title)

    # 英文实体：大写字母开头的连续词序列
    eng_entities = re.findall(r'[A-Z][a-zA-Z0-9.+-]{2,}(?:\s+[A-Z][a-zA-Z0-9.+-]+)*', title)
    for e in eng_entities:
        keywords.append(e.strip())

    # 中文2-4字滑动窗口
    chinese = re.findall(r'[一-鿿]+', normalized)
    for chunk in chinese:
        if len(chunk) < 2:
            continue
        for wlen in (4, 3, 2):
            for i in range(len(chunk) - wlen + 1):
                gram = chunk[i:i + wlen]
                if gram not in STOP_WORDS and len(gram) >= 2:
                    keywords.append(gram)

    # 去重，保持顺序
    seen = set()
    unique = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique.append(kw)
    return unique


def match_score(title_normalized: str, trending_word: str) -> float:
    tw = normalize(trending_word)
    tn = title_normalized
    if not tw or len(tw) < 2:
        return 0.0
    if tn == tw:
        return 1.0
    if tw in tn or tn in tw:
        return 0.8
    if len(tw) >= 3 and len(tn) >= 3:
        for i in range(len(tw) - 2):
            if tw[i:i + 3] in tn:
                return 0.5
    return 0.0


def fetch_trending() -> tuple[list, list]:
    """拉取百度/B站热搜，返回 (baidu_items, bilibili_items)"""
    bd, bl = [], []
    try:
        data = safe_get_json(BAIDU_HOT_URL)
        cards = data.get("data", {}).get("cards", [])
        bd = cards[0].get("content", []) if cards else []
    except Exception:
        pass

    try:
        data = safe_get_json(BILIBILI_HOT_URL)
        bl = data.get("data", {}).get("trending", {}).get("list", [])
    except Exception:
        pass

    return bd, bl


def calculate_crowd_heat(item_title: str, bd_items: list, bl_items: list) -> float:
    """计算0-10的人群热度分"""
    tn = normalize(item_title)

    bd_score = 0.0
    for bd in bd_items[:30]:
        word = bd.get("word", "")
        score = bd.get("hotScore", 0)
        ms = match_score(tn, word)
        if ms > 0:
            bd_score += ms * math.tanh(score / 300000) * 10

    bl_score = 0.0
    for bl in bl_items:
        word = bl.get("keyword", "")
        score = bl.get("heat_score", 0)
        ms = match_score(tn, word)
        if ms > 0:
            bl_score += ms * math.tanh(score / 50000) * 10

    # 百度为主（数据量大），B站为辅
    crowd_heat = max(0.0, min(10.0, max(bd_score, bl_score) * 0.7 + min(bd_score, bl_score) * 0.3))
    return round(crowd_heat, 1)


def crowd_verify(items: list[dict]) -> list[dict]:
    """主入口：对精选新闻做人群验证，注入 crowd_heat"""
    if not items:
        return items

    print("  拉取百度/B站热搜... ", end="", flush=True)
    bd_items, bl_items = fetch_trending()
    print(f"百度{len(bd_items)}条, B站{len(bl_items)}条")

    hot_count = 0
    for item in items:
        crowd_heat = calculate_crowd_heat(item.get("title", ""), bd_items, bl_items)
        scores = item.setdefault("scores", {})
        scores["crowd_heat"] = crowd_heat
        if crowd_heat >= 2:
            hot_count += 1

    print(f"  人群验证完成: {hot_count}/{len(items)} 条与热搜相关")
    return items


if __name__ == "__main__":
    # 独立测试
    test_items = [
        {"title": "DeepSeek拟募资最高500亿，腾讯阿里或参投"},
        {"title": "OpenAI发布GPT-5，多模态能力大幅提升"},
        {"title": "某明星离婚案引发网友热议"},
    ]
    print("=" * 50)
    print("人群验证独立测试")
    print("=" * 50)
    bd, bl = fetch_trending()
    print(f"百度热搜 {len(bd)}条  |  B站热搜 {len(bl)}条\n")
    for item in test_items:
        ch = calculate_crowd_heat(item["title"], bd, bl)
        badge = "🔥🔥" if ch >= 5 else ("🔥" if ch >= 2 else "  ")
        print(f"  {badge} [{ch:.1f}] {item['title']}")
    print()
    result = crowd_verify(test_items)
    for item in result:
        print(f"  crowd_heat={item['scores']['crowd_heat']} | {item['title']}")
