import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, ExternalLink, Pause, Play, Plus, RefreshCw, ShieldAlert, Sparkles } from "lucide-react";
import { api, type ProjectApproval, type ProjectDetail, type ProjectSummary } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import { humanizeEventType, humanizeProjectStatus, humanizeTaskStatus, summarizeApprovalRecommendation, summarizeApprovalRisk, summarizeEvent, summarizeTask } from "@/lib/boss_mode_labels";
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

function persistSelectedProject(projectId?: string | null) {
  if (!projectId) return;
  window.localStorage.setItem("hermes:selected-project", projectId);
}

function statusVariant(status: string): "success" | "warning" | "outline" {
  if (["approved", "done", "completed", "in_progress"].includes(status)) return "success";
  if (["waiting_on_human", "needs_revision", "blocked", "pending"].includes(status)) return "warning";
  return "outline";
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyProjectId, setBusyProjectId] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [approvalDrafts, setApprovalDrafts] = useState<Record<string, { title: string; summary: string }>>({});
  const [form, setForm] = useState({
    title: "",
    phase_goal: "",
    next_action_summary: "整理需求、建立主 phase，並把下一步推進到可執行狀態。",
  });
  const { toast, showToast } = useToast();

  const loadProjects = async (preferredProjectId?: string | null) => {
    const resp = await api.getProjects();
    const list = resp.projects;
    setProjects(list);
    const nextProjectId = preferredProjectId ?? selectedProjectId ?? window.localStorage.getItem("hermes:selected-project") ?? list[0]?.id ?? null;
    setSelectedProjectId(nextProjectId);
    if (nextProjectId) {
      persistSelectedProject(nextProjectId);
      const projectDetail = await api.getProjectDetail(nextProjectId);
      setDetail(projectDetail);
    } else {
      setDetail(null);
    }
  };

  useEffect(() => {
    (async () => {
      try {
        await loadProjects();
      } catch (error) {
        showToast(`載入專案失敗：${String(error)}`, "error");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const activeProjects = useMemo(() => projects.filter((p) => p.status !== "completed"), [projects]);

  const refreshDetail = async (projectId: string) => {
    persistSelectedProject(projectId);
    setSelectedProjectId(projectId);
    const projectDetail = await api.getProjectDetail(projectId);
    setDetail(projectDetail);
  };

  const runProjectAction = async (projectId: string, action: "push" | "pause" | "resume") => {
    setBusyProjectId(projectId);
    try {
      if (action === "push") {
        await api.pushProject(projectId);
        showToast("已替這個專案往下推進一輪", "success");
      }
      if (action === "pause") {
        await api.pauseProject(projectId);
        showToast("已暫停這個專案的自動推進", "success");
      }
      if (action === "resume") {
        await api.resumeProject(projectId);
        showToast("已恢復這個專案的自動推進", "success");
      }
      await loadProjects(projectId);
    } catch (error) {
      showToast(`操作失敗：${String(error)}`, "error");
    } finally {
      setBusyProjectId(null);
    }
  };

  const createProject = async () => {
    if (!form.title.trim()) {
      showToast("請先輸入專案名稱", "error");
      return;
    }
    setCreating(true);
    try {
      const project = await api.createProject({
        title: form.title.trim(),
        phase_goal: form.phase_goal.trim() || undefined,
        next_action_summary: form.next_action_summary.trim() || undefined,
      });
      showToast("已建立新專案控制面", "success");
      setForm({ title: "", phase_goal: "", next_action_summary: "整理需求、建立主 phase，並把下一步推進到可執行狀態。" });
      await loadProjects(project.id);
    } catch (error) {
      showToast(`建立失敗：${String(error)}`, "error");
    } finally {
      setCreating(false);
    }
  };

  const requestApproval = async (projectId: string) => {
    const draft = approvalDrafts[projectId] ?? { title: "需要你拍板下一步", summary: "請確認這個專案現在是否可繼續往下推進。" };
    if (!draft.title.trim()) {
      showToast("請先輸入待拍板標題", "error");
      return;
    }
    setBusyProjectId(projectId);
    try {
      await api.requestProjectApproval(projectId, { title: draft.title.trim(), summary: draft.summary.trim() || draft.title.trim() });
      showToast("已建立待拍板關卡", "success");
      await loadProjects(projectId);
    } catch (error) {
      showToast(`建立待拍板失敗：${String(error)}`, "error");
    } finally {
      setBusyProjectId(null);
    }
  };

  const runWorkspaceAction = async (projectId: string, action: "review" | "verify" | "escalate") => {
    setBusyProjectId(projectId);
    try {
      if (action === "review") {
        await api.reviewProject(projectId, { verdict: "PASS", notes: "網站控制面手動 review 通過" });
        showToast("已回寫 review verdict", "success");
      }
      if (action === "verify") {
        await api.verifyProject(projectId, { summary: "網站控制面手動 verification 通過", passed: true });
        showToast("已回寫 verification artifact", "success");
      }
      if (action === "escalate") {
        await api.escalateProject(projectId, { reason: "網站控制面手動標記 blocker escalation" });
        showToast("已標記 blocker escalation", "success");
      }
      await loadProjects(projectId);
    } catch (error) {
      showToast(`操作失敗：${String(error)}`, "error");
    } finally {
      setBusyProjectId(null);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center py-24"><div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" /></div>;
  }

  return (
    <div className="flex flex-col gap-6">
      {toast && <Toast toast={toast} />}

      <div className="grid gap-4 md:grid-cols-4">
        <MetricCard title="進行中專案" value={`${activeProjects.length}`} note="真正的 project control plane" />
        <MetricCard title="等待你拍板" value={`${projects.filter((p) => p.status === "waiting_on_human").length}`} note="可直接在審批頁處理" />
        <MetricCard title="已卡住" value={`${projects.filter((p) => p.status === "blocked").length}`} note="需要排除 blocker" />
        <MetricCard title="自動推進中" value={`${projects.filter((p) => p.autopilot_enabled).length}`} note="可暫停 / 恢復" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><Plus className="h-4 w-4" />建立新專案</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          <label className="grid gap-2 text-sm">
            <span>專案名稱</span>
            <input className="border bg-background px-3 py-2" value={form.title} onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))} placeholder="例如：Hermes Autopilot v0" />
          </label>
          <label className="grid gap-2 text-sm">
            <span>階段目標</span>
            <input className="border bg-background px-3 py-2" value={form.phase_goal} onChange={(e) => setForm((prev) => ({ ...prev, phase_goal: e.target.value }))} placeholder="例如：把 dashboard 變成真正的專案控制面" />
          </label>
          <label className="grid gap-2 text-sm">
            <span>預設下一步</span>
            <input className="border bg-background px-3 py-2" value={form.next_action_summary} onChange={(e) => setForm((prev) => ({ ...prev, next_action_summary: e.target.value }))} placeholder="先做哪一刀" />
          </label>
          <div className="md:col-span-3 flex flex-wrap gap-2">
            <Button onClick={createProject} disabled={creating}>{creating ? "建立中…" : "建立專案控制面"}</Button>
            <div className="text-xs text-muted-foreground self-center">建立後可直接在這頁推進、暫停、恢復，並打開對應代理對話。</div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">/projects — 專案盤面</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3">
            {projects.length === 0 ? (
              <div className="border p-4 text-sm text-muted-foreground">目前還沒有專案。先建立一個，網站就會開始有 project-level 控制面，而不是只看聊天紀錄。</div>
            ) : projects.map((project) => {
              const busy = busyProjectId === project.id;
              return (
                <div key={project.id} className={`border p-4 ${selectedProjectId === project.id ? "border-primary bg-primary/5" : "border-border"}`}>
                  <div className="flex flex-wrap items-center gap-2">
                    <button className="text-left text-sm font-medium cursor-pointer" onClick={() => refreshDetail(project.id)}>{project.title}</button>
                    <Badge variant={statusVariant(project.status)}>{humanizeProjectStatus(project.status)}</Badge>
                    <Badge variant="outline">{project.main_phase ?? "未設定 phase"}</Badge>
                    {!project.autopilot_enabled && <Badge variant="warning">已暫停自動推進</Badge>}
                  </div>
                  <div className="mt-2 grid gap-1 text-sm text-muted-foreground">
                    <div>目前 owner：{project.current_owner ?? "Hermes 公司系統"}</div>
                    <div>下一步：{project.next_action_summary ?? "尚未設定"}</div>
                    <div>最近結果：{project.last_cycle_summary ?? "還沒有 project push 記錄"}</div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground">
                    <span>開放任務 {project.open_tasks}</span>
                    <span>待拍板 {project.open_approvals}</span>
                    <span>更新於 {timeAgo(project.updated_at)}</span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button size="sm" disabled={busy} onClick={() => runProjectAction(project.id, "push")}>
                      <Sparkles className="mr-1 h-3.5 w-3.5" /> {busy ? "推進中…" : "往下推進"}
                    </Button>
                    {project.autopilot_enabled ? (
                      <Button size="sm" variant="outline" disabled={busy} onClick={() => runProjectAction(project.id, "pause")}>
                        <Pause className="mr-1 h-3.5 w-3.5" /> 暫停
                      </Button>
                    ) : (
                      <Button size="sm" variant="outline" disabled={busy} onClick={() => runProjectAction(project.id, "resume")}>
                        <Play className="mr-1 h-3.5 w-3.5" /> 恢復
                      </Button>
                    )}
                    <Button size="sm" variant="outline" onClick={() => refreshDetail(project.id)}>
                      <RefreshCw className="mr-1 h-3.5 w-3.5" /> 查看細節
                    </Button>
                    {project.session_id && (
                      <Button size="sm" variant="outline" onClick={() => openSession(project.session_id)}>
                        <ExternalLink className="mr-1 h-3.5 w-3.5" /> 打開代理對話
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">/projects/[id] — 專案工作區</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            {!detail ? (
              <div className="border p-4 text-sm text-muted-foreground">左邊選一個專案，就會顯示 main phase、待拍板、任務與事件。</div>
            ) : (
              <>
                <div className="border p-5 bg-primary/5 border-primary/20">
                  <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
                    <div className="grid gap-3">
                      <div>
                        <div className="text-xs text-muted-foreground">目前最重要的專案</div>
                        <div className="mt-1 text-xl font-semibold leading-relaxed">{detail.title}</div>
                        <div className="mt-2 text-sm leading-relaxed text-muted-foreground">
                          {detail.phase_goal ?? detail.next_action_summary ?? "這個專案目前仍在整理中，下一步尚未明確。"}
                        </div>
                      </div>
                      <div className="grid gap-3 md:grid-cols-3">
                        <SummaryCard title="目前方向" value={detail.main_phase ?? "未設定"} note={detail.phase_goal ?? detail.next_action_summary ?? "尚未設定階段目標"} />
                        <SummaryCard title="目前卡點" value={detail.waiting_reason || (detail.status === "blocked" ? "這個專案目前已卡住" : "目前沒有明確 blocker")} note={`狀態：${humanizeProjectStatus(detail.status)}`} warning={Boolean(detail.waiting_reason) || detail.status === "blocked"} />
                        <SummaryCard title="下一個決策" value={detail.next_action_summary ?? "尚未設定下一步"} note={detail.last_cycle_summary ?? "還沒有最近執行結果"} />
                      </div>
                    </div>

                    <div className="border bg-background/70 p-4">
                      <div className="text-sm font-medium">你現在最該做什麼</div>
                      <div className="mt-2 text-sm leading-relaxed">{detail.status === "blocked" ? "先看卡點並決定是否要排除 blocker。" : detail.approvals.filter((item) => item.status === "pending").length > 0 ? "先處理這個專案的待拍板事項，否則系統不會繼續往下走。" : "如果方向清楚，就可以直接按「往下推進」，讓系統繼續往下做。"}</div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <Button size="sm" disabled={busyProjectId === detail.id} onClick={() => runProjectAction(detail.id, "push")}>
                          <Sparkles className="mr-1 h-3.5 w-3.5" /> 往下推進
                        </Button>
                        {detail.approvals.some((item) => item.status === "pending") && (
                          <Button size="sm" variant="outline" onClick={() => document.getElementById(`project-approval-zone-${detail.id}`)?.scrollIntoView({ behavior: "smooth", block: "start" })}>
                            <AlertTriangle className="mr-1 h-3.5 w-3.5" /> 前往待拍板區
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border p-4">
                  <div className="text-sm font-medium">主控制動作</div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Button size="sm" disabled={busyProjectId === detail.id} onClick={() => runProjectAction(detail.id, "push")}>
                      <Sparkles className="mr-1 h-3.5 w-3.5" /> 往下推進
                    </Button>
                    <Button size="sm" variant="outline" disabled={busyProjectId === detail.id} onClick={() => runWorkspaceAction(detail.id, "review")}>
                      <CheckCircle2 className="mr-1 h-3.5 w-3.5" /> 核准本輪檢查
                    </Button>
                    <Button size="sm" variant="outline" disabled={busyProjectId === detail.id} onClick={() => runWorkspaceAction(detail.id, "verify")}>
                      <CheckCircle2 className="mr-1 h-3.5 w-3.5" /> 確認驗證完成
                    </Button>
                    <Button size="sm" variant="outline" disabled={busyProjectId === detail.id} onClick={() => runWorkspaceAction(detail.id, "escalate")}>
                      <ShieldAlert className="mr-1 h-3.5 w-3.5" /> 標記這案卡住
                    </Button>
                    {detail.session_id && (
                      <Button size="sm" variant="outline" onClick={() => openSession(detail.session_id)}>
                        <ExternalLink className="mr-1 h-3.5 w-3.5" /> 打開代理對話
                      </Button>
                    )}
                  </div>
                  <div className="mt-2 text-xs text-muted-foreground">
                    這些按鈕都不是假 UI，會真的回寫專案狀態、任務狀態與產物紀錄。
                  </div>
                </div>

                <div id={`project-approval-zone-${detail.id}`} className="border p-4">
                  <div className="text-sm font-medium">待你拍板</div>
                  {detail.approvals.filter((item) => item.status === "pending").length === 0 ? (
                    <div className="mt-2 text-sm text-muted-foreground">這個專案目前沒有待拍板事項。若你想主動插入人工決策，可以在下方建立新的待拍板關卡。</div>
                  ) : (
                    <div className="mt-3 grid gap-3">
                      {detail.approvals.filter((item) => item.status === "pending").map((approval) => (
                        <ApprovalSnippet key={approval.id} approval={approval} />
                      ))}
                    </div>
                  )}
                  <div className="mt-4 grid gap-2">
                    <input
                      className="border bg-background px-3 py-2 text-sm"
                      placeholder="這次要你決定什麼，例如：是否讓這案進入下一輪自動執行"
                      value={approvalDrafts[detail.id]?.title ?? ""}
                      onChange={(e) => setApprovalDrafts((prev) => ({ ...prev, [detail.id]: { title: e.target.value, summary: prev[detail.id]?.summary ?? "" } }))}
                    />
                    <textarea
                      className="min-h-24 border bg-background px-3 py-2 text-sm"
                      placeholder="補充這次為什麼輪到你拍板、主要風險是什麼、若不放行會退回哪裡。"
                      value={approvalDrafts[detail.id]?.summary ?? ""}
                      onChange={(e) => setApprovalDrafts((prev) => ({ ...prev, [detail.id]: { title: prev[detail.id]?.title ?? "", summary: e.target.value } }))}
                    />
                    <div>
                      <Button size="sm" variant="outline" disabled={busyProjectId === detail.id} onClick={() => requestApproval(detail.id)}>
                        <AlertTriangle className="mr-1 h-3.5 w-3.5" /> 建立待拍板關卡
                      </Button>
                    </div>
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="border p-4">
                    <div className="text-sm font-medium">工作進度</div>
                    <div className="mt-2 text-xs text-muted-foreground">先看現在有哪些工作正在推，哪些已卡住，不需要先讀內部 state 名稱。</div>
                    <div className="mt-3 grid gap-2">
                      {detail.tasks.length === 0 ? (
                        <div className="text-sm text-muted-foreground">目前沒有任務。</div>
                      ) : detail.tasks.map((task) => (
                        <div key={task.id} className="border p-3 text-sm">
                          <div className="flex flex-wrap gap-2 items-center">
                            <span className="font-medium">{task.title}</span>
                            <Badge variant={statusVariant(task.status)}>{humanizeTaskStatus(task.status)}</Badge>
                          </div>
                          <div className="mt-1 text-xs text-muted-foreground">
                            {summarizeTask(task)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="border p-4">
                    <div className="text-sm font-medium">最近活動</div>
                    <div className="mt-2 text-xs text-muted-foreground">只保留人話摘要，內部事件名稱放到第二層即可。</div>
                    <div className="mt-3 grid gap-2">
                      {detail.recent_events.length === 0 ? (
                        <div className="text-sm text-muted-foreground">目前沒有事件紀錄。</div>
                      ) : detail.recent_events.map((event) => (
                        <div key={event.id} className="border p-3 text-sm">
                          <div className="font-medium">{summarizeEvent(event)}</div>
                          <div className="mt-1 text-xs text-muted-foreground">{humanizeEventType(event.event_type)} · {timeAgo(event.created_at)}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function MetricCard({ title, value, note }: { title: string; value: string; note: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-semibold">{value}</div>
        <div className="mt-1 text-xs text-muted-foreground">{note}</div>
      </CardContent>
    </Card>
  );
}

function SummaryCard({ title, value, note, warning = false }: { title: string; value: string; note: string; warning?: boolean }) {
  return (
    <div className={`border p-4 ${warning ? "border-warning/40 bg-warning/5" : "border-border"}`}>
      <div className="text-xs text-muted-foreground">{title}</div>
      <div className="mt-1 text-sm font-medium leading-relaxed">{value}</div>
      <div className="mt-2 text-xs text-muted-foreground leading-relaxed">{note}</div>
    </div>
  );
}

function ApprovalSnippet({ approval }: { approval: ProjectApproval }) {
  return (
    <div className="border p-3 text-sm">
      <div className="flex flex-wrap items-center gap-2">
        <div className="font-medium">{approval.title}</div>
        <Badge variant={statusVariant(approval.status)}>{humanizeProjectStatus(approval.status)}</Badge>
      </div>
      <div className="mt-2 text-sm leading-relaxed">你現在要決定：{approval.summary ?? "等待你做決策"}</div>
      <div className="mt-2 text-xs text-muted-foreground">主要風險：{summarizeApprovalRisk(approval)}</div>
      <div className="mt-1 text-xs text-muted-foreground">系統建議：{summarizeApprovalRecommendation(approval)}</div>
    </div>
  );
}
