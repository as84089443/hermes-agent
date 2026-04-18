# AI Department OS v1 Contracts

這一組 contract 先用 markdown 固定 canonical shape。
等 v1 pilot 跑通後，再對齊 `docs/specs/ai-department-os-v1-minimal-data-model.md`，同步實作到 `docs/contracts/ai-department-os/v1/*.json`、Prisma、Zod、route validators。

Contract files:
- `project.md`
- `task.md`
- `handoff.md`
- `approval.md`
- `artifact.md`
- `event.md`
- `execution-graph.md`

Hard rails:
- No ownerless project
- No handoff without acceptance state
- No approval without exact artifact version
- No post-lock scope change without formal change review
- No branch merge without merge owner
