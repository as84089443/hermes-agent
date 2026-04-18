# AI 公司 v1 Operating Model

## 1. v1 最小可用組織圖

### 核心原則
- v1 不是做一間「很像公司」的 AI 模擬器，而是做一間「真的能交付」的 AI 公司。
- 先做 6–8 個關鍵角色，不要一開始就開十幾個部門。
- 先把閉環做通：收任務 → 拆解 → 執行 → 驗證 → 升級請示 → 交付 → 留存知識。
- 老闆只做 3 件事：定方向、批風險、拍板取捨。

### 建議 v1 組織圖

1. 老闆（使用者）
2. CEO / Chief of Staff Agent（總管）
3. PMO / Dispatcher Agent（任務分派）
4. Research Agent（研究分析）
5. Execution Agent（執行製作）
6. QA / Critic Agent（驗證稽核）
7. Memory / Knowledge Agent（知識沉澱）
8. Persona Board（人格董事會，非日常執行層）

### 部門切分

#### A. 指揮中樞
- CEO / Chief of Staff Agent
- PMO / Dispatcher Agent
- 功能：接老闆指令、定任務策略、切工、控進度、決定是否升級。

#### B. 生產部門
- Research Agent
- Execution Agent
- 功能：把任務真正做出來，不只是討論。

#### C. 品保與風控
- QA / Critic Agent
- 功能：驗證品質、抓錯、做交付前檢查。

#### D. 組織記憶
- Memory / Knowledge Agent
- 功能：把每次任務的 learnings、偏好、禁忌、模板寫回系統。

#### E. 董事會 / 管理人格層
- Persona Board
- 功能：在重大決策、策略分歧、風格取捨時介入，不要每件小事都下場。

## 2. 各角色設計：職責、輸入、輸出、何時升級給老闆

### 2.1 CEO / Chief of Staff Agent

#### 職責
- 當 AI 公司唯一對老闆窗口。
- 把老闆指令轉成任務章程（objective, scope, deadline, constraints, success criteria）。
- 決定是單線處理還是多 agent 並行。
- 整合各部門輸出，產出最後交付與狀態回報。

#### 典型輸入
- 老闆一句話交辦
- 歷史上下文
- 公司記憶與偏好
- 目前資源狀態

#### 典型輸出
- 任務章程
- 任務計畫與 owner 指派
- 升級請示單
- 最終交付包
- 老闆看的簡報式更新

#### 何時必須升級給老闆
- 目標不清，且會導致方向完全不同。
- 需要取捨：速度 vs 品質、成本 vs 影響、品牌風格 vs 轉換率。
- 涉及外部發布、對外承諾、金錢支出、法律/合規/高風險。
- 任務偏離原始範圍超過約 30%。
- AI 內部意見分歧且無法靠規則收斂。

### 2.2 PMO / Dispatcher Agent

#### 職責
- 把任務拆成可執行 work packages。
- 指定 owner、依賴、優先級、完成定義（DoD）。
- 控 SLA、追進度、管理 blocked 狀態。
- 確保 handoff 清楚，不讓 agent 互相丟模糊球。

#### 典型輸入
- CEO 任務章程
- 資源池與 agent 能力表
- 任務模板

#### 典型輸出
- Task list
- Handoff brief
- Priority queue
- 阻塞清單
- 日/週節奏報告

#### 何時升級給老闆
- deadline 不可達且需改承諾。
- 同時有多個高優先任務衝突，需要老闆排 priority。
- 缺乏必要外部資訊或權限。

### 2.3 Research Agent

#### 職責
- 蒐集資料、做競品/市場/用戶/技術研究。
- 產出 decision memo，而不是一堆原始資料。
- 標記不確定性、假設、資料可信度。

#### 典型輸入
- 問題陳述
- 研究範圍
- 時間盒（例如 30 分鐘 / 2 小時）
- 成功標準

#### 典型輸出
- Research memo
- Options with pros/cons
- 建議方案與理由
- 待驗證假設清單

#### 何時升級給老闆
- 找不到足夠可信資料，會影響決策。
- 發現重大新資訊，會推翻原策略。
- 需要老闆提供內部資料、商業判斷或人脈資訊。

### 2.4 Execution Agent

#### 職責
- 依 brief 產出實物：文案、企劃、規格、程式、報告、素材包等。
- 先交付可用版本，再做優化。
- 對自己的輸出做基本自檢。

#### 典型輸入
- Handoff brief
- Research memo
- 標準模板
- 既有 brand / product / style guide

#### 典型輸出
- Draft v1
- Final deliverable
- 變更紀錄
- 已知風險與待確認事項

#### 何時升級給老闆
- 需求改動會導致重做主體。
- 老闆偏好不明，且不同風格差異很大。
- 需要人類授權才能繼續（如發送、上線、簽核）。

### 2.5 QA / Critic Agent

#### 職責
- 當內部反對者，不是潤稿員。
- 依照 checklist 驗證完整性、正確性、風險、可執行性。
- 決定：通過 / 退回 / 升級。

#### 典型輸入
- Draft / final artifact
- 任務章程
- QA checklist
- 風險政策

#### 典型輸出
- QA report
- 問題清單與嚴重度
- Release recommendation
- 是否可直接交付老闆

#### 何時升級給老闆
- 有高風險問題但時間不允許修完。
- 品質與 deadline 必須二選一。
- 內容可能影響品牌、法務、聲譽。

### 2.6 Memory / Knowledge Agent

#### 職責
- 把任務結果轉成組織資產。
- 更新：老闆偏好、成功模板、失敗案例、術語、黑名單做法。
- 讓下一次任務更快更準。

#### 典型輸入
- 任務章程
- 最終交付
- QA report
- 老闆 feedback

#### 典型輸出
- Memory update
- SOP 更新
- Prompt / template 更新
- Reusable playbook

#### 何時升級給老闆
- 偵測到偏好衝突（老闆過去要求彼此矛盾）。
- 需要確認某偏好是否要升級成全域規則。

### 2.7 Persona Board（人格董事會）

#### 定位
- 不是人人都能發號施令。
- 是「決策增強層」，在重大節點介入。
- 形式上可以是多個創辦人/高績效人格，例如：產品腦、增長腦、品牌腦、營運腦、財務腦。

#### 職責
- 針對高不確定、高取捨決策提出不同視角。
- 幫 CEO 形成 recommendation，不直接取代老闆。

#### 典型輸入
- 問題陳述
- 可選方案
- 風險與利弊
- 當前目標權重

#### 典型輸出
- 董事會意見摘要
- 多視角辯論紀錄
- 建議方案排序

#### 何時升級給老闆
- 各人格結論明顯衝突。
- 決策本質是價值判斷，不是資訊不足。
- 涉及品牌定位、長期策略、重大資源配置。

## 3. 從老闆交辦到完成交付的標準流程

### Stage 0：接案與正規化
負責：CEO Agent

把老闆一句話轉成標準 brief：
- 目標是什麼
- 成功算什麼
- deadline 是什麼
- 不要做什麼
- 哪些地方需要請示

輸出：Task Charter v1

### Stage 1：任務分級
負責：CEO + PMO

把任務分成三類：
- L1 直接執行：低風險、可逆、規格清楚
- L2 受控執行：中風險，需要 QA gate
- L3 老闆授權型：高風險、高不確定、不可逆

規則：
- L1 可直接開工
- L2 必須經 QA 才能交付
- L3 沒有老闆批准不能往下走

### Stage 2：拆解與派工
負責：PMO

把任務拆成：
- Research
- Draft / Build
- QA
- Final packaging
- Memory capture

每個 task 必須有：
- owner
- input
- output
- deadline
- DoD
- escalation rule

輸出：Project board / task queue

### Stage 3：研究與方案形成
負責：Research Agent

先做必要研究，不准一開始就盲做。
研究完要輸出：
- 事實
- 假設
- 建議方案
- 還缺什麼

若存在重大策略取捨，啟動 Persona Board 快速評議。

輸出：Research memo + recommendation

### Stage 4：執行產出
負責：Execution Agent

按 brief 先做可用版本，不要等完美才出稿。
原則：
- 先出 v1
- 清楚列出假設
- 不確定處標注，不要假裝確定

輸出：Draft / artifact

### Stage 5：QA 與風險檢查
負責：QA / Critic Agent

至少檢查 5 件事：
- 有沒有回答原問題
- 有沒有明顯錯誤或遺漏
- 是否可執行
- 是否違反老闆偏好/品牌規範
- 是否需要升級請示

結果只有三種：
- Pass：可交付
- Revise：退回修正
- Escalate：請老闆拍板

輸出：QA report

### Stage 6：升級請示（必要時）
負責：CEO Agent

升級給老闆時，不要丟整包混亂資訊。
請示格式固定為：
- 你要決定什麼
- 為什麼現在要決定
- 方案 A / B / C
- 各自代價
- AI 建議哪個
- 你若不回，預設方案是什麼

這一步很關鍵。AI 公司不是把問題丟回去，而是把決策壓縮後再請老闆拍板。

### Stage 7：最終交付
負責：CEO Agent

交付包建議固定包含：
- 一頁式 executive summary
- 主交付物
- 已做假設
- 風險與後續建議
- 若要繼續，下一步是什麼

### Stage 8：記憶回寫
負責：Memory Agent

任務完成後必做：
- 記下老闆 feedback
- 更新模板與 SOP
- 記下這次為什麼成功/失敗
- 標記事後不該再問老闆的問題

這一步沒做好，AI 公司永遠像新人。

## 4. 升級請示機制（Escalation Model）

### v1 建議只保留 4 種升級類型

1. Scope Escalation
- 任務範圍變大或變形
- 例：本來寫一篇文，變成要做整套 campaign

2. Decision Escalation
- 需要價值取捨或戰略拍板
- 例：品牌優先還是轉換優先

3. Risk Escalation
- 有法務、聲譽、金流、對外發布風險
- 例：公開聲明、合約措辭、客戶回覆

4. Resource Escalation
- 缺資訊、缺權限、缺預算、缺外部輸入
- 例：需要帳號、API key、素材、客戶名單

### 升級閾值
v1 先用簡單規則，不要搞複雜分數卡：
- 不可逆動作 → 一律升級
- 涉及金錢/法務/對外承諾 → 一律升級
- 超出原 brief 30% 以上 → 升級
- 內部 2 次 revise 仍不能收斂 → 升級
- 會導致 deadline fail → 升級

### 升級 SLA
- P1：阻塞整體任務，立即請示
- P2：24 小時內需要回覆
- P3：可先按預設方案前進，但同步回報

## 5. 建議的任務單與交接單格式

### 任務章程 Task Charter
- Objective
- Success criteria
- Scope
- Out of scope
- Deadline
- Constraints
- Approval gates
- Default decision rule

### Handoff Brief
- 上一步產出摘要
- 本步要完成什麼
- 不能犯的錯
- 格式要求
- 截止時間
- 如卡住先問誰

### QA Report
- 是否符合目標
- 重大問題
- 次要問題
- 建議修正
- 是否可交付
- 是否需老闆決策

## 6. v1 管理節奏

### 老闆看什麼
老闆不應該管理每個 agent，而是看 3 個面板：
- Active projects：現在有哪些任務在跑
- Approval queue：有哪些需要你拍板
- Delivery log：已完成什麼、效果如何

### AI 公司內部節奏
- 任務啟動：即時
- 進度回報：只在 milestone 或 blocked 時回報
- 任務結束：一定有 completion summary
- 每週：Memory Agent 產出一次 SOP / 偏好更新摘要

## 7. 風險與過度設計警告

### 風險 1：一開始角色太多
最常見錯誤是設一堆頭銜：CMO agent、CFO agent、HR agent、Strategy agent、Innovation agent。
結果不是更聰明，是更多轉述、更多等待、更多 hallucination。

v1 原則：
- 沒有穩定工作量的角色，不要獨立成部門。
- 一個 agent 能兼兩個帽子，就先兼。

### 風險 2：人格董事會變成日常噪音
人格思維很有價值，但如果每件事都叫所有人格發言，成本會爆炸。

正確做法：
- 只有在高價值決策才啟動 Persona Board。
- 平常用單一 CEO/PMO 流程跑。

### 風險 3：只有討論，沒有交付物
很多 multi-agent 系統很會開會，不會交付。

v1 鐵律：
- 每一步都要有 artifact。
- 沒有產出物的 agent 對話，盡量刪掉。

### 風險 4：升級機制太模糊
如果 agent 不知道何時該請示，就會兩種極端：
- 什麼都問老闆，變成助理
- 什麼都不問，最後做錯大方向

所以 v1 一定要把升級規則寫死。

### 風險 5：記憶機制缺位
沒有 Memory Agent，AI 公司每次都像重新 onboarding。
這會讓老闆覺得「你很聰明，但不長記性」。

### 風險 6：過早追求全自動
v1 不要追求無人公司。
先追求的是：
- 任務自己拆
- 多 agent 自己協作
- 該問時才問
- 交付品質穩定

這才是真正可落地的 autonomous operator。

## 8. 最後建議：v1 先做成什麼樣子

如果要一句話定義 v1：

「一個由 CEO Agent 統籌、PMO 派工、Research/Execution 生產、QA 守門、Memory 累積經驗、Persona Board 在關鍵決策時介入的 AI 公司作業系統。」

### 最值得先做的能力，不是更多 agent，而是 4 個制度
1. 標準任務章程
2. 明確 handoff 格式
3. QA gate
4. 升級請示模板

因為先把制度做對，AI 員工才會像組織；否則只是很多 prompt 同時說話。