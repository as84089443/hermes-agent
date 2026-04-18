# Brian AI Workflow Implementation Handoff Map

日期：2026-04-14

## 1. 這份文件的目的

這份文件是 Brian AI workflow 從「規劃層」切到「最小實作層」的橋接文件。

它回答：
1. 哪份 spec 對哪份 contract 負責
2. 哪份 contract 對哪個模組負責
3. 哪個模組先做，哪個後做
4. 哪個 UI 只讀資料，哪個 UI 可以觸發寫入
5. 哪些規則在 v1 直接落地，哪些明確留到 v1.1

這份文件寫完後，規劃層應視為第一輪封板，不再無限制擴張文件數量。

## 2. 規格 → Contract 對接

### 2.1 `brian-ai-workflow-data-model.md`
主要對接：
- `docs/contracts/brian-ai-workflow-v1/case.schema.json`
- `docs/contracts/brian-ai-workflow-v1/customer-brand-sidecar.schema.json`
- `docs/contracts/brian-ai-workflow-v1/review-recap.schema.json`

作用：
- 定義有哪些主體
- 定義欄位群與 enum
- 定義哪些欄位是 required / optional / derived

### 2.2 `customer-brand-sidecar-schema.md`
主要對接：
- `customer-brand-sidecar.schema.json`

作用：
- 提供 customer / brand sidecar 欄位細節與 update rules

### 2.3 `review-recap-schema.md`
主要對接：
- `review-recap.schema.json`

作用：
- 提供 review recap 的輸出欄位與回寫邏輯

### 2.4 `brian-ai-workflow-routing-rules.md`
主要對接：
- `brian-ai-workflow-routing-engine-pseudo-spec.md`

作用：
- 提供 routing 判斷規則
- 提供 client_owner / pm_owner / brian_exec / brian_role 的推定順序

### 2.5 `brian-ai-workflow-state-machine.md`
主要對接：
- case repository 中的 status validator

作用：
- 定義合法 status
- 定義可轉移的狀態

### 2.6 `brian-ai-workflow-phase-gates.md`
主要對接：
- case transition guard
- change review trigger checker

作用：
- 定義每個 phase 的 entry / exit criteria
- 定義 confirmed 後的鎖定與變更規則

### 2.7 `brian-ai-workflow-decision-rails.md`
主要對接：
- AI action guard
- permission / allowed action checker

作用：
- 限制 AI 可做 / 不可做
- 避免越權

## 3. Contract → 模組 對接

### Module A：Case Repository
輸入：
- `case.schema.json`
- `state-machine.md`
- `phase-gates.md`

責任：
- 建立 / 讀取 / 更新 case
- 驗證 required fields
- 驗證 status 是否合法
- 驗證 transition 是否允許

v1 必須支援：
- create_case
- update_case_fields
- transition_case_status
- get_case
- list_cases

### Module B：Sidecar Resolver
輸入：
- `customer-brand-sidecar.schema.json`
- `vendor_master_sidecar_v1_*.json`
- `customer_brand_sidecar_v1_*.json`
- `analysis_rulebook_v1_*.json`

責任：
- 根據 customer / brand / alias / rulebook，給出 candidate values
- 先查已確認規則，再決定要不要補問

v1 必須支援：
- resolve_customer_context
- resolve_brand_context
- get_do_not_ask_rules

### Module C：Routing Engine
輸入：
- `brian-ai-workflow-routing-engine-pseudo-spec.md`
- `brian-ai-workflow-routing-rules.md`
- Sidecar Resolver 結果
- 原始 brief

責任：
- 給出 lane candidate
- 給出 owner / pm / brian_exec / brian_role candidate
- 給出 confidence
- 給出 missing_fields
- 給出 recommended questions
- 給出 next status / next owner

v1 必須支援：
- route_intake
- reroute_with_new_info

### Module D：Intake Normalizer
輸入：
- raw_brief
- source
- Sidecar Resolver 結果

責任：
- 產出 normalized brief
- 產出最少補問
- 產出 intake summary
- 把資料交給 Routing Engine

### Module E：Review Recap Writer
輸入：
- case
- review-recap.schema.json
- 歷史收入資料 / sidecar / rulebook

責任：
- 產出 recap 草稿
- 提示要不要更新 sidecar
- 提示要不要進 do-not-ask-again
- 提示是否可模板化

## 4. 模組 → UI 對接

### 4.1 Dashboard
只讀為主。
顯示：
- 今日最重要案件
- 哪些卡在 clarifying
- 哪些待 quote
- 哪些 confirmed 但未執行
- 哪些 delivered 但未 billing / collected
- 哪些 close 前缺 review recap

依賴模組：
- Case Repository
- Routing Engine（摘要）
- Review Recap Writer（缺 recap 提示）

### 4.2 Cases
只讀 + 基本操作。
顯示：
- case list
- status
- lane
- current_owner
- next_action
- confidence flags

依賴模組：
- Case Repository
- Sidecar Resolver（補充標籤）

### 4.3 Case Detail
是 v1 真正的主工作頁。
應能做到：
- 看 raw / normalized brief
- 看 routing candidates
- 看 owner / PM / Brian role
- 手動修正欄位
- 送出 transition
- 觸發 recap writer

依賴模組：
- Case Repository
- Routing Engine
- Review Recap Writer
- Sidecar Resolver

## 5. 哪些模組只讀、哪些允許寫入

### 5.1 只讀模組
- Dashboard
- Cases list
- Sidecar lookups（v1 先讀為主）

### 5.2 可寫入模組
- Case Repository
- Review Recap Writer（先寫出 draft，不自動 commit final truth）

### 5.3 半自動寫入
- Sidecar updates
- do-not-ask-again

規則：
- AI 可提出 write suggestion
- 最終仍應經 human 確認後寫入

## 6. v1 實作順序

### Phase 1：資料與規則引擎
1. Case Repository
2. Sidecar Resolver
3. Routing Engine v1

### Phase 2：入口與學習
4. Intake Normalizer
5. Review Recap Writer

### Phase 3：可見操作面
6. Dashboard
7. Cases
8. Case Detail

## 7. 哪些欄位允許先 pending

v1 可 pending：
- client_owner
- pm_owner
- brian_exec
- brian_role
- brand_or_system
- income_nature

v1 不可長期空白：
- case_id
- title
- source
- primary_lane（至少 candidate）
- current_owner
- status
- next_action
- next_owner

## 8. 這輪規劃封板後的規則

1. 若要新增文件，必須先說明它屬於：
- plan
- spec
- playbook
- contract
- exports
哪一層

2. 若要改規則，先改 source-of-truth 文件，再改次文件

3. v1.1 候選（如 operating_controller / upstream_source）不得偷渡進 v1 code path

4. 在進入實作前，這份 handoff map 視為最後一份主要規劃橋接文件

## 9. 下一步（實作前）

這份文件寫完後，下一步不應再擴規劃，而應：
1. 先定 code 目錄放哪
2. 先定最小 case repository 介面
3. 再決定最小 UI 要掛在哪個既有前台殼內

也就是說：
接下來應進入 implementation planning，而不是再繼續寫大量新 spec。
