# Brian AI Workflow Source-of-Truth Matrix

日期：2026-04-14

## 1. 這份文件的目的

這份文件明確定義 Brian AI workflow 各主題的 source of truth，避免同一規則散落在多份文件裡，之後修改時互相漂移。

原則：
- 每個主題只允許一份主文件
- 其他文件只能摘要、引用、翻譯，不應重複完整規則
- 若發現衝突，先修主文件，再同步次文件

## 2. 主題對照表

| 主題 | 主文件（Source of Truth） | 次文件（可引用） | 備註 |
| --- | --- | --- | --- |
| 系統總定位 / v1 範圍 | `docs/plans/2026-04-14-brian-ai-workflow-design-convergence.md` | `2026-04-14-brian-ai-workflow-v1.md` | convergence 為最新總摘要；v1 藍圖保留為初始設計脈絡 |
| 決策邊界 / AI 不可越權 | `docs/specs/brian-ai-workflow-decision-rails.md` | `pm-playbook.md`, `state-machine.md`, `phase-gates.md` | 任何 AI 可做/不可做行為先改 rails |
| case 欄位與實體 | `docs/specs/brian-ai-workflow-data-model.md` | `customer-brand-sidecar-schema.md`, `review-recap-schema.md` | data-model 定存在性，子 schema 定細節 |
| 主 lane / client_owner / pm_owner / brian_exec 判斷 | `docs/specs/brian-ai-workflow-routing-rules.md` | `intake-playbook.md`, `pm-playbook.md`, 各 lane playbook | routing rules 不應被 playbook 覆寫 |
| 正式狀態定義 | `docs/specs/brian-ai-workflow-state-machine.md` | `phase-gates.md`, `pm-playbook.md` | state-machine 定狀態名與合法轉移 |
| 關卡 / entry-exit criteria / scope lock 啟動點 | `docs/specs/brian-ai-workflow-phase-gates.md` | `pm-playbook.md`, `wedding-playbook.md`, `studio-rental-playbook.md` | scope lock / change review 細節以 phase-gates 為主 |
| customer sidecar 欄位 | `docs/specs/customer-brand-sidecar-schema.md` | `data-model.md`, `review-recap-schema.md` | 共享表單不是 source of truth |
| recap 欄位 / sidecar 回寫條件 / do-not-ask-again 輸出 | `docs/specs/review-recap-schema.md` | `review-and-learning-playbook.md` | do-not-ask-again 的正式輸出入口在 recap schema |
| intake 實際操作 | `docs/playbooks/intake-playbook.md` | `routing-rules.md`, `phase-gates.md` | playbook 不應重寫 routing 規則 |
| PM 實際操作 | `docs/playbooks/pm-playbook.md` | `phase-gates.md`, `decision-rails.md` | PM playbook 是操作翻譯，不是治理本體 |
| 婚禮線操作 | `docs/playbooks/wedding-playbook.md` | `routing-rules.md`, `phase-gates.md` | lane-specific，僅補婚禮特例 |
| 場租線操作 | `docs/playbooks/studio-rental-playbook.md` | `routing-rules.md`, `phase-gates.md` | lane-specific，僅補場租特例 |
| review / learning 操作 | `docs/playbooks/review-and-learning-playbook.md` | `review-recap-schema.md` | recap schema 定欄位，playbook 定人怎麼做 |
| 歷史收入 / 客戶 / 品牌知識基底 | `exports/google_calendar_history/*.json/csv` | sidecar / rulebook 文件 | 這些是事實層，不直接作為產品規格 |

## 3. 修改順序規則

### 3.1 若是規則改變
先改：
1. 主文件（spec / convergence）
2. 再改相關 playbook
3. 最後視需要更新 sidecar / exports

### 3.2 若是新案例帶來新知識
先改：
1. `review-recap-schema` 產生新 recap
2. sidecar / rulebook
3. 若新知識已成通則，再改 routing rules / rails

### 3.3 若是 UI 實作不符規格
先回頭看：
- routing rules
- phase gates
- decision rails
不要直接在 UI 層重新發明規則。

## 4. 衝突時的處理原則

若發現文件互相衝突：
1. 先查本表，找到主文件
2. 以主文件為準
3. 修正次文件中的過時描述
4. 若主文件本身有問題，先改主文件，再同步其他文件

## 5. 現階段最容易漂移的主題

1. scope lock / change review
- 容易在 state-machine、phase-gates、PM playbook、wedding/studio lane playbook 中重複書寫
- 以 `phase-gates.md` 為主

2. do-not-ask-again
- 容易在 routing、review playbook、schema 中各寫一版
- 以 `review-recap-schema.md` 為正式輸出入口

3. customer / brand sidecar
- 容易在 data-model 與 sidecar schema 中重複定義欄位
- 以 `customer-brand-sidecar-schema.md` 為欄位細節主文件

## 6. 執行建議

之後若要繼續推進，請遵守：
- 先查本表再改文件
- 優先少量、準確地更新主文件
- 避免在 playbook 裡重新抄寫完整規格
- 若 lane 有特殊規則，只寫該 lane 的增量差異
