# Review Recap Schema

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 在每個案件結束時，`review recap` 應輸出哪些欄位、哪些欄位必填、哪些欄位應回寫到 sidecar / rulebook。

它的目的，是把 review-and-learning playbook 進一步變成 machine-readable schema，讓未來：
- AI 可生成 recap 草稿
- PM 可檢查 recap 是否完整
- 系統可自動判斷要不要更新 sidecar
- 系統可自動標記 do-not-ask-again

## 2. Recap 的定位

recap 不是心得文，也不是結案備忘錄。
在這套 workflow 中，recap 是：
- 案件關閉前的知識抽取層
- 將一次性案件經驗變成系統可重用規則的中介格式

所以 recap schema 必須同時服務：
1. 事實回顧
2. 規則沉澱
3. 模板資產判斷

## 3. 核心原則

### 3.1 沒有 recap，不算完整 close
close 前必須至少有一份 recap 記錄。

### 3.2 recap 要分清楚「事實」與「判斷」
- 事實：這案子發生了什麼
- 判斷：這案子屬於哪條線、哪些規則值得沉澱

### 3.3 不確定的欄位可以標 pending
- 不可硬填高信心
- 但也不可完全不留痕跡

### 3.4 recap 不是終點，而是 sidecar 更新入口
review 的價值在於：
- 回寫 customer sidecar
- 回寫 brand sidecar
- 回寫 analysis rulebook
- 更新 do-not-ask-again

## 4. Recap 的三層內容

每份 recap 都必須包含：

### Layer A：Case Facts
- 這案的基本事實

### Layer B：Business Classification
- 這案應如何被分類

### Layer C：System Learning
- 這案讓系統該學到什麼

## 5. `review_recap` 核心欄位

### 5.1 識別欄位
- `recap_id`
- `case_id`
- `created_at`
- `created_by`
- `version`

### 5.2 基本事實欄位
- `case_title`
- `primary_lane`
- `brand_or_system`
- `customer_name`
- `client_owner_final`
- `pm_owner_final`
- `executor_summary`
- `brian_exec_final`
- `brian_role_final`

### 5.3 商務與交付欄位
- `quote_version_final`
- `artifact_version_final`
- `delivered_at`
- `collected_at`
- `brian_net`
- `jerry_net`
- `chu_post`
- `income_nature_final`

### 5.4 例外與變更欄位
- `change_review_triggered`
- `change_review_summary`
- `special_notes`
- `incident_flags`

### 5.5 學習與沉澱欄位
- `customer_sidecar_update_needed`
- `brand_sidecar_update_needed`
- `rulebook_update_needed`
- `do_not_ask_again_candidate`
- `template_candidate`
- `template_candidate_reason`
- `recurring_pattern_candidate`

### 5.6 待確認欄位
- `pending_fields`
- `pending_reason`

## 6. 欄位定義

### `client_owner_final`
最終確認的客戶歸屬。
值：
- `我`
- `Jerry`
- `共同`
- `其他`
- `待確認`

### `pm_owner_final`
最終確認的 PM 歸屬。
值：
- `我`
- `Jerry`
- `共同`
- `其他`
- `待確認`

### `brian_exec_final`
值：
- `是`
- `否`
- `待確認`

### `brian_role_final`
值：
- `主輸出`
- `支援`
- `僅管理`
- `未參與`
- `待確認`

### `income_nature_final`
值：
- `核心執行`
- `PM/接案`
- `兼具PM與執行`
- `共同客戶/共同PM`
- `協作支援`
- `資產收入`
- `待確認`

### `customer_sidecar_update_needed`
值：
- `true`
- `false`

### `brand_sidecar_update_needed`
值：
- `true`
- `false`

### `rulebook_update_needed`
值：
- `true`
- `false`

### `do_not_ask_again_candidate`
值：
- `true`
- `false`

### `template_candidate`
值：
- `true`
- `false`

## 7. 最小必填欄位

若要視為一份有效 recap，至少必填：
- `case_id`
- `case_title`
- `primary_lane`
- `customer_name`
- `client_owner_final`
- `pm_owner_final`
- `brian_exec_final`
- `brian_role_final`
- `income_nature_final`
- `customer_sidecar_update_needed`
- `brand_sidecar_update_needed`
- `rulebook_update_needed`
- `do_not_ask_again_candidate`

## 8. 可由 AI 自動草擬的欄位

AI 可先草擬：
- `executor_summary`
- `special_notes`
- `change_review_summary`
- `template_candidate_reason`
- `recurring_pattern_candidate`
- `pending_fields`

但這些欄位仍需人檢查，不能直接視為 final truth。

## 9. 必須由人確認的欄位

以下欄位不應由 AI 直接拍板：
- `client_owner_final`
- `pm_owner_final`
- `brian_exec_final`
- `brian_role_final`
- `income_nature_final`
- `do_not_ask_again_candidate`

原因：
這些欄位一旦錯，就會污染未來 routing。

## 10. Sidecar / Rulebook 回寫規則

### 10.1 回寫 customer sidecar
若下列任一條件成立：
- 新客戶第一次被確認歸屬
- 舊客戶的 owner / PM 規則變得更穩定
- 發現這是 BNI 夥伴客戶 / 上游合作方 / 共同客戶線

### 10.2 回寫 brand sidecar
若下列任一條件成立：
- 發現某案應歸到既有品牌線
- 發現某品牌主控角色應更新
- 發現品牌是共同經營而非單一客戶

### 10.3 回寫 analysis rulebook
若下列任一條件成立：
- 某條規則已被重複驗證
- 某條規則要被修正
- 某案以後不該再問

## 11. do-not-ask-again 判斷標準

可加入 do-not-ask-again 的條件：
- Brian 已明確確認兩次以上
- 同答案已在多案穩定成立
- 後續再問不會產生新資訊

不可加入的條件：
- Brian 自己也不確定
- 只是一次性猜測
- 客戶 / 品牌 / PM 線仍常改變

## 12. JSON 範例

```json
{
  "recap_id": "recap_case_20260414_001",
  "case_id": "case_20260414_001",
  "case_title": "Brian單機-哈利_跑跑薑餅人",
  "primary_lane": "commercial",
  "brand_or_system": "Brian direct",
  "customer_name": "永恆少年行銷",
  "client_owner_final": "我",
  "pm_owner_final": "我",
  "executor_summary": "Brian 接案，外發給哈利拍攝",
  "brian_exec_final": "否",
  "brian_role_final": "僅管理",
  "quote_version_final": "qv_3",
  "artifact_version_final": "av_1",
  "brian_net": 17000,
  "jerry_net": 0,
  "chu_post": 10000,
  "income_nature_final": "PM/接案",
  "change_review_triggered": false,
  "customer_sidecar_update_needed": true,
  "brand_sidecar_update_needed": false,
  "rulebook_update_needed": true,
  "do_not_ask_again_candidate": true,
  "template_candidate": false,
  "pending_fields": [],
  "pending_reason": ""
}
```

## 13. 與其他文件的關係

- 規則邊界：`brian-ai-workflow-decision-rails.md`
- 主資料欄位：`brian-ai-workflow-data-model.md`
- 狀態與 gates：
  - `brian-ai-workflow-state-machine.md`
  - `brian-ai-workflow-phase-gates.md`
- review 操作：`review-and-learning-playbook.md`

## 14. 待補問題

- 是否要拆成 lane-specific recap schema
- `operating_controller` 是否也應進 recap
- `upstream_source` 是否應正式成 recap 欄位
