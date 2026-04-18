# Review and Learning Playbook

日期：2026-04-14

## 1. 這份文件的目的

這份文件定義 Brian AI workflow 在案件完成後，應如何做 review、學習與規則沉澱。

這份文件要解決的不是一般 retrospective，而是你目前最痛的問題：
- 同樣的客戶線、品牌線、合作模式被反覆重新判斷
- 很多知識留在腦中或聊天裡，沒有穩定回寫
- AI 沒有真正學會，因為案件做完後沒有正式回寫流程

所以這份 playbook 的目標是：
1. 每個案件結束後，都留下可複用知識
2. 把「這案是誰的、怎麼做、怎麼賺」從一次性經驗變成系統規則
3. 讓未來 intake / routing / PM / closing 不再反覆重問同樣問題

## 2. Review / Learning 的定位

在 Brian AI workflow 中，review 不是附屬動作，而是案件真正結束前的最後一關。

換句話說：
- 沒有 review，不算完整 close
- 沒有 learning，不算系統真的完成這案

這點與 bw-sop 的 donor 精神一致：
- 已收款
- 已分帳
- 已結案
還不夠
還要：
- 保留案件摘要
- 保留版本
- 保留決策理由
- 保留明年可回看的資訊

## 3. 這份 playbook 想固定的核心原則

### 3.1 案件做完要留下「事實」與「判斷」
每次結案至少要留下兩種東西：

A. 事實
- 客戶是誰
- PM 是誰
- Brian 有沒有出工
- Brian 角色是什麼
- 收入怎麼分
- 是否有 Chu / Jerry / 外部執行者
- 哪個版本送出 / 交付 / 收款

B. 判斷
- 這案屬於哪條客戶線
- 這案屬於哪條品牌線
- 這案是核心執行 / PM / 共同客戶 / 協作支援 / 資產收入 的哪一類
- 哪條規則值得回寫
- 哪個問題以後不要再重問

### 3.2 Rulebook 比筆記更重要
review 不是把心得寫在 notes 就好。
真正有價值的是：
- 回寫到 customer sidecar
- 回寫到 brand sidecar
- 回寫到 analysis rulebook
- 更新 do-not-ask-again

### 3.3 不確定可以保留 pending，但不能直接消失
若某案仍有部分資訊不確定：
- 可以標記 pending
- 但必須寫清楚哪一欄 pending
- 不可直接結案後不留痕跡

### 3.4 已確認過的知識要進入「不再重問」層
若某案件線、客戶線、品牌線已被 Brian 明確確認多次：
- 不應只是備註
- 必須進入 `do_not_ask_again`

## 4. Review 的三層輸出

每案結束後，review 應至少輸出三層內容：

### 4.1 Case Recap
針對該案本身的摘要：
- 這案是什麼
- 誰做了什麼
- 最後結果如何

### 4.2 Rule Update Suggestion
這案對規則層有什麼貢獻：
- 需不需要補 sidecar
- 需不需要更新 routing rules
- 需不需要加入 do-not-ask-again

### 4.3 Reusable Asset Suggestion
這案有沒有東西值得留成模板或資產：
- 回覆模板
- 報價模板
- recurring 規則
- 婚禮流程模版
- 客戶線判斷規則

## 5. Review 的標準流程

### Step 0：確認案件真的到 close 條件
只有在以下基本條件成立後，才進 review：
- 已完成交付
- 已收款或已完成內部財務策略
- 已完成分帳或記錄不分帳原因

### Step 1：寫 Case Recap
Case recap 最少要回答：
1. 這案是哪條 lane
2. 客戶是誰的
3. PM 是誰
4. Brian 是否親自下場
5. Brian 的角色是什麼
6. 收入性質是什麼
7. 這案有沒有特殊地方

### Step 2：更新 sidecar
依案件內容決定是否回寫：
- customer sidecar
- brand sidecar
- vendor sidecar

### Step 3：決定是否加入 do-not-ask-again
符合以下條件之一，就要考慮加入：
- 同一案件線已被 Brian 重複確認
- 某客戶歸屬已穩定
- 某品牌線規則已穩定
- 之後再問只會浪費 Brian 時間

### Step 4：決定是否更新 routing 規則
若該案暴露出新的模式，例如：
- 客戶是 Brian 的，但執行外發
- 共同客戶但 Chu 主控
- BNI 線帶來特定案型
- 某品牌實際上是共同經營
則要更新 routing rules 或 analysis rulebook。

### Step 5：決定是否產生模板資產
若該案可複製，例如：
- 同型婚禮案
- recurring 商業案
- 固定品牌流程
- 固定回覆話術
則應標記為 template_candidate。

## 6. Review 完成標準

一個 review 只有在以下條件都成立時，才算完成：

1. case recap 已寫
2. 收入性質已明確或標註 pending
3. sidecar 是否更新已決定
4. do-not-ask-again 是否加入已決定
5. 是否有可複用資產已判斷

也就是說：
`closed` 不只是資料結束，而是學習完成。

## 7. 必須回寫的欄位

### 7.1 Case 主表
至少要補：
- `client_owner`
- `pm_owner`
- `brian_exec`
- `brian_role`
- `income_nature`
- `closed_at`
- `case_recap_written`

### 7.2 Customer sidecar
以下情況更新：
- 新客戶第一次被確認歸屬
- 舊客戶的歸屬更穩定
- 發現這其實是 BNI 夥伴客戶線 / 上游合作方 / 共同客戶

### 7.3 Brand sidecar
以下情況更新：
- 發現某案件其實屬某子品牌
- 發現某品牌是共同經營，不該當單一客戶
- 發現某品牌主控不是 Brian，而偏 Chu / Jerry

### 7.4 Analysis Rulebook
以下情況更新：
- 某條規則被重複驗證
- 某條規則被推翻
- 某案件已不該再重問

## 8. Do-Not-Ask-Again 規則

### 8.1 何時進入
若某案或某客戶線已符合以下任一條件：
- Brian 已明確確認兩次以上
- 同一答案已在多個案件中穩定出現
- 之後再問不會帶來新資訊

則應加入 `do_not_ask_again`。

### 8.2 何時不能進入
若目前仍存在：
- Brian 自己也不確定
- 客戶 / 品牌 / PM 線仍常變
- 只是一次性猜測
則不可過早加入

### 8.3 進入後的系統行為
- routing 前先查此清單
- 命中就直接套用
- 若真的還有需要問，只能問尚未確認的欄位

## 9. 典型 review 範例

### 範例 A：你的客戶，你親自做
輸出重點：
- client_owner = 我
- pm_owner = 我
- brian_exec = 是
- brian_role = 主輸出
- income_nature = 兼具 PM 與執行 或 核心執行

### 範例 B：你的客戶，但你外發
輸出重點：
- client_owner = 我
- pm_owner = 我
- brian_exec = 否
- brian_role = 僅管理
- income_nature = PM / 接案
- 若外發對象重複出現，可更新 sidecar

### 範例 C：麻花婚禮線
輸出重點：
- brand = 麻花影像
- client_owner = 共同
- pm_owner = 共同
- operating controller 偏 Chu
- 可複用婚禮模板是否有新增

### 範例 D：共同客戶 / 共同 PM
輸出重點：
- 客戶線是否屬共同
- 共同 PM 的判斷是否穩定
- 是否需要更新共同客戶規則

### 範例 E：資產收入（租棚）
輸出重點：
- 必須獨立標成資產收入
- 不可混入主動執行收入
- 若某租棚客模式固定，可考慮做標準回覆模板

## 10. Review 與 PM / Intake 的關係

### Intake 是入口
- 決定案子怎麼進來

### PM 是推進者
- 決定案子怎麼往前走

### Review / Learning 是系統學習器
- 決定案子做完後，系統學到什麼

所以這份文件是整套 workflow 不重複問、不重複猜的關鍵。

## 11. AI 在 Review 階段的角色

AI 可以做：
- 先產出 case recap 草稿
- 提示可能要更新的 sidecar
- 提示可加入 do-not-ask-again 的案例
- 提示哪些案子可轉成模板

AI 不可做：
- 自己宣布規則已完全確定
- 自己覆寫既有明確規則
- 自己把不確定資料強行標成高信心

## 12. 這份文件與其他文件的關係

- 決策邊界：`brian-ai-workflow-decision-rails.md`
- 主資料欄位：`brian-ai-workflow-data-model.md`
- 分流規則：`brian-ai-workflow-routing-rules.md`
- 狀態與關卡：
  - `brian-ai-workflow-state-machine.md`
  - `brian-ai-workflow-phase-gates.md`
- intake 與 PM：
  - `intake-playbook.md`
  - `pm-playbook.md`

## 13. 待補問題

- 什麼條件下應自動生成 recurring 模板候選
- wedding / studio rental 是否要有獨立 recap 模板
- 是否需要專門一份 `do-not-ask-again` 管理文件
