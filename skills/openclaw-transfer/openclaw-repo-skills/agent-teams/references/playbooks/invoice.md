# 電鰻發票 x agent-teams playbook

這份 playbook 是給這隻魚的定向學習版本，只抽方法論，不直接照搬外部 prompt。

## 優先參考的外部 prompts

- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/support/support-finance-tracker.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/support/support-legal-compliance-checker.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/project-management/project-management-project-shepherd.md`

## 本魚這次要學的重點

- 報價到發票是一條 state machine，不是單次文件產生。
- 正式對外文件要先過合規、稅務欄位與審計軌跡檢查。
- 逾期、尾款與催收要有固定節奏與升級門檻。

## 落地規則

- 外部 prompt 的價值在於 workflow、KPI、handoff、QA template。
- 若和本地腳本、權限、source of truth 衝突，以本地規則為準。
- 真正改 prompt 或流程時，優先保留龍蝦現有整合能力，只補強結構與方法論。
