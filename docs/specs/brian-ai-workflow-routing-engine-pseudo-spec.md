# Brian AI Workflow Routing Engine Pseudo-Spec

日期：2026-04-14

## 1. 這份文件的目的

這份文件不是正式程式碼設計，而是把目前已經寫好的：
- decision rails
- data model
- routing rules
- sidecar / rulebook

翻成一份可實作的 routing engine pseudo-spec。

它的目的是讓後續工程實作時，不必再從自然語言文件重新推理一次流程。

## 2. Routing Engine 輸入

### 必要輸入
- raw_brief
- source
- customer_name（可暫名）
- source_sheet / historical references（若為舊案）
- customer sidecar match
- brand sidecar match
- analysis rulebook match

### 可選輸入
- vendor_raw
- income normalization record
- calendar relevance context
- known contacts / aliases

## 3. Routing Engine 輸出

最少應輸出：
- primary_lane_candidate
- client_owner_candidate
- pm_owner_candidate
- brian_exec_candidate
- brian_role_candidate
- confidence
- matched_rules
- missing_fields
- recommended_questions
- recommended_next_status
- recommended_next_owner

## 4. 判斷順序

### Step 1：查 do-not-ask / rulebook
若命中：
- 直接套用已確認規則
- 不再重問同一題

### Step 2：查 customer sidecar
若命中高/中信心：
- 補 `client_owner_candidate`
- 補 `pm_owner_candidate`
- 補 `relationship_type`

### Step 3：查 brand sidecar
若命中：
- 補 `brand_or_system`
- 補 `primary_lane_candidate`
- 補 `operating_controller` 候選（若未來納入）

### Step 4：解析原始訊息
從 raw_brief / title / case name 中判斷：
- wedding / studio_rental / commercial / post_only / collab_ops
- 是否有 Brian/Jerry/Chu 顯式線索
- 是否有上游合作方線索

### Step 5：若仍不足，再產生補問
一次最多 2–4 題。

## 5. 判斷規則（高階）

### Rule A：客戶已確認
如果 sidecar / rulebook 已確認客戶屬於 Brian：
- `client_owner_candidate = 我`
- 若無反例，`pm_owner_candidate = 我`

### Rule B：共同客戶
如果：
- 命中共同品牌（如麻花影像）
- 或收入模式 / 既有規則顯示共同線
則：
- `client_owner_candidate = 共同`
- `pm_owner_candidate = 共同`

### Rule C：Brian 接案但外發
如果：
- 客戶屬 Brian 線
- 但 Brian 不親自執行
- 執行交給他人
則：
- `brian_exec_candidate = 否`
- `brian_role_candidate = 僅管理`
- `income_nature_candidate = PM/接案`

### Rule D：Brian 親自做
如果：
- Brian 是主輸出
则：
- `brian_exec_candidate = 是`
- `brian_role_candidate = 主輸出`
- 若 client_owner / pm_owner 同為 Brian，則傾向 `兼具PM與執行`

### Rule E：資產收入
如果明顯是租棚 / 場租：
- `primary_lane_candidate = studio_rental`
- `income_nature_candidate = 資產收入`

## 6. 信心分級

### high
- 命中 do-not-ask-again
- 命中 user-confirmed rule
- 命中高信心 sidecar

### medium
- 命中中信心 sidecar
- 命中穩定品牌規則
- 命中明顯 lane 規則

### low
- 只靠案名猜測
- 只有部分欄位能推定
- 尚需 Brian 補關鍵欄位

## 7. 推薦下一步規則

### 若 high 且資訊足夠
- 直接建 case
- 進 `ready_for_quote` 或 `clarifying`

### 若 medium 且缺 1–2 個關鍵欄位
- 建 case
- 進 `clarifying`
- 補問最少問題

### 若 low 且缺客戶 / lane / owner
- 停在 `clarifying`
- 不可進 quote

## 8. 補問產生器規則

只允許問：
- 客戶是誰？
- 這是哪一類案？
- 是否需要 Brian 親自下場？
- 截止日 / 檔期是什麼？

不得問：
- 已在 rulebook / sidecar 中有答案的問題

## 9. 與 Recap 的關係

Routing engine 不是一次性判斷器。
它應該在案件 close 後接收 recap 回寫的結果，更新未來判斷依據。

也就是：
- routing 用 sidecar / rulebook 判現在
- recap 用新案件結果更新 sidecar / rulebook
- 形成閉環

## 10. v1 實作邊界

v1 routing engine 先只做到：
- intake 後輸出 candidate values
- 輸出 confidence
- 輸出補問建議
- 輸出 next status / next owner

v1 先不做：
- 直接自動改資料庫正式欄位
- 自動發送訊息
- 自動觸發 confirmed / collected
