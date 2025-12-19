@echo off
echo ====================================
echo LINE Bot 啟動腳本
echo ====================================
echo.

REM 設定專案路徑（請修改成你的實際路徑）
set PROJECT_PATH=
set REDIS_PATH  =

echo [1/4] 啟動 Redis Server...
start "Redis Server" cmd /k "cd /d %REDIS_PATH% && redis-server.exe"
timeout /t 3 /nobreak >nul

echo [2/4] 啟動 Celery Worker...
start "Celery Worker" cmd /k "cd /d %PROJECT_PATH% && conda activate llm_env && celery -A line_bot.tasks worker --loglevel=info --pool=solo"
timeout /t 5 /nobreak >nul

echo [3/4] 啟動 Flask Bot...
start "Flask Bot" cmd /k "cd /d %PROJECT_PATH% && conda activate llm_env && python -m line_bot.bot"
timeout /t 3 /nobreak >nul

echo [4/4] 啟動 ngrok...
start "ngrok" cmd /k "ngrok http 5000"

echo.
echo ====================================
echo 所有服務已啟動！
echo ====================================
echo.
echo 請注意：
echo 1. 複製 ngrok 視窗中的 https URL
echo 2. 更新 LINE Webhook URL 為: https://YOUR_URL/callback
echo 3. 更新 line_bot/tasks.py 中的 download_url
echo.
pause