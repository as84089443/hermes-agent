# AI Department OS v1 Minimal Repo Scaffold

Date: 2026-04-13

## Goal

收斂出一個今天就能開始開發的 `ai-department-os` v1 最小骨架。

依據來源：
- `hermes-ai-department-rebuild-blueprint.md`
- `hermes-ai-video-pilot-kit.md`
- `bw-sop-decision-rails.md`
- `subagent-parallel-execution-fabric.md`

核心原則：
- 單一產品殼，不拆多站
- 先固定 contract / state machine / artifact folder
- v1 只閉環 AI 影片部門
- UI 只保留 command center / project workspace / approvals / settings
- worker 先接最少閉環：research / script / storyboard / qa
- render / auto publish / analytics dashboard 全部延後

## 建議 repo 目錄樹

```text
ai-department-os/
  app/
    layout.tsx
    page.tsx                       # 可直接 redirect -> /projects
    globals.css
    (app)/
      projects/
        page.tsx                   # Command Center
        [id]/
          page.tsx                 # One-page workspace
      approvals/
        page.tsx                   # Human approval queue
      settings/
        page.tsx                   # Brand/workflow/risk rails
    api/
      intake/
        route.ts                   # 自由描述 brief -> normalized intake
      projects/
        route.ts                   # list/create project
        [id]/
          route.ts                 # project detail / patch status
          tasks/
            route.ts               # create/list tasks
          handoffs/
            route.ts               # create/list handoffs
          approvals/
            route.ts               # request/list approvals
          artifacts/
            route.ts               # list/write artifact metadata
          events/
            route.ts               # event timeline
      approvals/
        [id]/decision/
          route.ts                 # approve / changes_requested / reject
      orchestration/
        projects/[id]/plan/route.ts # freeze execution graph
        tasks/[id]/run/route.ts     # worker dispatch hook
  components/
    command-center/
      project-list.tsx
      project-filters.tsx
      waiting-on-human-card.tsx
    project-workspace/
      brief-panel.tsx
      artifacts-panel.tsx
      tasks-handoffs-panel.tsx
      approvals-panel.tsx
      activity-log-panel.tsx
    approvals/
      approval-list.tsx
      approval-decision-form.tsx
    shared/
      status-badge.tsx
      owner-pill.tsx
      risk-badge.tsx
  lib/
    db/
      client.ts
    contracts/
      project.ts
      task.ts
      handoff.ts
      approval.ts
      artifact.ts
      event.ts
      execution-graph.ts
    domain/
      state-machine.ts
      ui-labels.ts
      approval-gates.ts
      artifact-types.ts
    orchestrator/
      build-graph.ts
      route-project.ts
      merge-branches.ts
    workers/
      research.ts
      script.ts
      storyboard.ts
      qa.ts
    repositories/
      projects.ts
      tasks.ts
      handoffs.ts
      approvals.ts
      artifacts.ts
      events.ts
    validators/
      intake.ts
      handoff.ts
      approval.ts
      artifact.ts
  prisma/
    schema.prisma
    seed.ts
  docs/
    specs/
      ai-department-os-v1-pages-and-routes.md
      ai-department-os-v1-state-machine.md
    contracts/
      ai-department-os-v1/
        README.md
        project.md
        task.md
        handoff.md
        approval.md
        artifact.md
        event.md
        execution-graph.md
    templates/
      ai-department-os-v1/
        brief.md
        handoff.yaml
        qa-gate.md
        publish-pack.md
        retro.md
  data/
    examples/
      sample-project.json
      sample-events.json
  storage/
    projects/
      .gitkeep                     # artifact root; each project maps to folder contract
  tests/
    contracts/
      handoff.spec.ts
      approval.spec.ts
      state-machine.spec.ts
    routes/
      projects.spec.ts
      approvals.spec.ts
```

## 必要 pages / routes

### App routes

1. `/projects`
- v1 command center
- 顯示 active / blocked / waiting-on-human
- 可直接進 project
- 驗收標準：operator 能知道今天先做哪 3 個專案

2. `/projects/[id]`
- v1 核心 workspace，必須單頁承載：
  - brief
  - artifacts
  - tasks / handoffs
  - approvals
  - activity log
- 驗收標準：能完成一次 handoff、approve、revise

3. `/approvals`
- 人工審核佇列
- 顯示 gate、artifact version、risk notes、decision actions
- 驗收標準：human 可在不翻完整歷史下做批准/退回

4. `/settings`
- 品牌規則、workflow rules、risk thresholds
- v1 可以很薄，但這個入口要先存在

### API routes

必要：
- `POST /api/intake`
- `GET|POST /api/projects`
- `GET|PATCH /api/projects/[id]`
- `GET|POST /api/projects/[id]/tasks`
- `GET|POST /api/projects/[id]/handoffs`
- `GET|POST /api/projects/[id]/approvals`
- `GET|POST /api/projects/[id]/artifacts`
- `GET /api/projects/[id]/events`
- `POST /api/approvals/[id]/decision`
- `POST /api/orchestration/projects/[id]/plan`
- `POST /api/orchestration/tasks/[id]/run`

可以先不做：
- `/agents`
- `/assets`
- `/analytics`
- `/publish`
- `/render`
- `/webhooks/*`

## 必要 docs / specs / contracts / template 檔案

### specs

1. `docs/specs/ai-department-os-v1-pages-and-routes.md`
- 固定 v1 UI surface
- 定義每頁 operator job
- 定義哪些 section 先內嵌，不獨立成新產品面

2. `docs/specs/ai-department-os-v1-state-machine.md`
- project / task / handoff / approval / artifact state
- scope lock 與 change review rail
- UI label mapping

### contracts

必要 contract：
- `project.md`
- `task.md`
- `handoff.md`
- `approval.md`
- `artifact.md`
- `event.md`
- `execution-graph.md`

今天先用 markdown contract bootstrap 即可，等 schema 穩定後，應對齊既有 `docs/specs/ai-department-os-v1-minimal-data-model.md`，再落成 machine-readable `docs/contracts/ai-department-os/v1/*.json`、zod、prisma、openapi。

### templates

必要模板：
- `brief.md`
- `handoff.yaml`
- `qa-gate.md`
- `publish-pack.md`
- `retro.md`

這五個是第一輪 pilot 真正會被打開、填寫、審核、存檔的文件。

## 哪些要先做真實內容，哪些 placeholder 即可

### 今天就要做真實內容

1. `project / task / handoff / approval / artifact / event` contract
- 因為它們會決定 DB、route payload、worker I/O

2. state machine
- 沒有它就無法做 queue、approval gate、scope lock

3. pages-and-routes spec
- 沒有它就會又長出多殼 UI

4. 模板：brief / handoff / QA / publish-pack / retro
- 因為第一個 pilot 的 artifact 直接依賴這些模板

### placeholder 即可

1. `workers/*.ts`
- 先 stub function / TODO 即可
- 重點是保留固定輸入輸出位置

2. `orchestrator/*.ts`
- 先只回傳 default v1 graph
- 不必第一天就做完整 fan-out runtime

3. `/settings`
- 先靜態頁或 local config 即可

4. `strategy`, `asset-planner`, `edit-packager`, `analytics-learning`
- 先在 contract / route / graph 中留位，不必先做完整 worker

5. `storage/projects`
- 先用檔案系統 artifact root 即可
- DB 只存 metadata 與 path

## 最小 build order

1. 建 repo 與 app shell
2. 固定 contract + state machine + artifact folder contract
3. 建 `/projects` 與 `/projects/[id]` 靜態骨架
4. 建 approval queue
5. 建 intake route + project create flow
6. 接 research / script / storyboard / qa worker stub
7. 接 event log + artifact write path
8. 跑第一個 video pilot

## 最小 DB / storage stance

v1 建議：
- DB: Postgres + Prisma
- artifact content: 檔案系統 `storage/projects/{project_id}/...`
- DB 只記 metadata、status、version、path、checksum

原因：
- 符合 blueprint 的 artifact plane
- 能保留 exact version / snapshot
- 不必一開始就做 blob/object storage 複雜度

## v1 project folder contract

```text
storage/projects/{project_id}/
  brief.md
  research.md
  script.md
  storyboard.md
  prompt-pack.md         # optional placeholder
  edit-plan.md           # optional placeholder
  qa-report.md
  publish-pack.md
  retro.md
  assets/
  exports/
```

v1 必做：
- `brief.md`
- `research.md`
- `script.md`
- `storyboard.md`
- `qa-report.md`
- `publish-pack.md`
- `retro.md`

phase 1.5 placeholder：
- `prompt-pack.md`
- `edit-plan.md`
- `asset-checklist.md`

## Hard rails to encode immediately

1. No ownerless project
2. No handoff without acceptance state
3. No approval without exact artifact version
4. No post-lock scope change without formal change review
5. No agent action outside contract / rails
6. No v1 phase accepted unless a real operator task is possible on a real page

## Strong recommendation

如果今天要開工，先不要做新的大而全 monorepo 或多 app workspace。
先做單一 Next.js app，先把：
- route tree
- contracts
- templates
- state machine
- artifact folder contract
固定下來。

這樣最符合目前來源文件的共同結論，也最能避免再次回到多 repo 半成品狀態。
