# 最小主動推進 operating loop v1

日期：2026-04-14

目的：
定義在 ai-department-os / Hermes 這類系統中，讓 agent 能夠「少 check-in、持續主動推進、留下可審計 artifact」所需的最小可實作閉環。

這份文件刻意不談抽象哲學，只聚焦最小機制。

## 一句話結論

最小 operating loop 不是「更會規劃的 prompt」，而是 6 個硬機制的組合：
1. 單一主 phase 鎖
2. 可機器判定的 next action ledger
3. artifact-first 任務完成契約
4. 明確 join owner 的 fan-out / merge
5. review / verification 的固定 verdict 與回寫
6. 週期性 re-entry driver（cron / queue / event trigger）

少掉其中任一個，agent 都會退化成：只會回報、不會前進；只會做事、不會收斂；或只會產生聊天內容、不會留下可接手成果。

## 1. 必要機制

### 機制 A：單一主 phase 鎖

最低要求：
- 一個 project 任一時間只能有一個 `main_phase`
- `main_phase` 必須綁定：核心問題、visible artifact、驗證方式、out-of-scope
- phase 切換必須寫回狀態，而不是只存在聊天上下文

為什麼必要：
- `hermes-phase-contract-v0.1` 已指出「一次只推進一個主 phase」與「每個 phase 都必須留下 visible artifact」
- 若沒有 phase 鎖，agent 很容易把 research、implementation、polish、下一輪規劃混成一團，最後沒有真正完成任何 join point

最小資料欄位：
- `project.main_phase`
- `project.phase_goal`
- `project.phase_artifact_target`
- `project.phase_verification_target`
- `project.phase_out_of_scope`

---

### 機制 B：next action ledger，而不是只有 todo

最低要求：
- 每個 project 永遠只能有一個 machine-readable `next_action`
- `next_action` 必須帶：owner、prerequisites、blocking_reason、deadline/SLA、成功後要寫出的 artifact/event
- agent 每次完成一步後，必須回寫下一步，不可停在「已完成」

為什麼必要：
- 現有 Hermes `todo` tool 是 session 內 in-memory store，適合當前對話，但不是跨 session / 跨 cron / 跨 subagent 的控制面
- `hermes-phase-contract-v0.1` 也明確指出目前缺 `phase end -> next phase entry` 的固定欄位
- 如果只有 todo 而沒有 next_action ledger，agent 會在 session 結束、context compression、subagent closeout 後失去再進場點

最小資料欄位：
- `project.next_action.type`
- `project.next_action.owner_role`
- `project.next_action.input_refs`
- `project.next_action.blocking`
- `project.next_action.blocking_reason`
- `project.next_action.exit_artifact_type`
- `project.next_action.exit_event_type`
- `project.next_action.not_before`

建議規則：
- 若 `next_action.blocking=true`，必須同時產生 escalation / approval / dependency 缺口之一
- 若 `next_action` 缺失，project 不允許保持 `in_progress`

---

### 機制 C：artifact-first completion contract

最低要求：
- 任務完成不是「assistant 說 done」，而是至少產生一個 artifact ref
- artifact 必須有 type、version、path、producer、checksum/immutable ref
- approval / review / merge 一律指向 artifact version，不指向模糊描述

為什麼必要：
- `company-core-sop-map-v1`、`ai-department-os-v1-minimal-data-model`、`artifact contract` 都已經把 exact artifact version 當成必要條件
- 若沒有 artifact-first contract，agent 只能交付聊天內容，manager 很難 audit，也無法讓下一個 lane 無歧義接手

最小規則：
- `task.done` 前必須有 `output_artifact_id`
- `approval_requested` 前必須有 `artifact_refs[{artifact_id, version}]`
- 新版本必須 supersede 舊版本，不可直接覆蓋

---

### 機制 D：fan-out / join / merge owner

最低要求：
- 只有 plan 階段能 freeze execution graph
- 每個 join point 必須只有一個 `join_owner`
- branch 結果未被選用時標記為 `superseded`，而不是消失
- subagent handoff 必須有 summary / risks / next action / acceptance

為什麼必要：
- `subagent-parallel-execution-fabric` 已定義：execution graph node/edge、handoff contract、單一 merge owner、branch merged event
- Hermes 已有 `delegate_task`、隔離子 agent、平行執行能力，但目前缺的是「把 delegation 回寫到 project control plane」
- 沒有 join owner，平行化只會製造更多未合併碎片

最小資料欄位：
- `task.join_owner`
- `handoff.requested_review_type`
- `handoff.next_action`
- `event.branch_merged`
- `artifact.status = draft | final | superseded`

---

### 機制 E：固定 review / verification verdict

最低要求：
- review verdict 只能是 `PASS | REQUEST_CHANGES | REJECT`
- verification package 至少包含：command / success condition / failure signal / report path / next phase entry
- verdict 必須回寫 project / task 狀態，不可只出現在聊天訊息

為什麼必要：
- `hermes-phase-contract-v0.1` 已明指 review schema 與 verification minimum package 尚未完全制度化
- 若沒有固定 verdict，agent 很容易卡在「看起來差不多」、「我檢查過了」這種不可操作狀態

最小資料欄位：
- `review.spec_compliance_verdict`
- `review.quality_verdict`
- `verification.command`
- `verification.report_artifact_id`
- `verification.failure_signal`
- `project.next_phase_entry`

---

### 機制 F：re-entry driver（重新進場驅動器）

最低要求：
- 要有一個週期性或事件式 driver，定時撿起 `in_progress` / `blocked` / `waiting_on_human` 專案重新判斷是否可前進
- driver 不是拿來「產出報表」，而是要執行 `read state -> choose next action -> act -> write state`
- driver 必須有 inactivity timeout 與 run isolation，避免卡死整個系統

為什麼必要：
- Hermes 現有 cron 已具備：fresh session、scheduler tick、delivery、inactivity-based timeout
- 這正好是主動推進的最小 runtime driver；缺的是 project-aware prompt 與 state write-back
- 沒有 re-entry driver，agent 只有人在 ping 時才會動，不可能真正主動推進

可直接沿用 Hermes 現成能力：
- cron scheduler 每 60 秒 tick
- cron run 使用 fresh `AIAgent` session
- 有 inactivity timeout 與 activity tracker
- 可把結果 delivery 回 origin / Telegram / local

最小執行步驟：
1. 掃描 `project where status in (in_progress, blocked, approval_pending)`
2. 對每個 project 載入 `main_phase + next_action + open approvals + recent artifacts`
3. 判斷：可自動執行 / 等人 / 等依賴 / 需 escalate
4. 若可執行，啟動對應 worker 或 subagent
5. 寫回 artifact / handoff / event / next_action
6. 若到 join point，交給 join owner merge

## 2. 會阻斷 autonomy 的 anti-patterns

### 反模式 1：把 todo 當 control plane

現況：
- Hermes 的 `todo` tool 是 session 內記憶體狀態，不是 project-level persisted ledger

問題：
- session 結束就失去控制狀態
- cron / subagent / manager 不能共用同一份真實進度
- 無法成為重新進場依據

---

### 反模式 2：只有聊天回報，沒有狀態回寫

現況：
- 目前許多規則存在於 spec / plan 文件與對話，但未必有對應 machine state

問題：
- agent 每次重啟都要重新理解上下文
- manager 看到的是敘述，不是可執行狀態
- 無法可靠驅動下一步

---

### 反模式 3：delegate_task 有了，但 delegation 結果沒進 project ledger

現況：
- Hermes 已能平行 subagent、隔離工具集、回傳 summary
- 但 repo 內尚未看到 project-aware 的 `artifact_written / handoff_sent / branch_merged` 真實落地鏈

問題：
- 子 agent 很忙，但系統狀態沒前進
- 多 lane 結果只能靠人肉 merge

---

### 反模式 4：review 與 verification 只是一段話

問題：
- 沒有固定 verdict，無法驅動狀態機
- 沒有 report artifact，無法回歸、無法審計
- 下一輪 agent 也無法知道到底是 spec gap 還是 quality gap

---

### 反模式 5：沒有 phase-end 的 next entry

問題：
- agent 做完一輪後常停在「本輪已完成」
- 這其實不是完成，而是缺少下一步編址
- `hermes-phase-contract-v0.1` 已把這點列為現存缺口

---

### 反模式 6：把 blocker 全部推回人類

問題：
- 很多 blocker 其實可分成：資訊不足、依賴未就緒、需要 approval、執行失敗需 retry
- 若不分類，agent 只會頻繁 check-in
- 正確做法是只把「真正的人類決策 gate」升級給人，其餘 blocker 轉成系統內可管理狀態

## 3. 最高槓桿的第一刀 implementation slice

## Slice 名稱
Project Autopilot Loop v0

## 目標
不是先做完整 AI Department OS，而是先讓 Hermes 能對「單一 project」形成真正可重入、可持續推進的閉環。

## 只做這 4 件事

### 1. 補一個 project runtime ledger

新增最小持久化物件：
- `project`
- `task`
- `artifact`
- `event`

但第一刀可以先不做完整 approval/handoff UI，只先保留欄位與 append-only event。

最低必備欄位：
- Project: `id, title, status, main_phase, current_owner, next_action_json, updated_at`
- Task: `id, project_id, type, status, owner_role, output_artifact_id`
- Artifact: `id, project_id, type, version, path, status, produced_by_task_id, checksum`
- Event: `id, project_id, event_type, entity_type, entity_id, payload_json, created_at`

### 2. 補一個 autopilot tick worker

可直接建立在 Hermes 現有 cron / scheduler 之上：
- 固定頻率掃描 active projects
- 對每個 project 執行單步推進，不做無限迴圈
- 每次 tick 最多前進一步，確保可觀察與可回滾

單步推進策略：
- 若 `next_action.type=execute_task`：啟動 agent/subagent 完成該 task
- 若 `next_action.type=request_review`：生成 review artifact + verdict
- 若 `next_action.type=request_approval`：建立 approval row / 通知 operator
- 若 `next_action.type=verify`：跑 command 並寫 report artifact
- 若 `next_action.type=await_human`：不重複打擾，只更新 SLA / reminder

### 3. 補固定 commander snapshot artifact

每次 tick 後都輸出一份 live status：
- 目前主 phase
- 各 lane 狀態
- 現在 blocker
- 下一個 join point
- 最新 artifact
- 下一步是否需要人介入

這其實就是把 `hermes-phase-contract-v0.1` 中建議的固定回報，制度化成 machine-produced artifact。

### 4. 補 next_action compiler

這是第一刀最關鍵的地方。

每次任務完成、review 完成、verification 完成，都執行一個純函式：
- 讀目前 project state
- 產出唯一合法 `next_action`

簡化規則：
- 若 task 已完成且未 review -> `request_review`
- 若 review PASS 且未 verify -> `verify`
- 若 verify PASS 且 phase 已完成 -> `advance_phase`
- 若 verify FAIL -> `execute_task` 或 `request_changes`
- 若 pending approval 存在 -> `await_human`
- 若 join prerequisites 都滿足 -> `merge_branch`
- 若缺 prerequisite -> `blocked_on_dependency`

## 為什麼這刀槓桿最高

因為它直接把目前 repo 已經分散存在的能力接成閉環：
- Hermes 已有 session persistence
- 已有 cron
- 已有 subagent delegation
- 已有 approval queue
- 已有 phase / handoff / artifact / event 的文件契約

現在真正缺的不是更多 agent 智能，而是：
- project-aware persisted runtime ledger
- next_action compiler
- autopilot tick

## 先不要做的事

第一刀不需要：
- 完整多部門 taxonomy
- 複雜 UI dashboard
- 全量 Slack / Telegram runtime 整合
- 花俏的自動 priority optimizer
- 完整 memory learning loop

因為只要先把「單一 project 能自己往前一步、留下 artifact、算出下一步」做好，autonomy 就會從 0 變成 1。

## 與現有 Hermes 能力的對接判斷

可直接重用：
- `cron/scheduler.py`：作為 autopilot tick driver
- `tools/delegate_tool.py`：作為 lane / specialist execution runtime
- `tools/approval.py`：作為人類 gate 的等待與解除機制
- `hermes_state.py`：可借鏡持久化與 session lineage 設計

仍缺實作：
- project-level runtime state store
- project-aware event writing
- artifact registry 實體落地
- next_action compiler
- 固定 commander snapshot artifact

## 最後結論

若目標是「agent 主動推進專案」而不是「agent 看起來很會回報」，最小 operating loop 應該是：

1. phase lock
2. persisted next action
3. artifact-first task completion
4. explicit join owner
5. fixed review / verification verdict
6. cron-driven re-entry

最高槓桿第一刀不是做更大的 planner，而是把這 6 件事中最缺的 3 件接起來：
- project runtime ledger
- next_action compiler
- autopilot tick

只要這三件落地，Hermes/ai-department-os 就會從「需要人常常催」變成「系統會自己找到下一步並留下可見成果」。
