"""生成示例数据到 web/data/ —— 用于前端预览"""
import json, os
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))
os.makedirs('web/data', exist_ok=True)

now = datetime.now(BJT)

selected = {
    "updated_at": now.isoformat(),
    "total": 5,
    "items": [
        {
            "id": "demo-1",
            "title": "OpenAI 发布 GPT-5.5 Instant，推理速度提升3倍，API价格下调60%",
            "source_name": "OpenAI 官方博客",
            "source_tier": "T1",
            "link": "#",
            "summary": "OpenAI正式发布了GPT-5.5 Instant模型，在保持GPT-5.5同等智能水平的同时，推理速度提升3倍，API价格下调60%。该模型特别适合需要低延迟的场景，如实时对话、代码补全等。",
            "published": now.isoformat(),
            "quality_score": 9.2,
            "scores": {"importance": 9, "timeliness": 10, "actionability": 9, "scarcity": 8, "virality": 9},
            "topics": [
                {"tag": "tutorial", "title": "GPT-5.5 Instant实测：速度到底有多快？", "angle": "上手实测，对比新旧模型速度差异", "difficulty": "入门"},
                {"tag": "money", "title": "GPT-5.5降价60%，接入AI的成本低了多少？", "angle": "算一笔账，讲商业机会", "difficulty": "进阶"},
            ],
        },
        {
            "id": "demo-2",
            "title": "DeepSeek 开源 DeepSeek-V4 技术报告，MoE架构细节首次披露",
            "source_name": "Hugging Face 博客",
            "source_tier": "T1",
            "link": "#",
            "summary": "DeepSeek发布了V4模型的技术报告，详细披露了其MoE（混合专家）架构的设计细节。报告显示V4使用了256个专家中激活8个的稀疏架构，在训练效率和推理成本上达到了新的平衡。",
            "published": now.isoformat(),
            "quality_score": 8.7,
            "scores": {"importance": 9, "timeliness": 8, "actionability": 7, "scarcity": 9, "virality": 8},
            "topics": [
                {"tag": "science", "title": "什么是MoE架构？DeepSeek V4为什么这么快？", "angle": "用通俗语言解释MoE原理", "difficulty": "进阶"},
                {"tag": "hotspot", "title": "DeepSeek V4开源意味着什么？", "angle": "评论开源对AI行业的影响", "difficulty": "入门"},
            ],
        },
        {
            "id": "demo-3",
            "title": "Claude Code 发布 Windows 原生版本，支持VS Code深度集成",
            "source_name": "Anthropic 官方博客",
            "source_tier": "T1",
            "link": "#",
            "summary": "Anthropic发布了Claude Code的Windows原生版本，支持VS Code和JetBrains IDE的深度集成。新增了Worktree隔离、多Agent协作等企业级功能。",
            "published": now.isoformat(),
            "quality_score": 8.1,
            "scores": {"importance": 7, "timeliness": 9, "actionability": 8, "scarcity": 7, "virality": 8},
            "topics": [
                {"tag": "tutorial", "title": "Claude Code Windows安装教程，5分钟上手", "angle": "Windows用户入门指南", "difficulty": "入门"},
                {"tag": "product", "title": "Claude Code vs GitHub Copilot，哪个更好用？", "angle": "横向对比评测", "difficulty": "进阶"},
            ],
        },
        {
            "id": "demo-4",
            "title": "AI视频生成赛道大洗牌：Runway发布Gen-4，可灵推出2.0版本",
            "source_name": "36氪",
            "source_tier": "T2",
            "link": "#",
            "summary": "AI视频生成领域迎来密集更新。Runway发布了Gen-4模型，支持长达30秒的连贯视频生成；快手可灵推出了2.0版本，在画面质量和运动流畅度上有显著提升。",
            "published": now.isoformat(),
            "quality_score": 7.5,
            "scores": {"importance": 7, "timeliness": 8, "actionability": 7, "scarcity": 6, "virality": 8},
            "topics": [
                {"tag": "tutorial", "title": "2026年5月AI视频工具横评：Gen-4 vs 可灵2.0", "angle": "实测对比各工具效果", "difficulty": "入门"},
                {"tag": "money", "title": "AI视频工具这么强，普通人怎么靠它赚钱？", "angle": "分析AI视频商业机会", "difficulty": "入门"},
            ],
        },
        {
            "id": "demo-5",
            "title": "Apple Intelligence 重大更新：Siri接入大模型，支持跨应用自动化",
            "source_name": "苹果机器学习研究",
            "source_tier": "T1",
            "link": "#",
            "summary": "苹果推送iOS 19更新，Siri全面接入大语言模型，支持跨应用自动化操作。用户可以用自然语言让Siri完成\"帮我把昨天的会议纪要发给张三并设置提醒\"等复杂任务。",
            "published": now.isoformat(),
            "quality_score": 8.3,
            "scores": {"importance": 8, "timeliness": 9, "actionability": 8, "scarcity": 7, "virality": 9},
            "topics": [
                {"tag": "product", "title": "iOS 19 Siri深度体验：苹果AI终于能用了？", "angle": "上手体验，讲新功能实际表现", "difficulty": "入门"},
                {"tag": "hotspot", "title": "苹果AI追上来了吗？Siri新版实测对比", "angle": "蹭苹果热度做对比内容", "difficulty": "入门"},
            ],
        },
    ],
}

report = {
    "title": f"AI日报 - {now.strftime('%Y年%m月%d日')}",
    "generated_at": now.isoformat(),
    "source_count": 20,
    "summary": "今日AI圈以模型迭代和产品更新为主旋律，OpenAI、DeepSeek同日释放重要更新，视频生成赛道竞争白热化。整体趋势：模型能力持续提升，同时价格不断下探，AI应用落地窗口正在加速打开。",
    "sections": [
        {
            "name": "模型/产品发布",
            "items": [
                {"title": "OpenAI 发布 GPT-5.5 Instant，推理速度提升3倍", "summary": "API价格下调60%，低延迟场景首选"},
                {"title": "DeepSeek 开源 DeepSeek-V4 技术报告", "summary": "MoE架构细节首次公开，256专家中激活8个"},
                {"title": "AI视频生成赛道大洗牌：Runway Gen-4 vs 可灵2.0", "summary": "视频生成迎来新突破，多家厂商同日更新"},
            ],
        },
        {
            "name": "行业动态",
            "items": [
                {"title": "Claude Code 发布 Windows 原生版本", "summary": "支持VS Code和JetBrains深度集成"},
                {"title": "Apple Intelligence 重大更新：Siri接入大模型", "summary": "iOS 19推送，Siri支持跨应用自动化"},
            ],
        },
        {
            "name": "论文/研究",
            "items": [
                {"title": "DeepSeek V4技术报告公布MoE架构细节", "summary": "稀疏激活策略在效率与性能间取得新平衡"},
            ],
        },
        {
            "name": "技巧与观点",
            "items": [
                {"title": "AI视频生成时代，内容创作者还需要学剪辑吗？", "summary": "工具进化不等于技能贬值，基础审美和叙事能力反而更重要"},
            ],
        },
    ],
}

with open("web/data/selected_news.json", "w", encoding="utf-8") as f:
    json.dump(selected, f, ensure_ascii=False, indent=2)
with open("web/data/daily_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("中文示例数据已生成: web/data/")
