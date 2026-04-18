# Routing Mismatch Schema

日期：2026-04-15

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 中 `routing mismatch` 的正式 schema。

它要解決的問題是：
- 系統一開始怎麼判
- 後來 Brian / PM 怎麼改
- 到底是哪一層判錯
- 這個錯誤應該回寫到哪裡

如果沒有這份 schema，routing 錯誤只會停留在聊天修正，無法變成可學習的 episode，也無法在 Phase B 形成 metric，更無法在 Phase C 餵給官方 self-evolution repo 當 eval dataset。

## 2. 一句話定義

Routing mismatch 是「系統初判」與「人類最終判定」之間的差異紀錄。

它不是 bug log，也不是一般備忘錄，而是 workflow self-improvement loop 的核心 episodic artifact。

## 3. 使用時機

應在以下情況建立 mismatch record：

1. intake / routing engine 給出的 candidate 被 Brian 修正
2. PM 在 `clarifying` 或 `ready_for_quote` 前後修正了 lane / owner / Brian role
3. review recap 發現最終 case classification 和初判不同
4. 系統多次對同型案件做出同樣錯誤推定

## 4. 核心原則

### 4.1 只記錄「有差異」的欄位
mismatch record 不是整份 case copy。
只記：
- 原判
- 最終判定
- 差異欄位
- 差異原因

### 4.2 要區分是「資料不足」還是「規則錯」
這兩種問題完全不同：
- 資料不足 → 先補 sidecar / customer / brand / upstream data
- 規則錯 → 修 routing rules / prompt / heuristics

### 4.3 mismatch 先進 episodic，不直接升 semantic
單次 mismatch 先記錄，不要直接把它升成高信心規則。

### 4.4 mismatch 最終要指向下一步動作
每筆 mismatch 至少要導向以下其中一種：
- update customer sidecar
- update brand sidecar
- update rulebook
- add do-not-ask candidate
- mark for routing prompt optimization
- no action

## 5. `routing_mismatch` 核心欄位

### 5.1 識別欄位
- `mismatch_id`
- `case_id`
- `created_at`
- `created_by`
- `status_at_detection`

### 5.2 上下文欄位
- `case_title`
- `raw_brief`
- `customer_name`
- `brand_or_system`
- `source`
- `primary_lane_at_detection`

### 5.3 系統初判欄位
- `system_lane_candidate`
- `system_client_owner_candidate`
- `system_pm_owner_candidate`
- `system_brian_exec_candidate`
- `system_brian_role_candidate`
- `system_confidence`
- `system_matched_rules`
- `system_missing_fields`

### 5.4 人類最終判定欄位
- `final_lane`
- `final_client_owner`
- `final_pm_owner`
- `final_brian_exec`
- `final_brian_role`

### 5.5 差異欄位
- `mismatched_fields`
- `mismatch_type`
- `root_cause_guess`
- `human_explanation`

### 5.6 後續處置欄位
- `customer_sidecar_update_needed`
- `brand_sidecar_update_needed`
- `rulebook_update_needed`
- `do_not_ask_candidate`
- `routing_prompt_eval_candidate`
- `resolved`
- `resolution_note`

## 6. 欄位定義

### `mismatched_fields`
值：字串陣列

例如：
- `["client_owner", "pm_owner"]`
- `["primary_lane"]`
- `["brian_exec", "brian_role"]`

### `mismatch_type`
建議枚舉：
- `customer_ownership_error`
- `pm_ownership_error`
- `lane_error`
- `execution_role_error`
- `brand_error`
- `insufficient_context`
- `multi_factor`

### `root_cause_guess`
建議枚舉：
- `missing_customer_sidecar`
- `missing_brand_sidecar`
- `missing_upstream_context`
- `missing_do_not_ask_rule`
- `heuristic_overreach`
- `ambiguous_raw_brief`
- `human_only_business_context`
- `unknown`

### `human_explanation`
由 Brian / PM 補充：
- 為什麼系統判錯
- 這案真正的脈絡是什麼

### `routing_prompt_eval_candidate`
值：`true | false`

用途：
- 表示這筆 mismatch 是否值得進官方 self-evolution 的 routing eval dataset

## 7. 最小必填欄位

若要算一筆有效 mismatch，至少需要：
- `mismatch_id`
- `case_id`
- `created_at`
- `case_title`
- `system_confidence`
- `mismatched_fields`
- `mismatch_type`
- `root_cause_guess`
- `resolved`

## 8. 什麼時候應建立 mismatch record

### 一定要建立
- client_owner 被改
- pm_owner 被改
- primary_lane 被改
- Brian 是否親自執行被改
- Brian 角色被改

### 可選建立
- 只補了缺欄位、沒有改變原判
- 只是補充 notes，未影響 routing

## 9. mismatch 的分類邏輯

### 類型 A：資料缺失型
特徵：
- 系統不是亂判，而是缺 sidecar / brand / upstream context
- 這類應優先補知識，不先改 prompt

### 類型 B：啟發式過度延伸型
特徵：
- 系統憑案名 / split ratio 猜過頭
- 這類要收斂 heuristic

### 類型 C：商業脈絡只有 Brian 知道
特徵：
- BNI / 舊同事 / 上游關係 / 黑名單 / 品牌歷史等
- 這類通常要先寫進 sidecar / rulebook

### 類型 D：可進 eval dataset 型
特徵：
- 有清楚的初判
- 有清楚的人類最終判定
- 有清楚 root cause
- 值得拿去優化 routing prompt / heuristic

## 10. 與 metrics 的關係

這份 schema 會直接支援：

### 10.1 routing correction rate
分母：有 routing 的案件數
分子：產生 mismatch 的案件數

### 10.2 mismatch type distribution
- 哪一種錯誤最多
- lane 錯最多，還是 owner 錯最多

### 10.3 root cause distribution
- sidecar 缺資料多
- 還是 heuristic 問題多

### 10.4 high-value mismatch pool
- 哪些 mismatch 值得進官方 evolution repo 的 eval dataset

## 11. 與 self-improvement loop 的關係

在 `brian-ai-workflow-self-improvement-loop.md` 中，routing mismatch 是 Trigger 3。

這份 schema 就是那個 trigger 的正式資料格式。

流程是：
1. routing 產生初判
2. human 修正
3. mismatch record 建立
4. mismatch 被分類
5. 決定寫回 sidecar / rulebook / do-not-ask / eval dataset

## 12. JSON 範例

```json
{
  "mismatch_id": "mm_20260415_001",
  "case_id": "case_20260415_001",
  "created_at": 1776200000,
  "created_by": "Brian",
  "status_at_detection": "clarifying",
  "case_title": "Brian單機-哈利_跑跑薑餅人",
  "raw_brief": "永恆少年行銷案源，我接案後發給哈利拍攝",
  "customer_name": "永恆少年行銷",
  "brand_or_system": "Brian direct",
  "source": "telegram",
  "primary_lane_at_detection": "commercial",
  "system_lane_candidate": "commercial",
  "system_client_owner_candidate": "我",
  "system_pm_owner_candidate": "我",
  "system_brian_exec_candidate": "是",
  "system_brian_role_candidate": "主輸出",
  "system_confidence": "medium",
  "system_matched_rules": ["永恆少年行銷"],
  "system_missing_fields": [],
  "final_lane": "commercial",
  "final_client_owner": "我",
  "final_pm_owner": "我",
  "final_brian_exec": "否",
  "final_brian_role": "僅管理",
  "mismatched_fields": ["brian_exec", "brian_role"],
  "mismatch_type": "execution_role_error",
  "root_cause_guess": "human_only_business_context",
  "human_explanation": "這案是我接案後外發，不是我親自拍。",
  "customer_sidecar_update_needed": false,
  "brand_sidecar_update_needed": false,
  "rulebook_update_needed": true,
  "do_not_ask_candidate": true,
  "routing_prompt_eval_candidate": true,
  "resolved": true,
  "resolution_note": "後續遇到此類外發案應傾向 PM/接案，而非核心執行。"
}
```

## 13. v1 不做的事

- 不做完整 mismatch lineage graph
- 不做自動 root cause clustering
- 不自動把所有 mismatch 送進官方 evolution repo
- 不直接讓 mismatch 自動改 routing rules

## 14. 與其他文件的關係

- routing 規則：`brian-ai-workflow-routing-rules.md`
- self-improvement 主邏輯：`brian-ai-workflow-self-improvement-loop.md`
- recap schema：`review-recap-schema.md`
- customer/brand sidecar：`customer-brand-sidecar-schema.md`

## 15. 待補問題

- mismatch 是否要納入 case repository 子表
- 是否要做 `routing_mismatch_writer`
- 何時把 mismatch 轉成官方 evolution repo 的 eval record
