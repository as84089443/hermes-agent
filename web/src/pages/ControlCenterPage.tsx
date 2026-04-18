import { useEffect, useState } from "react";
import { AlertTriangle, ArrowRight, Clock3, Pause, Play, RefreshCw, MessageSquareText, ExternalLink, Wrench, Briefcase, CheckSquare, Crown, Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import type { ControlCenterResponse, CronJob, GoalSummary, ImplementationTask, ProjectApproval, ProjectSummary, SelfEvolutionCandidate, SelfEvolutionCandidateQueue, SelfEvolutionStatus, TrackedSession } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import { bossHeroFromProject, humanizeApprovalState, humanizeProjectStatus, summarizeApprovalRecommendation, summarizeApprovalRisk, summarizeProjectCard, summarizeProjectNeed } from "@/lib/boss_mode_labels";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Toast } from "@/components/Toast";
import { useToast } from "@/hooks/useToast";

function openSession(sessionId?: string | null) {
  if (!sessionId) return;
  window.localStorage.setItem("hermes:selected-session", sessionId);
  window.dispatchEvent(new CustomEvent("hermes:navigate", { detail: { page: "sessions" } }));
}

function decisionBadgeVariant(state: string): "success" | "warning" | "outline" {
  if (state.includes("介入") || state.includes("pending") || state.includes("等待")) return "warning";
  if (state.includes("進行中") || state.includes("approved") || state.includes("done")) return "success";
  return "outline";
}

function taskBadgeVariant(state: string): "success" | "warning" | "outline" {
  if (state.includes("in_progress")) return "success";
  if (state.includes("pending")) return "outline";
  return "warning";
}

function firstLine(text?: string | null): string {
  if (!text) return "";
  const line = text
    .split(/\r?\n/)
    .map((part) => part.trim())
    .find(Boolean);
  return line ?? "";
}

type PushFeedback = {
  sessionId: string;
  scopeLabel: string;
  reply: string;
  completedAt: number;
};

export default function ControlCenterPage() {
  const [data, setData] = useState<ControlCenterResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyJobs, setBusyJobs] = useState<Set<string>>(new Set());
  const [busySessions, setBusySessions] = useState<Set<string>>(new Set());
  const [pushFeedback, setPushFeedback] = useState<PushFeedback | null>(null);
  const { toast, showToast } = useToast();

  const load = async () => {
    try {
      const resp = await api.getControlCenter();
      setData(resp);
    } catch (err) {
      showToast(`載入指揮台失敗：${String(err)}`, "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  const setJobBusy = (id: string, on: boolean) => {
    setBusyJobs((prev) => {
      const next = new Set(prev);
      if (on) next.add(id);
      else next.delete(id);
      return next;
    });
  };

  const setSessionBusy = (id: string, on: boolean) => {
    setBusySessions((prev) => {
      const next = new Set(prev);
      if (on) next.add(id);
      else next.delete(id);
      return next;
    });
  };

  const pushForwardPrompt = "請根據目前目標直接往下推進，優先完成當前下一步；如果需要我拍板，只回報待決策事項、風險與建議選項。";

  const pushSessionForward = async (sessionId?: string | null, scopeLabel = "這段對話") => {
    if (!sessionId) {
      showToast("這個項目目前還沒有可續推的對話", "error");
      return;
    }
    setSessionBusy(sessionId, true);
    try {
      const resp = await api.sendChatMessage({ session_id: sessionId, message: pushForwardPrompt });
      const reply = firstLine(resp.final_response) || "已完成一輪續推。";
      setPushFeedback({
        sessionId,
        scopeLabel,
        reply,
        completedAt: Date.now(),
      });
      showToast("已完成續推，結果已更新到頁面", "success");
      await load();
    } catch (e) {
      showToast(`續推失敗：${String(e)}`, "error");
    } finally {
      setSessionBusy(sessionId, false);
    }
  };

  const runJobAction = async (job: CronJob, action: "pause" | "resume" | "trigger") => {
    setJobBusy(job.id, true);
    try {
      if (action === "pause") await api.pauseCronJob(job.id);
      if (action === "resume") await api.resumeCronJob(job.id);
      if (action === "trigger") await api.triggerCronJob(job.id);
      showToast(action === "trigger" ? "已手動觸發排程" : action === "pause" ? "已暫停排程" : "已恢復排程", "success");
      load();
    } catch (e) {
      showToast(`操作失敗：${e}`, "error");
    } finally {
      setJobBusy(job.id, false);
    }
  };

  if (loading || !data) {
    return <div className="flex items-center justify-center py-24"><div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" /></div>;
  }

  const topJobs = data.cron_jobs.slice(0, 5);
  const trackedSessions = data.tracked_sessions ?? [];
  const processingSessionIds = new Set(
    trackedSessions
      .filter((session) => session.stage === "正在處理中")
      .map((session) => session.session_id),
  );
  const topGoals = data.top_goals ?? [];
  const implementationTasks = data.implementation_tasks ?? [];
  const projects = data.projects ?? [];
  const pendingApprovals = data.pending_approvals ?? [];
  const autopilot = data.autopilot;
  const selfEvolutionStatus = data.self_evolution_status;
  const selfEvolutionQueue = data.self_evolution_queue;
  const selfEvolutionJobs = data.self_evolution_cron_jobs ?? [];

  const activeSession = trackedSessions.find((session) => session.is_active) ?? trackedSessions[0] ?? null;
  const leadProject = projects[0] ?? null;
  const leadApproval = pendingApprovals[0] ?? null;
  const hero = bossHeroFromProject(leadProject);
  const nowCards = [
    {
      title: "現在最值得你先看",
      value: hero.title,
      note: hero.summary,
      tone: leadProject && (leadProject.status === "blocked" || leadProject.status === "waiting_on_human" || leadProject.status === "noop_already_waiting_on_human_approval") ? "warning" as const : "neutral" as const,
    },
    {
      title: "你現在要做什麼",
      value: hero.actionHint,
      note: leadApproval ? `待拍板：${leadApproval.title}` : (leadProject?.next_action_summary ?? "系統可先自行往下推進"),
      tone: leadApproval ? "warning" as const : "neutral" as const,
    },
    {
      title: "系統正在做什麼",
      value: autopilot?.started ? `${autopilot.status} / ${autopilot.interval_seconds}s` : (activeSession?.stage ?? "driver 未啟動"),
      note: autopilot?.last_cycle_reason ? `上次 cycle：${autopilot.last_cycle_reason}` : (activeSession?.recent_step ?? "等待第一輪 cycle"),
      tone: "neutral" as const,
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      {toast && <Toast toast={toast} />}

      <div className="grid gap-4 sm:grid-cols-4">
        <MetricCard title="進行中專案" value={`${data.counts.active_projects ?? projects.length}`} badge="project control plane" />
        <MetricCard title="等待你拍板" value={`${data.counts.waiting_on_human ?? pendingApprovals.length}`} badge={pendingApprovals.length > 0 ? "需要決策" : "目前無"} />
        <MetricCard title="Autopilot Driver" value={autopilot?.started ? (autopilot.status || "running") : "未啟動"} badge={autopilot?.last_cycle_reason ? `上次：${autopilot.last_cycle_reason}` : "等待首輪 cycle"} />
        <MetricCard title="進行中對話" value={`${data.counts.active_sessions}`} badge={data.counts.active_sessions > 0 ? "即時" : "目前無"} />
      </div>

      {pushFeedback && (
        <Card className="border-success/40 bg-success/5">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2"><Sparkles className="h-4 w-4" />剛剛已替你往下推進</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <div className="text-sm">
              已完成：<span className="font-medium">{pushFeedback.scopeLabel}</span>
              <span className="ml-2 text-xs text-muted-foreground">{new Date(pushFeedback.completedAt).toLocaleTimeString()}</span>
            </div>
            <div className="border border-success/30 bg-background/70 p-3 text-sm leading-relaxed">
              {pushFeedback.reply}
            </div>
            <div className="flex flex-wrap gap-2">
              <Button size="sm" onClick={() => openSession(pushFeedback.sessionId)}>
                <ExternalLink className="mr-1 h-3.5 w-3.5" /> 打開完整對話
              </Button>
              <Button size="sm" variant="outline" onClick={() => setPushFeedback(null)}>
                收起這則回饋
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">現在在做什麼</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 lg:grid-cols-3">
          {nowCards.map((card, idx) => (
            <div
              key={`${card.title}-${idx}`}
              className={`border p-3 ${card.tone === "warning" ? "border-warning/40 bg-warning/5" : "border-border"}`}
            >
              <div className="mb-1 text-xs text-muted-foreground">{card.title}</div>
              <div className="text-sm font-medium leading-relaxed">{card.value}</div>
              <div className="mt-2 text-xs text-muted-foreground/90 leading-relaxed">{card.note}</div>
            </div>
          ))}
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2"><Briefcase className="h-4 w-4" />今天最重要的專案</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {projects.length === 0 ? (
              <div className="border border-border p-3 text-sm text-muted-foreground">目前還沒有 project ledger 資料。請到「專案」頁建立第一個專案。</div>
            ) : projects.slice(0, 3).map((project) => (
              <ProjectOverviewCard key={project.id} project={project} />
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2"><Crown className="h-4 w-4" />現在需要你決定</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {pendingApprovals.length === 0 ? (
              <div className="border border-border p-3 text-sm text-muted-foreground">目前沒有待你拍板的事項。系統可先自行往下推進。</div>
            ) : pendingApprovals.slice(0, 3).map((approval) => (
              <PendingApprovalCard key={approval.id} approval={approval} />
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SelfEvolutionStatusCard status={selfEvolutionStatus} queue={selfEvolutionQueue} jobs={selfEvolutionJobs} />

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2"><CheckSquare className="h-4 w-4" />自我進化現在在做什麼</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <SelfEvolutionCandidateCard candidate={selfEvolutionQueue?.current_candidates?.[0] ?? null} />
            <div className="border border-border p-3 text-sm">
              <div className="font-medium">現在最重要的 learnings</div>
              <div className="mt-2 space-y-2 text-muted-foreground">
                {(selfEvolutionStatus?.latest_accepted_learnings?.slice(0, 3) ?? []).length > 0 ? (
                  (selfEvolutionStatus?.latest_accepted_learnings?.slice(0, 3) ?? []).map((item, idx) => (
                    <div key={idx}>- {item}</div>
                  ))
                ) : (
                  <div>目前還沒抓到最新 learnings。</div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2"><AlertTriangle className="h-4 w-4" />目前卡住</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {(projects.filter((project) => project.status === "blocked" || project.status === "waiting_on_human").slice(0, 3).map((project) => project.waiting_reason || project.last_cycle_summary).filter(Boolean) as string[]).length > 0 ? (
              (projects.filter((project) => project.status === "blocked" || project.status === "waiting_on_human").slice(0, 3).map((project) => project.waiting_reason || project.last_cycle_summary).filter(Boolean) as string[]).map((item, idx) => (
                <div key={idx} className="border border-border p-3 text-sm">{item}</div>
              ))
            ) : (
              <div className="border border-border p-3 text-sm text-muted-foreground">目前沒有需要你立即處理的 blocker。</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2"><ArrowRight className="h-4 w-4" />系統下一步</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {leadProject ? (
              <div className="border border-border p-3 text-sm">
                <div className="font-medium">{leadProject.title}</div>
                <div className="mt-2 text-muted-foreground">{leadProject.next_action_summary ?? "尚未設定下一步"}</div>
              </div>
            ) : (
              <div className="border border-border p-3 text-sm text-muted-foreground">下一步尚未寫入。</div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2"><Clock3 className="h-4 w-4" />自動推進狀態</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            <div className="border border-border p-3 text-sm">
              <div className="font-medium">{autopilot?.started ? "系統已啟動自動推進" : "自動推進尚未啟動"}</div>
              <div className="mt-2 text-muted-foreground">
                {autopilot?.last_cycle_reason ? `最近一輪：${autopilot.last_cycle_reason}` : "等待第一輪 cycle"}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <details className="border border-border p-4">
        <summary className="cursor-pointer text-sm font-medium">展開查看系統細節</summary>
        <div className="mt-4 grid gap-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2"><Briefcase className="h-4 w-4" />主線目標</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3">
                {topGoals.length === 0 ? (
                  <div className="border border-border p-3 text-sm text-muted-foreground">目前還沒有對外顯示的 goal。</div>
                ) : topGoals.map((goal, idx) => (
                  <GoalCard
                    key={`${goal.title}-${idx}`}
                    goal={goal}
                    busy={Boolean(goal.session_id && (busySessions.has(goal.session_id) || processingSessionIds.has(goal.session_id)))}
                    onPushForward={pushSessionForward}
                    busyLabel={goal.session_id && processingSessionIds.has(goal.session_id) && !busySessions.has(goal.session_id) ? "Hermes 處理中…" : "推進中…"}
                  />
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2"><CheckSquare className="h-4 w-4" />開發實作細節</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3">
                {implementationTasks.length === 0 ? (
                  <div className="border border-border p-3 text-sm text-muted-foreground">目前還沒有掛上的 implementation tasks。</div>
                ) : implementationTasks.map((task, idx) => <ImplementationTaskCard key={`${task.title}-${idx}`} task={task} />)}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2"><MessageSquareText className="h-4 w-4" />對話追蹤</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3">
              {trackedSessions.length === 0 ? (
                <div className="border border-border p-4 text-sm text-muted-foreground">目前沒有可追蹤的對話。</div>
              ) : trackedSessions.slice(0, 5).map((session) => (
                <TrackedSessionCard
                  key={session.session_id}
                  session={session}
                  busy={busySessions.has(session.session_id) || processingSessionIds.has(session.session_id)}
                  onPushForward={pushSessionForward}
                  busyLabel={processingSessionIds.has(session.session_id) && !busySessions.has(session.session_id) ? "Hermes 處理中…" : "推進中…"}
                />
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2"><Clock3 className="h-4 w-4" />排程管理</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3">
              {topJobs.map((job) => {
                const busy = busyJobs.has(job.id);
                return (
                  <div key={job.id} className="border border-border p-3 flex flex-col gap-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <div className="font-medium text-sm">{job.name || job.id}</div>
                        <div className="text-xs text-muted-foreground">{job.schedule_display} · {job.enabled ? "啟用中" : "已暫停"}</div>
                        {job.last_run_at && <div className="text-xs text-muted-foreground/80">上次執行：{job.last_run_at}</div>}
                      </div>
                      <Badge variant={job.enabled ? "success" : "outline"}>{job.state}</Badge>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Button size="sm" variant="outline" disabled={busy} onClick={() => runJobAction(job, "trigger")}>
                        <RefreshCw className="mr-1 h-3.5 w-3.5" /> 立即跑
                      </Button>
                      {job.enabled ? (
                        <Button size="sm" variant="outline" disabled={busy} onClick={() => runJobAction(job, "pause")}>
                          <Pause className="mr-1 h-3.5 w-3.5" /> 暫停
                        </Button>
                      ) : (
                        <Button size="sm" variant="outline" disabled={busy} onClick={() => runJobAction(job, "resume")}>
                          <Play className="mr-1 h-3.5 w-3.5" /> 恢復
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>
      </details>
    </div>
  );
}

function SelfEvolutionStatusCard({ status, queue, jobs }: { status?: SelfEvolutionStatus; queue?: SelfEvolutionCandidateQueue; jobs: CronJob[] }) {
  const nextJob = jobs.find((job) => job.enabled && job.next_run_at) ?? jobs[0];
  const topFocus = status?.current_focus?.slice(0, 3) ?? [];
  const deferred = status?.latest_deferred_changes?.slice(0, 2) ?? [];
  const candidateCount = queue?.current_candidates?.length ?? 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2"><Sparkles className="h-4 w-4" />Hermes 自我進化</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-3">
        <div className="border border-border p-3 text-sm">
          <div className="font-medium">這條線現在的主焦點</div>
          <div className="mt-2 space-y-2 text-muted-foreground">
            {topFocus.length > 0 ? topFocus.map((item, idx) => <div key={idx}>{idx + 1}. {item}</div>) : <div>目前還沒有可顯示的 focus。</div>}
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          <InfoBox title="上次回顧" value={status?.last_reviewed_at ?? "尚未記錄"} />
          <InfoBox title="候選變更" value={`${candidateCount} 項`} />
          <InfoBox title="下一次排程" value={nextJob?.next_run_at ?? "尚未排定"} />
        </div>

        <div className="border border-border p-3 text-sm">
          <div className="font-medium">最近先不做的事</div>
          <div className="mt-2 space-y-2 text-muted-foreground">
            {deferred.length > 0 ? deferred.map((item, idx) => <div key={idx}>- {item}</div>) : <div>目前沒有新的 deferred 項目。</div>}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function SelfEvolutionCandidateCard({ candidate }: { candidate: SelfEvolutionCandidate | null }) {
  if (!candidate) {
    return (
      <div className="border border-border p-3 text-sm text-muted-foreground">
        目前還沒有 candidate queue 資料。
      </div>
    );
  }

  return (
    <div className="border border-border p-3 text-sm">
      <div className="flex flex-wrap items-center gap-2">
        <div className="font-medium">{candidate.title ?? "未命名候選"}</div>
        <Badge variant={decisionBadgeVariant(candidate.status ?? "candidate")}>{candidate.status ?? "candidate"}</Badge>
        {candidate.target_cadence && <Badge variant="outline">{candidate.target_cadence}</Badge>}
      </div>
      <div className="mt-2 text-muted-foreground">這輪在推什麼：{candidate.expected_gain ?? candidate.evidence ?? "尚未補說明"}</div>
      <div className="mt-2 text-xs text-muted-foreground">落點：{candidate.layer ?? "未標記"} · change type：{candidate.change_type ?? "未標記"}</div>
      {candidate.required_proof && <div className="mt-2 text-xs text-muted-foreground/90">完成前還要證明：{candidate.required_proof}</div>}
    </div>
  );
}

function GoalCard({ goal, busy, onPushForward, busyLabel = "推進中…" }: { goal: GoalSummary; busy: boolean; onPushForward: (sessionId?: string | null, scopeLabel?: string) => Promise<void>; busyLabel?: string }) {
  return (
    <div className="border border-border p-3">
      <div className="flex items-center gap-2 mb-2">
        <div className="text-sm font-medium">{goal.title}</div>
        <Badge variant={taskBadgeVariant(goal.status)}>{goal.status}</Badge>
      </div>
      <div className="text-xs text-muted-foreground">目前 owner：{goal.owner}</div>
      {goal.next && <div className="mt-2 text-sm">下一步：{goal.next}</div>}
      <div className="mt-3 flex gap-2">
        {goal.session_id && (
          <Button size="sm" variant="outline" disabled={busy} onClick={() => onPushForward(goal.session_id, goal.title || "這段主線目標")}>
            {busy ? busyLabel : "往下推進"}
          </Button>
        )}
      </div>
    </div>
  );
}

function ImplementationTaskCard({ task }: { task: ImplementationTask }) {
  return (
    <div className="border border-border p-3 flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <div className="text-sm font-medium">{task.title}</div>
        <Badge variant={taskBadgeVariant(task.status)}>{task.status}</Badge>
      </div>
      {task.now && <div className="text-sm">現在：{task.now}</div>}
      {task.next && <div className="text-xs text-muted-foreground">下一步：{task.next}</div>}
      {task.verify && <div className="text-xs text-muted-foreground/90">完成標準：{task.verify}</div>}
    </div>
  );
}

function ProjectOverviewCard({ project }: { project: ProjectSummary }) {
  return (
    <div className="border border-border p-3 text-sm">
      <div className="flex flex-wrap items-center gap-2">
        <div className="font-medium">{project.title}</div>
        <Badge variant={taskBadgeVariant(project.status)}>{humanizeProjectStatus(project.status)}</Badge>
        <Badge variant="outline">{project.main_phase ?? "未設定 phase"}</Badge>
      </div>
      <div className="mt-2 text-sm leading-relaxed">{summarizeProjectCard(project)}</div>
      <div className="mt-2 text-xs text-muted-foreground">下一步重點：{project.next_action_summary ?? "尚未設定"}</div>
      <div className="mt-2 text-xs text-muted-foreground">是否需要你介入：{summarizeProjectNeed(project)}</div>
      <div className="mt-3">
        <Button size="sm" variant="outline" onClick={() => window.dispatchEvent(new CustomEvent("hermes:navigate", { detail: { page: "projects" } }))}>
          <ExternalLink className="mr-1 h-3.5 w-3.5" /> 打開專案頁
        </Button>
      </div>
    </div>
  );
}

function PendingApprovalCard({ approval }: { approval: ProjectApproval }) {
  return (
    <div className="border border-warning/30 bg-warning/5 p-3 text-sm">
      <div className="flex flex-wrap items-center gap-2">
        <div className="font-medium">{approval.title}</div>
        <Badge variant={decisionBadgeVariant(approval.status)}>{humanizeApprovalState(approval.status)}</Badge>
      </div>
      <div className="mt-2 text-sm leading-relaxed">你現在要決定：{approval.summary ?? "是否讓這個專案繼續往下走。"}</div>
      <div className="mt-2 text-xs text-muted-foreground">主要風險：{summarizeApprovalRisk(approval)}</div>
      <div className="mt-1 text-xs text-muted-foreground">系統建議：{summarizeApprovalRecommendation(approval)}</div>
      <div className="mt-3">
        <Button size="sm" variant="outline" onClick={() => window.dispatchEvent(new CustomEvent("hermes:navigate", { detail: { page: "approvals" } }))}>
          <ExternalLink className="mr-1 h-3.5 w-3.5" /> 前往審批頁
        </Button>
      </div>
    </div>
  );
}

function TrackedSessionCard({ session, busy, onPushForward, busyLabel = "推進中…" }: { session: TrackedSession; busy: boolean; onPushForward: (sessionId?: string | null, scopeLabel?: string) => Promise<void>; busyLabel?: string }) {
  return (
    <div className="border border-border p-3 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <div className="font-medium text-sm truncate">{session.title || "未命名會話"}</div>
            <Badge variant={decisionBadgeVariant(session.decision_state)}>{session.decision_state}</Badge>
            {session.is_active && <Badge variant="success">即時</Badge>}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {(session.model ?? "unknown").split("/").pop()} · {session.message_count} 則訊息 · {session.last_active ? timeAgo(session.last_active) : "剛剛"}
          </div>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="outline" disabled={busy} onClick={() => onPushForward(session.session_id, session.title || "這段對話")}>
            {busy ? busyLabel : "往下推進"}
          </Button>
          <Button size="sm" variant="outline" onClick={() => openSession(session.session_id)}>
            <ExternalLink className="mr-1 h-3.5 w-3.5" /> 打開
          </Button>
        </div>
      </div>

      <div className="grid gap-2 sm:grid-cols-2">
        <InfoBox title="目前進度" value={session.stage} />
        <InfoBox title="最近一步" value={session.recent_step} icon={session.last_tool ? <Wrench className="h-3.5 w-3.5" /> : undefined} />
        <InfoBox title="最近需求" value={session.latest_user_request ?? "尚未讀到明確需求摘要"} />
        <InfoBox title="最新回覆" value={session.latest_reply ?? "這輪還沒有完整回覆"} />
      </div>

      {session.attention && (
        <div className="border border-warning/30 bg-warning/5 p-3 text-sm">
          <div className="mb-1 text-xs font-semibold text-warning">需要注意</div>
          <div>{session.attention}</div>
        </div>
      )}
    </div>
  );
}

function InfoBox({ title, value, icon }: { title: string; value: string; icon?: React.ReactNode }) {
  return (
    <div className="border border-border p-3 text-sm">
      <div className="mb-1 flex items-center gap-1 text-xs text-muted-foreground">
        {icon}
        <span>{title}</span>
      </div>
      <div>{value}</div>
    </div>
  );
}

function MetricCard({ title, value, badge }: { title: string; value: string; badge: string }) {
  return (
    <Card>
      <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">{title}</CardTitle></CardHeader>
      <CardContent>
        <div className="text-xl font-bold leading-snug">{value}</div>
        <Badge variant="outline" className="mt-2">{badge}</Badge>
      </CardContent>
    </Card>
  );
}
