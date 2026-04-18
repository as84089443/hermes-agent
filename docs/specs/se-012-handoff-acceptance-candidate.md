# se-012 handoff acceptance candidate

狀態：candidate
對應 queue：`se-012`
目的：為雙 Agent handoff 補上最小 acceptance 規格，但先作為候選草案，不直接改 canonical protocol。

## 1) 建議新增的草案文件名稱

建議文件：`docs/specs/se-012-handoff-acceptance-candidate.md`

理由：
- 放在 `docs/specs/`，表示這是可討論、可驗證的規格草案
- 檔名直接綁定 `se-012`，方便和 candidate queue 對應
- 明確標註 `candidate`，避免被誤認成 canonical contract 或 protocol

## 2) 草案應包含的最小章節

### A. Scope
定義這份草案只處理雙 Agent 之間的 handoff acceptance，不重寫整份 collaboration protocol。

### B. When handoff is required
至少在以下情境要求 handoff：
- owner 要移轉給另一個 Agent
- 當前 Agent 已完成一段工作，但下一步必須由另一個 Agent 承接
- 當前 Agent 因能力邊界、工具邊界、或資訊邊界，需將任務正式交出

### C. Minimum handoff card
定義 sender 必填的最小交接包欄位。

### D. Receiver decision
定義 receiver 只能回三種結果：`accept` / `reject` / `request_clarification`。

### E. State + event rules
至少記錄：
- `handoff_sent`
- `handoff_accepted` / `handoff_rejected` / `handoff_clarification_requested`

### F. Freshness rule
handoff 必須帶 `created_at`，若 context、artifact、或前提已過時，receiver 應優先回 `request_clarification` 或 `reject`，不能默默接手。

### G. Lightweight rollout rule
先用於跨 Agent handoff；同 Agent 內部 task transition 暫不強制套用。

## 3) handoff card 最小欄位

建議最小欄位如下：
- `handoff_id`
- `from_agent`
- `to_agent`
- `task_or_workstream_ref`
- `summary`：這次交什麼
- `artifacts_or_links`：接手必看的輸出或路徑
- `done_definition`：目前已完成到哪
- `next_action_requested`：希望對方接下來做什麼
- `assumptions`
- `open_questions`
- `risks_or_blockers`
- `created_at`
- `fresh_until` 或 `context_freshness_note`

最小原則：
- 沒有 artifact ref，不算完整 handoff
- 沒有 next action，不算明確 ownership transfer
- 沒有 freshness 資訊，receiver 有權要求補件

## 4) accept / reject / request-clarification 三種結果定義

### accept
定義：
- receiver 確認資訊足夠、artifact 可用、責任邊界清楚
- receiver 同意成為 next owner

效果：
- ownership 正式轉移
- 記錄 `handoff_accepted`
- sender 不再假定自己仍是主 owner，除非後續又被退回

### reject
定義：
- receiver 明確認定這不是自己應接的 handoff，或前提明顯不成立
- 常見原因：路由錯誤、權責錯誤、缺關鍵 artifact、交接內容與 receiver 能力/工具邊界不符

效果：
- ownership 不轉移
- 必須附 `reason`
- 記錄 `handoff_rejected`
- handoff 回到 sender 或升級給 Brian 決策

### request_clarification
定義：
- receiver 認為這個 handoff 可能可接，但目前資訊不足，無法安全 accept
- 常見原因：summary 太抽象、artifact 不完整、前提不明、context 已 stale

效果：
- ownership 暫不轉移
- receiver 必須指出缺什麼
- 記錄 `handoff_clarification_requested`
- sender 補件後可重新送出同一 handoff 或新版本 handoff

## 5) 為何這份草案仍屬 candidate，不該直接 canonicalize

原因很簡單：
- `se-012` 在 candidate queue 的 required proof 還沒滿，還缺至少 2 個跨 Agent 結構化 handoff 案例
- 目前只有需求缺口與治理判斷，還不是已驗證的穩定規則
- 若現在直接寫進 canonical protocol，容易把格式提早寫死，造成流程過重
- freshness、acceptance、clarification 的欄位設計，仍需要用真實 handoff 測試是否剛好夠用
- 這份草案比較像「最小可試行規格」，目的是先收 evidence，再決定哪些欄位和狀態值得升格

## 建議的最小試行規則

在 evidence 補齊前，先只試行以下規則：
1. 跨 Agent handoff 一律要有 handoff card
2. receiver 一律明確回 `accept` / `reject` / `request_clarification`
3. 任何沒有明確回應的 handoff，都視為尚未完成 ownership transfer
4. 每個試行案例都要保留 artifact ref 與 decision 結果，供後續 weekly review 決定是否升格
