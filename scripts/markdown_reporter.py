"""
Markdown 日报生成器 — 将 AI 管线输出转为 Obsidian 标准 Markdown
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from config import (
    SELECTED_FILE, DAILY_FILE,
    OBSIDIAN_AI_REPORT_DIR, TOPIC_TAGS,
)

BJT = timezone(timedelta(hours=8))

# 选题标签 emoji 映射
TAG_EMOJI = {t["id"]: t["emoji"] for t in TOPIC_TAGS}
TAG_LABEL = {t["id"]: t["label"] for t in TOPIC_TAGS}


def generate_markdown(selected_items: list[dict] = None, report: dict = None) -> str | None:
    """
    从 JSON 数据生成 Obsidian Markdown 日报。
    优先使用传入参数，其次从文件读取。
    返回生成的文件路径，失败返回 None。
    """
    # 如果未传入数据，从文件读取
    if selected_items is None:
        try:
            with open(SELECTED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            selected_items = data.get("items", [])
        except (FileNotFoundError, json.JSONDecodeError):
            print("  [markdown] selected_news.json not found or invalid")
            return None

    if report is None:
        try:
            with open(DAILY_FILE, "r", encoding="utf-8") as f:
                report = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print("  [markdown] daily_report.json not found, generating with basic structure")
            report = {
                "title": f"AI日报 - {datetime.now(BJT).strftime('%Y年%m月%d日')}",
                "summary": "日报数据暂缺",
                "sections": [],
            }

    # 确保输出目录存在
    os.makedirs(OBSIDIAN_AI_REPORT_DIR, exist_ok=True)

    today = datetime.now(BJT)
    date_str = today.strftime("%Y-%m-%d")
    date_display = today.strftime("%Y年%m月%d日")

    md = _build_markdown(selected_items, report, date_str, date_display)

    filepath = os.path.join(OBSIDIAN_AI_REPORT_DIR, f"{date_str}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"  [markdown] Generated: {filepath}")
    return filepath


def _build_markdown(items: list[dict], report: dict, date_str: str, date_display: str) -> str:
    """构建完整的 Markdown 内容"""
    lines = []

    # ── Frontmatter ──
    lines.append("---")
    lines.append(f'title: "AI日报 - {date_display}"')
    lines.append("tags: [AI日报, 选题]")
    lines.append(f"created: {date_str}")
    lines.append(f"updated: {date_str}")
    lines.append("---")
    lines.append("")
    lines.append(f"# AI日报 - {date_display}")
    lines.append("")

    # ── 趋势总结 ──
    summary = report.get("summary", "").strip()
    if summary and summary != "日报生成失败":
        lines.append(f"> {summary}")
        lines.append("")

    # ── 选题推荐（按评分排序） ──
    items_with_topics = [it for it in items if it.get("topics")]
    if items_with_topics:
        lines.append("## 🔥 选题推荐")
        lines.append("")
        for i, item in enumerate(items_with_topics[:15], 1):
            title = item.get("title", "无标题")
            link = item.get("link", "")
            source = item.get("source_name", "")
            score = item.get("quality_score", 0)
            crowd_heat = item.get("scores", {}).get("crowd_heat", 0)

            extras = []
            if score:
                extras.append(f"评分 {score}")
            if crowd_heat >= 2:
                extras.append(f"🔥 热搜 {crowd_heat}")
            extra_str = " · ".join(extras) if extras else ""

            lines.append(f"### {i}. {title}")
            if extra_str:
                lines.append(f"- **{extra_str}** | 来源：{source}")
            else:
                lines.append(f"- 来源：{source}")

            for topic in item.get("topics", [])[:2]:
                tag = topic.get("tag", "")
                emoji = TAG_EMOJI.get(tag, "📌")
                label = TAG_LABEL.get(tag, tag)
                topic_title = topic.get("title", "")
                angle = topic.get("angle", "")
                difficulty = topic.get("difficulty", "入门")
                lines.append(f"  - {emoji} **[{label}] {topic_title}**")
                lines.append(f"    - 角度：{angle}")
                lines.append(f"    - 难度：{difficulty}")

            if link:
                lines.append(f"- 原文：[{link}]({link})")
            lines.append("")

    # ── 日报摘要（4版块） ──
    sections = report.get("sections", [])
    if sections:
        lines.append("## 📊 今日动态")
        lines.append("")
        section_emoji = {
            "模型/产品发布": "🚀",
            "行业动态": "📈",
            "论文/研究": "📄",
            "技巧与观点": "💡",
        }
        for sec in sections:
            name = sec.get("name", "")
            emoji = section_emoji.get(name, "📌")
            lines.append(f"### {emoji} {name}")
            lines.append("")
            for it in sec.get("items", []):
                t = it.get("title", "")
                s = it.get("summary", "")
                if s:
                    lines.append(f"- **{t}** — {s}")
                else:
                    lines.append(f"- **{t}**")
            lines.append("")

    # ── 完整新闻清单（表格） ──
    if items:
        lines.append("## 📋 今日精选清单")
        lines.append("")
        lines.append("| 评分 | 标题 | 来源 | 选题类型 |")
        lines.append("|------|------|------|---------|")
        for item in items:
            score = item.get("quality_score", 0)
            title = item.get("title", "").replace("|", "\\|")
            source = item.get("source_name", "")
            tags = ", ".join(
                TAG_EMOJI.get(t.get("tag", ""), "") + TAG_LABEL.get(t.get("tag", ""), t.get("tag", ""))
                for t in item.get("topics", [])[:2]
            ) or "—"
            lines.append(f"| {score} | {title} | {source} | {tags} |")
        lines.append("")

    # ── 人群热度关键词 ──
    hot_keywords = []
    for item in items:
        ch = item.get("scores", {}).get("crowd_heat", 0)
        if ch >= 5:
            hot_keywords.append(item.get("title", ""))
    if hot_keywords:
        lines.append("## 🔥 人群热度信号")
        lines.append("")
        for kw in hot_keywords[:8]:
            lines.append(f"- 🔥 {kw}")
        lines.append("")

    # ── 页脚 ──
    lines.append("---")
    lines.append(f"*由 AI选题助手 自动生成 · {datetime.now(BJT).strftime('%Y-%m-%d %H:%M')} 北京时间*")

    return "\n".join(lines)


if __name__ == "__main__":
    # 独立运行：从已有 JSON 生成 Markdown
    path = generate_markdown()
    if path:
        print(f"Done: {path}")
    else:
        print("Failed to generate markdown report")
