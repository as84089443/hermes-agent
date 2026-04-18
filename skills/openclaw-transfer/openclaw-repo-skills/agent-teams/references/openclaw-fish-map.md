# OpenClaw 魚群對照 `agent-teams`

這份表不是要一對一照搬，而是幫你快速找到「哪隻魚最值得借鏡哪個外部 agent」。

## 最值得先學的魚

### `marketing` 飛魚行銷

- 最接近的外部 agent:
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/marketing/marketing-content-creator.md`
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/marketing/marketing-social-media-strategist.md`
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/marketing/marketing-growth-hacker.md`
- 建議吸收:
  - 跨平台內容日曆和內容復用策略
  - 內容表現和 ROI 指標
  - 實驗節奏與漏斗優化框架
- 原因:
  - 龍蝦的行銷魚現在已經很接近「內容 + 發布 +通知」，最缺的是跨平台策略層和成效閉環。

### `seo` 藍鯨 SEO

- 最接近的外部 agent:
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/marketing/marketing-content-creator.md`
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/product/product-trend-researcher.md`
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/support/support-analytics-reporter.md`
- 建議吸收:
  - 關鍵字到內容支柱的規劃方式
  - 趨勢信號多源驗證
  - 報表中的置信度、數據品質和行動建議格式
- 原因:
  - SEO 魚已經有 GSC 主流程，下一步最值得補的是更成熟的研究模板與報表輸出。

### `admin` 八爪魚管

- 最接近的外部 agent:
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/specialized/agents-orchestrator.md`
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/project-management/project-management-studio-operations.md`
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/project-management/project-management-project-shepherd.md`
- 建議吸收:
  - 嚴格 stage gate 與 retry 上限
  - 流水線狀態報告模板
  - SOP 化的營運支援與風險升級格式
- 原因:
  - `admin` 本來就偏 orchestration，中介這個庫的價值最大。

### `qa`

- 最接近的外部 agent:
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/testing/testing-evidence-collector.md`
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/testing/testing-reality-checker.md`
- 建議吸收:
  - 證據優先的驗收語氣
  - 預設找問題而不是預設通過
  - QA 報告模板和自動失敗觸發條件
- 原因:
  - 這兩份 prompt 跟龍蝦的 QA / 健檢文化非常對味，幾乎可以直接拿方法論。

### `analyst`

- 最接近的外部 agent:
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/support/support-analytics-reporter.md`
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/product/product-trend-researcher.md`
- 建議吸收:
  - KPI dashboard 模板
  - 數據品質檢查和置信度聲明
  - 洞察轉行動建議的寫法
- 原因:
  - 龍蝦的 `analyst` 下一步就是把摘要升級成可追蹤的週/月輸出。

## 次優先但值得參考

### `cs`

- 最接近的外部 agent:
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/support/support-support-responder.md`
- 可借鏡:
  - 多渠道客服框架
  - 升級條件
  - 客服品質分析指標

### `finance` / `finance-company` / `invoice`

- 最接近的外部 agent:
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/support/support-finance-tracker.md`
- 可借鏡:
  - 現金流預測模板
  - 預算/差異分析格式
  - 審計軌跡與風險控制口吻

### `production`

- 最接近的外部 agent:
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/project-management/project-management-project-shepherd.md`
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/project-management/project-management-studio-operations.md`
- 可借鏡:
  - 專案狀態與風險欄位
  - 交付驗收門檻
  - 資源協調和 bottleneck 報告格式

### `content`

- 最接近的外部 agent:
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/marketing/marketing-content-creator.md`
  - `/Users/brian/.openclaw/skills/agent-teams/vendor/agent-teams/design/design-brand-guardian.md`
- 可借鏡:
  - 故事弧、內容支柱
  - 品牌一致性檢查
  - 多格式內容產線思維

## 不建議直接照搬的部分

- 外部 repo 裡很多 agent 假設的是一般軟體團隊或通用商業團隊，不知道龍蝦目前的真實整合限制。
- 其中部分 prompt 偏重理想化 KPI，搬進龍蝦前要先改成可由現有資料源量到的指標。
- 龍蝦的瀏覽器策略、真實世界權限、workspace 邊界都比這個外部庫更具體，不能被覆蓋。

## 實用建議

1. 第一批只建議吸收 `admin`、`marketing`、`qa`、`analyst`。
2. 每次只挑一份外部 prompt 的一到兩個段落移植，不要整份貼進現有魚。
3. 若要正式改 prompt，先保留龍蝦既有的外部整合規則，再補上外部庫的結構化模板。
