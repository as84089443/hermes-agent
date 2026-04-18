import type { ProjectApproval, ProjectEvent, ProjectSummary, ProjectTask } from "@/lib/api";

export function humanizeProjectStatus(status?: string | null): string {
  switch (status) {
    case "in_progress":
    case "running":
      return "執行中";
    case "waiting_on_human":
    case "noop_already_waiting_on_human_approval":
      return "等待你拍板";
    case "needs_revision":
    case "changes_requested":
      return "退回修改";
    case "blocked":
      return "已卡住";
    case "completed":
      return "已完成";
    case "review_passed":
      return "本輪檢查通過";
    case "verified":
      return "驗證完成";
    case "pending":
      return "等待處理";
    default:
      return status || "未設定";
  }
}

export function humanizeApprovalState(status?: string | null): string {
  switch (status) {
    case "pending":
      return "等待你拍板";
    case "approved":
      return "已核准";
    case "changes_requested":
      return "已退回修改";
    case "rejected":
      return "已駁回";
    default:
      return status || "未設定";
  }
}

export function humanizeTaskStatus(status?: string | null): string {
  switch (status) {
    case "queued":
      return "排隊中";
    case "in_progress":
      return "處理中";
    case "review_passed":
      return "檢查通過";
    case "verified":
      return "驗證完成";
    case "blocked":
      return "已卡住";
    case "done":
      return "已完成";
    default:
      return status || "未設定";
  }
}

export function humanizeOwnerRole(role?: string | null): string {
  switch (role) {
    case "Hermes 公司系統":
    case "orchestrator":
      return "Hermes 總控";
    case "operator":
      return "執行代理";
    case "reviewer":
      return "檢查代理";
    default:
      return role || "未指派";
  }
}

export function humanizeEventType(type?: string | null): string {
  switch (type) {
    case "project_created":
      return "專案已建立";
    case "project_pushed":
      return "系統已往下推進";
    case "approval_requested":
      return "已送出待拍板關卡";
    case "approval_decided":
      return "已記錄拍板結果";
    case "artifact_written":
      return "已產出新內容";
    case "review_decided":
      return "已完成檢查判定";
    case "verification_recorded":
      return "已記錄驗證結果";
    case "task_state_changed":
      return "任務狀態已更新";
    case "escalation_raised":
      return "已標記卡住";
    case "autopilot_resumed":
      return "已恢復自動推進";
    case "autopilot_paused":
      return "已暫停自動推進";
    default:
      return type || "系統更新";
  }
}

export function summarizeProjectCard(project: ProjectSummary): string {
  if (project.status === "blocked") {
    return project.waiting_reason || project.last_cycle_summary || "這個專案目前卡住，值得你先看。";
  }
  if (project.status === "waiting_on_human" || project.status === "noop_already_waiting_on_human_approval") {
    return project.waiting_reason || project.last_cycle_summary || "這個專案目前停在等待你拍板。";
  }
  return project.last_cycle_summary || project.next_action_summary || "系統正在往下推進這個專案。";
}

export function summarizeProjectNeed(project: ProjectSummary): string {
  if (project.status === "blocked") return "需要你先排除 blocker";
  if (project.status === "waiting_on_human" || project.status === "noop_already_waiting_on_human_approval") return "需要你現在拍板";
  return "目前可由系統自行往下推進";
}

export function summarizeApprovalRecommendation(approval: ProjectApproval): string {
  const text = approval.summary || "";
  if (/風險|缺少|不足|先補/i.test(text)) return "建議先退回修改";
  return "建議核准並繼續";
}

export function summarizeApprovalRisk(approval: ProjectApproval): string {
  const text = approval.summary || "";
  if (/風險|高|阻塞/i.test(text)) return "高風險或會卡住主線";
  if (/驗證|確認|拍板/i.test(text)) return "中等風險，主要是方向與放行確認";
  return "一般風險，主要是節點放行確認";
}

export function summarizeTask(task: ProjectTask): string {
  const who = humanizeOwnerRole(task.owner_role);
  const state = humanizeTaskStatus(task.status);
  if (task.blocking_reason) return `${who} · ${state} · 卡點：${task.blocking_reason}`;
  return `${who} · ${state}`;
}

export function summarizeEvent(event: ProjectEvent): string {
  return event.summary || humanizeEventType(event.event_type);
}

export function bossHeroFromProject(project?: ProjectSummary | null) {
  if (!project) {
    return {
      title: "目前沒有主專案",
      summary: "先建立第一個專案，前台就會開始進入真正的老闆模式。",
      actionHint: "前往專案頁建立新專案",
    };
  }
  return {
    title: project.title,
    summary: summarizeProjectCard(project),
    actionHint: summarizeProjectNeed(project),
  };
}
