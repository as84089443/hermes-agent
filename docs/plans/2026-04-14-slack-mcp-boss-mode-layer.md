# Slack MCP 老闆模式控盤層

已落地位置：
- `scripts/slack_mcp_boss_mode.py`

目的：
1. 用 Slack MCP 穩定主動發訊與回 thread
2. 用 Slack user token 讀取頻道最近訊息
3. 把原始 Slack 對話轉成適合手機決策的老闆模式摘要
4. 支援固定控盤頻道模式，讓你之後不用每次重講頻道名

## 可用指令

列出可讀取頻道：

```bash
source venv/bin/activate
python scripts/slack_mcp_boss_mode.py channels
```

讀指定頻道最近訊息，輸出老闆模式摘要：

```bash
source venv/bin/activate
python scripts/slack_mcp_boss_mode.py summary 一般 --limit 8
python scripts/slack_mcp_boss_mode.py summary ai_reply --limit 8
python scripts/slack_mcp_boss_mode.py summary bw-space --limit 8
```

主動發訊到指定頻道：

```bash
source venv/bin/activate
python scripts/slack_mcp_boss_mode.py post 一般 "結論：今天先處理 A。現況：B 已卡住。下一步：請你拍板。"
```

回覆指定 thread：

```bash
source venv/bin/activate
python scripts/slack_mcp_boss_mode.py reply 一般 1776124500.094329 "我已接手這條 thread。"
```

## 固定控盤頻道模式

設定預設控盤頻道：

```bash
source venv/bin/activate
python scripts/slack_mcp_boss_mode.py set-default 一般
```

查看目前預設控盤頻道：

```bash
source venv/bin/activate
python scripts/slack_mcp_boss_mode.py show-default
```

輸出預設控盤頻道的老闆模式快照：

```bash
source venv/bin/activate
python scripts/slack_mcp_boss_mode.py control-status --limit 8
```

對預設控盤頻道直接發訊：

```bash
source venv/bin/activate
python scripts/slack_mcp_boss_mode.py default-post "結論：先做 A。現況：B 卡住。下一步：請你拍板。"
```

對預設控盤頻道的 thread 直接回覆：

```bash
source venv/bin/activate
python scripts/slack_mcp_boss_mode.py default-reply 1776124500.094329 "我已接手這條 thread。"
```

## 目前已驗證

### 1. Slack MCP 已接上 Hermes native MCP

已配置：
- `~/.hermes/config.yaml`
- `mcp_servers.slack_bw`

可用 native MCP tools：
- `mcp_slack_bw_slack_list_channels`
- `mcp_slack_bw_slack_post_message`
- `mcp_slack_bw_slack_reply_to_thread`
- `mcp_slack_bw_slack_get_users`
- `mcp_slack_bw_slack_get_user_profile`
- 以及其他 prompt/resource tools

### 2. 主動發訊已驗證成功

已成功透過 Slack MCP 發送：
- DM 到 `D0ACEQYSUF4`
- 頻道訊息到 `#一般`

### 3. 頻道讀取已驗證成功

目前用 `SLACK_USER_OAUTH_TOKEN` 成功讀到以下公開頻道最近訊息：
- `#一般`
- `#ai_reply`
- `#ai_compile`
- `#隨機`
- `#bw-space`

其中 `#一般` 的最近測試訊息已成功抓到：
- `<@U0AD94D3J3S> 頻道測試`
- `<@B0AC8DM14CB> 頻道測試`

### 4. 固定控盤頻道模式已驗證成功

目前已將：
- `#一般`

設成預設控盤頻道。

實測成功：
- `show-default`
- `control-status`
- `default-post`

## 當前限制

1. 這套控盤層目前是「主動式」
   - 能主動讀
   - 能主動發
   - 能主動回 thread
   - 但不等於 Slack bot mention 被動自動觸發已修好

2. 頻道歷史讀取目前仰賴 `SLACK_USER_OAUTH_TOKEN`
   - 因現有 bot token 仍缺 `channels:history`
   - 所以讀取與摘要走 user token
   - 發送與 thread 回覆走 Slack MCP / bot token

## 建議使用方式

短期先把它當成：
- Slack 老闆模式後門
- 固定控盤頻道主線
- 不必等 mention 修好才可用

最實用流程：
1. `control-status`
2. 看摘要決定是否介入
3. `default-post ...` 或 `default-reply <thread_ts> ...`

## 實測範例

```bash
python scripts/slack_mcp_boss_mode.py control-status --limit 8
```

輸出：
- 控盤頻道
- 結論
- 現況
- 下一步
- 關鍵片段

這就是第二版可用的固定控盤頻道模式。
