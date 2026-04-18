# Brian AI Workflow Phase Gates

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 在每個 phase 的 control points：
- 何時可進入下一階段
- 何時必須停下來補資料
- 何時需要 Brian 人審
- 何時需要正式 change review
- 何時可視為完成

它的作用是把：
- decision rails
- data model
- routing rules
- state machine
- intake playbook

串成同一條可執行的關卡鏈。

如果沒有這份文件，PM playbook 很容易寫成一堆任務清單，卻沒有真正的 gate。

## 2. 核心原則

### 2.1 每個 phase 都必須有 entry 與 exit criteria
不能只說「開始做」「做完了」，而要明確知道：
- 進來前要有什麼
- 出去前要留下什麼

### 2.2 每個 phase 都必須有 owner
若沒有 owner，就不能視為進入該 phase。

### 2.3 每個 gate 都要可見
這些 gate 之後必須能在 UI 上被看見，而不是藏在腦中：
- waiting on clarification
- ready for quote
- waiting on approval
- scope lock active
- ready for billing
- ready to close

### 2.4 AI 只能幫你跨 gate，不可替你跳 gate
AI 可以幫：
- 補齊資訊
- 草擬內容
- 提醒風險
- 建議下一步

但 AI 不能：
- 自己宣布 confirmed
- 自己跳過變更審查
- 自己把案件標成 collected / closed

## 3. Phase 全覽

Brian AI workflow v1 建議分成 7 個 phase：

1. Intake
2. Clarify
3. Quote / Deal
4. Confirm / Lock
5. Execute
6. Deliver / Bill
7. Close / Learn

## 4. Phase 1 — Intake Gate

### 4.1 目的
把原始詢問轉成一個可被 routing 的 case。

### 4.2 Entry Criteria
- 收到原始詢問或手動新增案件

### 4.3 最低必要欄位
- `title`
- `source`
- `raw_brief`
- `created_at`
- `current_owner`（預設可先是 Brian）

### 4.4 AI 可做
- 產出 normalized brief
- 補問 2–4 題
- 產出 lane candidate
- 標記 missing fields

### 4.5 不可跳過的控制點
- 沒有 raw_brief，不能算 intake 完成
- 沒有 current_owner，不能進下一階段

### 4.6 Exit Criteria
以下至少成立：
- 已能大致判斷案型
- 已有客戶名稱或暫名
- 已有下一步與 next_owner

### 4.7 可轉入
- `clarifying`
- `ready_for_quote`
- `lost`

## 5. Phase 2 — Clarify Gate

### 5.1 目的
補足 routing 與報價前必須知道的最小資訊。

### 5.2 Entry Criteria
- Intake 完成
- 但資訊不足以進 quote 或直接 routing

### 5.3 最常見缺口
- 客戶是誰
- 這是哪條 lane
- 檔期 / 截止日
- 是否需要 Brian 親自下場
- 是否已有預算感

### 5.4 AI 可做
- 整理最少補問問題
- 根據 sidecar 補可能值
- 幫 Brian 標記 pending 欄位

### 5.5 必須停住的條件
若以下任一缺失，不能進 quote：
- `customer_name` 無法辨識
- `primary_lane` 無法判斷
- `client_owner` 完全無法猜
- `current_owner` 未明確

### 5.6 Exit Criteria
以下至少成立：
- customer_name 有值
- primary_lane 已可判
- client_owner / pm_owner 至少有 candidate
- Brian 是否需親自下場至少可初判

### 5.7 可轉入
- `ready_for_quote`
- `lost`

## 6. Phase 3 — Quote / Deal Gate

### 6.1 目的
讓案件進入可報價、可決定是否接案的階段。

### 6.2 Entry Criteria
- Clarify 完成
- 已有最小必要資訊

### 6.3 必填欄位
- `customer_name`
- `primary_lane`
- `client_owner`
- `pm_owner`
- `budget_status`
- `current_owner`

### 6.4 AI 可做
- 產生報價草稿
- 顯示類似歷史案件
- 建議 lane、風險、價格參考

### 6.5 人審 gate
以下必須 Brian / PM 決定：
- 是否正式送出 quote
- 是否進 soft hold
- 是否直接 confirmed

### 6.6 不可跳過的規則
- 正式送出一定要有 `quote_version`
- 每次重送都要新版本
- 不可覆蓋舊版本

### 6.7 Exit Criteria
- 正式送出報價 → `quote_sent`
- 企業案先暫保 → `soft_hold`
- 已談妥成立 → `confirmed`
- 不做 → `lost`

## 7. Phase 4 — Confirm / Lock Gate

### 7.1 目的
正式確立案件成立，並啟動 scope lock。

### 7.2 Entry Criteria
- 已有明確 deal 決策
- quote / booking 條件已成立

### 7.3 Lane-specific 成立條件

商業 / 企業案：
- 可由文字確認成立
- 或雙方確認執行

婚禮 / 私人案：
- 原則上訂金後才 confirmed

棚租案：
- 原則上訂金後才 confirmed

共同客戶案：
- 至少要先知道誰 current owner、誰負責交付

### 7.4 一旦 confirmed 就啟動的規則
- `scope_lock_active = true`
- 需記錄 `confirmed_at`

### 7.5 Confirmed 後不可直接改的東西
- 金額
- 時數 / 天數
- 交付物
- 主要人力
- 平台 / 核心訊息
- 風險等級

### 7.6 若改上述內容
- 一律進 `change review`

### 7.7 Exit Criteria
- 已具備最小執行分工
- 可正式進 execution

### 7.8 可轉入
- `in_execution`
- `lost`（極少數）

## 8. Phase 5 — Execution Gate

### 8.1 目的
進入拍攝、後製、協作、場地執行等實際產出階段。

### 8.2 Entry Criteria
- confirmed
- 已知 executor / owner / next action

### 8.3 最低要求
- `executor` 不可空
- `next_action` 不可空
- `next_owner` 不可空

### 8.4 AI 可做
- 跟催素材
- 跟催交期
- 整理當前風險
- 產出 progress summary

### 8.5 執行期 change review 觸發
如果 confirmed 後發生：
- 客戶加需求
- 人力改變
- Brian 從不下場變要下場
- 婚禮 / 場租條件改變
則需正式進 change review

### 8.6 Exit Criteria
- 已完成約定交付物
- 已可明確標記 delivered

### 8.7 可轉入
- `delivered`

## 9. Phase 6 — Deliver / Bill Gate

### 9.1 目的
把「做完」和「收完錢」分開。

### 9.2 Delivered Entry Criteria
- 已交出約定成果
- 已有 artifact version / deliverables summary

### 9.3 Delivered 後不可直接等於 close
原因：
- 還可能沒請款
- 還可能沒收款
- 還可能沒分帳

### 9.4 Billing Entry Criteria
- 已可請款
- 或已開票但未收款

### 9.5 Billing 階段 AI 可做
- 提醒 PM / Brian
- 草擬請款 / follow-up 訊息

### 9.6 Billing 階段 AI 不可做
- 自動對客送正式催款
- 自動標記已收款

### 9.7 Collected Entry Criteria
- 客戶款項已實際到帳
- 已記錄 collected_at / amount_received

### 9.8 Exit Criteria
- 已收款，可進 close

## 10. Phase 7 — Close / Learn Gate

### 10.1 目的
讓案件真的結束，而不是只停在做完。

### 10.2 Entry Criteria
- 已收款，或已完成內部財務策略
- 已完成分帳或記錄不分帳原因

### 10.3 Close 前必須完成
- `case recap`
- 收入性質回寫
- 必要 sidecar 更新
- 若是 recurring / 客戶線案例，標記可回看價值

### 10.4 Close 後應輸出
- final delivery summary
- billing / collection status
- payout status
- 是否可複製
- 哪條規則應更新

### 10.5 Exit Criteria
- `closed_at` 有值
- `case_recap_written = true`

## 11. Cross-Phase Control Rules

### 11.1 No ownerless case
任何 phase 都不可無 owner。

### 11.2 No quote without quote_version
正式報價一定要能被回看。

### 11.3 No post-lock change without review
這是整套系統最重要的控制點之一。

### 11.4 No close without recap
否則系統永遠學不會。

### 11.5 No repeated questioning of already-settled knowledge
若 rulebook / sidecar 已有答案，就不得再把同一題丟回 Brian。

## 12. AI 與 Human 的 phase 分工

### AI 主責
- intake normalization
- 最少補問
- lane candidate
- queue / reminder
- progress summary
- case recap 草稿

### Human 主責
- 正式報價送出
- confirmed 成立
- confirmed 後 scope 變更核准
- 對客正式催款
- 收款確認
- 最終 close

## 13. 這份文件與其他文件的關係

- 規則邊界：`brian-ai-workflow-decision-rails.md`
- 欄位與實體：`brian-ai-workflow-data-model.md`
- routing 決策：`brian-ai-workflow-routing-rules.md`
- intake 操作：`intake-playbook.md`

## 14. 待補問題

- wedding lane 的 booking 細則是否要獨立成 booking appendix
- `operating_controller` 是否應成正式欄位
- `billing` 是否要拆成 `invoice_pending` 與 `collection_followup`
- recurring / long-running cases 是否要加 `review checkpoint` 機制
