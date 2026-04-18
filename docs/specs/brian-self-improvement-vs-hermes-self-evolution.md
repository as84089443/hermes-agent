# Brian Self-Improvement vs Hermes Self-Evolution Plan

> For Hermes: Planner Mode only. This document is a planning/decision artifact and intentionally stops before any new implementation work.

日期：2026-04-15

## 目標

把「Brian 業務工作流的自我進化」與「官方 Hermes Agent Self-Evolution（DSPy + GEPA）」拆成兩條清楚的路線，避免混線；同時做紅白測試，決定什麼時候才值得把官方 evolution repo 接進來。

## 一句話結論

先把你自己的 workflow self-improvement loop 跑順，再把官方 self-evolution repo 當成第二層離線 optimizer，優化已經穩定的 routing / prompt target；不要反過來。

## 架構定位

### A. Brian Workflow Self-Improvement
定位：
- 線上、事件驅動、營運導向
- 目的是讓系統少重問、少重猜、會從案件學規則

主要學習對象：
- customer sidecar
- brand sidecar
- analysis rulebook
- do-not-ask-again
- routing mismatch
- recap/learning patterns

### B. Hermes Agent Self-Evolution（官方 repo）
定位：
- 離線、批次優化、模型/提示/skill 導向
- 目的是優化 skill text / prompt / tool description / code

主要優化對象：
- SKILL.md
- system prompt sections
- tool descriptions
- 未來可擴至 code

### 核心差異
- Brian workflow self-improvement = 學業務世界
- Hermes self-evolution = 優化 agent 本體

## Phase 計畫

### Phase A — 跑順你自己的 workflow self-improvement loop

範圍：
- case
- sidecar
- routing
- recap
- do-not-ask
- mismatch tracking

最低完成條件：
1. 新案件能進入 case repository
2. resolver 能命中既有客戶 / 品牌 / rulebook
3. routing engine 能產出 candidate values
4. 結案能產出 review recap
5. recap 能提出 sidecar / rulebook 更新建議
6. repeated clarification 能產生 do-not-ask candidate
7. routing mismatch 有地方可記錄

目前狀態（截至本計畫）：
- 已完成
  - Case Repository v1
  - Sidecar Resolver v1
  - Routing Engine v1
  - review recap schema
  - self-improvement loop spec
- 尚缺
  - review recap writer
  - do-not-ask candidate detector
  - routing mismatch tracker

### Phase B — 建 metric 與驗證閉環

至少先定這 4 個核心指標：
1. routing correction rate
2. repeated clarification count
3. do-not-ask hit rate
4. recap pending rate

建議補充指標：
5. sidecar confidence promotion rate
6. customer/brand hit rate
7. unresolved case ratio

最低完成條件：
- 以上指標能被定義、收集、回顧
- 至少能對最近一批案件算出一輪

### Phase C — 接官方 Hermes Self-Evolution repo

限制：
- 只優化一個 target
- 先不要優化全部 skill / prompt / code

首個 target 建議：
- Routing Engine 的 prompt / heuristic text

原因：
- Routing 是目前最容易形成 eval set 的地方
- 也是最容易從 mismatch / recap 中抽出乾淨 supervision 的地方

## 紅白測試（Red / Blue Tests）

### Blue Tests（成立後才算 workflow self-improvement 跑順）

#### Blue-1: 已知客戶線不再重問
條件：
- sidecar / rulebook 已確認的客戶或品牌線
- 新案 intake 時能直接命中

通過標準：
- 同線案件不再被重新問 `client_owner`
- 只補問尚未確認欄位

#### Blue-2: 每案 close 前都能產出 recap
條件：
- close 前觸發 recap

通過標準：
- recap 至少有：
  - client_owner_final
  - pm_owner_final
  - brian_exec_final
  - brian_role_final
  - income_nature_final
  - sidecar/rulebook/do-not-ask suggestions

#### Blue-3: Routing mismatch 能被記錄與回放
條件：
- AI 初判結果與人最終修正結果可同時保存

通過標準：
- 能回答：
  - 判錯在哪
  - 來自 sidecar 缺資料 / brand 缺資料 / routing rule 問題 / AI 語義判斷失誤

#### Blue-4: repeated clarification 會轉成 do-not-ask candidate
條件：
- 同類問題被 Brian 反覆回答

通過標準：
- 系統能提出 candidate
- review 時能決定是否正式升級

#### Blue-5: metric 開始可見地改善
條件：
- metrics 至少有兩輪可比資料

通過標準：
- repeated clarification 下降
- low-confidence routing 比例下降
- recap pending 比例下降

### Red Tests（若成立，就不能急著接官方 evolution repo）

#### Red-1: routing 仍大量依賴人工修正
判準：
- 高比例案件仍要由 Brian 大量手動重新分類

意義：
- target 還不穩
- 太早做 prompt evolution 只會放大錯誤規則

#### Red-2: sidecar / rulebook 常互相矛盾
判準：
- 同客戶線 / 品牌線在不同知識層結論不一致

意義：
- semantic memory 尚未收斂

#### Red-3: do-not-ask 機制沒有真正降低重問
判準：
- 已進 do-not-ask 的線仍頻繁被問

意義：
- workflow self-improvement loop 尚未跑順

#### Red-4: recap 常缺關鍵欄位
判準：
- client_owner_final / pm_owner_final / brian_exec_final / income_nature_final 經常 pending

意義：
- episode capture 還不穩
- 不適合拿去做官方 evolution 的 eval dataset

#### Red-5: schema 還在頻繁變動
判準：
- case / sidecar / recap contract 仍持續大改

意義：
- target interface 未穩定
- 先做 GEPA optimize 會追一個會動的目標

## 兩條系統的接口設計

### 1. 從 workflow loop 輸出的資料
未來可餵給官方 evolution repo 的東西：
- routing mismatch episodes
- corrected routing recap
- recap quality failures
- repeated clarification samples
- do-not-ask false negatives

### 2. 先不要輸出的資料
- 全部 raw chats
- 未確認的 customer/brand guesses
- 還在 schema 變動中的欄位

### 3. 官方 repo 最適合接的第一個 target
- routing engine prompt / heuristic text

而不是：
- 整個 PM playbook
- 整個 workflow system prompt
- 所有 skill 一起跑

## 實作順序建議

### Step 1 — 完成 Phase A 缺口
- review recap writer
- do-not-ask candidate detector
- routing mismatch tracker

### Step 2 — 完成 Phase B
- metrics schema
- metrics writer / aggregator
- baseline snapshot

### Step 3 — 定官方 evolution 輸入格式
- routing eval dataset format
- holdout split policy
- acceptance gate

### Step 4 — 只針對 routing target 試跑一次 evolution
- 單 target
- 單評估集
- 人工審查結果

## 建議文件與實作物

### 規劃文件（本輪應補齊）
- `docs/specs/brian-self-improvement-vs-hermes-self-evolution.md`
- `docs/specs/routing-mismatch-schema.md`
- `docs/specs/workflow-metrics-schema.md`

### 先做的實作物
- `review_recap_writer`
- `do_not_ask_candidate_detector`
- `routing_mismatch_tracker`
- `workflow_metrics_aggregator`

### 之後才接的實作物
- 官方 evolution repo 接口 adapter
- routing eval dataset exporter
- evolution run orchestrator

## 風險

1. 太早接官方 repo
- 會優化不穩定 target

2. 把 workflow loop 與 official evolution 混成一套
- 會讓人以為自我進化 = 直接優化 prompt
- 其實你最需要的是先學會業務規則

3. metrics 不先定
- 後面無法證明有沒有真的變好

## 建議的下一步

最有價值的下一步不是接官方 repo，而是：
1. `routing-mismatch-schema.md`
2. `workflow-metrics-schema.md`
3. review recap writer implementation plan

這三個完成後，再決定何時接 GEPA / DSPy optimize。

## 假設

- 你要的自我進化優先是「少重問、少重猜、少靠你手動糾正」，不是先優化 generic skill
- 你接受官方 evolution repo 屬於第二層 optimizer，而不是第一層 workflow core
- 你希望先把業務規則打穩，再做離線優化

## 決策建議

採用以下正式順序：
- Phase A 先跑順 workflow self-improvement loop
- Phase B 再定 metrics
- Phase C 最後才接官方 self-evolution repo，且只優化 routing target
