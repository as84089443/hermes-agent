# Brian AI Workflow Donor Triage Ledger v1

日期：2026-04-16

用途：
- 先把 donor / 方法 / 來源做成可升降級的 triage ledger
- 避免 donor 直接混進 v1 主體，卻沒有分類、邊界與回看條件
- 作為 se-005 後續升格的證據補件

依據脈絡：
- `docs/plans/2026-04-14-brian-ai-workflow-design-convergence.md`
- `docs/specs/brian-ai-workflow-v1-v1_1-boundary.md`
- `/Users/brian/wiki/concepts/hermes-ai-department-rebuild-blueprint.md`
- `/Users/brian/wiki/concepts/hermes-ai-department-ecosystem-map.md`
- `/Users/brian/wiki/concepts/control-center.md`
- `/Users/brian/wiki/concepts/skills-boss-mode-panel.md`

建議新增文件名稱：
- `docs/specs/brian-ai-workflow-donor-triage-ledger.md`

| donor | classification | scope | why now / not now | revisit trigger |
| --- | --- | --- | --- | --- |
| BW-SOP donor | adopt | decision rails、state machine、scope lock、change review、owner/handoff discipline | 已在 convergence 與 v1 blueprint 中被明確指定為 governance base；這是 v1 先制度化再自動化的直接底盤 | 若實作中出現 lane-specific 例外太多、無法用現有 rails 承接，再補 translator appendix，但不改其 adopt 地位 |
| thinking-hound-mode | adopt | 老闆模式下的 problem framing、research-to-plan、決策前收斂方法 | control-center 與 skills-boss-mode-panel 已把它放在高槓桿 donor 包；適合直接補強 triage、升格評估與證據整理 | 若實際使用中只剩命名價值、沒有穩定產出固定 deliverable，再降回 watchlist |
| OpenClaw transfer | watchlist | donor library 的按需借力入口，不是預設全載 | wiki 已明確寫「donor library，不是日常預設全載」；現在適合保留為來源池，不適合直接當主殼或默認依賴 | 當某個 imported skill 在 3+ 次真實任務中重複有效，且能映射 canonical schema，再把該 slice 升為 adopt |
| workspace-production | adopt | production workspace segmentation、artifact staging、執行中專案的資料落位參考 | ecosystem map 已把 `workspace-*` 視為已驗證過的部門切分參考；其中 production 最接近 v1 closed loop 的執行層 | 若實作發現 folder / artifact contract 無法穩定承接 production slice，再回頭補 schema 或降成 watchlist |
| workspace-content | watchlist | content assembly、campaign/material organization、內容工作包切分 | 與 ContentStudio / content package 很近，但目前 repo 主軸仍應先固定 canonical schema 與 closed loop，不宜直接把舊內容工作台照搬 | 當 brief → content package 的 artifact contract 固定後，可升為 adopt，吸收其欄位與資料夾慣例 |
| workspace-qa | watchlist | QA gate、review checklist、publish 前驗收視角 | phase gates 已要求 gate 必須可見；QA slice 明顯有價值，但現在先應由 canonical approval / review model 主導，不宜先搬第二套 QA 殼 | 當 approval_pending / review / publish_pack_ready 的主狀態已穩定，且需要更細 QA checklist 時升格 |
| gstack | watchlist | planning、review、investigate、guard 類方法包 | control-center 與 skills catalog 都把它定位成高槓桿 donor，但較像方法加速器，不是 Brian workflow 的 source-of-truth | 當 triage / review 任務需要更固定的 multi-step review cadence，且可轉成 playbook，再升為 adopt method |
| workspace-ai-biz | not-now | 營運管理、商務脈絡、跨部門業務工作台參考 | 對 Brian 真實經營有幫助，但不是 v1 closed loop 的最前 blocker；太早納入容易把 case OS 拉回大而全 biz OS | 當 client_owner / pm_owner / revenue lane 已穩定，且出現大量跨部門商務協調需求時再重開 |

這份 ledger 如何幫助 se-005 補證據：
- 把 donor 討論從「感覺可借」變成有分類、有 scope、有升降級條件的證據表。
- 可直接對照 wiki 既有原則：只做 slice migration、先映射 canonical schema、只優先服務 v1 closed loop。
- 能證明 se-005 不是一次性拍腦袋升格，而是先有 adopt / watchlist / not-now 的前置 triage。
- 後續只要補上真實案例次數、失敗/成功樣本，就能把 watchlist 項目升格成正式 spec 或 playbook。