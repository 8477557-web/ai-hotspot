"""
AI选题助手 — 主入口（个人版）
用法:
    python scripts/main.py                     # 完整管线: 抓取+AI处理
    python scripts/main.py --fetch-only        # 仅抓取RSS
    python scripts/main.py --ai-only           # 仅AI处理(使用已有raw数据)
    python scripts/main.py --no-crowd          # 关闭人群验证
    python scripts/main.py --no-markdown       # 不输出Markdown到Obsidian
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(__file__))


def check_env():
    """检查环境变量"""
    missing = []
    if not os.getenv("DEEPSEEK_API_KEY"):
        missing.append("DEEPSEEK_API_KEY")
    if missing:
        print("❌ 缺少环境变量，请先设置：")
        for m in missing:
            print(f"   $env:{m}='sk-xxx'   # PowerShell")
            print(f"   export {m}='sk-xxx'  # Bash")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="AI选题助手（个人版）")
    parser.add_argument("--fetch-only", action="store_true", help="仅抓取RSS")
    parser.add_argument("--ai-only", action="store_true", help="仅AI处理")
    parser.add_argument("--no-crowd", action="store_true", help="关闭人群验证（百度/B站热搜匹配）")
    parser.add_argument("--no-markdown", action="store_true", help="不输出Markdown到Obsidian")
    args = parser.parse_args()

    do_fetch = not args.ai_only
    do_ai = not args.fetch_only

    # 第一步：爬虫
    if do_fetch:
        from fetch_news import main as fetch_main
        fetch_main()

    # 第二步：AI处理
    if do_ai:
        if not check_env():
            return
        from ai_pipeline import main as ai_main
        ai_main(enable_crowd=not args.no_crowd,
                enable_markdown=not args.no_markdown)


if __name__ == "__main__":
    main()
