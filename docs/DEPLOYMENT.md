# LINE Bot 部署指南

## 環境需求

- Python 3.10+
- Redis Server
- ngrok（需註冊帳號）
- LINE Developer Account

---

## 安裝步驟

### 1. 安裝 Python 依賴套件
```bash
conda create -n llm_env python=3.10
conda activate llm_env
pip install -r requirements.txt
```

### 2. 安裝 Redis

**方法 A：下載編譯好的版本（推薦）**

1. 下載：https://github.com/tporadowski/redis/releases
2. 下載 `Redis-x64-5.0.14.1.zip`
3. 解壓到 `C:\Tools\Redis-x64-5.0.14.1`

**方法 B：使用 WSL**
```bash
wsl
sudo apt-get install redis-server
```

### 3. 安裝 ngrok

1. 下載：https://ngrok.com/download
2. 註冊帳號：https://dashboard.ngrok.com/signup
3. 取得 Authtoken
4. 設定 token：
```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
```

### 4. 設定 LINE Bot

1. 前往 LINE Developers Console：https://developers.line.biz/console/
2. 建立 Messaging API Channel
3. 取得：
   - Channel Secret
   - Channel Access Token
4. 填入 `config.py`：
```python
   LINE_CHANNEL_ACCESS_TOKEN = "your_token"
   LINE_CHANNEL_SECRET = "your_secret"
```

---

## 啟動步驟

### 手動啟動（4 個視窗）

**視窗 1 - Redis：**
```bash
cd YOUR_TOOL_PATH
redis-server.exe
```

**視窗 2 - Celery Worker：**
```bash
cd YOUR_TOOL_PATH
conda activate llm_env
celery -A line_bot.tasks worker --loglevel=info --pool=solo
```

**視窗 3 - Flask Bot：**
```bash
cd YOUR_TOOL_PATH
conda activate llm_env
python -m line_bot.bot
```

**視窗 4 - ngrok：**
```bash
ngrok http 5000
```

### 自動啟動（使用腳本）
```bash
start.bat
```

---

## 設定 LINE Webhook

1. 複製 ngrok 提供的 URL（例如：`https://xxx.ngrok-free.app`）
2. 前往 LINE Developers Console → Messaging API
3. 設定 Webhook URL：`https://xxx.ngrok-free.app/callback`
4. 開啟「Use webhook」
5. 關閉「Auto-reply messages」

---

## 測試

1. 用手機 LINE 掃描 QR Code 加 Bot 為好友
2. 傳送文字或上傳檔案（.txt, .pdf, .docx, .pptx）
3. Bot 會自動處理並回傳 PDF 下載連結

---

## 常見問題

**Q: Celery 無法連接 Redis？**
A: 確認 Redis server 正在運行，看到 "Ready to accept connections"

**Q: ngrok URL 每次都不同？**
A: 免費版 ngrok 每次啟動 URL 會改變，需要更新 LINE Webhook URL 和 `tasks.py` 中的 download_url

**Q: PDF 沒有中文？**
A: 確認系統有微軟正黑體（msjh.ttc）

**Q: 下載連結 404？**
A: 檢查 `temp/outputs/` 目錄是否存在檔案

---

## 關閉服務

按照順序關閉：
1. ngrok：`Ctrl+C`
2. Flask bot：`Ctrl+C`
3. Celery worker：`Ctrl+C`
4. Redis：`Ctrl+C`