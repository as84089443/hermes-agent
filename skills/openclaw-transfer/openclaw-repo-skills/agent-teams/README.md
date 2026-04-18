# Agent Teams for OpenClaw

這份安裝把 [`dsclca12/agent-teams`](https://github.com/dsclca12/agent-teams) 以本地 vendor 參考庫的方式放進龍蝦，不會直接註冊成 61 隻新魚。

## 安裝位置

- 技能入口：
  `/Users/brian/.openclaw/skills/agent-teams/SKILL.md`
- 原始庫：
  `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams`
- 對照表：
  `/Users/brian/.openclaw/skills/agent-teams/references/openclaw-fish-map.md`

## 來源

- Repo: `https://github.com/dsclca12/agent-teams`
- Snapshot commit: `e2a2e460a03d186fb274714ab3c9a21ca80b0cec`
- Installed at: `2026-03-22 Asia/Taipei`

## 為什麼不是直接變成 61 隻魚

- 龍蝦目前已經有自己的 workspace、handoff、cron、外部整合和魚群命名。
- 直接灌入 61 隻新魚會讓編排、身份、workspace 邊界和 source of truth 變亂。
- 這份 repo 最有價值的是 prompt 設計和交付模板，不是它的目錄結構本身。

## 建議下一步

1. 先用對照表挑出 3 到 5 隻最值得借鏡的魚。
2. 只把可執行的規則與模板吸收到現有魚 prompt。
3. 若之後真的要新增魚，再從這個庫挑單一角色做本地化移植。
