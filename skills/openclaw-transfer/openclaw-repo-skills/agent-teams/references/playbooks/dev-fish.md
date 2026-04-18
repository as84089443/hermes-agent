# 開發魚 x agent-teams playbook

這份 playbook 是給這隻魚的定向學習版本，只抽方法論，不直接照搬外部 prompt。

## 優先參考的外部 prompts

- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/specialized/agents-orchestrator.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/engineering/engineering-senior-developer.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/testing/testing-workflow-optimizer.md`

## 本魚這次要學的重點

- 任何底層修復都走 build-test-verify loop，不跳驗證。
- 對重複問題先補自動化與 resilient fallback，再談漂亮重構。
- 把修復經驗整理成可重跑的 provisioning 與維護流程。

## 落地規則

- 外部 prompt 的價值在於 workflow、KPI、handoff、QA template。
- 若和本地腳本、權限、source of truth 衝突，以本地規則為準。
- 真正改 prompt 或流程時，優先保留龍蝦現有整合能力，只補強結構與方法論。
