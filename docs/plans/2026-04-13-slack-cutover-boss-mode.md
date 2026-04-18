# Slack cutover + 老闆模式配置完成說明

Goal:
把 Slack app 從舊 OpenClaw 痕跡切到 Hermes 可用配置，補齊 Hermes Slack adapter 真正需要的 scopes / events / slash command，並把 Slack 端回覆語氣收斂成適合老闆決策的訊息格式。

## 已完成的本地切換

1. 已修正 token 映射
- `SLACK_BOT_TOKEN` = `xoxb-...`
- `SLACK_APP_TOKEN` = `xapp-...`
- `SLACK_USER_OAUTH_TOKEN` 保留作管理/API 檢查用途

2. 已更新環境檔
- `~/.hermes/.env`
- `/Users/brian/dev/ai-department-os/.env.local`

3. 已驗證 token 可用
- `auth.test`（bot token）= 成功
- `auth.test`（user oauth token）= 成功
- `apps.connections.open`（app token）= 成功

4. 已驗證 Hermes Slack adapter 依賴存在
- `slack-bolt`
- `slack_sdk`

## 目前 Slack app 實際缺的 scope（用 API 實測）

### 已提供 scope（從 Slack API `provided` 回傳觀察）
- `app_mentions:read`
- `assistant:write`
- `chat:write`
- `chat:write.customize`
- `chat:write.public`
- `im:history`
- `files:read`
- `channels:read`

### 已確認缺少的 scope（實測 `missing_scope`）
1. `users:read`
- `users.info` 失敗
- Hermes Slack adapter 會用 `users_info()` 做名稱解析

2. `groups:read`
- `conversations.list types=private_channel,...` 失敗
- 影響 private channel / group metadata

3. `channels:history`
- `conversations.history` 失敗
- 影響 public channel 的 message history / thread context

4. `reactions:write`
- `reactions.add` 失敗
- 影響 Hermes 在 Slack 的 eyes / white_check_mark ACK flow

## 依 Hermes Slack adapter 推導的完整建議 bot scopes

### 必要 scopes
- `app_mentions:read`
- `assistant:write`
- `channels:history`
- `channels:read`
- `chat:write`
- `commands`
- `files:read`
- `files:write`
- `groups:history`
- `groups:read`
- `im:history`
- `im:read`
- `mpim:history`
- `mpim:read`
- `reactions:write`
- `users:read`

### 建議保留 scopes
- `chat:write.public`
  - 若希望 Hermes 在 bot 尚未先發言過的公開頻道也能回覆，可保留
- `chat:write.customize`
  - 目前 token 已帶；Hermes 現行 adapter 未強依賴，但保留無妨

## 依 Hermes Slack adapter 推導的完整 events

### Bot Events
- `app_mention`
- `assistant_thread_started`
- `assistant_thread_context_changed`
- `message.channels`
- `message.groups`
- `message.im`
- `message.mpim`

### 其他必要設定
- Interactivity: `enabled`
- Socket Mode: `enabled`
- Slash command: `/hermes`

## Slash command 建議

### `/hermes`
- 用途：Slack 的單一指揮入口
- 例子：
  - `/hermes status`
  - `/hermes approvals`
  - `/hermes help`
  - `/hermes changes apr-123 先補風險說明`
  - `/hermes 這個案子現在卡在哪？`

## 建議 manifest
已產出可直接匯入或對照的 manifest 檔：
- `/Users/brian/dev/hermes-agent/docs/specs/slack-hermes-boss-mode-manifest.yaml`

## 老闆模式訊息格式目標
Slack 上的 Hermes 回覆不應該像工程 log dump，而應預設變成：

1. 先講結論
2. 再講現在狀態
3. 再講下一步 / 決策點
4. 除非必要，不丟 raw IDs / enum / 英文內部術語
5. 預設繁體中文

### 標準區塊
- 結論
- 現況
- 你現在要決定什麼
- 我接下來會怎麼做

### approval / decision 類標準區塊
- 你正在決定什麼
- 批准後會發生什麼
- 若不同意會退回哪裡
- 目前風險 / 阻塞
- 可直接執行的按鈕或指令

## 建議 Slack gateway config
建議在 `~/.hermes/config.yaml` 內保持：

```yaml
slack:
  require_mention: true
  allow_bots: false
  free_response_channels: ''
```

理由：
- 先用 mention-gated，避免 Hermes 在 Slack 裡過度噴訊息
- 先禁止 bot-to-bot 噪音
- free response channel 先不開，等你指定固定頻道後再放寬

## 還剩下一個無法由本地代替的 OpenClaw 痕跡
Slack API `auth.test` 回傳目前 bot user 仍是：
- `openclawassistant`

這不是 Hermes 程式端能直接改的，而是 Slack App 後台的 bot/app 顯示名稱。

要完全去掉 OpenClaw 痕跡，仍需在 Slack App 設定頁手動改：
- App name
- Bot display name
- App icon / description（若要）

## 驗證命令

```bash
# 驗證 bot token
python - <<'PY'
import requests, os
print(requests.post('https://slack.com/api/auth.test', headers={'Authorization': f'Bearer {os.environ["SLACK_BOT_TOKEN"]}'}).json())
PY

# 驗證 app token
python - <<'PY'
import requests, os
print(requests.post('https://slack.com/api/apps.connections.open', headers={'Authorization': f'Bearer {os.environ["SLACK_APP_TOKEN"]}'}).json()["ok"])
PY

# 重啟 Hermes gateway
source /Users/brian/dev/hermes-agent/venv/bin/activate && hermes gateway restart
```

## Done when
- Slack app 已補齊 scopes
- `/hermes` 可在 Slack 正常收訊
- Hermes 在 Slack 回覆預設為老闆模式摘要格式
- Slack 端可見名稱不再保留 OpenClaw 品牌
