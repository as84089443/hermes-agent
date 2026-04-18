# Brian AI Workflow Routing Rules

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 在新案件進來時，應如何決定：
- 這案是哪一條 lane
- 客戶歸屬是誰
- PM 歸屬是誰
- Brian 是否要親自下場
- 案件應先送到 Brian / Chu / Jerry / AI 哪一條處理線

這份文件的定位不是人類備忘錄，而是未來 routing engine、intake normalizer、case recap writer 共用的決策規則來源。

## 2. Routing 的總原則

### 2.1 先查規則，再問人
Routing 順序固定如下：

1. 先查 `analysis_rulebook`
2. 再查 `customer sidecar`
3. 再查 `brand sidecar`
4. 再查原始 intake / 收入 / 行事曆資料
5. 最後才補問 Brian

### 2.2 已確認案件線不得重複詢問
若某案件、客戶線、品牌線已被 Brian 明確確認：
- 應直接套用既有結論
- 不可反覆重問同一題
- 若資料不完整，只補問尚未確認的欄位

### 2.3 不完整資訊可以 pending
Brian 的歷史資料很多是回想式校正，因此：
- 允許 `client_owner = 待確認`
- 允許 `pm_owner = 待確認`
- 允許 `brian_exec = 待確認`
- 不可因缺欄位就自由亂猜

### 2.4 先判 lane，再判角色
先決定主 lane，再決定：
- client_owner
- pm_owner
- brian_exec
- brian_role

原因是 lane 會影響後面的 booking、handoff、approval、closing 邏輯。

## 3. 主 lane 定義

### 3.1 `commercial`
企業活動、品牌影片、商業影像、論壇、記者會、展覽、品牌內容。

### 3.2 `wedding_private`
婚禮、抓周、私人宴會、婚禮延伸拍攝等。

### 3.3 `studio_rental`
棚租、場租、工作室被動收入相關案件。

### 3.4 `post_only`
純後製、純剪輯、只接後端製作的案件。

### 3.5 `collab_ops`
共同客戶、共同 PM、共同出班、合作型運作案件。

## 4. Lane Routing 規則

### 4.1 若案名或 brief 明確包含租棚 / 場租
- `primary_lane = studio_rental`
- 並預設收入性質偏資產收入

### 4.2 若案型屬婚禮 / 抓周 / 早儀 / 午宴 / SDE / 婚攝
- `primary_lane = wedding_private`
- 若品牌命中麻花影像 / VAF，則優先走婚禮共同經營線

### 4.3 若案型屬論壇 / 活動 / 記者會 / 品牌拍攝 / 商業形象 / 展覽 / GCS / FSC 等
- `primary_lane = commercial`

### 4.4 若明確是後製 / 剪片 / 修片 / 後製支援
- `primary_lane = post_only`

### 4.5 若是已知共同品牌或共同客戶線，且主要工作是協作出班或共同交付
- `primary_lane = collab_ops`

## 5. Client Owner 判斷規則

### 5.1 直接客戶線
若符合以下任一條件，優先判為 `client_owner = 我`：
- customer sidecar 已標記為 Brian 客戶線
- brand sidecar 已標記為 Brian 客戶線
- Brian 已多次確認為「我的客戶」
- vendor sidecar 命中高/中信心 Brian 客戶

### 5.2 共同客戶線
若符合以下任一條件，優先判為 `client_owner = 共同`：
- brand sidecar 命中麻花影像 / 共同品牌
- Brian 與 Jerry 長期共同面對此客戶
- Brian 與 Jerry 收入接近，且 Brian 已明示這類通常是共同客戶

### 5.3 上游合作方
若案源來自：
- 三立 / 永恆少年 / 錨點等上游合作方
且最終執行與分工由 Brian 再往下派，則：
- 上游關係應被保留在 sidecar / note
- 但 `client_owner` 仍要看 Brian 是否把它視為自己的客戶線

### 5.4 不確定時的規則
若無 sidecar 命中、無規則命中、無 Brian 明示：
- 先標 `client_owner = 待確認`
- 不可因 `B比例 = 1.00` 就直接判定一定是 Brian 客戶

## 6. PM Owner 判斷規則

### 6.1 一般規則
若 Brian 已明確說明：
- 「若客戶是我的，我就算 PM」
則在沒有反例的情況下：
- `client_owner = 我` 時，預設 `pm_owner = 我`

### 6.2 共同客戶情況
若 Brian 與 Jerry 收入接近，且無明確指定 PM：
- 預設 `pm_owner = 共同`

### 6.3 麻花影像規則
婚禮品牌 `麻花影像`：
- 預設 `client_owner = 共同`
- 預設 `pm_owner = 共同`
- 但運作上 `Chu` 常為主控
- 因此 playbook 應另外支援 `operating_controller = Chu` 之類欄位，而不是直接改寫 PM owner

### 6.4 明確外發規則
若案子是 Brian 接的，但 Brian 自己不做，轉派給他人執行：
- `pm_owner = 我`
- `brian_exec = 否`
- 收入性質偏 `PM/接案`

## 7. Brian 是否親自下場

### 7.1 `brian_exec = 是`
適用於：
- Brian 本人有到場
- Brian 本人有實際執行工作
- Brian 是主輸出者或共同主輸出者

### 7.2 `brian_exec = 否`
適用於：
- Brian 沒有到場
- Brian 沒有做實際交付
- 案子是他接的，但交給哈利 / Jerry / Chu / 其他人執行

### 7.3 `brian_exec = 待確認`
適用於：
- 歷史資料不足
- 只有分帳與案名，沒有足夠情境

## 8. Brian 角色判斷

### 8.1 `主輸出`
- Brian 是主要執行者之一
- Brian 直接承擔關鍵交付

### 8.2 `支援`
- Brian 有出工
- 但只是助理 / 支援 / 陪跑
- 不算核心執行收入

### 8.3 `僅管理`
- Brian 接案、分工、控交付
- 但自己不下場做

### 8.4 `未參與`
- 僅帳務上有關聯、或資料殘留
- 實際上 Brian 沒做也沒管

## 9. 收入性質判斷

### 9.1 核心執行收入
條件：
- `client_owner = 我`
- `brian_exec = 是`
- `brian_role = 主輸出`
- Brian 是主要輸出者

### 9.2 PM / 接案收入
條件：
- `client_owner = 我`
- `pm_owner = 我`
- `brian_exec = 否`
或
- Brian 接案後外發給他人執行

### 9.3 兼具 PM 與執行
條件：
- `client_owner = 我`
- `pm_owner = 我`
- `brian_exec = 是`
- Brian 同時是接案者與主要執行者

### 9.4 共同客戶 / 共同 PM 收入
條件：
- `client_owner = 共同`
- `pm_owner = 共同`
- 依實際情況再加上 `brian_exec = 是/否`

### 9.5 協作支援收入
條件：
- `brian_exec = 是`
- `brian_role = 支援`

### 9.6 資產收入
條件：
- `primary_lane = studio_rental`
- 屬租棚 / 場租 / 工作室出租

## 10. 客戶與品牌特殊規則

### 10.1 碼非系統
- 視為 Brian 客戶線
- 中堅企業獎 / FSC / 森獎等案子，常同時具 PM 與執行屬性

### 10.2 麻花影像
- 婚禮共同經營子品牌
- 多數婚禮線屬共同客戶 / 共同 PM
- Chu 常為主控者

### 10.3 B.W.Studio
- 共同工作與共同出班系統
- 不等於 Brian 單人客戶線

### 10.4 BNI 夥伴客戶線
對 Brian 而言，BNI 不是純社交層，而是客戶來源層。
若某客戶已多次確認為 BNI 夥伴且屬你的客戶線，則之後應直接套用。

### 10.5 上游合作案
例如：
- 三立
- 永恆少年
- 錨點

這類案需區分：
- 上游來源是誰
- 最終客戶線算不算 Brian 的
- PM owner 是不是 Brian

## 11. Do-not-ask-again 規則

### 11.1 進入條件
若 Brian 已多次明確確認某案或某客戶線，則進入 `do_not_ask_again`。

### 11.2 實作原則
- 後續 routing 前先查 rulebook
- 命中後直接套用
- 只補問尚未被確認的欄位

### 11.3 已知不應重問的案例
- Randy / 雲祥線
- 小白故事線
- 立方品 / 邱惟隆線
- 哈利 / 永恆少年線
- Kenny 車展線

## 12. Pending 策略

### 12.1 可先 pending 的欄位
- pm_owner
- brian_exec
- brian_role
- income_nature

### 12.2 不可長期空白的欄位
- primary_lane
- current_owner
- status
- customer_name（至少暫名）

### 12.3 補齊時機
- 進 `Quote Draft` 前應補齊客戶歸屬
- 進 `Confirmed` 前應補齊 PM 與主要執行角色
- 結案 recap 時應補齊收入性質

## 13. v1 典型路由範例

### 範例 A：你的客戶，你也親自做
- client_owner = 我
- pm_owner = 我
- brian_exec = 是
- brian_role = 主輸出
- income_nature = 兼具 PM 與執行

### 範例 B：你的客戶，你外發給他人
- client_owner = 我
- pm_owner = 我
- brian_exec = 否
- brian_role = 僅管理
- income_nature = PM / 接案

### 範例 C：共同客戶，雙方一起做
- client_owner = 共同
- pm_owner = 共同
- brian_exec = 是
- brian_role = 主輸出
- income_nature = 共同客戶 / 共同 PM

### 範例 D：麻花婚禮線
- primary_lane = wedding_private
- brand_or_system = 麻花影像
- client_owner = 共同
- pm_owner = 共同
- operating controller 偏 Chu

### 範例 E：租棚線
- primary_lane = studio_rental
- income_nature = 資產收入
- 與 Brian 主動執行收入隔離

## 14. 待補問題
- 某些早年婚禮案尚未完全定出「麻花前時期」的客戶歸屬規則
- 上游合作案（如三立、錨點）還需要更細的 owner 規則
- `operating_controller` 是否要正式獨立成欄位待 data model 討論
