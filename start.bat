@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
echo Starting Game Companion...
cd /d "%~dp0frontend"
npx electron .
