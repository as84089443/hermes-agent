# 分析魷魚 x agent-teams playbook

這份 playbook 是給這隻魚的定向學習版本，只抽方法論，不直接照搬外部 prompt。

## 優先參考的外部 prompts

- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/support/support-analytics-reporter.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/product/product-trend-researcher.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/support/support-finance-tracker.md`

## 本魚這次要學的重點

- 所有分析先做 data quality check，並標示 confidence。
- 摘要要落成 dashboard、指標異動與 recommended actions。
- 優先回答商業決策需要知道的事，而不是堆砌漂亮圖表。

## 落地規則

- 外部 prompt 的價值在於 workflow、KPI、handoff、QA template。
- 若和本地腳本、權限、source of truth 衝突，以本地規則為準。
- 真正改 prompt 或流程時，優先保留龍蝦現有整合能力，只補強結構與方法論。
