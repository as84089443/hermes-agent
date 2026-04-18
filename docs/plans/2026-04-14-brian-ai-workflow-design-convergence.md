# Brian AI Workflow 總設計收斂

日期：2026-04-14

## 1. 這份文件要回答什麼

這份文件不是再新增一層規格，而是把目前已完成的 Brian AI workflow 文件收斂成一個老闆可判斷的總設計摘要。

它只回答四件事：
1. 這套系統的核心到底是什麼
2. 目前哪些東西已經定了
3. 哪些東西還沒定，不能假裝已解決
4. v1 真正應先做什麼，不該先做什麼

## 2. 一句話總結

Brian AI Workflow 的正確定位不是聊天助理、不是單點工具、不是報價系統，而是：

以 `case operating system` 為核心、以 `bw-sop decision rails` 為治理底盤、以 `AI routing + recap learning` 為加速器的營運系統。

它的目標不是把 Brian 從流程中移除，而是把 Brian 從「所有事情都要自己記、自己追、自己重新判斷」的狀態中抽離，讓系統先做 intake、分流、提醒、版本控制與學習沉澱，而 Brian 只處理高價值決策與關鍵輸出。

## 3. 目前已收斂出的核心設計

### 3.1 系統主體：以 case 為核心
這套系統不是以訊息、任務、客戶、檔案為核心，而是以 `case` 為主體。

原因：
- 收入與交付都是 case 發生
- owner / PM / Brian 是否出工都是 case 層決策
- approval、scope lock、change review 都是 case 層邏輯
- AI 的 intake、routing、recap 都圍繞 case 運作

### 3.2 治理底盤：直接吸收 bw-sop，而不是另造一套
已明確吸收的 bw-sop 核心精神：
- 先制度化，再自動化
- PM-driven，不讓 AI 越權
- 狀態機要固定
- quote / artifact version 要固定
- confirmed 後 scope lock
- confirmed 後變更需 formal change review
- docs 是人類規則，machine-readable contract 是系統投影

結論：
Brian AI workflow 應該視 `bw-sop` 為 donor governance layer，而不是平行產品。

### 3.3 業務結構不是單一收入模式
目前設計已正視 Brian 的真實經營結構至少有五條線：

1. Brian 核心執行收入
2. Brian PM / 接案收入
3. Brian 兼具 PM 與執行
4. 共同客戶 / 共同 PM 線
5. 資產收入（場租 / 租棚）

補充：
- 麻花影像是共同經營婚禮品牌
- B.W.Studio 是共同工作 / 共同出班系統
- Chu 在婚禮與部分後製線具有實際主控角色
- BNI 不是背景，而是重要 lead / relationship source

### 3.4 規則來源不再靠腦中記憶
系統目前已經建立 4 種知識層：
- case 主表
- customer sidecar
- brand sidecar
- analysis rulebook / do-not-ask-again

這表示未來系統應該先查規則，再問 Brian，而不是每次從零開始判斷。

## 4. 已完成的文件與它們的角色

### 藍圖層
- `docs/plans/2026-04-14-brian-ai-workflow-v1.md`
- 定義整體目標與 operating model

### 規格層
- `docs/specs/brian-ai-workflow-decision-rails.md`
- `docs/specs/brian-ai-workflow-data-model.md`
- `docs/specs/brian-ai-workflow-routing-rules.md`
- `docs/specs/brian-ai-workflow-state-machine.md`
- `docs/specs/brian-ai-workflow-phase-gates.md`
- `docs/specs/brian-ai-workflow-file-structure.md`

這層已經回答：
- 系統怎麼守規矩
- 系統要記什麼
- 系統怎麼分流
- 系統狀態怎麼推進
- 每個 phase 什麼時候能過關
- 檔案應怎麼放，不要混亂

### 操作層
- `docs/playbooks/intake-playbook.md`
- `docs/playbooks/pm-playbook.md`
- `docs/playbooks/wedding-playbook.md`
- `docs/playbooks/review-and-learning-playbook.md`
- `docs/playbooks/studio-rental-playbook.md`

這層已經回答：
- 新案怎麼進來
- PM 怎麼推案
- 婚禮線怎麼走
- 結案後怎麼學習
- 場租線怎麼獨立運作

### 資料與知識層
- `historical_income_normalized_v*.json/csv`
- `vendor_master_sidecar_v1_20260414.json`
- `customer_brand_sidecar_v1_20260414.json`
- `analysis_rulebook_v1_20260414.json`

這層不是產品規格，但它是現實世界知識基底。

## 5. 現在真正已經定下來的 10 個關鍵決策

1. 這是一個 case OS，不是單點功能。
2. AI 是加速器，不是最終決策者。
3. 新案進來先自由描述，再最少補問。
4. 所有案件都必須有 owner。
5. 每案必有一個主 lane。
6. confirmed 後 scope lock 生效。
7. confirmed 後關鍵變更一定走 change review。
8. quote / artifact 必須有 version。
9. 已確認的客戶 / 品牌 / 案件線要進 do-not-ask-again。
10. 租棚是資產收入線，不能混進主動執行收入。

## 6. 還沒有定完、不能假裝已解決的問題

### 6.1 `operating_controller` 是否正式入模
現在已知道：
- PM owner 不等於實際控制者
- 麻花影像線常是 Chu 主控

但目前 data model 還沒正式把 `operating_controller` 當欄位定下來。
這是一個 v1.1 很可能要補的點。

### 6.2 上游合作方的正式建模仍不夠完整
我們已經知道：
- 有些案子案源來自上游（如三立、永恆少年、錨點）
- 但最終客戶線可能算 Brian 的，也可能不是

目前規則有了，但資料結構還沒把 `upstream_source` 正式拉成一級欄位。

### 6.3 共同客戶 / 共同 PM 線的責任邊界仍待更精細化
雖然已經有 routing 規則，
但共同客戶線在：
- current_owner
- final_owner
- approval owner
- billing responsibility
上，之後還需要更精細。

### 6.4 review-and-learning 是否要分 generic 與 lane-specific recap
目前已有總 playbook，
但婚禮線、場租線、商業案線，可能都值得有不同的 recap 模板。

## 7. v1 真正應先做什麼

### 7.1 應先做的，不是完整前台，而是最小可用工作流骨架
優先順序建議：

1. case schema 落地
2. customer / brand sidecar 可查詢
3. routing engine v1
4. intake normalizer v1
5. review / recap writer v1

這五個做出來，系統就開始能跑。

### 7.2 如果要做頁面，先做這三頁
沿用 bw-sop 思路：
1. dashboard
2. cases
3. case detail

這三頁的目的不是好看，而是：
- 能看今日最重要案件
- 能看各案件卡在哪個 gate
- 能完成一次 routing / approve / recap

### 7.3 最先接 AI 的位置
不是全部地方都先接 AI。
最優先的 AI 模組應該是：

A. intake normalizer
- 吃訊息
- 出 normalized brief
- 補最少問題

B. routing assistant
- 根據 rulebook + sidecar 給 lane / owner 候選

C. case recap writer
- 案件結束後產出 recap 草稿
- 並提示 sidecar / do-not-ask-again 更新

這三個的 ROI 最高，也最符合你現在資料狀況。

## 8. v1 現在不該急著做什麼

1. 重型前台 UI
2. 全自動發報價
3. 全自動催款
4. 完整 CRM
5. 完整排程引擎
6. 複雜權限系統
7. 太細的 task tree

原因：
現在系統最缺的不是表面功能，而是規則穩定性與 case 資料一致性。

## 9. 目前最好的寫作策略

接下來文件不應繼續無止境增長，而應遵守：

1. 規則先寫到夠用
- 不追求一次寫成聖經

2. 每寫一份新文件，要有明確角色
- 是 blueprint？spec？playbook？還是 exports？

3. 新文件應優先服務：
- 實作 routing
- 實作 case schema
- 實作 recap learning

4. 新規則應先進 sidecar / rulebook，等穩定後再進 spec

## 10. 現在最值得做的下一步

如果不急著做產品頁面，最值得的下一步是：

### Option A：寫 `review recap schema`
把 review-and-learning 變成真正可執行的資料格式：
- recap 要有哪些欄位
- 哪些欄位回寫 sidecar
- 哪些欄位進 do-not-ask-again

### Option B：寫 `customer / brand sidecar schema`
因為這兩個是你目前 workflow 真的會一直用的知識層。

### Option C：寫 `routing engine pseudo-spec`
把現在的 routing rules 轉成更接近可實作格式。

### 建議優先順序
我建議下一步優先做：
1. `customer/brand sidecar schema`
2. `review recap schema`
3. `routing engine pseudo-spec`

原因：
你現在最大的價值，不是多一個頁面，而是把「會學習、不重問」這件事正式變成可實作結構。

## 11. 一句話收斂

Brian AI Workflow v1 的真正核心，不是更多 agent，而是：

用 bw-sop 的治理 rails，承接你真實的客戶 / 品牌 / 收入結構，做出一套會分流、會記住、會回寫、會逐步學習的 case operating system。
