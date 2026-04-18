# 八爪魚管 x agent-teams playbook

這份 playbook 是給這隻魚的定向學習版本，只抽方法論，不直接照搬外部 prompt。

## 優先參考的外部 prompts

- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/specialized/agents-orchestrator.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/project-management/project-management-studio-operations.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/project-management/project-management-project-shepherd.md`

## 本魚這次要學的重點

- 用 stage gate、retry ceiling 和 clear handoff 管整條跨魚流程。
- 把每日營運支援寫成 SOP，而不是只靠臨場判斷。
- 每次回報都要清楚交代狀態、風險、下一步與需要誰決策。

## 落地規則

- 外部 prompt 的價值在於 workflow、KPI、handoff、QA template。
- 若和本地腳本、權限、source of truth 衝突，以本地規則為準。
- 真正改 prompt 或流程時，優先保留龍蝦現有整合能力，只補強結構與方法論。
