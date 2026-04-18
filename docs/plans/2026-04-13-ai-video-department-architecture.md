# Hermes AI Video Department Architecture

Date: 2026-04-13

## 目標

把 Hermes 從通用助理，升級成「AI 影片部門」：能接收影片需求、拆解任務、產出腳本/分鏡/資產/剪輯包、完成發布與復盤，並逐步走向更高程度的自治。

核心原則：

- 以 Hermes 現有的 Skills / Memory / Session Search / Cron / Delegate / Gateway 為主幹
- 所有工作產物都落到可追蹤的 wiki / markdown / 資料夾結構
- 用「明確關卡」取代一次性黑盒生成
- 高風險決策保留 human-in-the-loop
- 若既有系統未完成，可直接重造為單一 AI Department OS；現有 repo 僅作參考與遷移素材，不是硬性延續邊界

## 目標態架構

```text
使用者需求
  → 影片總管 Orchestrator
    → 策略 / 腳本 / 分鏡 / 製作 / 剪輯 / 發布 / 觀測
      → 每個階段寫入 wiki 與專案資料夾
        → 進入下一關卡或回饋修正
```

Hermes 不應只是一個會生內容的模型，而是要成為一個「可排程、可分工、可審核、可學習」的影片營運系統。

## 角色與 Agent 分工

### 1) 影片總管 Orchestrator

責任：

- 接收需求、判斷影片類型與優先級
- 建立專案目錄與工作單
- 派發給下游 agents
- 追蹤進度、阻塞與截止日
- 彙整最終結果與復盤

輸入：brief、目標受眾、平台、時長、語氣、預算、截止日

輸出：專案計畫、任務拆解、狀態更新

### 2) 策略 Agent

責任：

- 定義影片目標、受眾、訊息、CTA
- 建議內容形式：教學、短影音、產品介紹、敘事、廣告、直播切片
- 產出影片定位與成功標準

### 3) 腳本 Agent

責任：

- 產出大綱、逐段腳本、旁白稿、字幕稿
- 控制節奏、字數、Hook、轉場、CTA
- 生成多版本：保守版 / 進攻版 / 精簡版

### 4) 分鏡 / 視覺導演 Agent

責任：

- 把腳本轉成 shot list、分鏡表、鏡頭節奏
- 指定畫面構圖、運鏡、B-roll、圖卡、動畫需求
- 對接圖片 / 影片生成工具的提示詞

### 5) 製作 Agent

責任：

- 生成或整理素材：圖像、短片段、音效、配樂、字幕包
- 管理檔案命名、版本、素材清單
- 將生成結果寫入專案資料夾

### 6) 剪輯 / 包裝 Agent

責任：

- 生成剪輯指令、時間軸建議、片頭片尾、字幕樣式、封面文案
- 針對平台做格式化：TikTok / Reels / Shorts / YouTube
- 提供可直接交給人或剪輯工具的「剪輯包」

### 7) 品質與合規 Agent

責任：

- 檢查事實、品牌語氣、敏感內容、版權風險
- 檢查字幕、標題、封面是否與內容一致
- 標記「可自動發布」或「需人工審核」

### 8) 發布與分發 Agent

責任：

- 產出發布文案、標籤、標題 A/B 版本
- 排程發布
- 推送到對應平台或通知人工發布

### 9) 觀測與記憶 Agent

責任：

- 收集播放、完播、點擊、留言、轉化等回饋
- 將有效模式沉澱成 Skill / Memory
- 更新下一支影片的最佳實務

## 工作流階段

### Stage 0: Brief Intake

標準化需求輸入，至少包含：

- 影片目標
- 受眾
- 平台
- 長度
- 語氣 / 品牌
- 素材來源
- 截止日
- 是否可自動發布

建議輸出：`brief.md`

### Stage 1: Strategy

輸出：

- 內容定位
- 核心訊息
- Hook
- CTA
- 風險清單
- 成功標準

### Stage 2: Script + Storyboard

輸出：

- `script.md`
- `storyboard.md`
- `shot-list.csv` 或 `shot-list.md`
- `prompt-pack.md`

### Stage 3: Production

輸出：

- 原始素材
- 生成資產
- 字幕檔
- 配樂 / 音效清單
- 素材版本記錄

### Stage 4: Edit + QC

輸出：

- 可交付剪輯包
- QC 報告
- 發布建議
- 需人工決策項目

### Stage 5: Publish + Distribute

輸出：

- 發布文案
- 平台特化版本
- 排程記錄
- 發布回執

### Stage 6: Analytics + Learning

輸出：

- 成效摘要
- 可複用模式
- 新技能 / 更新技能
- 記憶更新建議

## Hermes 的接口設計

### 1) Skills = 影片能力模組

把每個影片流程做成 skill：

- `video-brief`
- `video-strategy`
- `video-script`
- `video-storyboard`
- `video-production`
- `video-edit-pack`
- `video-qc`
- `video-publish`
- `video-postmortem`

每個 skill 都要有：

- When to Use
- Procedure
- Pitfalls
- Verification
- 對應輸出檔案格式

### 2) Memory = 長期偏好與品牌規格

應保存：

- 品牌語氣、禁用詞、Logo / 字色 / 字體規範
- 常用平台與輸出比例
- 使用者對節奏、風格、長度的偏好
- 已驗證有效的內容模板

不應保存：

- 大量腳本全文
- 一次性素材
- 每次影片的臨時草稿

### 3) Session Search = 查歷史案例

用於：

- 找回過去相似影片的策略
- 找出曾經成功的 hook / CTA / 視覺套路
- 回看失敗原因與修正方式

### 4) Cron = 自動化例行工作

適合：

- 每日選題掃描
- 每週內容排程
- 發布後 24h / 72h 成效回收
- 每月內容復盤

### 5) Gateway = 日常協作入口

適合把 Hermes 變成團隊工作流：

- 使用者在聊天工具丟 brief
- Hermes 回傳計畫、待審項、發布提醒
- 人工在同一入口按核准 / 退回 / 修改

### 6) Wiki / File System = 單一真相來源

建議專案結構：

```text
.hermes/video/
  projects/<project-id>/
    brief.md
    strategy.md
    script.md
    storyboard.md
    assets/
    edit/
    qc.md
    publish.md
    analytics.md
```

## 先自動化什麼

第一波優先自動化：

1. Brief 標準化與任務拆解
2. 腳本初稿與多版本生成
3. 分鏡表與 prompt pack
4. 發布文案與平台格式化
5. 成效回收與復盤摘要
6. 將成功流程沉澱成 skill / memory

第二波再自動化：

- 素材管理
- 基礎剪輯規則
- A/B 標題與封面生成
- 排程發布

第三波才考慮：

- 全自動成片
- 自動上架
- 自動迭代下一版內容

## 必須保留人工介入的項目

Human-in-the-loop 必須保留在：

- 最終創意方向與品牌策略
- 事實性高風險內容
- 法務、版權、肖像、授權
- 代言、醫療、金融、政治等敏感內容
- 最終發布 / 對外代表公司發言
- 任何涉及真實人物聲音 / 臉部的生成

建議原則：

- 低風險內容可自動執行
- 中風險內容先出建議，再人工核准
- 高風險內容一律人工簽核

## 建議的自治階段

### Phase 1: AI 助理

- Hermes 產出建議與草稿
- 人工執行與發布

### Phase 2: AI 製作助理

- Hermes 自動產出腳本、分鏡、包裝、排程
- 人工只做審核與發布

### Phase 3: AI 影片部門

- Hermes 自動管理多個影片專案
- 具備例行排程、復盤、記憶更新
- 人工只介入關鍵決策

### Phase 4: 半自治助手

- Hermes 可根據目標自發提出內容計畫
- 監控成效並主動優化流程
- 人工改為監督者

## 成功指標

- 從 brief 到可審腳本的時間
- 每支影片的返工次數
- 人工介入比例
- 發布後表現提升幅度
- 可復用 skill 的累積數量
- 復盤後被 memory 化的有效模式數

## 結論

Hermes 應被設計成「影片營運作業系統」而不是單一生成器。最關鍵的是：用 skills 管流程、用 memory 管偏好、用 wiki 管專案、用 cron 管例行、用 gateway 管協作、用 human gate 管風險。這樣才能從 AI 影片部門，逐步走向全自動 AI 助手。