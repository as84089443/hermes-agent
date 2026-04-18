# Brian AI Workflow File Structure

日期：2026-04-14

## 1. 這份文件的目的
- 定義 Brian AI workflow 應如何放置文件、規格、playbook 與資料輸出
- 避免 blueprint / specs / playbooks / exports 混在一起

## 2. 整體結構

```text
docs/
  plans/
    2026-04-14-brian-ai-workflow-v1.md

  specs/
    brian-ai-workflow-decision-rails.md
    brian-ai-workflow-data-model.md
    brian-ai-workflow-state-machine.md
    brian-ai-workflow-routing-rules.md

  playbooks/
    intake-playbook.md
    pm-playbook.md
    wedding-playbook.md
    studio-rental-playbook.md
    review-and-learning-playbook.md

exports/google_calendar_history/
  historical_income_normalized_v*.json
  historical_income_normalized_v*.csv
  vendor_master_sidecar_v1_20260414.json
  customer_brand_sidecar_v1_20260414.json
  analysis_rulebook_v1_20260414.json
```

## 3. `docs/plans/`
### 用途
- 放藍圖、總覽、方向文件

### 應放內容
- 為什麼做這套 workflow
- v1 / v2 範圍
- 與 bw-sop 的整合方向

### 不應放內容
- 詳細欄位 schema
- 枚舉值細節
- 歷史輸出資料

## 4. `docs/specs/`
### 用途
- 放系統規格
- 給 agent / app / future automation 共用

### 應放內容
- decision rails
- data model
- state machine
- routing rules

### 不應放內容
- 操作手冊
- 臨時討論
- 輸出資料快照

## 5. `docs/playbooks/`
### 用途
- 放人怎麼操作這套系統
- 面向 Brian / Chu / Jerry / PM / operator

### 應放內容
- intake 怎麼做
- PM 怎麼處理案子
- 婚禮線怎麼走
- 場租線怎麼走
- 結案後怎麼回寫與學習

## 6. `exports/google_calendar_history/`
### 用途
- 放真實分析資料與 sidecar
- 作為 AI workflow 的知識底層，不是正式產品規格文件

### 應放內容
- normalized income tables
- vendor sidecar
- brand sidecar
- rulebook
- clustering / map outputs

### 不應放內容
- 最終規格定義
- 正式 SOP 文件

## 7. sidecar 與共享表單的邊界
### 原則
- 不污染共享 Google Sheets 原表
- 所有分析補欄位先寫到 Hermes sidecar / exports

### 共享表單保留做什麼
- 原始營運資料
- 匯款 / 案名 / 分帳 / 基本記錄

### Hermes sidecar 補什麼
- 客戶歸屬
- PM 歸屬
- 品牌歸屬
- do-not-ask-again 規則
- relationship notes

## 8. 與 bw-sop 的文件關係
### bw-sop 提供
- masterplan
- state machine
- machine-readable contract 思想
- decision rails
- quote/change review/booking discipline

### Brian AI workflow 應新增
- 針對 Brian 真實客戶與品牌結構的規格
- Brian / Jerry / Chu 的角色關係
- AI routing 與案例回寫規則

## 9. 命名規則
### plans
- `YYYY-MM-DD-topic.md`

### specs
- `brian-ai-workflow-<topic>.md`

### exports
- `<dataset>_vN_YYYYMMDD.json`
- `<dataset>_summary_vN_YYYYMMDD.json`

## 10. 文件維護順序
1. 先改 specs
2. 再回寫 plans
3. playbooks 跟著 specs 更新
4. exports 只反映資料，不主導規格

## 11. 待補問題
- state-machine 文件尚未建立
- playbooks 尚未展開
- 之後是否需要將 exports 遷到獨立 knowledge/ 目錄待評估
