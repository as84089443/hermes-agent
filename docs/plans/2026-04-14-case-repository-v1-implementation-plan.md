# Case Repository v1 Implementation Plan

> For Hermes: Planner Mode only. This plan intentionally stops before editing implementation files.

日期：2026-04-14

## 目標

在 hermes-agent repo 中落地 Brian AI workflow 的第一個最小可用內核：`Case Repository v1`。

它要做到的事很單純：
- 能建立 case
- 能讀取單筆 case
- 能列出 cases
- 能更新 case 欄位
- 能做合法狀態轉移
- 能驗證 required fields / enums / transition

它暫時不做：
- sidecar resolver
- routing engine
- review recap writer
- 真正前端頁面
- quote / approval / change review 子系統

## 已確認的架構方向

### 1. 存放位置
新增模組：
- `agent_workflow/`
  - `__init__.py`
  - `case_models.py`
  - `case_validation.py`
  - `case_state_machine.py`
  - `storage.py`
  - `case_repository.py`

### 2. 參考模式
已檢查 repo 內現成模式：
- `hermes_project_state.py`
  - SQLite
  - profile-aware `get_hermes_home()`
  - WAL
  - `sqlite3.Row`
  - schema bootstrap pattern
- `hermes_state.py`
  - 狀態儲存與 SQLite 使用習慣

### 3. 為什麼不用直接塞進現有 SessionDB
因為 Brian workflow case 不是聊天 session。
如果硬塞進 session store：
- 概念會混線
- API namespace 會混亂
- 後續 sidecar / routing / review 會變難維護

所以先獨立一個最小 control-plane module 是對的。

## v1 最小規格

### 必做能力
1. `create_case()`
2. `get_case(case_id)`
3. `list_cases(filters)`
4. `update_case_fields(case_id, patch)`
5. `transition_case(case_id, to_status, reason=None)`

### 最小欄位
必填：
- `case_id`
- `title`
- `source`
- `customer_name`
- `primary_lane`
- `status`
- `current_owner`
- `next_action`
- `next_owner`
- `created_at`
- `updated_at`

可選但先保留：
- `client_owner`
- `pm_owner`
- `brian_exec`
- `brian_role`
- `brand_or_system`
- `raw_brief`
- `normalized_brief`
- `budget_status`
- `due_date`
- `executor`
- `approver`
- `quote_version`
- `artifact_version`
- `notes`
- `risk_flags`
- `parent_case_id`
- `project_group_id`
- `sidecar_type`
- `scope_locked_at`
- `approved_at`
- `accepted_at`
- `closed_at`
- `lost_reason`

### 狀態轉移
v1 只允許最小 transition 集合：
- `intake -> clarifying`
- `intake -> ready_for_quote`
- `intake -> lost`
- `clarifying -> ready_for_quote`
- `clarifying -> lost`
- `ready_for_quote -> quote_sent`
- `ready_for_quote -> soft_hold`
- `ready_for_quote -> confirmed`
- `ready_for_quote -> lost`
- `quote_sent -> soft_hold`
- `quote_sent -> confirmed`
- `quote_sent -> lost`
- `quote_sent -> quote_sent`
- `soft_hold -> confirmed`
- `soft_hold -> quote_sent`
- `soft_hold -> lost`
- `confirmed -> in_execution`
- `confirmed -> lost`
- `in_execution -> delivered`
- `delivered -> billing`
- `delivered -> collected`
- `delivered -> closed`
- `billing -> collected`
- `billing -> closed`
- `collected -> closed`

## 建議實作設計

### A. `case_models.py`
責任：
- 定義 `CaseRecord` typed structure
- 定義 enum constants
- 定義預設值 helper

建議內容：
- `TypedDict` or `dataclass` for external/public record shape
- enum tuple constants for validation layer共用

### B. `case_validation.py`
責任：
- 驗證 required fields
- 驗證 enum 合法性
- 驗證 patch 不可亂改 immutable fields

需要注意：
- `create_case` 時 required fields 嚴格檢查
- `update_case_fields` 時只檢查 patch touched fields
- `status` 不應由 patch 直接改；只能透過 transition API

### C. `case_state_machine.py`
責任：
- 提供 allowed transitions
- 提供 `can_transition(from_status, to_status)`
- 提供 transition error messages

### D. `storage.py`
責任：
- 建 SQLite DB path
- bootstrap schema
- 提供 connection helper

建議：
- 路徑使用 `get_hermes_home() / "workflow_cases.db"`
- 沿用 WAL / foreign_keys / Row factory

### E. `case_repository.py`
責任：
- 封裝所有 CRUD 與 transition
- 對外暴露唯一 repository 介面

建議 API：
- `create_case(...) -> dict`
- `get_case(case_id) -> dict | None`
- `list_cases(status=None, lane=None, owner=None, limit=..., offset=...) -> list[dict]`
- `update_case_fields(case_id, patch) -> dict`
- `transition_case(case_id, to_status, reason=None) -> dict`

## 資料庫 schema 建議

最小 table：`cases`
欄位：
- `case_id TEXT PRIMARY KEY`
- `title TEXT NOT NULL`
- `source TEXT NOT NULL`
- `customer_name TEXT NOT NULL`
- `primary_lane TEXT NOT NULL`
- `status TEXT NOT NULL`
- `current_owner TEXT NOT NULL`
- `next_action TEXT NOT NULL`
- `next_owner TEXT NOT NULL`
- `client_owner TEXT`
- `pm_owner TEXT`
- `brian_exec TEXT`
- `brian_role TEXT`
- `brand_or_system TEXT`
- `raw_brief TEXT`
- `normalized_brief TEXT`
- `budget_status TEXT`
- `due_date TEXT`
- `executor TEXT`
- `approver TEXT`
- `quote_version TEXT`
- `artifact_version TEXT`
- `notes TEXT`
- `risk_flags_json TEXT`
- `parent_case_id TEXT`
- `project_group_id TEXT`
- `sidecar_type TEXT`
- `scope_locked_at REAL`
- `approved_at REAL`
- `accepted_at REAL`
- `closed_at REAL`
- `lost_reason TEXT`
- `created_at REAL NOT NULL`
- `updated_at REAL NOT NULL`

可加 index：
- `status`
- `primary_lane`
- `current_owner`
- `updated_at DESC`

## 測試計畫

最小測試檔建議：
- `tests/workflow/test_case_repository.py`

至少覆蓋：
1. create case success
2. create case missing required field -> fail
3. invalid enum -> fail
4. get existing case
5. list cases by status
6. update allowed field
7. update tries to mutate status directly -> fail
8. legal transition success
9. illegal transition fail
10. timestamps update correctly

## 風險與注意事項

### 1. `operating_controller` 不要現在偷塞進 schema
它已被判定為 v1.1 候選。
先不要進 case repository core schema。

### 2. `upstream_source` 也不要偷塞進 schema
同上，先留給 v1.1。

### 3. 不要一次做 API server 與 web
這次只做 repository 核心。
避免 blast radius 擴大。

### 4. 不要把 sidecar 寫入一起做
Case repository 先只處理 case。
sidecar resolver 之後再接。

## 任務表

### Task 1 — 建模與驗證
- 建 `agent_workflow/case_models.py`
- 建 `agent_workflow/case_validation.py`
- 建 `agent_workflow/case_state_machine.py`

### Task 2 — SQLite storage
- 建 `agent_workflow/storage.py`
- bootstrap `workflow_cases.db`
- 建最小 `cases` table + indexes

### Task 3 — Repository
- 建 `agent_workflow/case_repository.py`
- 完成 create/get/list/update/transition

### Task 4 — Tests
- 建 `tests/workflow/test_case_repository.py`
- 跑最小 pytest 驗證

## 驗證標準

完成後至少要能證明：
- 能建立一筆合法 case
- 能拒絕缺欄位 case
- 能拒絕非法 enum
- 能拒絕非法狀態轉移
- 能列出與查回 case
- 能維持 profile-aware DB path

## 實作後下一步

Case Repository v1 穩後，再做：
1. Sidecar Resolver
2. Routing Engine v1
3. Intake Normalizer

這樣順序最穩。
