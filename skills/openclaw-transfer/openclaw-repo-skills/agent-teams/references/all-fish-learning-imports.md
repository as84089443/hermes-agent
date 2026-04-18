# Agent Teams 導入守則

這份文件把 `agent-teams` 的通用方法論導入 OpenClaw 龍蝦，但不覆蓋本地 source of truth。

## 全魚共通原則

1. **多源驗證**
   - 趨勢、市場、客戶與財務結論，至少交叉驗證兩到三個可信來源或資料面。
   - 若資料不完整，明確標記 `confidence`，不要硬下結論。

2. **Evidence First**
   - 對品質、狀態與成果的聲明，盡量附上可驗證證據：檔案、數據、截圖、腳本輸出或明確欄位。
   - 沒有證據時，預設為 pending / needs work，而不是直接宣告完成。

3. **Stage Gate + Clear Handoff**
   - 多步流程要拆成明確階段，寫清楚 owner、blocker、next step。
   - 每次 handoff 要讓下一隻魚能接手，不留下模糊背景。

4. **KPI / ROI / Dashboard Mindset**
   - 每份輸出盡量落成 `status`、`nextStep`、`risk`、`evidenceOrMetric`。
   - 若任務屬於經營、內容、財務或分析，優先補 KPI、變化量與建議動作。

5. **SOP Before Heroics**
   - 先把可重複工作整理成 SOP、模板或腳本，再追求一次性的神操作。
   - 遇到重複 blocker，優先補自動化、fallback 或治理規則。

## 不可覆蓋的龍蝦規則

- 既有 `workspace-*` 的 `SYSTEM_PROMPT.md` / `SOUL.md`
- 真實 API / 腳本入口與本地資料路徑
- 瀏覽器策略與 Chrome + MCP 優先規則
- 既有 cron / orchestration / source-of-truth 邊界

## 正確吸收方式

1. 先讀本文件，再讀各魚的 playbook。
2. 吸收外部 prompt 的 workflow、decision framework、deliverable template。
3. 回到本地工作區，用龍蝦現有的資料源、腳本和邊界落地。
