# Workflow Metrics Schema

日期：2026-04-15

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 在 Phase B 需要收集的 metrics schema。

目標：
- 讓 workflow self-improvement loop 可量測
- 讓 routing、recap、do-not-ask、mismatch 不再只靠感覺判斷
- 為未來是否接官方 self-evolution repo 提供客觀 gate

## 2. 一句話定義

workflow metrics 不是 dashboard 漂亮數字，而是用來回答：
- 系統到底有沒有少重問
- routing 到底有沒有變準
- recap 到底有沒有越來越完整
- 哪一層知識還沒有收斂

## 3. Metrics 分層

### Layer A：Routing Metrics
衡量 intake / routing 的判斷品質。

### Layer B：Learning Metrics
衡量 sidecar / rulebook / do-not-ask 是否真的在學。

### Layer C：Closure Metrics
衡量案件是否真的走完 close / recap / writeback 閉環。

## 4. 核心 Metrics（v1 必做）

### 4.1 `routing_correction_rate`
定義：
- routing 後，最終被 human 修正的比例

計算：
- 分母：有進 routing 的 case 數
- 分子：產生 routing mismatch 的 case 數

意義：
- 越高代表 routing 仍常判錯
- 若長期不下降，不適合接官方 evolution repo

### 4.2 `repeated_clarification_count`
定義：
- 同類客戶 / 品牌 / lane 問題被重複詢問的次數

建議切法：
- by customer line
- by brand
- by question type

意義：
- 越高代表 sidecar / do-not-ask 沒有真正生效

### 4.3 `do_not_ask_hit_rate`
定義：
- 命中 do-not-ask 規則後，成功避免重問的比例

計算概念：
- 分母：命中 do-not-ask 的 routing 次數
- 分子：命中後未再詢問同問題的次數

意義：
- 這是衡量「系統有沒有真的學會」的直接指標之一

### 4.4 `recap_pending_rate`
定義：
- review recap 中仍有 pending_fields 的比例

計算：
- 分母：已產生 recap 的 case 數
- 分子：pending_fields 非空的 recap 數

意義：
- 越低代表 review capture 越完整
- 若長期偏高，代表 episode capture 還不穩

## 5. 建議 Metrics（v1 可以一起做）

### 5.1 `customer_sidecar_hit_rate`
定義：
- routing 過程中命中 customer sidecar 的比例

### 5.2 `brand_sidecar_hit_rate`
定義：
- routing 過程中命中 brand sidecar 的比例

### 5.3 `sidecar_confidence_promotion_rate`
定義：
- customer / brand sidecar 從 low/medium 升到 high 的比例

### 5.4 `rulebook_writeback_rate`
定義：
- recap 後，有多少案件真的產生有效 rulebook 更新

### 5.5 `high_value_mismatch_pool_size`
定義：
- 可進官方 evolution repo eval dataset 的 mismatch 筆數

## 6. Metrics 記錄單位

### 6.1 `workflow_metric_event`
每一筆事件記錄：
- 發生了什麼
- 發生在哪個 case
- 影響哪個 metric

### 6.2 `workflow_metric_snapshot`
週期性快照：
- 某時間點的總體統計
- 供 dashboard / retrospection / milestone review 使用

## 7. `workflow_metric_event` schema

### 7.1 基本欄位
- `event_id`
- `created_at`
- `case_id`
- `event_type`
- `metric_family`
- `value`
- `dimension`
- `notes`

### 7.2 枚舉建議

#### `event_type`
- `routing_mismatch_created`
- `clarification_repeated`
- `do_not_ask_hit`
- `do_not_ask_miss`
- `recap_created`
- `recap_pending`
- `sidecar_promoted`
- `rulebook_updated`

#### `metric_family`
- `routing`
- `learning`
- `closure`

### 7.3 JSON 範例

```json
{
  "event_id": "wme_20260415_001",
  "created_at": 1776200000,
  "case_id": "case_20260415_001",
  "event_type": "routing_mismatch_created",
  "metric_family": "routing",
  "value": 1,
  "dimension": "client_owner",
  "notes": "system guessed shared, human corrected to Brian-owned"
}
```

## 8. `workflow_metric_snapshot` schema

### 8.1 基本欄位
- `snapshot_id`
- `created_at`
- `window_start`
- `window_end`
- `routing_correction_rate`
- `repeated_clarification_count`
- `do_not_ask_hit_rate`
- `recap_pending_rate`
- `customer_sidecar_hit_rate`
- `brand_sidecar_hit_rate`
- `sidecar_confidence_promotion_rate`
- `high_value_mismatch_pool_size`

### 8.2 JSON 範例

```json
{
  "snapshot_id": "wms_20260415_weekly",
  "created_at": 1776209999,
  "window_start": "2026-04-08",
  "window_end": "2026-04-15",
  "routing_correction_rate": 0.22,
  "repeated_clarification_count": 6,
  "do_not_ask_hit_rate": 0.71,
  "recap_pending_rate": 0.18,
  "customer_sidecar_hit_rate": 0.63,
  "brand_sidecar_hit_rate": 0.28,
  "sidecar_confidence_promotion_rate": 0.09,
  "high_value_mismatch_pool_size": 14
}
```

## 9. 哪些 metrics 可以當 gate

### 9.1 接官方 self-evolution repo 前的 gate
若以下條件尚未達成，不建議接官方 evolution：
- `routing_correction_rate` 還很高
- `recap_pending_rate` 還很高
- `do_not_ask_hit_rate` 還很低
- `high_value_mismatch_pool_size` 還太少或太髒

### 9.2 建議 gate（第一版）
可先用這組保守門檻：
- `routing_correction_rate < 0.30`
- `recap_pending_rate < 0.25`
- `do_not_ask_hit_rate > 0.60`
- `high_value_mismatch_pool_size >= 10`

這不是最終門檻，但足以當第一版 go / no-go 判斷。

## 10. AI 可以做什麼

AI 可以：
- 自動產生 metric events
- 自動聚合成 snapshot
- 提示趨勢是否改善
- 提示哪個 lane / 客戶線問題最多

AI 不可以：
- 自己篡改 baseline
- 自己把 bad run 當成 good run
- 自己決定已達到 evolution gate 而不提示人審

## 11. 與其他文件的關係

- self-improvement 主邏輯：`brian-ai-workflow-self-improvement-loop.md`
- mismatch：`routing-mismatch-schema.md`
- recap：`review-recap-schema.md`
- routing 規則：`brian-ai-workflow-routing-rules.md`

## 12. 待補問題

- metrics events 是否要直接掛在 case timeline 下
- snapshot 產生頻率：每日 / 每週 / milestone 待定
- 是否要為 wedding / studio_rental 做 lane-specific metrics
