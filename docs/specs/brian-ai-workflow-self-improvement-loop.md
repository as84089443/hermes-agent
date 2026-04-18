# Brian AI Workflow Self-Improvement Loop

日期：2026-04-14

## 1. 這份文件的目的

這份文件正式定義 Brian AI workflow 的自我進化機制。

它回答：
1. 系統從哪些事件學習
2. 學到的東西先放哪一層記憶
3. 什麼條件下可升級成穩定規則
4. 哪些東西可以由 AI 建議、哪些必須人確認
5. 知識要回寫到哪裡
6. 如何避免系統一邊學、一邊把自己學壞

這份文件的定位不是長篇理念，而是：
- 讓 recap writer
- sidecar updater
- do-not-ask detector
- routing mismatch tracker
未來都能有共同的 governing logic。

## 2. 一句話定義

Brian AI workflow 的自我進化，不是自動改 code，而是：

把每個案件、每次變更、每次修正、每次重複提問，轉成可驗證的規則與知識回寫，讓未來 intake / routing / PM / review 不再重複犯同樣的錯。

## 3. 核心原則

### 3.1 先學規則，再談自動改自己
v1 的自我進化重點不是 code self-edit，而是：
- 不再重問已知問題
- 不再重猜已知客戶線
- 能從案例萃取穩定 routing 規則
- 能把 recurring pattern 轉成模板資產

### 3.2 記憶必須分層
不能把所有聊天或案件都直接當長期規則。

### 3.3 所有規則升級都要有 confidence
沒有 confidence 的規則，不能直接變成高信心 routing 基礎。

### 3.4 AI 可以提出 writeback 建議，但不能自己定案關鍵歸屬
特別是：
- `client_owner`
- `pm_owner`
- `brian_exec`
- `brian_role`
- `income_nature`
- `do_not_ask_again`
都不能由 AI 直接拍板。

## 4. 三層記憶架構

### 4.1 Working Memory
用途：
- 存當前案件或當前 session 的暫時資訊
- 用完可丟，不應直接視為長期知識

在 Brian workflow 中對應：
- current case draft
- pending clarification
- latest routing candidates
- current owner / next action

### 4.2 Episodic Memory
用途：
- 記錄單次事件 / 單次案件 / 單次錯誤 / 單次修正
- 保留具體脈絡

在 Brian workflow 中對應：
- review recap
- change review record
- routing mismatch record
- single-case correction note

### 4.3 Semantic Memory
用途：
- 存穩定規則與可跨案件重用的知識

在 Brian workflow 中對應：
- customer sidecar
- brand sidecar
- analysis rulebook
- do-not-ask-again
- 穩定後的 routing rules / playbook 更新

## 5. 觸發自我進化的事件

### Trigger 1：Case Close
當案件進入 `closed` 前：
- 必須產生 recap
- recap 應判斷是否更新 sidecar / rulebook

### Trigger 2：Change Review
若 confirmed 後發生 scope change：
- 記錄這次變更
- 判斷這是例外還是規則缺漏
- 若是規則缺漏，標記為 update candidate

### Trigger 3：Routing Mismatch
若系統原本判 A，最後被 Brian / PM 改成 B：
- 記錄 mismatch
- 判斷問題來自：
  - customer sidecar 缺資料
  - brand sidecar 缺資料
  - routing rule 不完整
  - AI 語意判讀失誤

### Trigger 4：Repeated Clarification
若同類問題被 Brian 重複回答：
- 應視為 `do_not_ask_again_candidate`
- 提示更新 customer / brand sidecar 或 rulebook

### Trigger 5：Recurring High-Value Pattern
若同型案件、同型客戶線、同型 lane 持續出現：
- 應標記為 template candidate
- 或 routing shortcut candidate

## 6. 自我進化流程

### Phase A：Capture
先把事件留成 episode，不急著升規則。

輸入來源：
- case close
- review recap
- routing mismatch
- change review
- user correction

輸出：
- episode record

### Phase B：Classify
判斷這是：
- 單次例外
- 重複模式
- 高價值 recurring 模式
- 需要修正既有規則

### Phase C：Recommend Writeback
系統提出建議：
- update customer sidecar?
- update brand sidecar?
- update analysis rulebook?
- add do-not-ask-again?
- create template candidate?

### Phase D：Human Confirmation
Brian / PM 決定：
- 接受
- 延後
- 拒絕

### Phase E：Promote
通過確認後，把知識從 episodic 提升到 semantic。

## 7. Confidence 規則

### 7.1 初始 confidence
- 單次 heuristic 推論 → `low`
- 單次 Brian 明確確認 → `medium`
- 多次 Brian 明確確認或多案穩定驗證 → `high`

### 7.2 升級條件
可從 `low -> medium`：
- 同一規則被 Brian 明確確認一次
- vendor / brand / income 資料互相支持

可從 `medium -> high`：
- 同一規則在多案成立
- 或 Brian 已重複確認兩次以上
- 或被設為 do-not-ask-again 且長期無反例

### 7.3 降級條件
若：
- 新案 repeatedly 打臉舊規則
- Brian 明確修正既有規則
則 confidence 應下降，必要時移出 do-not-ask-again。

## 8. 什麼可以直接回寫，什麼不可以

### 8.1 AI 可直接建議回寫的項目
- `notes`
- `known_contacts`
- `known_org_context`
- `relationship_type` 候選
- `template_candidate_reason`
- `recurring_pattern_candidate`

### 8.2 必須人確認的項目
- `client_owner`
- `pm_owner`
- `brian_exec`
- `brian_role`
- `income_nature`
- `do_not_ask_again`

## 9. 回寫目標

### 9.1 回寫到 customer sidecar
適用於：
- 新客戶第一次被確認
- 舊客戶歸屬更穩定
- 發現這是 BNI 夥伴 / 上游合作方 / 共同客戶線

### 9.2 回寫到 brand sidecar
適用於：
- 發現某案其實是麻花 / B.W.Studio / 其他品牌線
- 發現某品牌主控角色改變

### 9.3 回寫到 analysis rulebook
適用於：
- 某條規則已在多案成立
- 某條規則被修正
- 某案已不該再重問

### 9.4 回寫到 playbook / spec
適用於：
- 某種模式已不是單案知識，而是系統級規則
- 例如：某 lane 常見變更模式、某 recurring 類型 SOP

## 10. Do-Not-Ask-Again 機制

### 10.1 進入條件
符合以下任一條件：
- Brian 已明確確認兩次以上
- 同一答案已在多案反覆成立
- 這條知識已足以直接用於 routing

### 10.2 不可進入的情況
- Brian 自己仍不確定
- 只是一次性猜測
- 案型太特例

### 10.3 系統行為
命中 do-not-ask-again 時：
- 先套用既有規則
- 只補問尚未確定欄位
- 不可重問已知客戶 / 品牌 / 路由結論

## 11. 典型例子

### 例 1：哈利案
- 起初看似 Brian 單機案
- 後來 Brian 說明：是他接案，再外發給哈利
- 系統學到：
  - 這條案屬 Brian 客戶線
  - 但收入性質偏 PM/接案
  - 不該誤算成 Brian 親自執行

### 例 2：麻花影像婚禮線
- 多個婚禮案逐步顯示：
  - 品牌屬共同經營
  - PM owner 可共同
  - 但實際主控偏 Chu
- 系統學到：
  - 婚禮線不可只按普通共同客戶看待

### 例 3：小白故事 / 立方品
- Brian 已多次確認它們是他的客戶線
- 系統學到：
  - 這些應進 do-not-ask-again
  - 後續 intake / routing 不該再反覆提問

## 12. v1 最值得先落地的自我進化模組

### Module A：Review Recap Writer
- 從 close / review 階段產出 recap draft

### Module B：Sidecar Update Recommender
- 根據 recap 建議是否更新 customer / brand sidecar

### Module C：Do-Not-Ask Candidate Detector
- 根據 repeated clarification 與高信心規則提出候選

### Module D：Routing Mismatch Tracker
- 記錄系統原判與 human 最終修正的差異

## 13. v1 不做的事

- 不直接讓 AI 自動改 code
- 不直接讓 AI 自動改 spec 主文件
- 不直接讓 AI 自動提升所有規則到 high confidence
- 不先做超複雜 multi-memory infra

## 14. 與其他文件的關係

- 規則邊界：`brian-ai-workflow-decision-rails.md`
- sidecar schema：`customer-brand-sidecar-schema.md`
- recap schema：`review-recap-schema.md`
- review 操作：`review-and-learning-playbook.md`
- routing：`brian-ai-workflow-routing-rules.md`

## 15. 待補問題

- 是否要把 episodic records 正式存成獨立檔案格式
- 是否要把 routing mismatch 做成獨立 schema
- 何時允許 AI 對低風險欄位自動回寫 sidecar
