# Multi-Agent System Framework
本專案開發過程中使用 Claude (Anthropic) 作為技術諮詢和部分程式碼審查工具!!

此專案是基於 LangGraph 的多代理系統框架,提供可重用的基礎架構以提供快速開發新的 agent。

## 專案功能

### 核心功能：文本摘要與分析
- **自動意圖分類**：識別文本類型（KEYPOINT / SYNTHESIS）
- **重點提取**：壓縮資訊，提取關鍵要點
- **綜合分析**：深入解析，提供背景脈絡與應用建議

### LINE Bot 整合
- **多格式支援**：接受文字訊息和檔案上傳（.txt, .pdf, .docx, .pptx）
- **非同步處理**：使用 Celery + Redis 避免 webhook timeout
- **PDF 報告輸出**：自動生成格式化 PDF 並提供下載連結
- **24小時自動清理**：暫存檔案定期清理節省空間

---

## 專案結構與功能說明

### 核心模組

#### `agents/mycore/`
所有 agent 共用的基礎工具層。包含可重用的抽象類別,讓你專注在業務邏輯而不用處理 LangGraph 的底層細節:
- **BaseGraph**: 自動處理圖的編譯流程(節點註冊、邊緣連接)
- **BaseSchema**: 聲明式定義圖結構(狀態、節點、邊緣)
- **BaseTool**: 工具基礎類別,提供統一的錯誤追蹤
- **LLMClient**: OpenAI API 封裝,處理請求與回應格式化
- **error_formatter**: 格式化多層錯誤訊息,顯示完整錯誤路徑

#### `agents/top_controller/`
頂層控制器,負責協調所有子圖的執行:
- 接收外部輸入並初始化系統狀態
- 根據意圖分類結果決定後續流程
- 管理子圖之間的狀態映射
- 整合各個 agent 的輸出成最終結果

#### `agents/intent_agent/`
意圖分類 agent,分析輸入文本的類型

#### `agents/keypoint_agents/`
重點提取 agent,壓縮資訊並提取關鍵要點

#### `agents/synthesis_agents/`
綜合分析 agent,深入解析並提供應用建議

### LINE Bot 模組

#### `line_bot/bot.py`
Flask webhook 伺服器,處理 LINE 訊息事件:
- 接收文字訊息和檔案上傳
- 檔案格式驗證與大小限制（5MB）
- 非同步任務分發

#### `line_bot/tasks.py`
Celery 非同步任務處理:
- Agent 處理流程執行
- Markdown 轉 PDF 生成
- 下載連結推送與檔案清理排程

#### `line_bot/file_extractor.py`
多格式檔案內容提取:
- 支援 .txt, .pdf, .docx, .pptx
- 自動編碼偵測
- 錯誤處理與驗證

#### `line_bot/formatter.py`
結果格式化模組:
- JSON 轉 Markdown
- KEYPOINT 和 SYNTHESIS 模板
- 中文排版優化

### 系統入口

#### `api.py`
統一的 API 介面,封裝整個系統的調用邏輯:
- 初始化頂層控制器並編譯執行圖
- 提供 `process()` 方法處理外部請求
- 統一錯誤處理,回傳標準格式 `{"success": bool, "data": dict, "error": str}`

#### `main.py`
Agent 系統測試入口，從檔案讀取測試文本並輸出結果

### 配置檔案

#### `config.py` / `config.example`
系統配置檔案:
- OpenAI API 金鑰
- LLM 模型參數(model、top_p、temperature 等)
- LINE Bot 設定（Channel Access Token, Channel Secret）
- Redis 連線設定

**注意**: `config.py` 包含敏感資訊已加入 `.gitignore`。請複製 `config.example` 改名為 `config.py`,再填入以下資訊:
```python
# OpenAI Configuration
OPENAI_APIKEY = "your-openai-api-key"

DEFLAUT_CONFIG = {
    "model": "gpt-5.1",
    "top_p": 1,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "response_format": {"type": "text"}
}

# LINE Bot Configuration
LINE_CHANNEL_ACCESS_TOKEN = "your-line-channel-access-token"
LINE_CHANNEL_SECRET = "your-line-channel-secret"

# Redis Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
```

---

## 核心特色

### 1. 清晰的架構分層
- **聲明式 Schema 層**: 定義圖的結構(狀態、節點、邊緣)
- **命令式 Controller 層**: 實作具體的業務邏輯
- **可重用的 Core 層**: 提供所有代理共享的基礎設施

### 2. 自動化的圖編譯
繼承 `BaseGraph` 後,只需要定義 schema,系統會自動處理:
- 節點註冊與函式綁定
- 條件邊緣與直接邊緣的連接
- 入口點設定
- 圖的編譯與優化

### 3. 統一的錯誤追蹤
錯誤會自動附加完整的調用路徑,從 API 層一路追蹤到底層工具:
```
Error Path:
  → TopController: call_intent_agent
  → IntentAgent: check_input_intent
  → IntentAgentTool.classify
  → LLMClient.invoke
Final Error: API request failed
```

### 4. 狀態隔離與映射
- 每個子圖只操作自己的狀態欄位
- 父圖透過 `state_mapping` 定義輸入/輸出的欄位對應
- 避免不同層級之間的狀態污染

### 5. 依賴注入設計
- 使用依賴注入而非直接 import,避免循環依賴
- LLMClient 由頂層傳遞給所有需要的代理
- 便於測試與模組替換

---

## 快速開始

### 環境需求
- Python 3.10+
- Windows / Linux / macOS
- Redis Server
- ngrok（LINE Bot 功能需要）

### 安裝步驟

#### 1. 克隆專案
```bash
git clone <repository-url>
cd <project-folder>
```

#### 2. 建立虛擬環境（建議使用 conda）
```bash
conda create -n llm_env python=3.10
conda activate llm_env
```

#### 3. 安裝依賴套件
```bash
pip install -r requirements.txt
```

#### 4. 配置系統
```bash
# 複製範例配置檔
cp config.example config.py

# 編輯 config.py，填入必要資訊：
# - OPENAI_APIKEY
# - LINE_CHANNEL_ACCESS_TOKEN（如需使用 LINE Bot）
# - LINE_CHANNEL_SECRET（如需使用 LINE Bot）
```

#### 5. 測試 Agent 系統
```bash
python main.py
```

### LINE Bot 部署

完整部署指南請參考：[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

**快速啟動（Windows）：**
```bash
# 雙擊執行啟動腳本
start.bat
```

**手動啟動：**
```bash
# 終端 1: Redis
cd C:\Tools\Redis-x64-5.0.14.1
redis-server.exe

# 終端 2: Celery Worker
celery -A line_bot.tasks worker --loglevel=info --pool=solo

# 終端 3: Flask Bot
python -m line_bot.bot

# 終端 4: ngrok
ngrok http 5000
```

---

## 基本使用

### Agent 系統測試
```python
from __init__ import app

# 處理單一文本
result = app.process("牛頓第二定律表明，施加於物體的外力等於此物體動量的時變率：F = dp/dt。")

if result["success"]:
    print("處理成功!")
    print(f"任務類型: {result['data']['selected_task_type']}")
    print(f"結果: {result['data']['final_result_text']}")
else:
    print("處理失敗!")
    print(f"錯誤訊息:\n{result['error']}")
```

### LINE Bot 使用

1. 掃描 QR Code 加 Bot 為好友
2. 傳送文字或上傳檔案（.txt, .pdf, .docx, .pptx）
3. Bot 自動處理並回傳 PDF 下載連結
4. 點擊連結下載報告（連結 24 小時有效）

---

## 如何擴展新 Agent

詳細步驟請參考原文檔中的「如何擴展新 Agent」章節。

### 關鍵設計原則

1. **Schema 只定義結構,Controller 實作邏輯**
2. **子圖只操作自己的狀態**
3. **使用依賴注入**
4. **錯誤會自動追蹤**

---

## 專案文件

- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - LINE Bot 完整部署指南
- **[TODO.md](TODO.md)** - 開發進度與待辦事項

---

## 故障排除

### Agent 系統

**Q: API 請求失敗？**
A: 檢查 `config.py` 中的 OPENAI_APIKEY 是否正確

**Q: 錯誤訊息看不懂？**
A: 系統會自動格式化錯誤路徑，從上到下追蹤問題來源

### LINE Bot

**Q: Celery 無法連接 Redis？**
A: 確認 Redis server 正在運行，看到 "Ready to accept connections"

**Q: Bot 沒有回應？**
A: 檢查 LINE Webhook URL 是否正確設定，且「Use webhook」已開啟

**Q: PDF 沒有中文？**
A: 確認系統有微軟正黑體字型（msjh.ttc）

**Q: 下載連結失效？**
A: ngrok 免費版每次重啟 URL 會改變，需更新 LINE Webhook 和 `tasks.py` 中的 download_url

---

## 協作方式

### 給組員的快速上手指南

1. 克隆專案並安裝依賴
2. 閱讀 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
3. 設定 `config.py`（向團隊索取 API Keys）
4. 執行 `start.bat` 啟動所有服務
5. 測試 Agent 和 LINE Bot 功能

### 開發規範

- **Commit 格式**：`feat/fix/docs/chore: description`
- **新增 Agent**：遵循「如何擴展新 Agent」的步驟
- **測試**：每個 Agent 都應有對應的 `test_tool.py`

---

## 技術棧

- **LangGraph** - 多代理系統框架
- **OpenAI API** - LLM 推理引擎
- **Flask** - Web 框架
- **Celery + Redis** - 非同步任務處理
- **ReportLab** - PDF 生成
- **LINE Messaging API** - 聊天機器人介面
- **ngrok** - 本地開發公開 URL

---

**開發者**: Wallace  
**最後更新**: 2025-12-19