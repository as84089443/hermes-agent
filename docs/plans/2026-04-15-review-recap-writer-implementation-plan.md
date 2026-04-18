# Review Recap Writer Implementation Plan

> For Hermes: Planner Mode only. This plan intentionally stops before implementation edits.

日期：2026-04-15

## 目標

落地 Brian AI workflow 的 `Review Recap Writer v1`，讓案件在 close 前能自動產生 machine-readable recap draft，並提出：
- customer sidecar update 建議
- brand sidecar update 建議
- rulebook update 建議
- do-not-ask candidate 建議
- template candidate 建議

這是 Brian workflow self-improvement loop 真正形成閉環的第一個關鍵模組。

## 這個模組為什麼現在值得先做

目前已完成：
- Case Repository v1
- Sidecar Resolver v1
- Routing Engine v1
- review recap schema
- self-improvement loop spec
- workflow metrics schema
- routing mismatch schema

目前真正還缺的，是把「案件做完之後學到什麼」穩定寫出來。

沒有 recap writer，系統就會：
- 能存 case
- 能判 routing
- 但不會真的學會

## v1 範圍

### 必做
1. 根據 case 資料生成 recap draft
2. 依 `review-recap.schema.json` 產出結構化輸出
3. 根據既有 sidecar / rulebook 給出 update 建議
4. 根據重複 confirmed 規則，給出 do-not-ask candidate 建議
5. 為 metrics 提供可記錄的事件輸出

### 不做
- 不直接回寫 sidecar
- 不直接寫入 do-not-ask
- 不自動 close case
- 不做 lane-specific recap writer
- 不做完整 UI

## 建議模組位置

新增：
- `agent_workflow/review_recap_writer.py`

測試：
- `tests/workflow/test_review_recap_writer.py`

後續可能會接：
- `agent_workflow/metrics.py`
- `agent_workflow/mismatch_tracker.py`
- `agent_workflow/do_not_ask_detector.py`

## 依賴來源

這個模組應讀：
- `CaseRepository` 輸出的 case dict
- `SidecarResolver`（可選，用於補背景）
- `docs/contracts/brian-ai-workflow-v1/review-recap.schema.json`
- sidecar / rulebook JSON 知識層

## 建議 API

### 主函數
- `build_recap(case: dict, context: Optional[dict] = None) -> dict`

### 補助函數
- `suggest_sidecar_updates(case, recap) -> dict`
- `suggest_rulebook_updates(case, recap) -> dict`
- `suggest_do_not_ask(case, recap) -> dict`
- `suggest_template_candidate(case, recap) -> dict`

## 輸出格式

主輸出應對齊 `review-recap.schema.json`：
- recap_id
- case_id
- case_title
- primary_lane
- customer_name
- client_owner_final
- pm_owner_final
- brian_exec_final
- brian_role_final
- income_nature_final
- customer_sidecar_update_needed
- brand_sidecar_update_needed
- rulebook_update_needed
- do_not_ask_again_candidate
- pending_fields
- pending_reason

## 初版判斷邏輯

### 1. 直接從 case 複製的欄位
若 case 已有：
- client_owner
- pm_owner
- brian_exec
- brian_role
則先帶入對應的 `*_final`

### 2. pending 判斷
若下列任一欄位缺失，加入 pending_fields：
- client_owner
- pm_owner
- brian_exec
- brian_role

### 3. income_nature 初判
初版用簡單規則：
- client_owner=我, pm_owner=我, brian_exec=是, brian_role=主輸出 -> 兼具PM與執行
- client_owner=我, pm_owner=我, brian_exec=否 -> PM/接案
- client_owner=共同, pm_owner=共同 -> 共同客戶/共同PM
- primary_lane=studio_rental -> 資產收入
- brian_exec=是, brian_role=支援 -> 協作支援
- 否則 -> 待確認

### 4. sidecar update 建議
若：
- customer_name 未出現在已知 customer sidecar
- 或 brand_or_system 未出現在 brand sidecar
- 或某條 case 結論比現有 sidecar 更明確
則對應欄位標 `*_update_needed = true`

### 5. do-not-ask 候選
v1 保守策略：
- 只有當 case 命中已知 confirmed line、且角色欄位完整時，才提出 `do_not_ask_again_candidate = true`
- 否則維持 false

## 測試計畫

最少測試：
1. 已完整 case -> recap 無 pending
2. 缺 client_owner -> recap 有 pending
3. studio_rental -> income_nature = 資產收入
4. 已知 brand/customer 命中時，不亂提 sidecar update
5. 新 customer_name 時，customer_sidecar_update_needed = true
6. 共同客戶 / 共同 PM -> income_nature 正確
7. 支援型出工 -> income_nature = 協作支援

## 風險

1. 太早讓 recap writer 自動回寫
- 風險：把錯誤規則寫進 semantic memory
- 解法：v1 只產 suggestion，不自動 commit

2. 把 case 缺欄位硬補成 final truth
- 解法：嚴格使用 pending_fields

3. 過早做 lane-specific recap
- 解法：v1 先做 generic recap writer

## 任務表

### Task 1 — 建模與讀 contract
- 建 `review_recap_writer.py`
- 讀 `review-recap.schema.json`
- 定義最小輸出骨架

### Task 2 — 寫最小 recap 生成邏輯
- 從 case 複製 facts
- 產出 pending_fields
- 產出 income_nature 初判

### Task 3 — 寫 sidecar / rulebook suggestion helpers
- customer sidecar 建議
- brand sidecar 建議
- do-not-ask candidate 建議

### Task 4 — 測試
- 建 `tests/workflow/test_review_recap_writer.py`
- 覆蓋 happy path + pending path + lane special case

## 驗證標準

完成後至少能證明：
- 對任何合法 case record 都能產生 recap dict
- 對缺欄位 case 不會亂猜，而會產生 pending_fields
- 能正確判斷最小 income_nature
- 能提出 sidecar update 建議

## 實作後下一步

Review Recap Writer v1 穩後，再接：
1. Do-Not-Ask Candidate Detector
2. Routing Mismatch Tracker
3. Workflow Metrics Aggregator

這樣就能真正完成 Phase A 與 Phase B 的閉環。
