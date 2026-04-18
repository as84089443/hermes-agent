import { useEffect, useMemo, useState } from "react";
import { Check, ExternalLink, RefreshCw, RotateCcw, ShieldAlert } from "lucide-react";
import { api, type ProjectApproval } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Toast } from "@/components/Toast";
import { useToast } from "@/hooks/useToast";

function openProject(projectId?: string | null) {
  if (!projectId) return;
  window.localStorage.setItem("hermes:selected-project", projectId);
  window.dispatchEvent(new CustomEvent("hermes:navigate", { detail: { page: "projects" } }));
}

function badgeVariant(status: string): "success" | "warning" | "outline" {
  if (["approved", "done"].includes(status)) return "success";
  if (["pending", "changes_requested", "rejected"].includes(status)) return "warning";
  return "outline";
}

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<ProjectApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyApprovalId, setBusyApprovalId] = useState<string | null>(null);
  const [notes, setNotes] = useState<Record<string, string>>({});
  const { toast, showToast } = useToast();

  const load = async () => {
    try {
      const resp = await api.getApprovals("pending", 100);
      setApprovals(resp.approvals);
    } catch (error) {
      showToast(`載入審批失敗：${String(error)}`, "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const decide = async (approvalId: string, decision: "approved" | "changes_requested" | "rejected") => {
    setBusyApprovalId(approvalId);
    try {
      await api.decideApproval(approvalId, { decision, notes: notes[approvalId] || undefined });
      showToast("已記錄這次決策", "success");
      await load();
    } catch (error) {
      showToast(`送出決策失敗：${String(error)}`, "error");
    } finally {
      setBusyApprovalId(null);
    }
  };

  const priorityApproval = useMemo(() => approvals[0] ?? null, [approvals]);

  if (loading) {
    return <div className="flex items-center justify-center py-24"><div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" /></div>;
  }

  return (
    <div className="flex flex-col gap-6">
      {toast && <Toast toast={toast} />}

      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard title="待拍板關卡" value={`${approvals.length}`} note="今天最值得你先處理的決策佇列" />
        <MetricCard title="現在最該先批哪一件" value={priorityApproval ? priorityApproval.title : "目前沒有待批項目"} note={priorityApproval ? `已等待 ${timeAgo(priorityApproval.requested_at)}` : "系統可先自行往下推進"} />
        <MetricCard title="這頁的用途" value="快速拍板" note="看懂原因、判斷風險、按下核准或退回" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2"><RefreshCw className="h-4 w-4" />/approvals — 決策工作區</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4">
          {approvals.length === 0 ? (
            <div className="border p-4 text-sm text-muted-foreground">目前沒有 pending approval。當專案真的需要你拍板時，這裡會顯示每一張決策卡。</div>
          ) : approvals.map((approval) => {
            const busy = busyApprovalId === approval.id;
            return (
              <div key={approval.id} className="border p-4">
                <div className="flex flex-wrap items-center gap-2">
                  <div className="text-sm font-medium">{approval.title}</div>
                  <Badge variant={badgeVariant(approval.status)}>{approval.status}</Badge>
                  <Badge variant="outline">等待你拍板</Badge>
                </div>

                <div className="mt-3 grid gap-2 text-sm">
                  <DecisionLine title="你現在在決定什麼" value={approval.summary ?? "是否讓這個專案繼續往下推進。"} />
                  <DecisionLine title="為什麼輪到你決定" value="這一步會影響專案是否繼續往下走，所以系統先停在這裡等你拍板。" />
                  <DecisionLine title="核准後會發生什麼" value="系統會恢復推進，繼續執行下一步，不會停在待拍板狀態。" />
                  <DecisionLine title="退回後會發生什麼" value="專案會退回修改，不會假裝已放行，也不會繼續空轉。" />
                  <DecisionLine title="系統建議" value="如果你認為方向清楚、風險可接受，就直接核准並繼續；若資訊不足，優先退回修改。" accent />
                </div>

                <div className="mt-3 flex flex-wrap gap-3 text-xs text-muted-foreground">
                  <span>專案：{approval.project_id}</span>
                  <span>已等待：{timeAgo(approval.requested_at)}</span>
                </div>

                <textarea
                  className="mt-3 min-h-24 w-full border bg-background px-3 py-2 text-sm"
                  placeholder="可選：補充你核准、退回修改或駁回的原因，例如：請先補齊成功標準 / 可以直接進下一步 / 先不要做這條線。"
                  value={notes[approval.id] ?? ""}
                  onChange={(e) => setNotes((prev) => ({ ...prev, [approval.id]: e.target.value }))}
                />

                <div className="mt-3 flex flex-wrap gap-2">
                  <Button size="sm" disabled={busy} onClick={() => decide(approval.id, "approved")}>
                    <Check className="mr-1 h-3.5 w-3.5" /> 核准並繼續
                  </Button>
                  <Button size="sm" variant="outline" disabled={busy} onClick={() => decide(approval.id, "changes_requested")}>
                    <RotateCcw className="mr-1 h-3.5 w-3.5" /> 退回修改
                  </Button>
                  <Button size="sm" variant="outline" disabled={busy} onClick={() => decide(approval.id, "rejected")}>
                    <ShieldAlert className="mr-1 h-3.5 w-3.5" /> 駁回本案
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => openProject(approval.project_id)}>
                    <ExternalLink className="mr-1 h-3.5 w-3.5" /> 查看完整詳情
                  </Button>
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>
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

function DecisionLine({ title, value, accent = false }: { title: string; value: string; accent?: boolean }) {
  return (
    <div className={`border p-3 ${accent ? "border-warning/30 bg-warning/5" : ""}`}>
      <div className="text-xs text-muted-foreground">{title}</div>
      <div className="mt-1 leading-relaxed">{value}</div>
    </div>
  );
}
