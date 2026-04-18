# Brian AI 工作流 v1

日期：2026-04-14

目標：
把 Brian 目前的真實經營結構，收斂成一套可以逐步自動化的 AI 工作流；並把既有 BW-SOP 的 decision rails 當成治理底盤，而不是另起一套互相打架的系統。

## 一句話定位

這不是再做一個聊天助理，也不是做單一報價工具。
這是一個以「案件 operating system」為核心的 AI 工作流：
從 lead intake → 分流 → 報價/接案 → 執行 → 交付 → 收款/分帳 → 回訪/學習，全流程有 owner、有狀態、有資料欄位、有 AI 能幫忙的節點。

## 先用目前已知的現實，不再空想

目前 Brian 的經營結構，已可先視為 5 條線：

1. Brian 核心執行收入
- 你本人直接下場做

2. Brian PM / 接案收入
- 你接案、控交付、但不一定親自做

3. Brian 兼具 PM 與執行
- 最常見也最容易爆掉的角色

4. 共同客戶 / 共同 PM 線
- Brian + Jerry
- Brian + Chu
- 或共同品牌（如麻花影像）

5. 資產收入線
- 例如當下攝影棚租棚

這 5 條不能再混在一起記。
AI workflow 必須一進件就先把案子分到正確 lane。

## 與 BW-SOP 的整合原則

這套 v1 直接吸收 BW-SOP 的決策 rails：

1. 先制度化，再自動化
- 先定 owner、state、change review、artifact snapshot
- 後做 webhook / 全自動發送 / 重型自動化

2. PM-driven，不是 agent 越權系統
- AI 幫分流、整理、提醒、草稿
- 不替 Brian 做商務與風險最終決策

3. 先自由 intake，再最少補問
- 不一開始逼填完整表單
- 先吃自然語言，再補 2–4 題關鍵問題

4. 不可無 owner
- 每個 case 建立時就要有 current_owner

5. 不可無 exact version 的 approval
- 報價、交付、請款、變更都要可追蹤版本

6. phase 驗收必須可見
- 每個 phase 完成時要能真的打開頁面做事

## v1 工作流主幹

### Stage 0 — Intake

輸入來源：
- LINE / Telegram / Slack / Email / 電話整理紀錄
- BNI 轉介
- 舊客回流
- 麻花影像自來客
- 場租詢問

AI 任務：
- 把原始訊息整理成 normalized brief
- 自動判斷缺口
- 只補問最少問題

最少補問 4 題：
1. 這是哪一類案子？（拍攝 / 後製 / 婚禮 / 場租 / 其他）
2. 客戶是誰？
3. 這案需要 Brian 親自做嗎？
4. 截止日 / 檔期是什麼？

輸出：
- lead card
- normalized brief
- 建議 lane

### Stage 1 — Triage / Routing

系統要先判斷案子進哪條線：

A. Brian 核心執行
B. Brian PM / 接案
C. Brian 兼具 PM + 執行
D. 共同客戶 / 共同 PM
E. 資產收入（場租）

Routing rules（v1 版）：
- 客戶是 Brian 的，通常 PM 先預設 Brian
- 若 Brian 親自下場且是主輸出 → 核心執行
- 若 Brian 接案但外發 → PM / 接案
- 若共同客戶且收入接近 → 共同客戶 / 共同 PM
- 若婚禮品牌 → 麻花影像線
- 若是租棚 → 資產收入線

輸出：
- case created
- current_owner
- lane
- next_action

### Stage 2 — Quote / Deal

AI 任務：
- 依案型產出報價草稿
- 產出對客回覆草稿
- 補上注意事項與交付界線

Brian 任務：
- 最終定價
- 決定是否接
- 決定交給誰做

輸出：
- quote version
- approval status
- 成交 / 未成交

### Stage 3 — Delivery Planning

AI 任務：
- 依 lane 建立執行 checklist
- 自動拆成：前置 / 拍攝 / 後製 / 交付 / 收款
- 指派 owner / executor / approver

角色分配邏輯：
- Brian：高價值對客 / 主決策 / 核心執行
- Chu：婚禮 / 後製 / 婚禮品牌主控
- Jerry：共同客戶 / 共同執行 / 合作案
- AI：行政 PM、追蹤、提醒、草稿、彙整

### Stage 4 — Execution

AI 任務：
- 跟催素材
- 跟催檔期
- 每週輸出簡報式狀態摘要
- 對客 draft reply

這裡最重要的是把 Brian 從重複行政與追蹤中抽離。

### Stage 5 — Delivery / Billing / Split

AI 任務：
- 交付提醒
- 修稿整理
- 請款提醒
- 分帳記錄整理

關鍵：
這裡要回寫到收入主表，並保留：
- 客戶歸屬
- PM 歸屬
- Brian 是否出工
- Brian 角色

### Stage 6 — Review / Learn

每個完成案件，至少要能回答：
- 客戶是誰的？
- PM 是誰？
- Brian 有沒有親自做？
- Chu / Jerry 是否參與？
- 這案是可複製、可委派，還是必須 Brian 親自做？

輸出：
- case recap
- reusable rule
- customer update
- sidecar update

## 最小資料結構（不要過度設計）

v1 只需要一個 case 主表 + 幾個 sidecar。

### A. case 主表

必要欄位：
- case_id
- title
- source
- customer_name
- client_owner
- pm_owner
- brian_exec
- brian_role
- lane
- brand_or_system
- current_owner
- executor
- approver
- budget_status
- due_date
- status
- raw_brief
- normalized_brief
- next_action
- next_owner
- quote_version
- artifact_version
- created_at
- updated_at

### B. customer sidecar

用途：
- 不污染共享匯款表
- 讓 Hermes 自己記住客戶歸屬與關係

必要欄位：
- customer_name
- owner_guess
- pm_guess
- relationship_type
- confidence
- notes

### C. brand sidecar

目前至少要支援：
- 麻花影像
- B.W.Studio
- 其他之後擴充的品牌/產品線

### D. income normalization table

這張已經在做了，繼續沿用：
- historical_income_normalized_v*.json/csv

## v1 必做的 3 個自動化

### 1. Intake normalizer

輸入：
- 原始訊息

輸出：
- normalized brief
- 補問問題
- 初步 lane

這是第一優先。

### 2. Routing engine

根據已確認規則，自動決定：
- 你的客戶 / 共同客戶 / 上游合作方
- PM 歸屬
- Brian 是否該親自下場
- 交給 Brian / Chu / Jerry / AI 哪一條路

### 3. Case recap writer

每案結束後自動輸出：
- 這案怎麼分類
- 哪個客戶線
- 哪個品牌線
- 是否可複製
- 哪條規則該更新

這樣資料才會越跑越準，而不是每次回頭重新猜。

## Brian AI 工作流 v1 的真正目的

不是為了把所有事自動化。
而是為了讓 Brian：
- 不再靠腦袋硬記客戶/品牌/角色邏輯
- 不再每個案子都重新判斷一次誰是客戶、誰是 PM、誰該做
- 把真正該由 AI 處理的行政、追蹤、整理、補問交出去
- 把自己集中在高價值決策、成交與核心輸出上

## 和 bw-sop 整合的方式

不是把 bw-sop 直接搬過來，而是把它當 donor：

導入內容：
- PM-driven
- state machine
- scope lock
- change review
- exact artifact version
- owner / handoff / acceptance rails

對 Brian 工作流的翻譯：
- 沒 owner 不准進下一階段
- 沒 quote version 不准正式報價
- 沒 final artifact version 不准標記完成
- 變更需求要進 change review，不要口頭漂移

## 下一步建議（直接可做）

### Phase 1
先做 3 個物件：
1. case 主表 schema
2. customer sidecar schema
3. routing rules v1

### Phase 2
把 intake normalizer 跑起來：
- 吃訊息
- 出 normalized brief
- 自動補問
- 進主表

### Phase 3
把你現在已整理的 historical income / customer sidecar / brand sidecar 接到 routing layer
讓新案一進來，就能吃舊知識，而不是每次重新問你。
