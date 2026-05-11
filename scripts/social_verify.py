"""
社交舆情验证 — 调用 last30days 引擎获取 Reddit/HN/GitHub 社区讨论数据
作为 ai-hotspot AI 管线的可选增强层
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# last30days 引擎路径
_SCRIPT_DIR = Path(__file__).parent.resolve()
_ENGINE_PATH = _SCRIPT_DIR.parent.parent / "skills" / "last30days" / "skills" / "last30days" / "scripts" / "last30days.py"

# 每个话题最长等待时间
_TIMEOUT_SECONDS = 120
# 最小引擎间隔（避免 API 限流）。verify_topics 串行调用，天然线程安全。
_MIN_INTERVAL = 5.0
_last_call = 0.0


def _call_engine(topic: str, depth: str = "quick") -> dict:
    """
    调用 last30days 引擎，返回结构化 JSON 报告。
    失败或超时返回空 dict。
    """
    global _last_call

    if not _ENGINE_PATH.exists():
        print(f"  [social_verify] 引擎未安装: {_ENGINE_PATH}")
        return {}

    # 限流
    elapsed = time.time() - _last_call
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(_ENGINE_PATH),
                topic,
                "--depth", depth,
                "--emit", "json",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_TIMEOUT_SECONDS,
            cwd=str(_ENGINE_PATH.parent),
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        _last_call = time.time()

        # stderr 包含进度日志，忽略
        if not result.stdout.strip():
            print(f"  [social_verify] 引擎无输出: {topic[:60]}...")
            return {}

        data = json.loads(result.stdout)
        return data

    except subprocess.TimeoutExpired:
        print(f"  [social_verify] 超时: {topic[:60]}...")
        _last_call = time.time()
        return {}
    except json.JSONDecodeError:
        print(f"  [social_verify] JSON 解析失败: {topic[:60]}...")
        _last_call = time.time()
        return {}
    except Exception as e:
        print(f"  [social_verify] 引擎异常: {e}")
        _last_call = time.time()
        return {}


def extract_metrics(engine_output: dict) -> dict:
    """
    从 last30days JSON 输出中提取关键社交指标。
    返回格式与 ai-hotspot 评分管线兼容。
    """
    if not engine_output:
        return _empty_metrics()

    items_by_source = engine_output.get("items_by_source", {})
    clusters = engine_output.get("clusters", [])
    errors = engine_output.get("errors_by_source", {})

    # 各源统计
    source_stats = {}
    total_items = 0
    total_engagement = 0
    for src, items in items_by_source.items():
        count = len(items)
        total_items += count
        engagement = 0
        for item in items:
            eng = item.get("engagement", {})
            engagement += sum(eng.values())
        total_engagement += engagement
        source_stats[src] = {"count": count, "engagement": engagement, "error": errors.get(src)}

    # 精选讨论（取前 5 个聚类代表）
    discussions = []
    for cluster in clusters[:5]:
        score = cluster.get("score", 0)
        if score <= 0:
            continue
        reps = cluster.get("representative_ids", [])
        discussions.append({
            "title": cluster.get("title", ""),
            "sources": cluster.get("sources", []),
            "score": round(score, 1),
            "url": reps[0] if reps else "",
        })

    # 热度指标（0-10 分）
    social_heat = min(10.0, round((total_items * 0.5 + total_engagement * 0.1) / 3, 1))

    return {
        "total_items": total_items,
        "total_engagement": total_engagement,
        "social_heat": social_heat,
        "source_stats": source_stats,
        "top_discussions": discussions,
        "available_sources": [s for s in source_stats if not source_stats[s].get("error")],
        "errors": errors,
        "generated_at": engine_output.get("generated_at", ""),
    }


def _empty_metrics() -> dict:
    return {
        "total_items": 0,
        "total_engagement": 0,
        "social_heat": 0,
        "source_stats": {},
        "top_discussions": [],
        "available_sources": [],
        "errors": {},
        "generated_at": "",
    }


def verify_topic(topic: str, depth: str = "quick") -> dict:
    """
    对单个话题进行社交验证。
    返回:
    {
        "topic": str,
        "metrics": {...},
        "success": bool,
        "error": str or None,
    }
    """
    print(f"  [social_verify] 搜索: {topic[:80]}...", end=" ", flush=True)
    output = _call_engine(topic, depth)
    if not output:
        print("无结果")
        return {"topic": topic, "metrics": _empty_metrics(), "success": False, "error": "no_output"}

    metrics = extract_metrics(output)
    print(f"OK ({metrics['total_items']}项, {len(metrics['available_sources'])}源)")
    return {"topic": topic, "metrics": metrics, "success": True, "error": None}


def verify_topics(topics: list[str], depth: str = "quick") -> list[dict]:
    """
    批量验证多个话题（串行，有限流）。
    每个话题一次引擎调用，约 60-120 秒。
    """
    results = []
    for i, topic in enumerate(topics):
        print(f"  [{i+1}/{len(topics)}]", end="")
        results.append(verify_topic(topic, depth))
    return results


def add_social_to_item(item: dict, verify_result: dict) -> dict:
    """
    将社交验证结果合并到 ai-hotspot 条目的 score 和 topics 中。
    复用 ai_pipeline.calc_quality_score 避免公式重复。
    """
    metrics = verify_result.get("metrics", _empty_metrics())
    item["social_metrics"] = metrics
    existing_scores = item.get("scores", {})
    existing_scores["social_heat"] = metrics["social_heat"]
    item["scores"] = existing_scores
    # 复用 config 的共享评分公式（含 social_heat 第六维度）
    from config import calc_quality_score
    item["quality_score"] = calc_quality_score(item)
    return item


def main():
    """命令行测试入口"""
    if len(sys.argv) < 2:
        print("usage: python social_verify.py <topic> [topic2] ...")
        return

    topics = [" ".join(sys.argv[1:])]
    results = verify_topics(topics)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
