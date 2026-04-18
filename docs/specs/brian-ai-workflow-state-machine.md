# Brian AI Workflow State Machine

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 的正式案件狀態機。

目的不是做漂亮流程圖，而是固定：
- 案件什麼時候算建立
- 什麼時候可以報價
- 什麼時候算成立
- 什麼時候開始 scope lock
- 什麼時候必須 change review
- 什麼時候能交付、請款、分帳、結案

之後：
- dashboard
- case detail
- AI 提醒
- recap writer
- 報價版控
- 收款與分帳追蹤
都要對齊這份狀態機。

## 2. 設計原則

### 2.1 沿用 bw-sop 精神，但翻譯成 Brian workflow 語言
- 先制度化，再自動化
- PM-driven，不讓 AI 越權
- 重要變更必須可追蹤
- 版本要能回看

### 2.2 一案只有一個主狀態
- 每個 case 在任一時間點只能有一個 `status`
- 其他資訊用欄位表達，不要額外發明平行狀態機

### 2.3 狀態機服務的是「下一步責任」
狀態本身不是裝飾。
每個狀態都要能回答：
- 現在卡在哪
- 誰負責下一步
- 能不能進下一關

### 2.4 AI 可以推進資訊，但不能越過關卡
AI 可以：
- 補問
- 摘要
- 建議
- 草擬訊息
- 提醒 queue

AI 不可以：
- 自己送正式報價
- 自己把案件標成 confirmed
- 自己批准 confirmed 後的 scope 變更
- 自己對客送正式催款

## 3. 正式狀態列表

v1 建議只保留以下狀態：

1. `intake`
2. `clarifying`
3. `ready_for_quote`
4. `quote_sent`
5. `soft_hold`
6. `confirmed`
7. `in_execution`
8. `delivered`
9. `billing`
10. `collected`
11. `closed`
12. `lost`

## 4. 狀態定義

### 4.1 `intake`

定義：
- 新需求剛進來
- 可能是 LINE、Telegram、Slack、Email、口頭整理
- 還沒有足夠資訊做正式 routing

進入條件：
- 收到新詢問
- 或手動建立一個新案件草稿

必要欄位：
- `title`（可暫名）
- `source`
- `raw_brief`
- `created_at`
- `current_owner`（若未指定，預設 Brian）

可轉出到：
- `clarifying`
- `ready_for_quote`
- `lost`

AI 可做：
- 整理 normalized brief
- 補問 2–4 題
- 建議 lane

AI 不可做：
- 直接跳過到 `quote_sent`

### 4.2 `clarifying`

定義：
- 已知道這是一個案件
- 但關鍵資訊不完整，仍需補問或人工釐清

典型缺口：
- 客戶是誰
- 檔期 / 交期
- 預算
- 誰做
- 是婚禮、商業、場租還是後製

進入條件：
- intake 後資訊不足
- 或 routing 有關鍵欄位無法判定

必要欄位：
- `raw_brief`
- `normalized_brief`
- `next_action`
- `next_owner`

可轉出到：
- `ready_for_quote`
- `lost`

AI 可做：
- 產生補問訊息草稿
- 標記 missing fields
- 建議先用哪個 lane

### 4.3 `ready_for_quote`

定義：
- 已足夠進入報價 / 接案判斷
- 不代表報價已送出

進入條件：
- 客戶 / lane / 基本需求 / 檔期已足夠判定
- `current_owner` 已明確

必要欄位：
- `customer_name`
- `primary_lane`
- `client_owner`
- `pm_owner`
- `budget_status`
- `due_date`（若有）

可轉出到：
- `quote_sent`
- `soft_hold`
- `confirmed`
- `lost`

備註：
- 對某些內部 / 已談妥案件，可跳過正式報價文字往 `confirmed`
- 但必須保留版本或決策紀錄

### 4.4 `quote_sent`

定義：
- 對客已送出某一版正式報價或正式合作條件

進入條件：
- 已存在 `quote_version`
- 該版本已明確送出

必要欄位：
- `quote_version`
- `artifact_version`（若有附正式說明或包）
- `updated_at`

可轉出到：
- `soft_hold`
- `confirmed`
- `quote_sent`（重送新版）
- `lost`

強制規則：
- 每次正式重送都必須建立新版本
- 不得覆蓋舊版本

AI 可做：
- 草擬報價訊息
- 整理相似案例
- 補提醒

AI 不可做：
- 自動送出正式報價

### 4.5 `soft_hold`

定義：
- 案件暫時保留檔期 / 資源
- 但尚未正式 confirmed

適用情況：
- 商業 / 企業案暫保
- 某些等待最終確認的合作案

不適用情況：
- 婚禮與棚租若制度上要求訂金成立，則不應亂用 soft hold 取代 confirmed

進入條件：
- PM 明確決定暫保
- 且符合 lane 規則

可轉出到：
- `confirmed`
- `quote_sent`
- `lost`

強制規則：
- `soft_hold` 不等於 booking 成立
- 不可因此自動佔滿所有資源

### 4.6 `confirmed`

定義：
- 案件正式成立
- 自此進入 scope lock 條件

進入條件依 lane 而異：

商業 / 企業案：
- 可用文字確認成立
- 或雙方已正式確認執行

婚禮 / 私人案：
- 依你的制度，通常要到訂金成立後

場租案：
- 依場租 booking 規則成立

共同客戶案：
- 需明確知道誰在主導下一步與交付

必要欄位：
- `client_owner`
- `pm_owner`
- `current_owner`
- `primary_lane`
- `quote_version` 或等價決策紀錄
- `confirmed_at`

可轉出到：
- `in_execution`
- `lost`

關鍵規則：
- `scope_lock_active = true`
- 之後若改：
  - 金額
  - 時數
  - 交付物
  - 人力
  - 主要執行角色
  - 品牌 / 平台 / 核心訊息
  必須進 `change review`

### 4.7 `in_execution`

定義：
- 案件進入實際執行
- 包含拍攝、後製、協作、場地準備等

進入條件：
- confirmed 後
- 已有最小執行分工
- 已知道誰做、何時做、交什麼

必要欄位：
- `executor`
- `next_action`
- `next_owner`
- `artifact_version`（若開始產出素材 / 交付物）

可轉出到：
- `delivered`
- `billing`
- `closed`（極少數內部小案）

AI 可做：
- 跟催素材
- 提醒檔期
- 整理交付清單
- 生成對內 progress summary

### 4.8 `delivered`

定義：
- 已完成約定交付
- 但帳務流程未必完成

進入條件：
- 客戶已收到交付物
- 或內部已完成交件

必要欄位：
- `artifact_version`
- `delivered_at`
- `deliverables`

可轉出到：
- `billing`
- `collected`
- `closed`

### 4.9 `billing`

定義：
- 已進入請款 / 開票 / 等待款項進帳階段

進入條件：
- 已可請款
- 或已開票但未收款

必要欄位：
- `billing_started_at`
- `amount_due`
- `invoice_reference`（若有）

可轉出到：
- `collected`
- `closed`

AI 可做：
- 提醒 PM / Brian
- 草擬請款與 follow-up 訊息

AI 不可做：
- 自動對客送正式催款
- 自動標記已收款

### 4.10 `collected`

定義：
- 對客款項已收齊

進入條件：
- 客戶款項已到帳

必要欄位：
- `collected_at`
- `amount_received`

可轉出到：
- `closed`

### 4.11 `closed`

定義：
- 案件完成所有營運閉環

進入條件：
- 已收款或確定不需收款
- 已完成分帳或記錄不分帳原因
- 已留下 case recap
- 已更新必要 sidecar / 規則

必要欄位：
- `closed_at`
- `case_recap_written = true`

可轉出到：
- 無

### 4.12 `lost`

定義：
- 案件未成交 / 取消 / 終止

進入條件：
- 明確不再推進

必要欄位：
- `lost_reason`
- `last_quote_version`（若曾報價）

可轉出到：
- 無

## 5. 狀態轉移圖（文字版）

標準主路徑：

`intake`
→ `clarifying`
→ `ready_for_quote`
→ `quote_sent`
→ `soft_hold`（可選）
→ `confirmed`
→ `in_execution`
→ `delivered`
→ `billing`
→ `collected`
→ `closed`

失單分支：
- `intake -> lost`
- `clarifying -> lost`
- `ready_for_quote -> lost`
- `quote_sent -> lost`
- `soft_hold -> lost`
- `confirmed -> lost`（罕見，但保留）

## 6. Scope Lock

正式定義：
- `scope lock = confirmed 後`

locked 後不可直接改的內容：
- 金額
- 執行天數 / 時數
- 交付物範圍
- 主要人力配置
- 平台 / 核心訊息
- 需人工審核的風險等級

遇到上述任一變更：
- 必須建立 `change review`
- 並保留前一版 `quote_version` / `artifact_version`

## 7. Change Review 何時啟動

以下任一情況，進入 formal change review：
- 客戶臨時加需求
- 客戶砍需求但要求維持價格
- 執行方式改變（如單機改雙機）
- 主要執行者改變
- 原本 Brian 不下場，後來要 Brian 下場
- 婚禮 / 場租 booking 條件改變
- 已送出版本被要求大改

change review 最小欄位應有：
- `case_id`
- `trigger_type`
- `changed_fields`
- `requested_by`
- `requires_new_quote_version`
- `approval_status`
- `decision_note`

## 8. 與 AI 的互動邊界

### AI 可直接參與的狀態
- `intake`
- `clarifying`
- `ready_for_quote`
- `in_execution`
- `delivered`
- `billing`
- `closed`（只做 recap / 整理）

### AI 只能草擬、不能定案的狀態
- `quote_sent`
- `confirmed`
- `billing`
- `change review`

### AI 明確不可越權的動作
- 自動送正式報價
- 自動把案件改成 confirmed
- confirmed 後跳過 change review
- 自動對客發正式催款
- 自動認定款項已收齊

## 9. 與不同 lane 的差異

### 商業 / 企業案
- 可使用 `soft_hold`
- 可由文字確認進 `confirmed`

### 婚禮 / 私人案
- booking / 訂金條件比較硬
- 不應用 `soft_hold` 取代正式成立
- 若屬麻花影像，需注意 Chu 的操作主控角色

### 場租 / 租棚案
- 應明確與主動執行收入分離
- 其 state machine 可沿用同框架，但 lane 與 recap 要標成資產收入

### 純後製案
- 可作為獨立案，也可作為 parent case 的子案
- 若是你接案後外發，容易偏 PM / 接案收入

### 共同客戶 / 共同 PM 案
- confirmed 前必須先搞清楚：
  - 誰是 current_owner
  - 誰是 executor
  - 誰負責最終對客交付

## 10. 與 BW-SOP 的映射

Brian workflow 與 bw-sop 的映射關係：
- `intake / clarifying` 對應 bw-sop 的 inquiry / qualified 前段
- `ready_for_quote / quote_sent / soft_hold / confirmed` 對應報價與 booking 軌
- `in_execution` 對應 production / technical handoff 後
- `delivered / billing / collected / closed` 對應交付、請款、收款、分帳、結案

沿用的核心精神：
- owner 明確
- quote version 明確
- confirmed 後 scope lock
- change review 正式化
- AI 不越權

## 11. v1 必須守住的 6 條硬規則

1. No ownerless case.
2. No confirmed case without minimal owner / lane / quote decision record.
3. No post-lock change without change review.
4. No approval without exact version reference.
5. No AI action outside allowed rails.
6. No case closed without recap and rule update decision.

## 12. 待補問題

- 婚禮成立條件是否要寫成獨立 booking 規範引用
- `operating_controller` 是否應正式進 data model
- `billing` 與 `invoice_pending` 是否在 Brian workflow 需要合併或拆開
- 共同客戶線在 confirmed 前是否要有額外 handoff gate
