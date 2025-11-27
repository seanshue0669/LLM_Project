# Multi-Agent System Framework
本專案開發過程中使用 Claude (Anthropic) 作為技術諮詢和部分程式碼審查工具!!

此專案是基於 LangGraph 的多代理系統框架,提供可重用的基礎架構以提供快速開發新的 agent。
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
意圖分類 agent,分析輸入文本的類型:
- 使用 LLM 對輸入文本進行分類
- 識別體裁類型(Narrative、Informational、Argumentative 等)
- 識別語境類型
- 提供分類結果給後續流程使用

### 系統入口

#### `api.py`
統一的 API 介面,封裝整個系統的調用邏輯:
- 初始化頂層控制器並編譯執行圖
- 提供 `process()` 方法處理外部請求
- 統一錯誤處理,回傳標準格式 `{"success": bool, "data": dict, "error": str}`

#### `main.py`
簡單的使用範例。從檔案讀取測試文本,調用 API 處理,並輸出結果。

### 配置檔案

#### `config.py` / `config.example`
系統配置檔案:
- OpenAI API 金鑰
- LLM 模型參數(model、top_p、temperature 等)
- 回應格式設定

**注意**: `config.py` 包含敏感資訊已加入 `.gitignore`。請複製 `config.example` 改名為 `config.py`,再填入你的 API 金鑰。

#### `agents/intent_agent/config.json`
Intent Agent 專用的 LLM 配置,定義 JSON Schema 強制輸出格式,確保分類結果符合預期結構。

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

## 快速開始

### 環境需求
- Python 3.10.18
- Windows

### 安裝步驟

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd <project-folder>
   ```

2. **建立虛擬環境** (建議)
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **安裝依賴套件**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置 API 金鑰**
   ```bash
   # 複製範例配置檔
   cp config.example config.py
   
   # 編輯 config.py,填入你的 OpenAI API Key
   # OPENAI_APIKEY = "your-api-key-here"
   ```

5. **執行測試**
   ```bash
   python main.py
   ```

### 基本使用範例

```python
from __init__ import app

# 處理單一文本
result = app.process("這是一段測試文本")

if result["success"]:
    print("處理成功!")
    print(f"分類結果: {result['data']}")
else:
    print("處理失敗!")
    print(f"錯誤訊息:\n{result['error']}")
```

### 測試 Intent Agent

```bash
python agents/intent_agent/test_tool.py
```

## 如何擴展新 Agent

### 步驟 1: 建立資料夾結構
在 `agents/` 下建立新的 agent 資料夾:
```
agents/
└── your_new_agent/
    ├── __init__.py
    ├── schema.py        # 定義狀態和節點
    ├── controller.py    # 實作業務邏輯
    ├── tool.py          # (選用) 外部工具封裝
    └── config.json      # (選用) Agent 專用配置
```

### 步驟 2: 定義 Schema
在 `schema.py` 中定義你的 agent 狀態和節點:

```python
from typing import TypedDict
from agents.mycore.base_schema import BaseSchema

class YourAgentState(TypedDict):
    input_field: str
    output_field: str

def process_node(state: YourAgentState) -> dict:
    """佔位節點,實際邏輯在 controller 實作"""
    return state

class YourAgentSchema(BaseSchema):
    state_type = YourAgentState
    
    # 定義狀態映射(給父圖用)
    state_mapping = {
        "scenario_name": {
            "input": {
                "parent_field": "agent_field"
            },
            "output": {
                "agent_field": "parent_field"
            }
        }
    }
    
    nodes = [
        ("process_node", process_node),
    ]
    
    direct_edges = []
    conditional_edges = []
```

### 步驟 3: 實作 Controller
在 `controller.py` 中實作實際邏輯:

```python
from agents.mycore.base_graph import BaseGraph
from agents.mycore.LLMclient import LLMClient
from .schema import YourAgentSchema

class YourAgent(BaseGraph):
    def __init__(self, llm_client: LLMClient):
        super().__init__(YourAgentSchema.state_type)
        
        self.nodes = YourAgentSchema.nodes
        self.conditional_edges = YourAgentSchema.conditional_edges
        self.direct_edges = YourAgentSchema.direct_edges
        
        # 如果需要用到 LLM 或工具
        self.llm_client = llm_client
    
    def process_node(self, state: dict) -> dict:
        """實作實際業務邏輯"""
        # 你的處理邏輯
        result = self.llm_client.invoke(...)
        state["output_field"] = result["content"]
        return state
    
    def compile(self):
        return super().compile()
```

### 步驟 4: 整合到 TopController
在 `agents/top_controller/controller.py` 中註冊你的新 agent:

```python
# 1. Import 你的 controller 和 schema
from agents.your_new_agent.controller import YourAgent
from agents.your_new_agent.schema import YourAgentSchema

# 2. 在 __init__ 加入 DEPENDENT_GRAPHS_AND_SCHEMA
DEPENDENT_GRAPHS_AND_SCHEMA = {
    "intent_agent": {...},
    "your_new_agent": {
        "controller": YourAgent,
        "schema": YourAgentSchema
    }
}

# 3. 新增調用方法
def call_your_agent(self, state: dict) -> dict:
    scenario = "scenario_name"
    graphmapping = self.subgraph_mappings["your_new_agent"]
    mapping = graphmapping.get(scenario)
    
    subgraph_input = self._map_input_state(state, mapping["input"])
    result_state = self.subgraphs["your_new_agent"].invoke(subgraph_input)
    parent_update = self._map_output_state(result_state, mapping["output"])
    
    return parent_update
```

### 步驟 5: 更新 TopController Schema
在 `agents/top_controller/schema.py` 中:

```python
# 1. 在 TopControllerState 加入新欄位
class TopControllerState(TypedDict):
    input_text: str
    selected_context_type: str
    selected_genre_type: str
    your_new_field: str  # 新增

# 2. 定義節點函式
def call_your_agent(state: TopControllerState) -> dict:
    return state

# 3. 註冊節點和邊緣
class TopControllerSchema(BaseSchema):
    nodes = [
        ("call_intent_agent", call_intent_agent),
        ("call_your_agent", call_your_agent),  # 新增
        ("passthrough", passthrough),
    ]
    
    # 根據需求加入 conditional_edges 或 direct_edges
```

### 關鍵設計原則

1. **Schema 只定義結構,Controller 實作邏輯**
   - Schema: 聲明式的狀態、節點、邊緣定義
   - Controller: 命令式的業務邏輯實作

2. **子圖只操作自己的狀態**
   - 透過 `state_mapping` 定義與父圖的介面
   - 避免直接修改父圖的狀態欄位

3. **使用依賴注入**
   - 需要的資源(如 LLMClient)從上層傳入
   - 避免在 controller 內部直接 import 或建立實例

4. **錯誤會自動追蹤**
   - BaseGraph 的 `_wrap_node` 會自動包裝錯誤
   - 工具類別使用 `@auto_wrap_error` 裝飾器

### 測試 Intent Agent

```bash
python agents/intent_agent/test_tool.py
```

---

## 協作方式

(待補充)

---

**開發者**: Wallace
**最後更新**: 2025-11-27
