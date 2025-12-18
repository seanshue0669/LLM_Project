# TODO & Progress
以下為整個專案的代辦事項，請在完成後自行更新，並按照依賴順序開發。
## TopController
- [x] Schema 定義
- [x] Graph_init 框架
- [x] call_intent_agent 實作
- [x] call_keypoint_agent 實作
- [x] call_synthesis_agent 實作
- [x] 端對端測試

## IntentAgent
- [x] Schema + state_mapping
- [x] Graph_init
- [x] Tool 實作
- [x] Prompt 調整
- [x] 整合測試

## KeypointAgent
- [x] Schema + state_mapping
- [x] Graph_init
- [x] Tool 框架
- [x] Prompt 設計與調整
- [x] 整合到 TopController
- [x] 測試

## SynthesisAgent
- [x] Schema + state_mapping
- [x] Graph_init
- [x] Tool 框架
- [x] Prompt 設計
- [x] 整合到 TopController
- [x] 測試

### LineBot Integration
- [ ] LineBot API 設定
- [ ] Webhook 處理
- [ ] 訊息接收與回應
- [ ] 錯誤處理
- [ ] 部署測試

### System Integration Testing
- [x] 整合測試流程
- [x] 端對端測試案例


## 📋 Detailed Task Breakdown

### TopController

#### 1. Schema
- [x] 定義 TopControllerState (input_text, selected_task_type, final_result_text)
- [x] 定義 routing logic (route_to_task_agent)
- [x] 定義 nodes (call_intent_agent, call_keypoint_agent, call_synthesis_agent)
- [x] 定義 conditional_edges (KEYPOINT/SYNTHESIS routing)
- [x] 定義 direct_edges (agents → END)

#### 2. Graph_init (Controller 框架)
- [x] 載入 schema definitions (nodes, edges)
- [x] 宣告 DEPENDENT_GRAPHS_AND_SCHEMA 字典
- [x] 載入 subgraphs (compile subgraph instances)
- [x] 載入 subgraph_mappings (state mapping for each subgraph)

#### 3. Node Implementation
- [x] call_intent_agent 完整實作
  - [x] 取得 state_mapping
  - [x] map input state
  - [x] invoke subgraph
  - [x] map output state
- [x] call_keypoint_agent 實作
  - [x] 載入 KeypointAgent 到 DEPENDENT_GRAPHS
  - [x] 實作狀態映射邏輯
  - [x] 測試調用
- [x] call_synthesis_agent 實作
  - [x] 載入 SynthesisAgent 到 DEPENDENT_GRAPHS
  - [x] 實作狀態映射邏輯
  - [x] 測試調用

#### 4. Integration & Testing
- [x] 整體流程測試 (input → intent → keypoint/synthesis → output)
- [x] 錯誤處理驗證
- [x] 邊界案例測試

---

### IntentAgent

#### 1. Schema + state_mapping
- [x] 定義 IntentAgentState (input_text, task_type_candidate)
- [x] 定義 state_mapping (check_input_intent scenario)
- [x] 定義 nodes (check_input_intent)

#### 2. Graph_init
- [x] 載入 schema
- [x] 初始化 IntentAgentTool

#### 3. Tool 實作
- [x] IntentAgentTool class
- [x] classify 方法實作
- [x] config.json 配置

#### 4. Prompt 調整
- [x] system_prompt 設計
- [x] JSON schema 定義 (KEYPOINT/SYNTHESIS enum)
- [x] 錯誤處理 (fallback to "Other")

#### 5. 整合測試
- [x] test_tool.py 驗證

---

### KeypointAgent

#### 1. Schema + state_mapping
- [x] 定義 KeypointAgentState (input_text, keypoint_result)
- [x] 定義 state_mapping (extract_keypoints scenario)
  - [x] input mapping: input_text → input_text
  - [x] output mapping: keypoint_result → final_result_text
- [x] 定義 nodes (extract_keypoints)

#### 2. Graph_init
- [x] 載入 schema
- [x] 初始化 KeypointAgentTool
- [x] extract_keypoints node 實作框架

#### 3. Tool 框架
- [x] KeypointAgentTool class
- [x] extract 方法簽名定義
- [x] config.json 基礎配置

#### 4. Prompt 設計與調整
- [x] 完善 system_prompt (關鍵點提取規則)
- [x] 設計 user_prompt 格式
- [x] 測試不同類型文本的提取效果
- [x] 根據測試結果調整 prompt
- [x] 確定輸出格式 (numbered list / JSON / etc.)

#### 5. 整合到 TopController
- [x] 在 TopController 的 DEPENDENT_GRAPHS 加入 KeypointAgent
- [x] 實作 call_keypoint_agent 的完整邏輯
- [x] 測試 TopController → KeypointAgent 的狀態映射

#### 6. 測試
- [x] 單元測試 (test_tool.py)
- [x] 整合測試 (透過 TopController 調用)
- [x] 邊界案例測試

---

### SynthesisAgent

#### 1. Schema + state_mapping
- [x] 定義 SynthesisAgentState
- [x] 定義 state_mapping
- [x] 定義 nodes

#### 2. Graph_init
- [x] 建立 controller.py
- [x] 載入 schema
- [x] 初始化 SynthesisAgentTool

#### 3. Tool 框架
- [x] 建立 tool.py
- [x] 定義主要方法簽名
- [x] 建立 config.json

#### 4. Prompt 設計
- [x] 設計 system_prompt
- [x] 設計 user_prompt 格式
- [x] 測試與調整

#### 5. 整合到 TopController
- [x] 在 DEPENDENT_GRAPHS 加入 SynthesisAgent
- [x] 實作 call_synthesis_agent
- [x] 測試狀態映射

#### 6. 測試
- [x] 單元測試
- [x] 整合測試
- [x] 邊界案例測試

---
