---
name: boss-mode-mobile-decision-ui
description: 將充滿內部術語、事件名、ID、流程節點的工程後台，重構成適合手機使用者與決策者閱讀的「老闆模式」介面。先做資訊翻譯，再做結構收斂，不要盲目擴功能。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [mobile, ux, product, dashboard, decision-ui, executive, zh-hant]
---

# Boss-Mode Mobile Decision UI

用在這種情況：
- 使用者主要從手機看系統
- 使用者看得到頁面，但看不懂「到底有什麼功效」
- 頁面充滿 event 名稱、artifact id、task_state_changed、內部 gate 名稱、流程術語
- 系統已經有後台骨架，但還沒有跨過「使用者感受到價值」那條線

核心原則：
先把系統語言翻成決策語言，再擴功能。
如果使用者看不懂，優先修內容與資訊層級，不要繼續加 schema、artifact、workflow 節點。

## 先判斷：現在缺的是功能，還是可理解性？

如果使用者說出類似這些話：
-「一堆文字，看不到實際功效」
-「我看不懂哪裡有問題，或能不能繼續推進」
-「這些 event 名稱 / id / 狀態我都看不懂」

就先不要擴功能。
先做這 3 步：
1. 重新審查首頁、專案頁、審批頁的可理解性
2. 找出第一次使用者最看不懂的詞與區塊
3. 把主畫面改成「決策入口」，把系統字串降到第二層

## 審查方法：第一次使用者視角

用瀏覽器實際看三頁：
- `/projects`
- `/projects/[id]`
- `/approvals`

每頁問自己：
- 我一眼知道這頁要我做什麼嗎？
- 我一眼知道現在卡在哪嗎？
- 我一眼知道我要不要介入嗎？
- 主畫面是不是先顯示人話摘要，而不是系統狀態？

特別把這些字標成高風險術語：
- `task_state_changed`
- `artifact_written`
- `art-xxxx`
- `vid-xxxx`
- `payload shape`
- `direction_lock`
- `publish pack`
- `research`
- 任何 eventType / enum / internal id

## 改造順序

### 第一階段：先做摘要卡，不先動底層流程

專案頁最上方先放 3 張摘要卡：
1. 目前方向
2. 目前卡點
3. 下一個決策

這三張卡要回答：
- 系統現在在做什麼
- 現在卡在哪個具體問題
- 你現在要拍板什麼

文案格式建議：
- 目前方向：`目前先依 brief 推進：...`
- 目前卡點：`現在卡在：...`
- 下一個決策：`現在要你決定：...`

不要用模糊句型，例如：
- `Next action not assigned`
- `task_state_changed · research`
- `artifact_written · director`

### 第二階段：長文折疊，摘要優先

把長文內容折疊到第二層：
- 完整 brief
- 導演方向草稿
- 執行流程圖
- 完整活動紀錄

首頁和專案頁第一屏不要先出現長篇 raw content。
先顯示摘要卡，然後用：
- `展開查看完整 brief`
- `展開查看導演方向`
- `展開查看執行流程圖`

但要注意：折疊標題必須說清楚資料來源與空狀態。
例如：
- `展開查看完整 brief（來自需求簡報 v1）`
- `導演方向尚未建立`

### 第三階段：首頁改成老闆模式

把 `/projects` 首頁專案列表從表格改成卡片摘要列。
每個專案只顯示：
- 專案名
- 負責人 / 期限
- 狀態 badge
- 現在在做什麼
- 目前卡點
- 是否需要你介入

範例結構：
- 現在在做什麼：`正在等待你做人工決策。`
- 目前卡點：`目前卡在：待確認方向與需求。`
- 是否需要你介入：`需要你現在決定是否放行。`

首頁主畫面不要再放：
- event 名稱
- artifact id
- project id
- raw nextGate enum

必要時保留在第二層，不能當主訊息。

### 第四階段：審批快照改成決策卡

首頁的審批佇列快照不要列出：
- `art-xxx:v1`
- raw gate 名稱
- 系統用流程字串

改成每張卡只顯示：
- 專案名
- 本次關卡（白話）
- 現在要你決定什麼
- 主要風險
- 如果不通過會怎樣

範例：
- 現在要你決定：是否鎖定這支片的方向與需求，讓後續腳本與研究開始工作。
- 主要風險：最重要的目標還沒有定清楚。
- 如果不通過：退回重新確認創意方向。

### 第五階段：審批頁是 decision workspace，不是 admin form

在 `/approvals` 每張卡至少要先講清楚：
1. 你正在決定什麼
2. 批准後會發生什麼
3. 若不批准會退回哪裡

再顯示：
- 必看項目
- 阻塞問題
- 決策按鈕與理由輸入

重要：
- 預設決策不要是 `批准`
- 實務上可改成 `要求修改` 或空白選項，避免誤送

## 內容優先，結構其次，流程最後

這類情況通常最該先修的是「內容」。
也就是：
- 把術語翻成人話
- 把機器狀態翻成決策語言
- 補上使用者需要的判斷依據

其次才是結構：
- 哪裡折疊
- 哪裡做卡片
- 哪裡放 CTA

最後才是流程擴張：
- 新 workflow
- 新 entity
- 新 schema
- 新 orchestration 節點

如果順序反過來，很容易把系統做得更強，但更看不懂。

## 高價值替換範例

把這些字優先換掉：
- `task_state_changed` → `任務狀態已更新`
- `artifact_written` → `已新增產物`
- `vid-xxxx` → 不在首頁主畫面顯示
- `art-xxxx` → 不在首頁主畫面顯示
- `intake` → `需求整理中` 或 `待需求整理`
- `approval_pending` → `等待你決定`
- `direction_lock` → `待確認方向與需求`
- `Gate A — Brief / Direction Lock` → `待確認方向與需求`
- `QA pass before publish pack` → `發布前品質確認`
- `research` → `前期研究`
- `director-direction` → `創意方向確認` 或 `退回重新確認創意方向`

## 實作訣竅：翻譯層要集中，不要散在頁面裡

如果系統已有共用 UI helper（例如 `lib/ui.ts` 這類檔案），優先把翻譯集中在那裡：
- status label map
- gate label map
- artifact type label map
- 必要時補 literal phrase 對照，不只處理 enum

原因：
- 同一個英文流程詞可能同時出現在 `status`、`nextGate`、`approvalPayload.gateLabel`、`rejectionRoute`
- 只改單一頁面很容易漏掉其他入口
- 集中翻譯層之後，首頁、審批頁、專案頁會一起受益

實務上要注意兩種來源都要翻：
1. enum / key 型值
   - `direction_lock`
   - `final_qa`
   - `change_review`
2. 已落地到資料裡的 literal phrase
   - `Gate A — Brief / Direction Lock`
   - `Gate D — Publish Closeout`
   - `QA pass before publish pack`
   - `director-direction`
   - `research`
   - `publish-pack-rework`
   - `publish-closeout-fix`

另外，不要只翻 `approval.gate`。
也要檢查並包住這些欄位：
- `project.nextGate`
- `approval.approvalPayload?.gateLabel`
- `approval.approvalPayload?.rejectionRoute`

如果系統首頁會露出角色名，也要集中翻譯角色層：
- `director` / `Director` → `導演控盤`
- `Research` → `前期研究`
- `Storyboard` → `分鏡設計`
- `QA / Compliance` → `品質與風險確認`
- `Brian` 這類決策者本人，可視情境翻成 `你`

不然你會發現首頁卡點改好了，但審批快照、退回路由、角色列還在露出舊術語。

另外還有一個常見漏網點：
不是只有標題和 badge 要翻。
連「介入句 / 決策句」也要一起去工程化。
例如把：
- `需要你現在決定是否放行。`
- `建議你優先看這個關卡，避免專案空轉。`

改成更口語的：
- `你現在可以決定要不要讓它繼續往下走。`
- `這件事現在最值得你先拍板，不然專案會繼續卡著。`

這種句子對手機決策者的體感影響很大，常常比再加一個資料欄位更有效。

## 驗證與預覽的實戰注意事項

如果你是用 Next build/start 或任何靜態輸出預覽：
- 改完文案後先跑 `typecheck`
- 再跑 `build`
- 若已有 `next start` / preview server 在跑，重啟它再驗證

不要只改完碼就看原本的預覽連結，因為你可能看到的是舊 build。

若外部 tunnel 頁面抓不到內容或瀏覽器快照出現空白：
- 先回頭驗證 `localhost` 是否已正確更新
- 再確認 tunnel 只是轉發問題，不要誤判成 UI 沒改成功

### Commander / visible-first 實戰補充

如果使用者要的是「先看到有效果的 commander 介面」，第一刀可以先做 visible layer，而不是先補 orchestration：
1. 共用翻譯層
   - status / event / risk / role label map
2. `/projects`
   - 先補「今天優先」「等你決定」「已卡住」三個區塊
3. `/approvals`
   - 改成大按鈕快速決策，不要先塞 select admin form
4. `/projects/[id]`
   - 第一屏先放 `決策摘要`，回答：目前狀態 / 待你決定 / 下一步
5. `/settings`
   - 至少變成治理頁語言，不要只是英文工程說明

這種順序很適合 Phase A/B：
- 先把產品體感從工程後台拉到可決策前台
- 再往下補 orchestration / Prisma / validators

### Next.js worktree 驗證坑

在 Next.js worktree 或多實例開發環境，驗證時要注意兩個常見坑：

1. `next build` / `next dev` 可能改動追蹤檔
- 常見是：
  - `next-env.d.ts`
  - `tsconfig.tsbuildinfo`
- 這些通常不是你要提交的產品改動。
- build / typecheck 後要先 `git status` 檢查，必要時把這類衍生檔 `checkout --` 回去，再 commit 真正的 UI 變更。

2. 你看到的頁面可能是舊 dev server，不是新改好的那份
- 如果同機器已有其他 `next dev` 在跑，可能出現：
  - port 被占用
  - `.next/dev/lock` 無法取得
  - 瀏覽器其實連到另一個舊 server
- 所以不要只看 `localhost:3000` 就相信畫面已更新。
- 要先確認：
  - 哪個 port 正在服務這個 worktree
  - 是否有舊 dev server 沒關
  - browser snapshot 指到的是不是正確 port

簡單說：
在做 boss-mode UI 驗證時，最大的假象不是文案沒改好，而是你其實看錯了 server。

## 第二層清理：不要只翻 enum，還要翻說明句與 checklist

實戰上，做完第一輪首頁去術語之後，常常還會殘留第二層工程味：
- `research / script / visual-development`
- `claim / accuracy`
- `brand / tone`
- `asset completeness`
- `platform formatting`
- `human gate`
- `retro closeout`
- `scope lock`
- 以及夾在完整句子裡的 `brief`

這些字不一定出現在 badge 或標題，反而常躲在：
- `approvalPayload.decisionScope`
- `approvalPayload.approvalSummary`
- `approvalPayload.mustReview[]`
- `approvalPayload.blockingQuestions[]`
- `approval.riskNotes[]`
- 首頁審批快照中的說明句
- 審批頁卡片內文
- 專案頁下一個決策摘要

所以第二輪要做的是：
1. 建一個共用的 `humanizeWorkflowText()` 文字替換層
2. 再建一個 `humanizeChecklistItems()` 專門處理 checklist 陣列
3. 把頁面上所有 decisionScope / approvalSummary / riskNotes / mustReview / blockingQuestions 都包進去

高價值替換範例：
- `research / script / visual-development` → `前期研究、腳本撰寫與畫面發想`
- `claim / accuracy` → `對外說法與內容是否正確`
- `brand / tone` → `品牌語氣是否一致`
- `asset completeness` → `素材是否齊全`
- `platform formatting` → `平台格式是否正確`
- `human gate` → `人工確認`
- `retro closeout` → `結案回顧`
- `scope lock` → `方向鎖定`
- `brief`（在完整說明句裡）→ `需求摘要`

重點不是逐字翻譯，而是讓卡片內文真的能支援手機決策。

## 第三層清理：直接把低價值內部識別從主畫面拿掉

有些內容不是翻譯問題，而是根本不該先出現在主畫面：
- `art-xxxx:v1`
- artifactRefs
- raw payload
- event id / approval id

在審批頁與首頁快照，如果這些資訊對當下決策沒有直接幫助，就不要放在第一屏。
寧可只留下：
- 決策主題
- 必看項目
- 主要風險
- 打回後果

例如：
- 審批頁可直接移除 artifact ref code block
- 首頁快照不要出現 artifact id 串列

## 第四層清理：專案細節頁也要做同樣的去工程化

常見錯誤是首頁與審批頁變好看了，但 `/projects/[id]` 還在露出：
- artifact id
- approval id
- task id
- handoff id
- `project_created`
- `artifact_written`
- raw JSON payload

這會讓使用者一點進細節頁又被打回工程後台體感。

實戰上要一起做這幾件事：
1. 產物列表
   - `art-xxxx · brief:v1 · final`
   - 改成 `簡報需求第 1 版 · 定稿`
2. 任務 / 交接
   - 不顯示 task / handoff id
   - 改成 `前期研究 · 目前由前期研究處理 · 進行中`
   - 交接改成 `腳本規劃 → 分鏡設計 · 已送出`
3. 審批摘要
   - 去掉 approval id 與 artifactRefs
   - 只保留關卡、人話摘要、風險、退回去向
4. 活動紀錄
   - 把 event type 轉成 display label：
     - `project_created` → `專案已建立`
     - `artifact_written` → `已產出新內容`
     - `approval_requested` → `已送出審批`
     - `task_state_changed` → `任務狀態已更新`
   - 不要直接 render `JSON.stringify(event.payload)`
   - 依 event type 生成一句人話摘要

推薦做法：
- 在共用 UI helper 裡新增 `formatEventTypeLabel()`
- 在頁面內建立小型 summarize helpers，例如：
  - `summarizeArtifact()`
  - `summarizeTask()`
  - `summarizeHandoff()`
  - `summarizeEventPayload()`

這層做好後，使用者即使進入專案細節頁，也不會再先看到內部流水號和事件原碼。

## 第五層：管理欄位與 placeholder 也要收尾

當首頁、審批頁、專案細節頁的主閱讀區已經乾淨後，
最後還會殘留一批讓人出戲的管理欄位文字，例如：
- `artifactId`
- `producedByTaskId`
- `來源任務 ID`
- `script`
- `ownerRole`
- `dueAt`
- `nextAction`
- `這次要 Brian 看什麼`
- actor 顯示成 `system` / `api`

這些通常出現在：
- 專案細節頁表單 placeholder
- 後台建立任務 / 交接 / 審批的欄位
- 活動紀錄 actor 顯示

實戰上要一起做這幾件事：
1. placeholder 改寫成人話
   - `產物類型，例如 script` → `產物類型，例如腳本或分鏡`
   - `producedByTaskId（可留空）` → `由哪個任務產出（可留空）`
   - `來源任務 ID` → `從哪個任務交出`
   - `artifactId` → `對應哪份產物（輸入代號）`
   - `這次要 Brian 看什麼` → `這次要你看什麼、做什麼決定`
2. 欄位標題改成人話
   - `目前負責人` → `目前由誰負責`
   - `下一個關卡` → `下一步重點`
4. actor 顯示統一翻譯
   - `system` / `api` → `系統`
   - `director` → `導演控盤`
5. 補齊「種子任務 / 流程角色」映射，這是很容易漏掉的一層
   - `intake-normalizer` → `需求整理`
   - `approval-prep` → `審批準備`
   - `handoff-prep` → `交接準備`
   - `orchestrator` → `流程總控`
   - `qa-compliance` → `品質與風險確認`
   - `production` → `製作協調`
   - `workflow-engine` → `流程系統`

   這些字常出現在：
   - 新 intake 專案剛建立時的任務列表
   - seeded task / event payload
   - 專案細節頁的任務區與活動紀錄

   如果只翻首頁關卡與審批文案，使用者一進細節頁仍會看到：
   - `intake-normalizer · orchestrator`
   - `approval-prep · qa-compliance`
   - `handoff-prep · production`

   所以一定要把 task type 與 ownerRole 也納入共用翻譯層。
6. 若 `nextGate` 是 `Next action not assigned`，主畫面直接不顯示，不要把內部 fallback 字串端給使用者

這一層做完之後，整個產品的體感會從「主要頁面還可以，但細節仍像工程後台」
進一步變成「連管理介面都像給決策者看的系統」。

## 第六層：做首頁 Phase 表，先給老闆盤面感

當首頁已經完成第一輪去工程化之後，下一個高價值步驟不是再塞更多卡片，
而是補一個「Phase 表 / 階段總覽」，讓決策者先看整體盤面。

適合放在首頁 KPI 區塊下方，並維持手機可掃讀：
- 每列只放一個 phase
- 顯示案量
- 顯示一句這個階段代表什麼
- 顯示 1–3 個代表案

推薦 phase 分類：
- `需求整理`
- `待你拍板`
- `製作進行中`
- `卡住中`
- `已完成`

每列建議結構：
- 標題：`需求整理`
- badge：`2 案`
- 說明：`需求還在整理、補問與收斂方向。`
- 代表案：`AI 導演系統 v1 ／ Intake Auto Draft Test`

Phase 表的用途不是取代專案列表，
而是先回答老闆最重要的問題：
- 現在大多數案子卡在哪個階段？
- 目前是決策塞車，還是製作卡關？
- 有沒有越來越多案子留在「待你拍板」？

實作上可以直接由首頁既有分組推導，不需要新 schema：
- `intake` / `triage` → `需求整理`
- `approval_pending` / `review` → `待你拍板`
- `in_progress` / `publish_pack_ready` → `製作進行中`
- `blocked` / `high risk` → `卡住中`
- `completed` → `已完成`

命名上也要去工程化：
- `CEO 優先看` → `老闆優先看`
- `已完成 closeout` → `已完成`
- `高風險 / 已阻塞` → `高風險或已卡住`

首頁專案卡若還顯示 `下一個關卡：...`，建議同步改成：
- `下一步重點：...`

## 不只改顯示，也要改未來生成內容

如果系統的 approval / workflow 文案是後端動態生成的，
不要只在頁面顯示層做翻譯。
也要回頭改生成來源，例如：
- `routeIntakeBrief()` 產出的 `decisionScope`
- `approvalSummary`
- `mustReview`
- `riskNotes`
- publish closeout auto-created approval payload

否則舊資料看起來改善了，新專案一建立又會長回英文工程語。

## Phase C slicing rule：先做聊天入口，不要先做抽象 taxonomy

如果 Web 首頁 / 專案頁 / 審批頁已經初步進入 boss-mode，但日常指揮其實主要走 Telegram 或 Slack，
那麼下一個最高槓桿 slice 往往不是：
- deeper workflow enforcement
- 新 command schema
- 複雜 settings CMS
- 純文件型 review personas / taxonomy

而是：
1. 先把聊天入口回覆升級成 boss-mode operator language
2. 再補一個可閱讀的治理快照頁，把語言政策、流程護欄、review personas、command taxonomy 收成 visible artifact

實戰上可優先覆蓋：
- `/status`
- `/approvals`
- `/approve`
- `/changes`
- `/reject`
- `/intake`
- unauthorized / usage / unknown / runtime failure replies

聊天入口的共同格式建議：
- 結論
- 現況
- 下一步

若是決策卡，再補：
- 你現在要決定什麼
- 風險
- 若不同意會退回哪裡

原因：
- 這比 taxonomy 文件更快產生使用者可感知效果
- 這比先做 deeper enforcement 更貼近日常指揮入口
- 可以直接把 Web 已成熟的人話決策語言借到聊天平台

## Settings 治理頁的最小落地法

當 `/settings` 仍只是 placeholder 時，不要一開始就做完整 CMS。
先做一個 governance snapshot：
- 顯示最後更新
- 顯示維護責任
- 顯示核心治理區塊數量
- 用卡片列出：
  - 流程護欄
  - 介面語言政策
  - Telegram / Slack 回覆格式
  - review personas
  - boss-mode command taxonomy

這樣能先讓治理規則變成可讀、可檢查、可對齊的產品基線，之後再決定要不要進一步做可編輯設定。

## 驗證標準

改完後重新用手機視角看首頁，問：
- 我現在能不能一眼知道哪個專案卡住？
- 我能不能一眼知道哪個專案要我決定？
- 我看首頁時，還會不會先被 event 名稱和 id 打臉？
- 我能不能不看長文，也知道下一步是什麼？

如果這輪包含聊天入口，也要補問：
- `/status` 是否像盤面摘要，而不是數量統計？
- `/approvals` 是否像決策卡，而不是 queue dump？
- error / usage / unknown command 是否仍在吐英文或工程語？
- `/settings` 是否已從 placeholder 變成可閱讀治理快照？

建議最低工程驗證：
- `npm run typecheck`
- `npm run build`

如果答案仍然是否定，就不要擴新功能，繼續收斂文案與資訊層級。

## 一句話版本

當使用者說「我看不懂這堆東西有沒有價值」時，
不要再加功能。
先把首頁做成：
- 現在在做什麼
- 卡在哪
- 要不要你介入

這才是從後台骨架跨到可感知產品價值的關鍵一步。
