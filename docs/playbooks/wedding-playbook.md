# Wedding Playbook

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 在婚禮 / 私人案線的操作方式。

它不是一般商業案的縮小版，因為婚禮線具有幾個特殊性：
- 多數不是冷啟動客戶，而是關係導向 / 口碑導向
- booking 成立條件較硬，通常是訂金後才算 confirmed
- 品牌層不能忽略，尤其麻花影像已是共同經營子品牌
- Chu 在實際運作上常是主控角色
- 客戶情緒、信任、即時回覆與交付感受，權重比企業案高

因此 wedding playbook 必須和一般商業案分開寫。

## 2. 婚禮線的定位

婚禮線在 Brian AI workflow 裡，不只是「另一種案型」，而是一條獨立的經營線：
- 客戶決策情緒強
- 服務感知高
- 交付期待高
- recurring 較少，但口碑轉介紹很強
- 很多案子與麻花影像、Chu、Brian、Jerry 的角色配置綁在一起

## 3. wedding lane 的主原則

### 3.1 主 lane
- `primary_lane = wedding_private`

### 3.2 booking 規則
- 原則上訂金後才算 `confirmed`
- 單靠文字確認，不足以視為正式成立

### 3.3 品牌優先判斷
若命中以下任一條件，先判為婚禮品牌線：
- 麻花影像
- VAF
- 婚禮 / 早儀 / 午宴 / 婚攝 / SDE / 抓周等關鍵詞

### 3.4 Chu 的操作角色
婚禮線中，需預設存在一個事實：
- `pm_owner` 可能是共同
- 但實際 `operating_controller` 常偏 Chu

因此系統上不能只看 PM owner，而要在操作層保留：
- 誰實際主控客戶互動
- 誰主控後製 / 交付

## 4. 婚禮線 Intake

### 4.1 最少要知道的資訊
- 日期
- 地點
- 是平面 / 動態 / 雙機 / 混合
- 是否屬麻花影像線
- 客戶或介紹來源
- 是否已有訂金 / booking 傾向

### 4.2 若是已知品牌線
若已知是麻花影像 / VAF / 既有婚禮合作線：
- 不要再重問基本品牌歸屬
- 直接進 wedding lane routing

### 4.3 最少補問問題
1. 日期與時段？
2. 類型是婚禮 / 抓周 / 其他私人活動？
3. 要平面、動態，還是都有？
4. 目前是詢價、確認檔期，還是已經接近 booking？

## 5. wedding lane 的角色分工

### 5.1 Brian
Brian 在婚禮線常見角色：
- 客戶關係建立 / 收斂關鍵需求
- 重要拍攝執行
- 高價值協調 / 最後決策
- 部分案件的主輸出

### 5.2 Chu
Chu 在婚禮線常見角色：
- 實際主控 PM
- 後製主控
- 客戶溝通主控
- 婚禮品牌系統的穩定操作者

### 5.3 Jerry
Jerry 在婚禮線常見角色：
- 共同執行
- 協作攝影 / 動態
- 部分共同客戶線的合作主力

### 5.4 AI
AI 在婚禮線應做：
- intake normalization
- FAQ / 補問草稿
- 檔期整理
- 執行 checklist
- 後製 / 交付 / 修稿追蹤
- 結案 recap

AI 不應做：
- 自動確認 booking
- 自動對客送出正式條款
- 自動答應額外需求

## 6. wedding lane 的典型流程

### Stage A：詢問 / intake
- 收到訊息
- 判定是否為婚禮線
- 若已知品牌線，直接掛品牌

### Stage B：檔期 / 初步需求確認
- 確認日期、地點、服務類型
- 看是否有檔期空間
- 決定是否進報價

### Stage C：報價 / proposal
- 整理方案
- 明確平面 / 動態 / 人力 / 交付範圍
- 對客送正式版本

### Stage D：訂金 / confirmed
- 訂金後 `confirmed`
- 啟動 scope lock

### Stage E：執行前交接
- 確定誰出班
- 確定器材 / 時程 / 聯絡點
- 確定後製責任

### Stage F：拍攝與後製
- 現場執行
- 素材整理
- 後製安排
- 若有 teaser / SDE / 即時出圖需特別標記

### Stage G：交付 / 修稿
- 交付版控
- 修稿輪次
- 確認最終交件

### Stage H：收款 / 分帳 / 結案
- 收尾款
- 確定 Chu / Jerry / 外包分工與分帳
- 留下案例 recap
- 標記是否可成為模板 / 品牌素材 / 轉介紹來源

## 7. wedding lane 的主要控制點

### 7.1 Booking Gate
- 未訂金前，不可視為正式 confirmed

### 7.2 Scope Lock
confirmed 後若變更：
- 服務類型
- 時數
- 交付數量
- 是否加 SDE / teaser / 其他額外內容
- 出班人力
必須有正式 change review

### 7.3 Delivery Gate
- 不可把 rough cut 當 final delivery
- 交付版本需可回溯

### 7.4 Closing Gate
- 不可交完片就直接算結案
- 必須補：
  - 收款狀態
  - 分帳狀態
  - 案例評語 / 風格備註
  - 是否可轉為婚禮模板資產

## 8. wedding lane 的資料欄位特別要求

在一般 case 欄位之外，婚禮線特別建議補：
- event_date
- venue
- package_type
- photo_required
- video_required
- teaser_required
- sde_required
- primary_operator
- postproduction_owner
- revision_rounds
- deposit_received_at
- final_balance_status

## 9. wedding lane 的 recurring 資產思維

婚禮線不一定 recurring，但應把「可複用資產」沉澱下來，例如：
- 常見問答回覆模板
- 報價套餐模板
- 出班 checklist
- 後製交接 checklist
- 修稿說明模板
- 結案回訪訊息模板

所以婚禮線的結案，不只是結束，而是要把可複製部分留下來。

## 10. 麻花影像的特殊規則

### 10.1 品牌定位
- 麻花影像 = 共同經營婚禮品牌

### 10.2 owner / PM
- client_owner 常偏 `共同`
- pm_owner 常偏 `共同`
- 但 operation controller 常偏 Chu

### 10.3 系統要求
所以這條線一定要記住：
- 共同 ownership
- 但實際主控者可不同
- 不可只看 PM owner 就當成所有事都由 Brian 主控

## 11. wedding lane 常見錯誤

### 11.1 沒收訂金就當 confirmed
錯。

### 11.2 把婚禮線當一般企業案處理
錯。

### 11.3 不把 Chu 的主控角色寫進系統
錯。

### 11.4 交片就算結案
錯。

### 11.5 不留模板與回訪資產
錯。

## 12. wedding lane 與其他文件的關係

- 規則邊界：`brian-ai-workflow-decision-rails.md`
- 路由：`brian-ai-workflow-routing-rules.md`
- 狀態：`brian-ai-workflow-state-machine.md`
- 關卡：`brian-ai-workflow-phase-gates.md`
- intake：`intake-playbook.md`
- PM：`pm-playbook.md`

## 13. 待補問題

- 婚禮價格套餐是否要獨立一份 package spec
- 麻花影像是否要做獨立品牌 sidecar 規範頁
- Chu 主控相關欄位是否要正式寫入 data model
