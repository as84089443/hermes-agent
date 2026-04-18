# Brian AI Workflow v1 / v1.1 Boundary

日期：2026-04-14

## 1. 這份文件的目的

這份文件把 Brian AI workflow 的設計分成：
- v1：現在就該做，否則 workflow 無法穩定落地
- v1.1：明顯有價值，但現在先不要硬塞進 v1

目標是避免 scope creep。

## 2. v1 的判準

只有符合以下任一條件，才應進 v1：
1. 沒有它，routing 會不穩
2. 沒有它，case 無法安全跨關卡
3. 沒有它，AI 一定會重複問同樣問題
4. 沒有它，無法形成最小可用 dashboard / case detail

## 3. v1 內容

### 3.1 核心規格
- decision rails
- data model
- routing rules
- state machine
- phase gates
- file structure
- customer/brand sidecar schema
- review recap schema

### 3.2 核心 playbooks
- intake playbook
- PM playbook
- wedding playbook
- review-and-learning playbook
- studio-rental playbook

### 3.3 核心資料底盤
- customer sidecar
- brand sidecar
- analysis rulebook
- do-not-ask-again
- historical income normalized 主表

### 3.4 最小可實作模組
- case schema
- intake normalizer v1
- routing engine v1
- recap writer v1
- dashboard / cases / case detail 的最小骨架

## 4. v1.1 內容

### 4.1 `operating_controller` 正式欄位
原因：
- 很重要
- 但目前主要集中在婚禮 / Chu 主控場景
- 先保留為 schema candidate，待你再確認是否正式納入主模型

### 4.2 `upstream_source` 一級欄位
原因：
- 上游合作方很重要
- 但現在先用 notes / sidecar 還能撐住
- 等 routing engine 真落地時，再正式升欄位

### 4.3 lane-specific recap schema
原因：
- wedding / studio rental / commercial 的 recap 可能真的不同
- 但 v1 先用通用 recap schema 已足夠

### 4.4 recurring tenant sidecar
原因：
- 場租 recurring renter 很值得做
- 但不是 v1 的 routing 核心阻塞點

### 4.5 完整 UI
- 完整 dashboard
- cases 列表最佳化
- case detail 全功能
- lane-specific views
這些都是重要，但應建立在 schema / routing 穩定後。

### 4.6 machine-readable contracts 真正生成
原因：
- 方向正確
- 但現在先把 human-readable spec 寫穩更重要

## 5. 明確不進 v1 的東西

- 重型 CRM
- 複雜排程引擎
- 自動發報價
- 自動催款
- 完整財務 / 稅務模型
- 過細 task tree
- 多角色權限系統

## 6. 升級條件

以下情況成立時，可把 v1.1 項目升級進 v1 主軸：

### 6.1 `operating_controller`
若 Chu 主控、Brian 共同 PM、共同客戶這種情況反覆大量出現，且沒有這欄會導致 routing 誤判，就正式升級。

### 6.2 `upstream_source`
若上游合作方成為大量案件來源，且只靠 notes / sidecar 已不足，則升級。

### 6.3 lane-specific recap
若 generic recap 開始無法支撐婚禮 / 場租 / 商業案的差異，就升級。

## 7. 現在最重要的守則

- 不要把 v1.1 的需求偷渡回 v1 文件主體
- 先用 notes / sidecar / appendix 承接曖昧但重要的概念
- 等這些概念在真實案件中反覆成立，再正式升級入模
