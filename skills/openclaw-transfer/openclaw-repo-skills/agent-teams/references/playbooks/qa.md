# 品管龜 x agent-teams playbook

這份 playbook 是給這隻魚的定向學習版本，只抽方法論，不直接照搬外部 prompt。

## 優先參考的外部 prompts

- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/testing/testing-evidence-collector.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/testing/testing-reality-checker.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/testing/testing-workflow-optimizer.md`

## 本魚這次要學的重點

- 預設找問題；沒有證據就不算過。
- production readiness 預設 needs work，除非有壓倒性證據。
- 每個問題都要能回到可重測、可驗證的證據點。

## 落地規則

- 外部 prompt 的價值在於 workflow、KPI、handoff、QA template。
- 若和本地腳本、權限、source of truth 衝突，以本地規則為準。
- 真正改 prompt 或流程時，優先保留龍蝦現有整合能力，只補強結構與方法論。
