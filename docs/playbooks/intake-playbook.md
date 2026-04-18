# Intake Playbook

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 的 intake 階段應如何操作。

它回答的是：
- 新詢問進來時先做什麼
- AI 應先整理什麼
- 哪些資訊一定要補齊
- 什麼情況可直接進 routing
- 什麼情況必須停在 clarifying

這份 playbook 是給：
- Brian
- Chu
- Jerry
- 未來的 PM / 行政角色
- AI intake normalizer
共同使用的操作手冊。

## 2. Intake 的定位

Intake 不是填表而已。
它的目的有三個：

1. 把原始詢問轉成可判斷的案件資訊
2. 盡快知道這案應進哪條 workflow lane
3. 在不打擾客戶太多的前提下，補足最小關鍵資訊

所以 intake 階段的原則不是「問完所有問題」，
而是「只問足以 routing 的最少問題」。

## 3. Intake 的核心原則

### 3.1 先自由描述，再最少補問
新詢問進來時，先收原始訊息。
不要一開始就逼客戶填完整欄位。

### 3.2 補問不能超過必要程度
優先只補：
- 這是什麼案型
- 客戶是誰
- 截止日 / 檔期
- 是否需要 Brian 親自下場

### 3.3 已知客戶線不要重問
若此客戶或品牌已在 sidecar / rulebook 裡有明確規則：
- 直接套用
- 不重問已知資訊

### 3.4 補不齊可以先 pending
若客戶暫時沒回、Brian 一時也想不起來：
- 允許保留 pending
- 不要為了填滿欄位亂猜

## 4. Intake 階段的輸入來源

可能來源：
- LINE 訊息
- Telegram 指令或對話
- Slack 對話 / thread
- Email
- 口頭轉述後人工建立
- BNI 轉介
- 舊客回流
- 麻花影像自來客
- 場租詢問

每個來源進來後，都先統一轉成：
- raw_brief
- source
- created_at
- current_owner（若未指定先預設 Brian）

## 5. Intake 操作流程

### Step 0：接收原始訊息
保留原始描述，不要先過度整理。

必存：
- 原始文字
- 來源 channel
- 時間
- 若知道，先記客戶名或聯絡人名

### Step 1：AI 做第一次 normalization
AI 先把 raw brief 轉成：
- 一句話案件摘要
- 可能的案型
- 可能的客戶 / 品牌 / 系統線
- 缺失欄位
- 建議下一步

### Step 2：先查知識層
在補問之前，先查：
1. analysis rulebook
2. customer sidecar
3. brand sidecar
4. historical income / calendar patterns

如果已知：
- 這是碼非線
- 這是麻花影像線
- 這是某 BNI 夥伴客戶
- 這是場租
那就不要再問已知問題。

### Step 3：補問最少問題
若仍不足以 routing，才補問。

v1 補問上限：2–4 題。

優先順序：
1. 客戶是誰？
2. 這是什麼類型的案子？
3. 截止日 / 檔期是什麼？
4. 需要 Brian 親自做嗎？

### Step 4：判斷進哪個狀態
- 資訊不足 → `clarifying`
- 足夠進報價 / 接案判斷 → `ready_for_quote`
- 若只是剛進來且還沒整理 → `intake`

### Step 5：建立最小 case
即使資訊不完整，也可以先建立 minimal case。

最小 case 應至少包含：
- title
- source
- customer_name（可暫名）
- raw_brief
- normalized_brief
- primary_lane（若可判）
- current_owner
- status
- next_action
- next_owner

## 6. v1 最少補問問題庫

### 類型 A：案型不清
- 這次是拍攝、後製、婚禮、場租，還是其他？

### 類型 B：客戶不清
- 這是你的客戶、共同客戶，還是上游合作方？
- 如果你只記得人，不記得公司，也先記人名

### 類型 C：執行模式不清
- 這案需要你本人下場嗎？
- 還是你只接案 / 分工 / 交付？

### 類型 D：時間不清
- 檔期 / 交期大概在哪時候？

## 7. AI normalizer 輸出格式

每次 intake 後，AI 應該輸出一份固定結構：

- `summary`
- `lane_candidate`
- `customer_candidate`
- `brand_candidate`
- `client_owner_candidate`
- `pm_owner_candidate`
- `brian_exec_candidate`
- `missing_fields`
- `recommended_questions`
- `recommended_next_status`
- `recommended_next_owner`

目的：
讓後續 routing engine 可以直接吃。

## 8. 哪些情況可直接略過補問

以下情況可直接進下一步：

### 8.1 已知客戶 + 已知品牌 + 已知案型
例如：
- 碼非某延伸案
- 麻花影像婚禮線
- 已確認過的立方品 / 雲祥 / 小白故事線

### 8.2 場租詢問
若明確是租棚 / 場租：
- 直接進 `studio_rental` lane
- 補問檔期、時段、用途即可

### 8.3 已知 recurring 案
若是 recurring / 老客固定案：
- 優先查舊 case 與 recurring 規則
- 不要從零重問

## 9. Intake 常見錯誤

### 9.1 一開始問太多
錯誤：
- 預算多少？
- 幾機？
- 幾個人？
- 格式？
- 音控？
- 直播平台？
- 幾版修稿？
在客戶第一句話後全部一起問

正確：
- 先取得足夠 routing 的最少資訊
- 細節留到 `ready_for_quote` 後

### 9.2 沒查 rulebook 就重問
若客戶線已被確認，重問等於浪費 Brian 認知與時間。

### 9.3 把 pending 當成錯誤
pending 不是失敗。
pending 是誠實。
亂猜才是錯誤。

### 9.4 把 intake 當成報價
intake 的工作是分類與補齊，不是直接定價。

## 10. 與不同 lane 的 intake 差異

### 10.1 商業 / 企業案
最重要先確認：
- 客戶 / 上游關係
- 案型
- 檔期
- 是否 Brian 要親自下場

### 10.2 婚禮 / 私人案
最重要先確認：
- 是不是麻花影像線
- 日期 / 地點
- 是平面、動態還是混合
- 誰主控（常偏 Chu）

### 10.3 場租案
最重要先確認：
- 日期 / 時段
- 用途
- 是否需要額外設備

### 10.4 純後製案
最重要先確認：
- 原始素材是否齊
- 截止日
- 交付格式
- 是否是子案 / 掛主案

## 11. Intake 完成標準

一個 intake 算完成，不是因為欄位全部填滿，
而是因為已經能明確回答：

1. 這是什麼類型的案子？
2. 客戶大致是誰？
3. 要不要 Brian 親自做？
4. 現在應該進哪個狀態？
5. 下一步誰負責？

只要這五件事能回答，案件就可以往下走。

## 12. 與其他文件的關係

- 決策邊界看：`brian-ai-workflow-decision-rails.md`
- 欄位定義看：`brian-ai-workflow-data-model.md`
- 分流邏輯看：`brian-ai-workflow-routing-rules.md`
- 狀態轉移看：`brian-ai-workflow-state-machine.md`

## 13. 待補問題

- intake 正式表單是否要分 lane 動態變欄位
- BNI 轉介案件是否要額外記介紹人回報欄位
- 婚禮 / 場租 / recurring 案是否要有不同的 intake shortcut
