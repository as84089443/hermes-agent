# Hermes 多部門 Agent Operating Model

Date: 2026-04-13

## 目標

把 Hermes 從「單一通用代理」升級為「可編排的多部門代理體系」，讓不同工作類型由專責 agent 處理，再由編排層統一協調，支援：

- 研發 / 技術推進
- 排程 / 任務追蹤 / 例行運營
- 設計工作流 / 視覺與內容產出
- 多部門協作與交付
- 知識沉澱與資產管理

核心理念：

1. 一個任務，一個 owner。
2. 所有跨部門工作都要有結構化交接。
3. 記憶分層：短期執行記憶、部門記憶、全域知識庫。
4. 編排層負責路由、同步、升級、結案。
5. 可觀測、可審計、可回放。
6. 若現有工具群過於分散，可整體重造為單一產品殼，部門能力以 module 存在，而不是被歷史 repo 邊界綁住。

## 部門總覽

| 部門 | 主要職責 | 輸入 | 輸出 |
|---|---|---|---|
| Creative（創意） | 文案、視覺概念、品牌語氣、原型內容 | 需求摘要、品牌規範、受眾資訊 | 文案草稿、設計方向、素材提案 |
| Research（研究） | 資料蒐集、事實核查、方案比較、技術可行性 | 問題定義、研究假設、查證需求 | 研究報告、證據鏈、建議方案 |
| Operations（運營） | 排程、任務拆解、資源協調、SLA 管理 | 交付需求、時程限制、依賴關係 | 任務計畫、里程碑、執行看板 |
| Client / Service（客戶 / 服務） | 需求接收、澄清、狀態回報、對外溝通 | 客戶訊息、工單、FAQ | 已釐清需求、回覆草稿、升級請求 |
| QA / Compliance（品質 / 合規） | 驗收、風險檢查、政策/法務/安全審查 | 內容草案、操作紀錄、外部依賴 | 通過 / 退回 / 需修正清單 |
| Knowledge / Asset Ops（知識 / 資產） | 知識整理、模板、素材庫、版本控管 | 完成產物、復用素材、最佳實務 | Wiki 條目、模板、資產索引 |
| Orchestration（編排） | 路由、派工、狀態同步、衝突解決、結案 | 任務請求、部門回報、事件 | 任務分派、合併決策、最終交付 |

## 部門職能定義

### 1) Creative

適合處理：
- 品牌文案、活動文案、UI 文字
- 圖像/影片/互動內容構想
- 提案簡報的敘事與版型方向
- 使用者可見的內容潤飾

成功標準：
- 風格一致
- 內容可交付
- 能被 QA 直接審核

限制：
- 不負責事實驗證
- 不直接決定排程

### 2) Research

適合處理：
- 技術方案比較
- 市場 / 競品 / 文獻蒐集
- 需求背後的原因拆解
- 風險與假設驗證

成功標準：
- 證據可追溯
- 結論可重現
- 來源與推論分離

限制：
- 不直接產出最終對外稿
- 遇到規範風險需交給 QA / Compliance

### 3) Operations

適合處理：
- 工作切片、里程碑、排程
- 依賴項管理
- 會議與待辦整理
- 例行作業、巡檢、提醒

成功標準：
- 任務粒度清晰
- 時間與責任明確
- 阻塞點可見

限制：
- 不改寫內容結論
- 不做最終品質裁決

### 4) Client / Service

適合處理：
- 客戶問題分流
- 澄清需求與收斂範圍
- 狀態更新與回覆草稿
- 工單升級與客訴處理

成功標準：
- 回覆及時
- 語氣適配對象
- 需求被正確轉譯

限制：
- 不隨意承諾未確認的交期
- 不直接修改內部系統配置

### 5) QA / Compliance

適合處理：
- 內容審核
- 風險掃描
- 合規檢查
- 發佈前驗收

成功標準：
- 缺陷明確分類
- 可執行的修正建議
- 審核結果可追蹤

限制：
- 不直接完成修正，除非被明確授權
- 若風險高，必須回升級路徑

### 6) Knowledge / Asset Ops

適合處理：
- 將任務成果沉澱成 wiki / SOP / 模板
- 管理版本、標籤、可重用資產
- 維護組織知識圖譜
- 建立可搜尋的案例庫

成功標準：
- 能被快速檢索
- 能被重用
- 有版本與責任歸屬

限制：
- 不替代內容創作或研究判斷
- 不覆寫原始證據與原始交付物

### 7) Orchestration

適合處理：
- 任務分流與派工
- 多 agent 並行控制
- 狀態機推進
- 衝突仲裁
- 最終封版

成功標準：
- 路由正確
- 交接清楚
- 任務有閉環

限制：
- 不替代專業判斷
- 不直接改動部門內容，除非做匯總與排程

## 推薦運作模式

### 模式 A：Hub-and-Spoke

以 Orchestration 為中心，其他部門為專責節點。

流程：

1. 使用者提交任務。
2. Orchestration 判斷任務類型、風險、時限、依賴。
3. 分派給一個或多個部門 agent。
4. 部門 agent 回傳結構化結果。
5. QA / Compliance 驗收。
6. Knowledge / Asset Ops 沉澱成果。
7. Orchestration 產出最終回覆或交付包。

適用：
- 大多數產品型任務
- 需要多步驟、可追蹤、可交接的工作

### 模式 B：Pipeline

適合需要固定順序的工作：

Research → Creative → QA / Compliance → Knowledge / Asset Ops → Orchestration

適用：
- 研究報告
- 對外提案
- SOP / 文件撰寫
- 內容上線前審核

### 模式 C：Parallel Specialist Mesh

適合需要快速收斂的複雜任務：

- Research 與 Operations 並行
- Creative 與 Client / Service 並行
- QA / Compliance 對所有候選結果做檢查

Orchestration 最後做整合與決策。

## 結構化交接規格

每個部門 agent 的輸出都應該符合固定交接格式：

```yaml
agent_role: research
task_id: T-20260413-001
status: done
summary: "..."
findings:
  - "..."
open_questions:
  - "..."
risks:
  - severity: high
    item: "..."
next_action:
  owner: qa
  action: "review_claims"
artifacts:
  - type: doc
    path: "..."
```

交接原則：
- 不用自由格式描述重要決策
- 事實、推論、建議分欄
- 每次交接都要帶 task_id
- 明確標示下一個 owner

## 共享記憶與 Wiki 資產

Hermes 需要三層共享資產：

### 1) Global Memory（全域記憶）

用途：跨部門共享的穩定上下文。

內容建議：
- 組織使命與優先級
- 常用術語與命名規則
- 客戶偏好與禁忌
- 長期技術決策
- 已確認的標準流程

存取原則：
- 可讀為主，寫入需有來源
- 需保留 provenance
- 避免把臨時草案寫入全域記憶

### 2) Department Memory（部門記憶）

用途：部門內的工作上下文與常用模式。

每個部門各自維護：
- 常用 prompt / checklist
- 驗收標準
- 常見失敗案例
- 專用模板
- 部門特有詞彙表

### 3) Knowledge Wiki / Asset Library（知識與資產庫）

用途：可搜尋、可重用、可版本化。

建議資產類型：
- SOP
- 決策紀錄（ADR / DR）
- 提案模板
- QA checklist
- 研究摘要
- 可重用素材（圖、表、文案、指令模板）
- 案例庫

必備欄位：
- title
- owner
- department
- tags
- status
- version
- source links
- last_reviewed_at
- confidence / validity window

## Hermes 建議的共享資產清單

最少要有以下幾個共用 wiki 項目：

1. `org-playbook`
   - 組織目標、優先級、語氣、決策原則

2. `task-routing-taxonomy`
   - 任務分類法、路由規則、升級條件

3. `handoff-contract`
   - 部門間交接的標準 schema

4. `qa-checklists`
   - 內容、技術、合規、發佈前檢查表

5. `asset-library-index`
   - 所有模板、圖片、簡報、文檔的索引

6. `decision-log`
   - 重大決策與原因，避免重複討論

7. `client-preferences`
   - 客戶/帳戶偏好、語氣、常見限制

## 任務路由規則

Orchestration 先判斷以下維度：

- 工作類型：研究 / 創意 / 排程 / 客服 / 品質 / 知識整理
- 風險等級：低 / 中 / 高
- 是否需要外部對話
- 是否需要多人並行
- 是否有時間約束
- 是否可自動完成，或需人工批准

路由示例：

- 「幫我整理一份新產品提案」→ Research + Creative + QA
- 「把今天的待辦排到下週」→ Operations
- 「客戶抱怨功能異常」→ Client / Service → QA / Compliance → Operations
- 「把這次專案沉澱成 SOP」→ Knowledge / Asset Ops
- 「設計一個新的多部門流程」→ Orchestration + Research + Operations

## 狀態機

建議所有跨部門任務遵循同一狀態機：

1. intake
2. triage
3. assigned
4. in_progress
5. review
6. revise
7. approved
8. published / delivered
9. archived

任何任務若遇到以下情況，應升級：
- 資訊不足
- 風險高於門檻
- 需求衝突
- 超過 SLA
- QA 未通過三次以上

## 權限與安全邊界

- Client / Service 不可直接修改核心配置。
- QA / Compliance 對高風險任務有否決權。
- Knowledge / Asset Ops 只能寫入已驗證成果。
- Orchestration 可讀所有部門回報，但不應在缺乏依據時覆蓋專業結論。
- 涉及密鑰、個資、客戶敏感資訊時，必須標記存取等級與保存期限。

## 觀測指標

建議追蹤：

- 任務路由正確率
- 平均交接次數
- 首次通過率
- QA 退回率
- 任務逾期率
- 知識沉澱覆蓋率
- 可重用資產命中率
- 客戶回覆延遲

## 建議的初始落地順序

1. 先做 Orchestration + Task Routing taxonomy。
2. 加入 Research / Operations / QA 三個核心部門。
3. 建立 handoff contract 與 shared wiki。
4. 再擴充 Creative 與 Client / Service。
5. 最後補上 Knowledge / Asset Ops 做長期沉澱。

## 一句話總結

Hermes 的多部門 agent operating model 應該是「編排層負責路由與閉環，專責部門負責判斷與產出，共享記憶負責沉澱與復用」。
