@echo off
chcp 65001 >nul
echo ================================
echo   AI选题助手 - 生成本地日报
echo ================================
echo.

cd /d "F:\claude code\ai-hotspot"

echo [1/2] 拉取最新数据...
git pull origin main

echo.
echo [2/2] 生成 Markdown 日报...
python scripts\markdown_reporter.py

echo.
echo ================================
echo   完成！在 Obsidian 中查看日报
echo ================================
pause
