# Hermes：AI 公司 / 多 AI 員工 / 老闆人格管理

## 建議結論

### Phase 1 最值得先做的切口
做「任務委派與交接（Delegation + Handoff）」，不是先做完整 AI 組織圖。

一句話定義：
老闆（使用者 + boss persona）下達一個目標後，Hermes 能把工作拆成數個可指派任務，交給不同 AI 員工角色處理，並在明確節點要求老闆批示或介入。

這個切口要落在既有能力上：
- boss-mode 指揮台
- web 對話
- 對話追蹤
- 排程管理

也就是把 Hermes 從「單一對話 agent」升級成「有主管、有員工、有交接狀態的任務流系統」。

### Phase 2 延伸切口
做「老闆人格治理層（Boss Policy Layer）」。

一句話定義：
不是只讓老闆人格存在於 prompt，而是把它變成可影響委派、審核、升級、風險偏好的管理規則。

例如：
- 哪類任務必須先請示老闆
- 哪類任務可自動委派
- 哪些輸出風格遵循老闆人格
- 什麼情況要升級回報
- 不同 AI 員工各自適合什麼工作

## 為什麼這是最高槓桿切口

### 1. 它直接把現有能力串成閉環
現在 Hermes 已有：
- boss-mode 指揮台
- 對話入口
- 對話追蹤
- 排程

缺的不是更多聊天頁，而是「任務如何被分派、執行、交接、升級、回報」。

只要補上 delegation/handoff，原本分散的能力就會變成一個可運作的 AI 團隊閉環：
目標輸入 → 任務拆解 → 指派員工 → 交付產物 → 要老闆批示 → 繼續推進。

### 2. 它比先做『多 agent 展示』更容易證明價值
很多多 AI 產品會先做：
- agent roster
- agent 頭像
- agent 聊天室
- agent 互聊

這些很容易看起來厲害，但很難形成穩定商業價值。

相反，委派與交接能直接回答使用者最在意的問題：
- 現在誰在做事？
- 卡在哪？
- 下一步是誰？
- 什麼時候需要我批？
- 最後交付是什麼？

### 3. 它天然承接『老闆人格管理』
老闆人格最適合先介入的不是生成內容本身，而是管理決策：
- 拆解偏好
- 風險偏好
- 審核門檻
- 升級規則
- 回報風格

這樣老闆人格就不是一個抽象 persona，而是實際變成管理系統的一部分。

### 4. 它是未來 AI 公司的底座，不是一次性功能
未來若要長成 AI 公司，後面會加：
- 部門
- KPI
- 專案模板
- 跨任務記憶
- 自動化排班
- 員工能力評級

但這些都建立在同一個底層事實上：
「一個工作如何被分派、接手、追蹤、審批、結案。」

先把這層做好，後面才能自然擴張。

## Phase 1：最小落地範圍

### 產品定義
做一個「AI 員工任務流」：
- 一個目標 / brief
- 系統拆成數個任務
- 每個任務有 owner（某 AI 員工角色）
- 任務之間可 handoff
- 某些節點要求 boss approval
- 指揮台能看到全局狀態

### 優先支援的員工角色
先不要開放完全自定義組織。先固定 3-4 個通用角色：
- Researcher：搜集資訊、整理脈絡
- Planner / PM：拆任務、排優先級、定下一步
- Operator / Maker：執行產出
- Reviewer：做 QA、風險檢查、補漏

重點不是 agent 個性有多豐富，而是角色責任清楚。

### 成功標準
使用者在同一個指揮台可以完成：
- 提出目標
- 看見 Hermes 自動拆解任務
- 看見任務被不同 AI 角色承接
- 在必要節點親自批示
- 收到最終交付與過程摘要

## 需要新增的最小資料欄位 / 狀態

不要一開始做超大的 org schema。v1 只補任務流需要的最小欄位。

### 1. Work Item / Task
建議新增：
- task_id
- parent_goal_id
- title
- objective
- owner_type
  - `boss`
  - `ai_role`
  - `human`
- owner_id
  - 例如 `researcher`, `planner`, `reviewer`
- status
  - `draft`
  - `queued`
  - `in_progress`
  - `waiting_handoff`
  - `waiting_boss_approval`
  - `blocked`
  - `done`
  - `cancelled`
- priority
- due_at
- input_context_refs
- output_artifact_refs
- handoff_to
- approval_required
- approval_reason
- created_by
- last_updated_at

### 2. Goal / Mission
如果目前只有 conversation/thread，需補一個較高階容器：
- goal_id
- title
- desired_outcome
- success_criteria
- boss_persona_id
- overall_status
  - `active`
  - `waiting_on_boss`
  - `blocked`
  - `completed`
- next_decision
- next_owner

### 3. Handoff Event
這是多 AI 協作真正的關鍵事件：
- handoff_id
- from_owner_id
- to_owner_id
- related_task_id
- handoff_note
- expected_output
- status
  - `pending_accept`
  - `accepted`
  - `rejected`
  - `completed`
- created_at
- completed_at

### 4. Boss Approval / Escalation
- approval_id
- related_task_id
- approval_type
  - `go_no_go`
  - `content_review`
  - `priority_decision`
  - `risk_exception`
- requested_by
- decision_status
  - `pending`
  - `approved`
  - `revise`
  - `rejected`
- decision_note
- decided_at

### 5. Persona Policy（先做輕量版）
不要先做完整人格系統，先做管理策略欄位：
- boss_persona_id
- management_style
  - `hands_on`
  - `delegative`
  - `high_standard`
  - `fast_execution`
- approval_threshold
- escalation_rules
- output_style_prefs

這樣就夠讓人格先影響管理流程。

## 指揮台應新增哪些區塊

重點不是新增更多頁，而是在 boss-mode 指揮台增加 4 個管理區塊。

### 1. 任務委派總覽（Delegation Board）
要回答：現在有哪些工作、誰在做、卡在哪。

區塊內容：
- 任務列表 / 看板
- 依 owner / status / priority 篩選
- 顯示 next owner、due time、是否需老闆批示
- 可直接重派任務

### 2. 交接與阻塞區（Handoff + Blockers）
這是 v1 的核心區塊。

區塊內容：
- 最近 handoff 流
- 哪些交接等待接受
- 哪些任務卡住、卡因為缺資料/缺批示/缺外部回覆
- 一鍵催辦 / 重新指派 / 升級給 boss

### 3. 老闆待決策佇列（Boss Decision Queue）
把老闆介入從聊天訊息中抽出來，變成明確 queue。

區塊內容：
- 待批准項目
- 為什麼需要你決策
- 建議選項
- 一鍵 approve / revise / reject
- 決策後自動推進後續任務

### 4. 組織脈搏摘要（Team Pulse）
不是做 BI 儀表板，而是做營運感知。

區塊內容：
- 目前活躍中的 AI 員工角色
- 每位角色的任務數、完成數、阻塞數
- 最近 24h 重要進展
- 需要老闆注意的 3 件事

## Phase 2：老闆人格治理層

Phase 1 做出任務流後，Phase 2 再把老闆人格從「可選 prompt」升級成「治理配置」。

### 要做的不是更多人格聊天
而是讓人格影響：
- 任務拆解方式
- 授權邏輯
- 審核門檻
- 回報頻率
- 語氣與輸出風格
- 風險升級條件

### Phase 2 的最小功能
- Boss policy profile 編輯器
- 每個 goal 綁定一個 boss policy
- AI 員工依 policy 決定何時自行推進、何時升級
- 指揮台可看到「這次決策是依哪條 boss policy 做的」

### Phase 2 才值得新增的東西
- 員工能力分級 / 信任分數
- 部門視角（research / ops / content）
- 常見工作模板
- 不同 boss persona 切換
- 跨專案學習與最佳委派建議

## v1 不應先做的事

### 1. 不要先做完整 AI 公司組織圖
例如：
- 部門樹
- 匯報線
- 職級系統
- 薪酬 / KPI 模擬

這些很有戲，但對第一個閉環價值不高。

### 2. 不要先做大量自定義 AI 員工
先固定少數角色即可。
若一開始就支援：
- 自訂職稱
- 自訂 prompt
- 自訂部門
- 自訂權限
會把產品拖進配置泥沼。

### 3. 不要先做 agent-to-agent 自由對話空間
自由互聊很炫，但不容易管理，也難以追責。
應先要求所有協作都落在 task / handoff / approval 上。

### 4. 不要先做重型 analytics / KPI 儀表板
v1 先看：
- 任務是否完成
- 哪裡阻塞
- 哪裡要老闆介入

不用先做複雜報表。

### 5. 不要先做過深的人格編排系統
不要一開始就做：
- 多人格混編
- 人格繼承
- 人格版本樹
- 哲學式心理模型

先把人格收斂成管理 policy，才有落地價值。

## 最後的產品判斷

如果要把「AI 公司 / 多 AI 員工 / 老闆人格管理」收斂成 Hermes 接下來 1-2 個 phase 的落地切口：

### 最佳切口
Phase 1 = 任務委派與交接層
Phase 2 = 老闆人格治理層

### 核心原因
因為它們：
- 最能復用 Hermes 已有 boss-mode / 對話 / 追蹤 / 排程能力
- 最容易形成可觀測、可管理、可審批的 AI 團隊閉環
- 最能把「老闆人格」從抽象 prompt 變成真正的管理機制
- 同時為未來更完整的 AI 公司產品打底

### 一句話版本
先不要做一間看起來很大的 AI 公司；先做一個真的能委派、交接、升級、批示的 AI 小團隊。