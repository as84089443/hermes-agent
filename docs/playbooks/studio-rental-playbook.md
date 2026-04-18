# Studio Rental Playbook

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 在棚租 / 場租這條資產收入線上的操作方式。

這條線的定位和一般接案完全不同：
- 它不是 Brian 核心執行收入
- 也不是典型 PM / 接案收入
- 它更接近資產營運與時段管理

所以這份 playbook 的目的，是把棚租從主動接案線裡真正拆出來，讓未來可以高度標準化與自動化。

## 2. 棚租線的定位

在 Brian AI workflow 中，棚租線應視為：
- `primary_lane = studio_rental`
- 收入性質 = 資產收入

它和商業案 / 婚禮案最大的不同是：
1. 核心資源不是 Brian 本人的時間，而是場地時段
2. booking 規則要比企業案更硬
3. 客戶價值不只看單次成交，也看場地使用風險與維護成本
4. 很多步驟適合模板化與自動化

## 3. 核心原則

### 3.1 不混入 Brian 主動執行收入
所有棚租案都應獨立標記為資產收入，不可混進 Brian 核心執行或 PM / 接案分析。

### 3.2 booking 條件比企業案更硬
- 原則上訂金後才算 `confirmed`
- 不能只靠口頭保留檔期

### 3.3 先保護場地，再追求成交
若客戶需求、用途、時間安排、風險不清楚，應優先保守，而不是先接了再說。

### 3.4 這條線要優先標準化
棚租線非常適合先做標準模板：
- 詢價回覆
- 場地說明
- 可租時段
- 訂金與取消規則
- 現場使用須知

## 4. 棚租線的流程

### Stage A：詢問進來
輸入常見來源：
- LINE / IG / 轉介紹
- 舊客回流
- 朋友介紹
- 現有租戶延伸詢問

AI 任務：
- 整理成棚租詢問卡
- 先判定是否真的是棚租案
- 標記：日期 / 時段 / 用途 / 人數 / 是否需設備

### Stage B：可租性判斷
要先確認：
- 日期與時段可不可租
- 用途是否合法 / 合適
- 人數與器材需求是否超過場地負荷
- 是否有特殊風險

若條件不明，停在 `clarifying`。

### Stage C：報價與條件
輸出內容通常應標準化：
- 場租價格
- 可用時段
- 是否含基礎設備
- 訂金規則
- 超時規則
- 取消規則
- 現場使用規則

這一階段不應靠臨場亂講。

### Stage D：訂金 / confirmed
- 訂金到帳後才能進 `confirmed`
- confirmed 後檔期正式鎖定
- 之後若改時段 / 改用途 / 改設備需求，要進 change review

### Stage E：執行前確認
要確認：
- 到場時間
- 離場時間
- 聯絡窗口
- 現場規則
- 是否需要額外協助 / 設備

### Stage F：使用與結束
- 確認是否準時進出
- 是否超時
- 是否產生額外費用
- 是否有損壞 / 清潔 / 異常

### Stage G：收款 / 結案
- 確認尾款
- 確認是否有額外費用
- 確認是否適合列為 recurring / 常租戶
- 寫入 recap

## 5. 棚租 intake 最少要問的問題

棚租詢問建議最少問：
1. 日期與時段？
2. 用途是什麼？
3. 大概幾人？
4. 是否需要額外設備 / 技術支援？

如果這四個都不清楚，不應直接報 confirmed 價格。

## 6. 棚租線的最低資料欄位

在一般 case 欄位外，建議至少補：
- rental_date
- rental_start_time
- rental_end_time
- rental_use_case
- expected_headcount
- extra_equipment_needed
- deposit_required
- deposit_received_at
- overtime_policy_applied
- damage_or_incident_note

## 7. 棚租線的關鍵控制點

### 7.1 Availability Gate
在報價前先確認：
- 有沒有檔期
- 場地是否適配用途

### 7.2 Booking Gate
- 訂金前不可 confirmed
- confirmed 後檔期正式鎖定

### 7.3 Change Review Gate
confirmed 後若變更以下任一項，需 review：
- 時段
- 使用用途
- 人數
- 額外設備需求
- 現場技術支援需求

### 7.4 Incident Gate
若發生：
- 超時
- 損壞
- 使用超出原約定
- 清潔異常
則不能直接 close，必須留下 incident note。

## 8. Brian / Chu / Jerry / AI 在棚租線的角色

### Brian
- 負責最終規則與高風險例外判斷
- 不應被每筆詢價拖進來做重複行政

### Chu
- 若未來有參與行政與後端營運，可承接部分標準流程

### Jerry
- 不應默認進入棚租主流程，除非有額外技術支援或特殊協作需求

### AI
最適合承接：
- 詢價摘要
- FAQ 回覆草稿
- 檔期整理
- 訂金提醒
- 使用規則模板
- 結案 recap 草稿

## 9. 哪些事情最適合先自動化

棚租線是整套 workflow 中最適合優先自動化的線之一。

### 第一優先
- 自動詢價整理
- 自動回覆草稿
- 自動列出可租資訊

### 第二優先
- 訂金提醒
- 行前提醒
- 尾款提醒

### 第三優先
- recurring 租戶辨識
- 常見客戶偏好摘要
- 場地使用風險標記

## 10. 棚租線常見錯誤

### 10.1 口頭保留檔期太久
這會讓場地資源被模糊佔住。

### 10.2 沒問用途就先報價
可能接到不適合的租用。

### 10.3 棚租案混進主動執行收入
這會讓經營分析失真。

### 10.4 沒記錄 incident
之後容易對同一類客人反覆踩坑。

## 11. 棚租 recap 要留下什麼

每個棚租案結束後，至少要留下：
- 實際使用時段
- 是否超時
- 是否有額外費用
- 是否有異常 / 損壞 / 清潔問題
- 是否適合列為 recurring renter
- 是否值得加入 do-not-ask-again 或風險備註

## 12. 與其他文件的關係

- 決策邊界：`brian-ai-workflow-decision-rails.md`
- 路由：`brian-ai-workflow-routing-rules.md`
- 狀態：`brian-ai-workflow-state-machine.md`
- 關卡：`brian-ai-workflow-phase-gates.md`
- 回顧學習：`review-and-learning-playbook.md`

## 13. 待補問題

- 是否要把場租 FAQ 與場地須知獨立成模板檔
- recurring 租戶是否要獨立做一張 sidecar
- 棚租是否要分純場地與場地+技術支援兩種子 lane
