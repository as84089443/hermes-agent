# Brian AI Workflow Data Model

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow v1 的最小資料模型。
目標不是先做完整 ERP / CRM，而是先讓這套 workflow 能穩定回答：
- 這是什麼案子
- 是誰的客戶
- 誰在當 PM
- Brian 要不要親自下場
- 下一步是誰
- 哪個版本被送出、被核准、被交付

這份資料模型應直接服務：
- intake normalizer
- routing engine
- dashboard / cases / case detail
- review / learning / recap

## 2. 建模原則

### 2.1 先支撐 workflow，不先追求完美正規化
v1 的目標是能跑，而不是先把所有資料拆成最細的關聯圖。

### 2.2 先支撐 owner / lane / approval / recap
如果一個欄位不能幫助系統判斷 owner、lane、approval、next action，就不應先進 v1。

### 2.3 可由 AI 自動補值的欄位，不必一開始都人工填滿
例如：
- normalized_brief
- lane_hint
- scope_clarity
- candidate client_owner
- candidate pm_owner
都可先由 AI 補，之後再被人確認。

### 2.4 sidecar 與共享表單要分離
共享 Google Sheets 保留營運用途。
Hermes 的分析與角色判斷，應寫在 sidecar，不直接污染共享表單。

### 2.5 case 是主體，sidecar 是知識層
- `case` 是 workflow 主體
- `customer sidecar`、`brand sidecar`、`analysis rulebook` 是決策知識層
- `income normalization record` 是歷史事實層

## 3. 核心實體總覽

### 3.1 `case`
代表單一正式案件或可被管理的一次工作單位。

### 3.2 `customer sidecar`
代表 Hermes 對客戶歸屬、PM 歸屬、關係類型的補充知識。

### 3.3 `brand sidecar`
代表品牌 / 子品牌 / 系統線的補充知識，例如：
- 麻花影像
- B.W.Studio

### 3.4 `income normalization record`
代表歷史收入資料的標準化記錄，用於回推客戶線、PM 線、Brian 執行模式。

### 3.5 `review note / rulebook`
代表使用者在校正過程中講過的明確規則與 do-not-ask-again 知識。

## 4. `case` 主表

`case` 是 workflow 的中心。所有 dashboard、queue、提醒、交付、recap，都應以 `case` 為主體。

### 4.1 必填欄位

- `case_id`
  - 系統唯一 ID
  - 例如：`case_20260414_001`

- `title`
  - 人類可讀的案件名稱

- `source`
  - 案件來源
  - 例如：`line`, `telegram`, `slack`, `email`, `manual`, `bni-referral`, `returning-client`

- `customer_name`
  - 客戶名稱；若尚未確定，可暫時用口語名稱或聯絡人名

- `primary_lane`
  - 主 lane
  - 由 routing rules 判定

- `status`
  - 當前狀態

- `current_owner`
  - 目前誰持有這個案子的下一步責任

- `next_action`
  - 系統認為下一步應做什麼

- `next_owner`
  - 下一步由誰做

- `created_at`
- `updated_at`

### 4.2 角色欄位

這組欄位是 Brian workflow 的核心差異，不可省略。

- `client_owner`
  - 值：`我 | Jerry | 共同 | 其他 | 待確認`
  - 定義：客戶關係主要算在誰頭上

- `pm_owner`
  - 值：`我 | Jerry | 共同 | 其他 | 待確認`
  - 定義：誰在主導報價、分工、交付、節點推進

- `brian_exec`
  - 值：`是 | 否 | 待確認`
  - 定義：Brian 是否親自出工 / 下場執行

- `brian_role`
  - 值：`主輸出 | 支援 | 僅管理 | 未參與 | 待確認`
  - 定義：Brian 在這案中的角色

- `executor`
  - 值可為單人或多人
  - 例如：`Brian`, `Chu`, `Jerry`, `哈利`, `外部攝影`, `AI`, `未定`

- `approver`
  - 最終需要核准的人
  - 通常是 Brian 或客戶

### 4.3 商務欄位

- `budget_status`
  - 建議值：`unknown | needs_quote | quoted | approved | internal`

- `quote_version`
  - 當前對客正式報價版本

- `due_date`
  - 交付期限或檔期日期

- `artifact_version`
  - 與交付物、交付包、核准版本綁定

- `pricing_mode`
  - 建議值：`standard | negotiated | recurring | custom | internal`

### 4.4 內容欄位

- `raw_brief`
  - 原始訊息，不做太多清洗

- `normalized_brief`
  - AI 或 PM 整理後的工作描述

- `deliverables`
  - 預期交付物
  - 可先用文字或陣列表示

- `notes`
  - 補充說明

- `risk_flags`
  - 例如：`scope_unclear`, `deadline_risky`, `brand_sensitive`, `cashflow_risk`

### 4.5 關聯欄位

- `brand_or_system`
  - 例如：`麻花影像`, `B.W.Studio`, `Brian direct`, `studio_rental`

- `parent_case_id`
  - 純後製、子案、延伸案可掛在主案底下

- `project_group_id`
  - recurring / 系列案分組

- `sidecar_type`
  - 建議值：`none | client_sidecar | brand_sidecar | internal_sidecar`

## 5. `customer sidecar`

### 5.1 目的

它不是共享客戶表，而是 Hermes 自己的客戶理解層。
用來回答：
- 這通常是誰的客戶？
- PM 通常是誰？
- 這個客戶屬於哪種關係？
- 之後要不要再重問？

### 5.2 最小欄位

- `customer_name`
- `owner_guess`
- `pm_guess`
- `relationship_type`
- `confidence`
- `notes`

建議可再補：
- `source_of_truth`
  - 例如：`user_confirmed`, `vendor_sheet`, `brand_rule`, `historical_income`, `heuristic`

- `do_not_ask_again`
  - `true / false`

### 5.3 何時更新

在以下時機更新：
- Brian 明確口頭確認
- 某客戶線重複出現且規則穩定
- 收入表與行事曆已能互相驗證

### 5.4 與共享匯款表的關係

- 共享匯款表保留匯款與營運基礎資料
- customer sidecar 不應回寫到共享表，除非未來你決定正式納入 SOP

## 6. `brand sidecar`

### 6.1 目的

有些案子的本體不是公司名稱，而是品牌 / 系統線。
例如：
- 麻花影像
- B.W.Studio
- Brian 自有工作流線

這些不能只依附在 customer sidecar 裡。

### 6.2 最小欄位

- `brand_name`
- `owner_type_guess`
- `pm_owner_guess`
- `operating_note`
- `confidence`

可再補：
- `lane_default`
- `associated_people`
- `do_not_ask_again`

### 6.3 已知品牌範圍

目前至少應支援：
- 麻花影像
- B.W.Studio
- 其他待增補（例如某些長期線若不只是一家公司，而是一種運作系統）

## 7. `income normalization record`

### 7.1 目的

它不是正式 case 主表，而是歷史事實層。
用來回答：
- 這筆錢怎麼分
- 客戶可能是誰
- PM 可能是誰
- Brian 有沒有下場
- 這筆收入屬於哪種模式

### 7.2 目前已有欄位

已整理出的主表至少包含：
- `year`
- `source_sheet`
- `date`
- `case`
- `gross_income`
- `brian_net`
- `jerry_net`
- `chu_post`
- `b_ratio_raw`
- `j_ratio_raw`
- `post_support_raw`
- `client_owner_guess`
- `pm_owner_guess`
- `vendor_raw`
- `vendor_mapped_name`
- `confidence`
- `rule_source`

### 7.3 後續要補的欄位

最值得再補的是：
- `case_role_guess`
- `brand_or_system_guess`
- `upstream_source`
- `do_not_ask_again`
- `human_verified`

### 7.4 與 `case` 主表如何對接

- 新案走 `case` 主表
- 舊案用 `income normalization record` 回推規則
- 若某歷史規則足夠穩定，就回寫到 customer / brand sidecar

## 8. 枚舉值建議

### 8.1 `client_owner`
- `我`
- `Jerry`
- `共同`
- `其他`
- `待確認`

### 8.2 `pm_owner`
- `我`
- `Jerry`
- `共同`
- `其他`
- `待確認`

### 8.3 `brian_exec`
- `是`
- `否`
- `待確認`

### 8.4 `brian_role`
- `主輸出`
- `支援`
- `僅管理`
- `未參與`
- `待確認`

### 8.5 `primary_lane`
- `commercial`
- `wedding_private`
- `studio_rental`
- `post_only`
- `collab_ops`

### 8.6 `status`
建議沿用 bw-sop 精神，簡化成：
- `intake`
- `clarifying`
- `ready_for_quote`
- `quote_sent`
- `confirmed`
- `in_execution`
- `delivered`
- `billing`
- `collected`
- `closed`
- `lost`

### 8.7 `budget_status`
- `unknown`
- `needs_quote`
- `quoted`
- `approved`
- `internal`

## 9. 狀態與版本欄位關係

### 9.1 `quote_version`
所有對客正式報價，都必須有版本。

### 9.2 `artifact_version`
所有正式交付、正式審核、正式 approval，都要能指向 exact artifact version。

### 9.3 `scope_locked_at`
一旦進入 lock 節點，就要記錄時間，後續變更需進 change review。

### 9.4 `approved_at / accepted_at`
作為交付、handoff、核准的明確證據欄位。

## 10. 哪些欄位可由 AI 自動推定

### 10.1 從 intake 自動推定
- `primary_lane` 候選
- `budget_status` 候選
- `normalized_brief`
- `risk_flags`
- `missing_fields`

### 10.2 從 sidecar 自動補值
- `client_owner`
- `pm_owner`
- `brand_or_system`
- `relationship_type`

### 10.3 從歷史收入資料自動補值
- 類似客戶線
- 類似品牌線
- 常見 Brian 角色
- recurring / repeated patterns

## 11. v1 不做的事情

- 複雜 CRM 關聯
- 多層 task tree
- 複雜帳務與稅務模型
- 完整排程引擎
- 多層權限系統
- 過度正規化資料庫

## 12. 待補問題

- `operating_controller` 是否應正式成欄位（特別是 Chu 主控的婚禮線）
- `upstream_source` 是否應獨立成正式欄位
- `relationship_owner` 是否與 `client_owner` / `pm_owner` 分開建模
- 麻花影像成立前的婚禮歷史案，是否需要單獨一套過渡規則
