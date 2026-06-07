@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
echo Starting Game Companion...
cd /d "%~dp0"

REM 安装 Python 依赖
echo Checking Python dependencies...
pip install -r backend/requirements.txt -q

REM 启动 Electron
cd /d "%~dp0frontend"
npx electron .
