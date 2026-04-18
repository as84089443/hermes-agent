# PM Playbook

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 中，PM 角色在每個階段應該做什麼、判斷什麼、不能跳過什麼。

它不是 generic 專案管理手冊，
而是專門對應 Brian 的實際經營結構：
- Brian 自己的客戶線
- 共同客戶 / 共同 PM 線
- 麻花影像婚禮線
- Chu / Jerry 協作線
- 場租與資產收入線

這份文件的核心目的，是讓 PM：
- 不只是追進度
- 而是守住案件 operating system 的控制點

## 2. PM 的定位

在 Brian AI workflow 裡，PM 不是純行政。
PM 的核心責任是：

1. 判斷案件是否能進下一關
2. 確保 owner 與角色清楚
3. 確保版本、scope、變更有紀錄
4. 把案件從 intake 推到 close，而不是讓它們卡死在聊天裡

### PM 不是做什麼
PM 不應：
- 自行創造制度
- 跳過 confirmed 條件
- 跳過 quote version
- confirmed 後默默改 scope
- 用口頭默契取代記錄

### PM 需要靠什麼工作
PM 不靠記憶管理案件。
PM 依賴：
- case 主表
- customer sidecar
- brand sidecar
- analysis rulebook
- routing rules
- phase gates

## 3. PM 在每個 phase 的核心任務

### 3.1 Intake 階段
PM 的任務：
- 確保 intake 不是卡在聊天紀錄
- 確保 AI 已做 first-pass normalization
- 決定是：
  - 直接進 routing
  - 還要補問
  - 還是升級人工接手

PM 必查：
- 是否已有相同客戶線規則
- 是否命中既有品牌線
- 是否命中 do-not-ask-again

PM 不該做：
- 一開始就問一大串細節
- 在沒查既有知識前重問老問題

### 3.2 Clarify 階段
PM 的任務：
- 只補足「足以 routing / quote」的資訊
- 不把客戶問到煩
- 不為了填滿表格而亂猜

PM 判斷重點：
- 客戶是誰
- 這是哪條 lane
- 這案是否需要 Brian 親自下場
- 截止日 / 檔期

PM 完成標準：
- 這案已能進 `ready_for_quote`

### 3.3 Quote / Deal 階段
PM 的任務：
- 整理需求
- 看歷史相似案
- 準備正式報價版本
- 判斷是否：
  - 直接報價
  - 先 soft hold
  - 直接 confirmed
  - 或不做

PM 必守規則：
- 每次正式重送都要新 `quote_version`
- 不得覆蓋舊版本

PM 要問自己的問題：
- 這案是 Brian 的客戶、共同客戶，還是上游合作方？
- 這案是 Brian 核心執行、PM / 接案，還是共同 PM 線？
- 這案是否會把 Brian 綁死？

### 3.4 Confirm / Lock 階段
PM 的任務：
- 明確記錄案件何時正式成立
- 啟動 scope lock
- 確保 confirmed 前，owner / executor / approver 已知

PM 必守規則：
- confirmed 後，改金額 / 時數 / 交付 / 人力 / 主要角色，都要進 change review

PM 要問自己的問題：
- 這個案子現在真的成立了嗎？
- 成立條件對這條 lane 是否合理？
- 一旦 confirmed，有哪些風險會開始變高？

### 3.5 Execute 階段
PM 的任務：
- 控節點，不是自己下去做所有事
- 確保執行前資訊清楚
- 確保知道誰做、何時做、交什麼
- 盯住會影響交付的風險

PM 要維護：
- executor
- next_action
- next_owner
- blockers
- artifact version

PM 必守規則：
- confirmed 後若需求漂移，不能口頭硬吞，必須回到 change review

### 3.6 Deliver / Bill 階段
PM 的任務：
- 把 delivered 與 collected 分開
- 確保交付紀錄留下來
- 進入請款 / 開票 / 收款追蹤

PM 要判斷：
- 這案現在是 delivered 還是 billing？
- 已可請款了嗎？
- 還缺什麼才可以進 collected？

PM 必守規則：
- AI 可草擬請款與 follow-up，但不可自己對客正式催款
- collected 要有明確到帳依據

### 3.7 Close / Learn 階段
PM 的任務：
- 不是把案件「關掉」，而是把它轉成可複用知識

close 前至少要留下：
- 客戶最終歸屬
- PM 歸屬
- Brian 是否親自執行
- Brian 角色
- 收入性質
- 是否可複製
- 哪條規則值得回寫 sidecar / rulebook

PM 必守規則：
- 沒 recap 不可 close
- 沒分帳判斷 / 不分帳理由，不可視為完整 close

## 4. PM 的四個核心 decision blocks

這是 PM playbook 最重要的骨架。
PM 工作不應寫成一堆任務，而應寫成 4 個 decision blocks。

### Block A — Intake Decision
PM 要決定：
- 這案能不能建
- 先補問還是直接進 routing
- 是否需要 Brian 直接介入

### Block B — Deal / Booking Decision
PM 要決定：
- 現在能不能送正式報價
- 要不要 soft hold
- 什麼時候 confirmed
- 什麼時候開始 scope lock

### Block C — Execution Control Decision
PM 要決定：
- 誰做
- 是否需要 handoff
- 哪些變更要正式 review
- 現在是不是該交付了

### Block D — Billing / Closing Decision
PM 要決定：
- 什麼時候請款
- 誰追款
- 何時算已收款
- 何時能結案
- 哪些規則應回寫系統

## 5. PM 對不同業務線的操作重點

### 5.1 Brian 直接客戶線
PM 重點：
- 要區分 Brian 是主執行、兼具 PM 與執行，還是只接案外發
- 不要因為客戶是 Brian 的，就自動假設 Brian 每次都要下場

### 5.2 共同客戶 / 共同 PM 線
PM 重點：
- 先搞清楚權責與邊界
- 不要讓共同客戶變成無人真正負責的客戶
- 共同客戶案要特別寫清 current_owner / final_owner

### 5.3 麻花影像婚禮線
PM 重點：
- 麻花影像是共同經營品牌
- Chu 常是實際主控者
- PM 不應只把它視為普通共同客戶，而要看婚禮品牌 SOP

### 5.4 場租 / 租棚線
PM 重點：
- 這不是 Brian 核心執行案
- 應視為資產收入線
- 不要讓場租流程和主動接案流程混在一起

### 5.5 上游合作方線
PM 重點：
- 分清楚：
  - 上游來源是誰
  - 最終客戶線算誰的
  - PM 是不是 Brian
- 否則容易把上游合作案誤判成你的直接客戶線

## 6. PM 與 AI 的分工

### AI 幫 PM 做什麼
- intake normalization
- 缺欄位標記
- 下一步建議
- 報價草稿
- follow-up 草稿
- queue 與風險摘要
- case recap 草稿

### PM 不能交給 AI 的事
- 最終報價送出
- confirmed 放行
- confirmed 後 scope change 放行
- 正式催款
- 收款確認
- close 最終拍板

## 7. PM 需要的最小 dashboard 視角

若未來做 UI，PM 至少需要看得到：

1. 今天最該處理的 cases
2. 哪些卡在 clarifying
3. 哪些已 quote_sent 但未回
4. 哪些已 confirmed 但還沒進 execution
5. 哪些已 delivered 但還沒 billing / collected
6. 哪些 close 前還沒 recap

也就是說，PM dashboard 不是看很多資料，
而是看：
- 哪裡卡住
- 下一步是誰
- 哪裡有風險

## 8. PM 常見錯誤

### 8.1 把 intake 當成報價
錯。先分類，再報價。

### 8.2 沒 version 就送正式內容
錯。之後無法回看。

### 8.3 confirmed 後口頭改 scope
錯。這會讓系統記錄失真。

### 8.4 把 delivered 當 collected
錯。做完不等於收完錢。

### 8.5 沒有 recap 就 close
錯。這會讓你永遠無法學習。

### 8.6 已知規則還重問 Brian
錯。應先查 rulebook / sidecar。

## 9. PM Playbook 與其他文件的關係

- Intake 細節看：`intake-playbook.md`
- 決策邊界看：`brian-ai-workflow-decision-rails.md`
- 狀態與 gates 看：
  - `brian-ai-workflow-state-machine.md`
  - `brian-ai-workflow-phase-gates.md`
- 路由判定看：`brian-ai-workflow-routing-rules.md`
- 欄位定義看：`brian-ai-workflow-data-model.md`

## 10. 待補問題

- Chu 的 `operating_controller` 角色是否要正式進 playbook
- wedding / studio_rental 是否要拆成各自獨立 PM 子 playbook
- recurring 客戶是否要有 PM 專用 follow-up cadence
