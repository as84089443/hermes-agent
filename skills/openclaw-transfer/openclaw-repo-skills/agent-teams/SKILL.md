---
name: agent-teams
description: 將 dsclca12/agent-teams 作為 OpenClaw 龍蝦的本地參考提示詞庫使用；用來借鏡角色設計、交付物格式、品質門檻與跨代理協作方式，而不是直接生成 61 隻新魚。
---

# Agent Teams Reference

這個 skill 把 `agent-teams` 安裝成本地參考庫，方便在龍蝦裡查閱和借鏡外部 agent 設計。

## 何時使用

- 需要幫現有魚補強 persona、工作流程或交付物格式。
- 需要替新魚找成熟 prompt 範本，但不想從零寫。
- 需要比較 OpenClaw 現有魚和外部 agent library 的差異。

## 重要原則

1. 這是「參考庫」，不是要一次把 61 個 agent 全部註冊進龍蝦。
2. OpenClaw 既有 `workspace-*` 的 `SYSTEM_PROMPT.md` / `SOUL.md` 仍是 source of truth。
3. 借鏡時優先抽取：
   - 工作流程
   - 決策框架
   - KPI / 驗收標準
   - 交付物模板
4. 不要直接覆蓋龍蝦既有的瀏覽器策略、真實整合規則、cron/flow 慣例。

## 路徑

- 原始提示詞庫：
  `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams`
- 龍蝦魚群對照：
  `/Users/brian/.openclaw/skills/agent-teams/references/openclaw-fish-map.md`
- 安裝說明：
  `/Users/brian/.openclaw/skills/agent-teams/README.md`

## 建議用法

1. 先看對照表，找到最接近的魚。
2. 再開對應的外部 prompt 檔，抽取可沿用段落。
3. 最後把可用部分改寫進 OpenClaw 既有魚的 prompt 或 SOP，而不是整份照搬。

## 快速例子

- `marketing` 可先看：
  - `marketing/marketing-content-creator.md`
  - `marketing/marketing-social-media-strategist.md`
  - `marketing/marketing-growth-hacker.md`
- `admin` / `dev-fish` 可先看：
  - `specialized/agents-orchestrator.md`
  - `project-management/project-management-studio-operations.md`
- `qa` 可先看：
  - `testing/testing-evidence-collector.md`
  - `testing/testing-reality-checker.md`
