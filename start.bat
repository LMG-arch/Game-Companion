@echo off
chcp 65001 >nul
echo 启动游戏伴侣...
cd /d "%~dp0frontend"
npx electron .
