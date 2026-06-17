@echo off
REM 每日素材获取 — Windows 批处理入口
REM 可用于任务计划程序调用

cd /d "%~dp0.."
set PYTHONIOENCODING=utf-8
set PYTHONPATH=.

echo [%date% %time%] Starting daily material fetch...
python scheduler\run.py
echo [%date% %time%] Done. Exit code: %ERRORLEVEL%
