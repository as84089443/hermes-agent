# 海豚客服自動化 x agent-teams playbook

這份 playbook 是給這隻魚的定向學習版本，只抽方法論，不直接照搬外部 prompt。

## 優先參考的外部 prompts

- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/support/support-support-responder.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/product/product-behavioral-nudge-engine.md`
- `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/specialized/report-distribution-agent.md`

## 本魚這次要學的重點

- 把客服流程明確分成 intent routing、support tier 和 escalation。
- 把滿意度、補資料與回購提醒設計成低摩擦 nudges。
- 任何自動回覆都要保留人工接手與例外處理的閘門。

## 落地規則

- 外部 prompt 的價值在於 workflow、KPI、handoff、QA template。
- 若和本地腳本、權限、source of truth 衝突，以本地規則為準。
- 真正改 prompt 或流程時，優先保留龍蝦現有整合能力，只補強結構與方法論。
