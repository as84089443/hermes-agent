# Customer / Brand Sidecar Schema

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 中 `customer sidecar` 與 `brand sidecar` 的正式 schema。

目的：
- 不污染共享 Google Sheets 原表
- 讓 Hermes 能長期記住客戶 / 品牌 / 關係線知識
- 讓 intake、routing、PM、review 都能先查 sidecar，再決定要不要問 Brian

## 2. 為什麼需要 sidecar

Brian 現在的真實知識很多不在原始表單裡，而是在：
- 你腦中的脈絡
- 歷史聊天校正
- BNI / 舊同事 / 上游合作方關係
- 品牌層（麻花影像、B.W.Studio）

如果不把這些獨立成 sidecar，系統每次都會：
- 重新猜一次
- 重問一次
- 或把角色判斷做錯

## 3. 設計原則

### 3.1 sidecar 是知識層，不是共享營運主表
- 原始共享表仍保留匯款、帳務、營運用途
- sidecar 只存 Hermes 分析與 routing 需要的補充知識

### 3.2 先支援 routing，不先追求 CRM 完整度
v1 sidecar 的第一目的不是管理所有客戶資料，而是幫系統回答：
- 客戶通常是誰的？
- PM 通常是誰？
- 這是什麼關係？
- 之後還要不要再問？

### 3.3 要允許 `待確認`
sidecar 不是全部都要高信心。
應允許：
- 高信心
- 中信心
- 低信心
- 待確認

### 3.4 一個客戶 / 品牌可以有 operating note
因為很多關鍵知識不是 enum，而是操作脈絡。

## 4. Customer Sidecar Schema

### 4.1 核心欄位

- `customer_id`
  - 系統內唯一 ID
  - 例：`cust_maffrey`, `cust_yongheng_shaonian`

- `customer_name`
  - 正式客戶名稱

- `display_name`
  - 常用簡稱
  - 例：碼非、台北金融、永恆少年

- `aliases`
  - 別名陣列
  - 例：`["碼非創意", "碼非"]`

- `owner_guess`
  - 值：`我 | Jerry | 共同 | 其他 | 待確認`

- `pm_guess`
  - 值：`我 | Jerry | 共同 | 其他 | 待確認`

- `relationship_type`
  - 建議值：
    - `我的直接客戶`
    - `共同客戶`
    - `上游合作方`
    - `供應商/外包`
    - `資產租戶`
    - `待確認`

- `confidence`
  - 值：`high | medium | low`

- `notes`
  - 文字補充說明

### 4.2 建議欄位

- `source_of_truth`
  - 例：`user_confirmed`, `vendor_sheet`, `historical_income`, `bnl_memory`, `heuristic`

- `do_not_ask_again`
  - `true | false`

- `known_contacts`
  - 人名陣列
  - 例：`["Randy", "Eric", "Sherry"]`

- `known_org_context`
  - 例：`BNI長榮`, `前同事`, `上游發案方`

- `lane_defaults`
  - 客戶常見 lane
  - 例：`["commercial"]`

- `recurring_hint`
  - 是否 recurring / 可複製

- `upstream_sources`
  - 若常有固定上游來源，可記在這裡

### 4.3 JSON 範例

```json
{
  "customer_id": "cust_maffrey",
  "customer_name": "碼非創意企業有限公司",
  "display_name": "碼非",
  "aliases": ["碼非創意", "碼非"],
  "owner_guess": "我",
  "pm_guess": "我",
  "relationship_type": "我的直接客戶",
  "confidence": "high",
  "source_of_truth": "user_confirmed",
  "do_not_ask_again": true,
  "known_contacts": ["Ken", "Jeffrey"],
  "known_org_context": "Brian direct client line",
  "lane_defaults": ["commercial"],
  "notes": "碼非是 Brian 的客戶線；其下案子常同時具有 PM/接案與核心執行屬性。"
}
```

## 5. Brand Sidecar Schema

### 5.1 核心欄位

- `brand_id`
  - 系統內唯一 ID

- `brand_name`
  - 品牌名稱
  - 例：麻花影像、B.W.Studio

- `aliases`
  - 品牌別名陣列

- `owner_type_guess`
  - 值：`我 | Jerry | 共同 | 其他 | 待確認`

- `pm_owner_guess`
  - 值：`我 | Jerry | 共同 | 其他 | 待確認`

- `operating_note`
  - 品牌運作方式說明

- `confidence`
  - `high | medium | low`

### 5.2 建議欄位

- `default_lane`
  - 例：`wedding_private`, `collab_ops`, `studio_rental`

- `operating_controller`
  - 若實務上常由某人主控，先以可選欄位保留
  - 例：`Chu`

- `do_not_ask_again`
  - `true | false`

- `linked_customers`
  - 關聯客戶陣列

- `notes`
  - 補充說明

### 5.3 JSON 範例

```json
{
  "brand_id": "brand_mahua",
  "brand_name": "麻花影像",
  "aliases": ["麻花", "麻花婚禮線"],
  "owner_type_guess": "共同",
  "pm_owner_guess": "共同",
  "default_lane": "wedding_private",
  "operating_controller": "Chu",
  "confidence": "high",
  "do_not_ask_again": true,
  "notes": "婚禮子品牌，屬共同經營；通常看誰有空發案，主控偏 Chu。"
}
```

## 6. Sidecar 與主表的互動

### 6.1 Intake 時
- 先查 customer / brand sidecar
- 若命中高信心規則，直接補 candidate values

### 6.2 Routing 時
- sidecar 可直接提供：
  - client_owner candidate
  - pm_owner candidate
  - lane default
  - do-not-ask-again

### 6.3 Review 時
- 若新案確認了新規則，就回寫 sidecar
- 若規則被推翻，也要更新 sidecar

## 7. 欄位更新原則

### 7.1 什麼情況可升高信心
- Brian 明確口頭確認
- 同樣規則在多案反覆被驗證
- vendor / brand / historical income 三方一致

### 7.2 什麼情況只能維持 medium / low
- 只是 heuristic
- 只是單次推論
- Brian 自己也不確定

### 7.3 什麼情況進 do-not-ask-again
- 已多次確認
- 再問不會得到新資訊
- 對 routing 有明顯價值

## 8. v1 不做的事

- 不先做完整 CRM 客戶資料庫
- 不先建聯絡人關係圖
- 不先做大量自動同步共享表單
- 不先做每個品牌完整 KPI 系統

## 9. 與其他文件的關係

- routing 規則看：`brian-ai-workflow-routing-rules.md`
- case 欄位看：`brian-ai-workflow-data-model.md`
- recap / 規則回寫看：`review-and-learning-playbook.md`

## 10. 待補問題

- `operating_controller` 是否在 customer sidecar 也要存在
- 是否需要獨立 `relationship sidecar`
- sidecar 未來要不要升級成 machine-readable contracts 的一部分
