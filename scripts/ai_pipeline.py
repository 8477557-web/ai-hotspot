"""
AI处理管线 — 批量预筛 → 批量评分 → 批量选题 → 日报摘要
DeepSeek API, compatible with OpenAI SDK
"""
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from openai import OpenAI

sys.path.insert(0, os.path.dirname(__file__))
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL,
    DEEPSEEK_PRE_FILTER_MODEL, DEEPSEEK_SCORE_MODEL,
    RAW_FILE, SELECTED_FILE, DAILY_FILE,
    WEB_DATA_DIR, WEB_SELECTED_FILE, WEB_DAILY_FILE,
    TOP_N_SELECTED, TOPIC_TAGS, DATA_DIR,
    calc_quality_score,
)

BJT = timezone(timedelta(hours=8))
BATCH_PRE_FILTER = 10   # 预筛每批10条
BATCH_SCORE = 5          # 评分每批5条
BATCH_TOPIC = 5          # 选题每批5条

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


def extract_json(text: str) -> str:
    """从AI回复中提取第一个有效JSON对象"""
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    # 尝试匹配数组或对象
    m = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
    return m.group(0) if m else text


def call_deepseek(prompt: str, model: str = None, temperature: float = 0.3, max_tokens: int = 2000) -> str:
    """调用DeepSeek，带重试"""
    model = model or DEEPSEEK_SCORE_MODEL
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return r.choices[0].message.content
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                raise e


def parallel_process(batches, process_fn, max_workers=5):
    """多线程并行处理batch，返回保持原始顺序的结果列表"""
    futures = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for idx, batch in enumerate(batches):
            futures[executor.submit(process_fn, batch)] = idx
        results = [None] * len(batches)
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                results[idx] = e
    return results


# ══════════════════════════════════════════════════════════════
# 第一步：批量预筛
# ══════════════════════════════════════════════════════════════

BATCH_PRE_FILTER_PROMPT = """Judge whether each news item below is AI-related. Reply ONLY a JSON array:
[{{"id": 0, "related": true, "reason": "short"}}, ...]

Rules: LLM/AI model news, AI product launches, AI research/papers, AI policy/ethics -> related.
Pure stock/crypto/metaverse/general software (no AI) -> not related.

News items:
{items_json}"""


def pre_filter(items: list[dict]) -> list[dict]:
    """批量+并行预筛"""
    batches = [items[i:i+BATCH_PRE_FILTER] for i in range(0, len(items), BATCH_PRE_FILTER)]
    print(f"  {len(items)} items in {len(batches)} batches, parallel exec...")

    def process_batch(batch):
        payload = [{"id": j, "title": it["title"], "summary": it.get("summary", "")[:300]} for j, it in enumerate(batch)]
        prompt = BATCH_PRE_FILTER_PROMPT.format(items_json=json.dumps(payload, ensure_ascii=False))
        raw = call_deepseek(prompt, model=DEEPSEEK_PRE_FILTER_MODEL, temperature=0.2)
        raw = extract_json(raw)
        results = json.loads(raw)
        if isinstance(results, dict):
            results = [results]
        return results

    results_list = parallel_process(batches, process_batch)

    passed = []
    for batch, results in zip(batches, results_list):
        if isinstance(results, Exception):
            for it in batch:
                it["pre_filter_reason"] = "parallel_fallback"
                passed.append(it)
            continue
        try:
            for r in results:
                idx = r.get("id", -1)
                if 0 <= idx < len(batch):
                    batch[idx]["pre_filter_reason"] = r.get("reason", "")
                    if r.get("related", True):
                        passed.append(batch[idx])
        except Exception:
            for it in batch:
                it["pre_filter_reason"] = "batch_fallback"
                passed.append(it)

    print(f"  Pre-filter: {len(items)} -> {len(passed)} (dropped {len(items)-len(passed)})")
    return passed


# ══════════════════════════════════════════════════════════════
# 第二步：批量五维度评分
# ══════════════════════════════════════════════════════════════

BATCH_SCORE_PROMPT = """Score each news item below on 5 dimensions (1-10). Reply ONLY a JSON array:
[{{"id": 0, "importance": 7, "timeliness": 8, "actionability": 6, "scarcity": 5, "virality": 7}}, ...]

Dimensions:
- importance: impact on AI industry (10=landmark event)
- timeliness: how recently it happened, urgency
- actionability: suitable for content creation / discussion
- scarcity: uniqueness of this information
- virality: potential to spread / go viral

News items:
{items_json}"""


def score_items(items: list[dict]) -> list[dict]:
    """批量+并行评分"""
    batches = [items[i:i+BATCH_SCORE] for i in range(0, len(items), BATCH_SCORE)]
    print(f"  {len(items)} items in {len(batches)} batches, parallel exec...")

    def process_batch(batch):
        payload = [
            {"id": j, "title": it["title"], "source": it.get("source_name", ""),
             "tier": it.get("source_tier", ""), "summary": it.get("summary", "")[:400]}
            for j, it in enumerate(batch)
        ]
        prompt = BATCH_SCORE_PROMPT.format(items_json=json.dumps(payload, ensure_ascii=False))
        raw = call_deepseek(prompt, model=DEEPSEEK_SCORE_MODEL, temperature=0.2)
        raw = extract_json(raw)
        results = json.loads(raw)
        if isinstance(results, dict):
            results = [results]
        return results

    results_list = parallel_process(batches, process_batch)

    for batch, results in zip(batches, results_list):
        if isinstance(results, Exception):
            for it in batch:
                it["scores"] = {"importance": 5, "timeliness": 5, "actionability": 5, "scarcity": 5, "virality": 5}
                it["quality_score"] = calc_quality_score(it)
            continue
        try:
            for r in results:
                idx = r.get("id", -1)
                if 0 <= idx < len(batch):
                    batch[idx]["scores"] = {
                        "importance": int(r.get("importance", 5)),
                        "timeliness": int(r.get("timeliness", 5)),
                        "actionability": int(r.get("actionability", 5)),
                        "scarcity": int(r.get("scarcity", 5)),
                        "virality": int(r.get("virality", 5)),
                    }
                    batch[idx]["quality_score"] = calc_quality_score(batch[idx])
        except Exception:
            for it in batch:
                it["scores"] = {"importance": 5, "timeliness": 5, "actionability": 5, "scarcity": 5, "virality": 5}
                it["quality_score"] = calc_quality_score(it)

    return items


# ══════════════════════════════════════════════════════════════
# 第三步：批量选题推荐
# ══════════════════════════════════════════════════════════════

BATCH_TOPIC_PROMPT = """You are an AI content strategist. For each news item below, suggest 1-2 content angles for short videos / articles. Reply ONLY a JSON array:
[{{"id": 0, "topics": [{{"tag": "tutorial", "title": "title in Chinese", "angle": "angle in Chinese", "difficulty": "入门"}}]}}, ...]

News items:
{items_json}"""


def generate_topics(items: list[dict]) -> list[dict]:
    """批量+并选题推荐"""
    batches = [items[i:i+BATCH_TOPIC] for i in range(0, len(items), BATCH_TOPIC)]
    print(f"  {len(items)} items in {len(batches)} batches, parallel exec...")

    def process_batch(batch):
        payload = [{"id": j, "title": it["title"], "summary": it.get("summary", "")[:300]} for j, it in enumerate(batch)]
        prompt = BATCH_TOPIC_PROMPT.format(items_json=json.dumps(payload, ensure_ascii=False))
        raw = call_deepseek(prompt, model=DEEPSEEK_SCORE_MODEL, temperature=0.5, max_tokens=3000)
        raw = extract_json(raw)
        results = json.loads(raw)
        if isinstance(results, dict):
            results = [results]
        return results

    results_list = parallel_process(batches, process_batch)

    for batch, results in zip(batches, results_list):
        if isinstance(results, Exception):
            for it in batch:
                it["topics"] = []
            continue
        try:
            for r in results:
                idx = r.get("id", -1)
                if 0 <= idx < len(batch):
                    batch[idx]["topics"] = r.get("topics", [])
        except Exception:
            for it in batch:
                it["topics"] = []

    return items


# ══════════════════════════════════════════════════════════════
# 第四步：日报摘要（单次调用，不变）
# ══════════════════════════════════════════════════════════════

DAILY_PROMPT = """你是一个AI日报编辑。根据以下精选新闻列表，生成一份简洁的AI日报。

要求：
1. 分成4个版块：模型/产品发布、行业动态、论文/研究、技巧与观点
2. 每个版块选最重要的2-4条，用一句话概括并附带原始标题
3. 结尾写一句总结(50字以内)，概括今日AI圈的整体趋势
4. 输出JSON(必须严格JSON格式，不要任何额外文字)：
{{
  "title": "AI日报 - 2026年X月X日",
  "sections": [
    {{"name": "模型/产品发布", "items": [{{"title": "...", "summary": "..."}}]}},
    {{"name": "行业动态", "items": [...]}},
    {{"name": "论文/研究", "items": [...]}},
    {{"name": "技巧与观点", "items": [...]}}
  ],
  "summary": "今日总结一句话"
}}

新闻数据：
{news_json}"""


def generate_daily_report(items: list[dict]) -> dict:
    print("  Generating daily report...", end=" ", flush=True)

    simplified = [{"title": it.get("title"), "source": it.get("source_name"),
                   "quality_score": it.get("quality_score")} for it in items]

    prompt = DAILY_PROMPT.format(news_json=json.dumps(simplified, ensure_ascii=False, indent=2))

    try:
        raw = call_deepseek(prompt, model=DEEPSEEK_SCORE_MODEL, temperature=0.5, max_tokens=3000)
        raw = extract_json(raw)
        report = json.loads(raw)
        # Override title with correct date
        report["title"] = f"AI日报 - {datetime.now(BJT).strftime('%Y年%m月%d日')}"
        report["generated_at"] = datetime.now(BJT).isoformat()
        report["source_count"] = len(items)
        print("OK")
        return report
    except Exception as e:
        print(f"-> fallback: {e}")
        return {
            "title": f"AI日报 - {datetime.now(BJT).strftime('%Y年%m月%d日')}",
            "sections": [], "summary": "日报生成失败",
            "generated_at": datetime.now(BJT).isoformat(), "source_count": len(items),
        }


# ══════════════════════════════════════════════════════════════
# 第五步：社交验证（可选，调用 last30days 引擎）
# ══════════════════════════════════════════════════════════════

def social_verify(selected: list[dict], top_n: int = 5) -> list[dict]:
    """对精选新闻前 top_n 条执行社区讨论搜索，增强评分"""
    try:
        from social_verify import verify_topics, add_social_to_item
    except ImportError:
        print("  social_verify module not available, skipping")
        return selected

    print(f"\n  Social Verify: top {top_n} items")
    topics = [item["title"] for item in selected[:top_n]]
    results = verify_topics(topics, depth="quick")

    success_count = sum(1 for r in results if r["success"])
    total_items = sum(r["metrics"]["total_items"] for r in results)
    print(f"  Social Verify done: {success_count}/{len(results)} successful, {total_items} community items found")

    for i, result in enumerate(results):
        if i < len(selected) and result["success"]:
            selected[i] = add_social_to_item(selected[i], result)

    # 按更新后的 quality_score 重排
    selected.sort(key=lambda x: x["quality_score"], reverse=True)
    return selected


# ══════════════════════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════════════════════

def main(enable_social: bool = False, social_top_n: int = 5, enable_crowd: bool = False):
    if not DEEPSEEK_API_KEY:
        print("ERROR: DEEPSEEK_API_KEY not set")
        return

    print("=" * 50)
    print(f"AI Pipeline Start: {datetime.now(BJT).strftime('%Y-%m-%d %H:%M:%S')}")
    if enable_crowd:
        print(f"[Crowd Verify: ENABLED (Baidu/Bilibili)]")
    if enable_social:
        print(f"[Social Verify: ENABLED (top {social_top_n})]")
    print("=" * 50)

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    items = raw["items"]
    print(f"Loaded: {len(items)} raw items\n")

    # Step 1: Pre-filter
    print("Step 1: Pre-filter (batch)")
    items = pre_filter(items)

    # Step 2: Scoring
    print(f"\nStep 2: Scoring (batch, {len(items)} items)")
    items = score_items(items)

    # Step 3: Sort & select top N
    items.sort(key=lambda x: x["quality_score"], reverse=True)
    selected = items[:TOP_N_SELECTED]
    print(f"\nStep 3: Sort & select top {TOP_N_SELECTED} (scores: {selected[0]['quality_score']:.1f} - {selected[-1]['quality_score']:.1f})")

    # Step 3.5: Crowd verify (optional — Baidu/Bilibili trending match)
    if enable_crowd:
        print(f"\nStep 3.5: Crowd verification")
        try:
            from crowd_verify import crowd_verify
            selected = crowd_verify(selected)
            items[:len(selected)] = selected
            selected.sort(key=lambda x: x["quality_score"], reverse=True)
        except ImportError:
            print("  crowd_verify module not available, skipping")

    # Step 4: Topic generation
    print(f"\nStep 4: Topic suggestions (batch)")
    selected = generate_topics(selected)

    # Step 5: Social verify (optional)
    if enable_social:
        print(f"\nStep 5: Social verification")
        selected = social_verify(selected, top_n=social_top_n)

    # Step 6: Daily report
    step_label = "6" if enable_social else "5"
    print(f"\nStep {step_label}: Daily report")
    report = generate_daily_report(selected)

    # Save
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(WEB_DATA_DIR, exist_ok=True)
    output = {"updated_at": datetime.now(BJT).isoformat(), "total": len(selected), "items": selected}

    for path in (SELECTED_FILE, WEB_SELECTED_FILE):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
    for path in (DAILY_FILE, WEB_DAILY_FILE):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {DATA_DIR}/ and {WEB_DATA_DIR}/")
    print(f"\nDone! {len(items)} filtered -> {len(selected)} selected -> report generated")


if __name__ == "__main__":
    # 直接调试入口（正式使用请通过 main.py --social-verify）
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--social-verify", action="store_true")
    parser.add_argument("--social-top-n", type=int, default=5)
    args = parser.parse_args()
    main(enable_social=args.social_verify, social_top_n=args.social_top_n)
