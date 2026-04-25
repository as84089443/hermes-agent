import { useEffect, useState } from "react";
import {
  Activity,
  AlertCircle,
  Brain,
  CheckCircle2,
  Circle,
  Clock,
  FolderTree,
  GitBranch,
  History,
  Layers,
  LineChart,
  MessageSquare,
  Network,
  RefreshCw,
  Send,
  Timer,
  TrendingDown,
  TrendingUp,
  X,
  Zap,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

// -------- Types --------
interface ScoreSignal {
  // Backend returns breakdown as {name: [emoji, reason]}
  // but Python tuples serialize as arrays in JSON
  [key: string]: [string, string];
}

interface DualAgentStatus {
  data: {
    ts: string;
    openclaw: {
      gateway_state?: string;
      last_exit_code?: string;
      codex_app_server_running?: boolean;
      error?: string;
    };
    sync_bridge: {
      overall_ok?: boolean;
      checks?: Array<{ id: string; ok: boolean; detail: string }>;
      error?: string;
    };
    bus: {
      open_count?: number;
      status_counts?: Record<string, number>;
      events_7d?: Record<string, number>;
      keep_alive_7d?: number;
      amend_learning_7d?: number;
      error?: string;
    };
    evolution: {
      total_outbound_hermes_to_openclaw?: number;
      total_inbound_openclaw_to_hermes?: number;
      this_week_outbound?: number;
      this_week_inbound?: number;
      m2_symmetry_ok?: boolean;
      inbound_files?: string[];
      outbound_files?: string[];
    };
    hf: {
      total?: number;
      by_status?: Record<string, number>;
      oldest_pending_hours?: number;
      pending_files?: string[];
      health_ok?: boolean;
    };
    queue: {
      total?: number;
      fresh?: number;
      stale?: number;
      force_review?: number;
      pilot_at_risk?: number;
      terminal?: number;
    };
    coaching: {
      blanks_openclaw?: number;
      empty_chair_filled?: number;
    };
    ratelimit?: {
      total_ever?: number;
      last_7d?: number;
      last_24h?: number;
    };
    daily_review?: {
      hermes_last_reviewed?: string;
      latest_change_log_date?: string;
      today_done?: boolean;
    };
  };
  scorecard: {
    score: number;
    max: number;
    breakdown: ScoreSignal;
    trend: string;
    next_actions: string[];
  };
}

interface BusTask {
  task_id: string;
  status: string;
  from_agent: string;
  to_agent: string;
  goal: string;
  result: string;
  created_at: number;
  acked_at: number | null;
  completed_at: number | null;
}

interface HFCard {
  file: string;
  title: string;
  status: string;
  from_agent: string;
  to_agent: string;
  freshness_ts: string;
  mtime: number;
}

interface ActivityEvent {
  kind: string;
  title: string;
  subtitle?: string;
  path?: string;
  status?: string;
  agent?: string;
  ts: number;
  source: string;
}

interface Snapshot {
  file: string;
  ts: string;
  score: number | null;
}

interface ThrottleState {
  enforcement_enabled: boolean;
  pairs: Record<string, { allowed: boolean; reason: string | null; stats: Record<string, unknown> }>;
}

interface MiddlewareEntry {
  name: string;
  order: number;
  env_var: string | null;
  critical: boolean;
  enabled: boolean;
}

interface MiddlewareStatus {
  master_enabled: boolean;
  master_mode: string;
  entries: MiddlewareEntry[];
}

interface AutoMemoryFact {
  id: string;
  content: string;
  category: string;
  confidence: number;
  created_at: number;
  source: string;
}

interface AutoMemoryData {
  exists: boolean;
  path: string;
  count?: number;
  updated_at?: number;
  facts: AutoMemoryFact[];
  error?: string;
}

interface TraceSpan {
  name: string;
  hook: string;
  thread_id: string | null;
  agent: string | null;
  start_ts: number;
  end_ts: number;
  duration_ms: number;
}

interface TracesData {
  exists: boolean;
  path: string;
  total_lines?: number;
  spans: TraceSpan[];
  error?: string;
}

interface SandboxThread {
  thread_id: string;
  mtime: number;
  workspace_count: number;
  uploads_count: number;
  outputs_count: number;
}

interface SandboxesData {
  root: string;
  threads: SandboxThread[];
}

interface CodexStats {
  exists: boolean;
  window_hours?: number;
  total?: number;
  ok?: number;
  fail?: number;
  avg_ms?: number | null;
  p95_ms?: number | null;
  by_attempt?: Record<string, number>;
  by_error?: Record<string, number>;
  error?: string;
}

// -------- Translation maps --------
const SIGNAL_LABEL: Record<string, string> = {
  "OpenClaw liveness": "龍蝦在線狀態",
  "Sync bridge": "知識庫同步",
  "Bus close hygiene": "任務收尾乾淨度",
  "HF discipline": "交接卡紀律",
  "M2 symmetry": "雙向學習平衡",
  "Queue decay": "候選池新陳代謝",
};

const TASK_STATUS_LABEL: Record<string, string> = {
  pending: "待處理",
  ack: "已收到",
  progress: "處理中",
  "keep-alive": "還在跑",
  done: "完成",
  fail: "失敗",
  timeout: "超時",
};

const HF_STATUS_LABEL: Record<string, string> = {
  "pending-acceptance": "等對方回應",
  "pending-decision": "等對方裁決",
  accepted: "已接受",
  "accepted-closed": "已接受並收尾",
  "accepted-closed-by-seal": "已隨計劃封盤",
  rejected: "已拒絕",
  "clarification-requested": "等對方澄清",
  "draft-for-receiver-review": "等對方 review",
};

const KIND_LABEL: Record<string, string> = {
  evolution: "學習筆記",
  "bus-learning": "任務心得",
  memory: "記憶",
  ratelimit: "限流事件",
  "hf-card": "交接卡",
  "bus-event": "任務事件",
};

const HOOK_LABEL: Record<string, string> = {
  before_model: "AI 思考前",
  after_model: "AI 回應後",
  before_tool: "工具呼叫前",
  after_tool: "工具回傳後",
  on_session_end: "結束前清理",
};

const MIDDLEWARE_LABEL: Record<string, string> = {
  tracing: "計時追蹤",
  "thread-data": "工作區建立",
  "dangling-tool-call": "補回斷掉的工具回應",
  guardrail: "禁用工具守門",
  summarization: "長對話壓縮",
  "todo-list": "待辦清單追蹤",
  "memory-extraction": "對話抽事實",
  "loop-detection": "重複迴圈偵測",
};

const SYNC_CHECK_LABEL: Record<string, string> = {
  H1: "Hermes 端 wiki 存在",
  H2: "OpenClaw 端 wiki 存在",
  H3: "兩邊內容一致",
  H4: "排程同步有在跑",
};

const CATEGORY_LABEL: Record<string, string> = {
  preference: "偏好",
  goal: "目標",
  fact: "事實",
  context: "脈絡",
  habit: "習慣",
  identity: "身份",
  blocker: "阻礙",
  other: "其他",
};

const HF_DECISION_LABEL: Record<string, string> = {
  accept: "接受",
  reject: "拒絕",
  "request-clarification": "請對方澄清",
};

function localizeStatus(status: string): string {
  return TASK_STATUS_LABEL[status] || status;
}

function localizeHfStatus(status: string): string {
  return HF_STATUS_LABEL[status] || status;
}

function localizeKind(kind: string): string {
  return KIND_LABEL[kind] || kind;
}

function localizeMiddleware(name: string): string {
  return MIDDLEWARE_LABEL[name] || name;
}

function localizeHook(hook: string): string {
  return HOOK_LABEL[hook] || hook;
}

function localizeSyncCheck(id: string): string {
  return SYNC_CHECK_LABEL[id] || id;
}

function localizeCategory(cat: string): string {
  return CATEGORY_LABEL[cat] || cat;
}

// -------- Helpers --------
function statusBadgeVariant(status: string): "success" | "warning" | "destructive" | "outline" {
  if (status === "done") return "success";
  if (status === "fail" || status === "timeout") return "destructive";
  if (status === "ack" || status === "progress" || status === "keep-alive") return "warning";
  if (status === "pending") return "warning";
  return "outline";
}

function hfStatusBadge(status: string): "success" | "warning" | "destructive" | "outline" {
  if (status.startsWith("accepted")) return "success";
  if (status.includes("rejected")) return "destructive";
  if (status.includes("pending")) return "warning";
  return "outline";
}

function timeAgoShort(epoch: number): string {
  const sec = Date.now() / 1000 - epoch;
  if (sec < 60) return `${Math.round(sec)}s`;
  if (sec < 3600) return `${Math.round(sec / 60)}m`;
  if (sec < 86400) return `${Math.round(sec / 3600)}h`;
  return `${Math.round(sec / 86400)}d`;
}

// -------- Page --------
export default function AgentsPage() {
  const [status, setStatus] = useState<DualAgentStatus | null>(null);
  const [bus, setBus] = useState<BusTask[]>([]);
  const [hf, setHf] = useState<HFCard[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showDispatch, setShowDispatch] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [refreshNonce, setRefreshNonce] = useState(0);
  const [activity, setActivity] = useState<ActivityEvent[]>([]);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [throttle, setThrottle] = useState<ThrottleState | null>(null);
  const [middleware, setMiddleware] = useState<MiddlewareStatus | null>(null);
  const [autoMemory, setAutoMemory] = useState<AutoMemoryData | null>(null);
  const [traces, setTraces] = useState<TracesData | null>(null);
  const [sandboxes, setSandboxes] = useState<SandboxesData | null>(null);
  const [codexStats, setCodexStats] = useState<CodexStats | null>(null);
  const [showCoaching, setShowCoaching] = useState(false);

  function flashToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(null), 4000);
  }

  function refresh() {
    setRefreshNonce((n) => n + 1);
  }

  useEffect(() => {
    const load = async () => {
      try {
        const [s, b, h, a, sn, th, mw, am, tr, sx, cs] = await Promise.all([
          fetch("/api/dual-agent/status").then((r) => r.json()),
          fetch("/api/dual-agent/bus").then((r) => r.json()),
          fetch("/api/dual-agent/handoffs").then((r) => r.json()),
          fetch("/api/dual-agent/activity?hours=24").then((r) => r.json()),
          fetch("/api/dual-agent/snapshots").then((r) => r.json()),
          fetch("/api/dual-agent/throttle").then((r) => r.json()),
          fetch("/api/dual-agent/middleware").then((r) => r.json()),
          fetch("/api/dual-agent/auto-memory").then((r) => r.json()),
          fetch("/api/dual-agent/traces?limit=80").then((r) => r.json()),
          fetch("/api/dual-agent/sandboxes").then((r) => r.json()),
          fetch("/api/dual-agent/codex-stats?hours=24").then((r) => r.json()),
        ]);
        if (s.error) setErr(s.error);
        else setStatus(s as DualAgentStatus);
        setBus((b.tasks || []) as BusTask[]);
        setHf((h.cards || []) as HFCard[]);
        setActivity((a.events || []) as ActivityEvent[]);
        setSnapshots((sn.snapshots || []) as Snapshot[]);
        setThrottle(th as ThrottleState);
        setMiddleware(mw as MiddlewareStatus);
        setAutoMemory(am as AutoMemoryData);
        setTraces(tr as TracesData);
        setSandboxes(sx as SandboxesData);
        setCodexStats(cs as CodexStats);
        setLoading(false);
      } catch (e) {
        setErr(String(e));
        setLoading(false);
      }
    };
    load();
    const iv = setInterval(load, 30000);
    return () => clearInterval(iv);
  }, [refreshNonce]);

  async function closeBusTask(taskId: string, outcome: "done" | "fail" | "keep-alive") {
    const outcomeZh =
      outcome === "done" ? "完成" : outcome === "fail" ? "失敗" : "延長時限";
    const summary = prompt(
      `為任務 ${taskId} 標記「${outcomeZh}」— 請輸入一句說明：`,
      outcome === "keep-alive" ? "仍在進行中，延長截止時間" : ""
    );
    if (!summary || !summary.trim()) return;
    const res = await fetch(`/api/dual-agent/bus/${taskId}/close`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ outcome, summary }),
    });
    const j = await res.json();
    if (j.ok) {
      flashToast(`✅ ${taskId} → ${outcomeZh}`);
      refresh();
    } else {
      flashToast(`❌ ${j.error || "收尾失敗"}`);
    }
  }

  async function hfDecision(
    cardFile: string,
    decision: "accept" | "reject" | "request-clarification"
  ) {
    const decisionZh = HF_DECISION_LABEL[decision] || decision;
    const note = prompt(`為交接卡 ${cardFile} 加一句說明（可空）：`, "") ?? "";
    const res = await fetch(
      `/api/dual-agent/hf/${encodeURIComponent(cardFile)}/decision`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision, note: note.trim() || null }),
      }
    );
    const j = await res.json();
    if (j.ok) {
      flashToast(`✅ ${cardFile} → ${localizeHfStatus(j.new_status) || decisionZh}`);
      refresh();
    } else {
      flashToast(`❌ ${j.error || "處理失敗"}`);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (err) {
    return (
      <div className="mx-auto max-w-4xl p-6">
        <Card>
          <CardContent className="flex items-center gap-3 py-6">
            <AlertCircle className="h-5 w-5 text-destructive" />
            <div>
              <div className="font-medium">載入雙 Agent 狀態失敗</div>
              <div className="mt-1 text-sm text-muted-foreground">{err}</div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!status) return null;

  const d = status.data;
  const sc = status.scorecard;
  const busOpen = bus.filter((t) => !["done", "fail", "timeout"].includes(t.status));
  const busRecent = bus.filter((t) => ["done", "fail", "timeout"].includes(t.status)).slice(0, 5);
  const hfPending = hf.filter((c) => c.status.includes("pending"));
  const hfAccepted = hf.filter((c) => c.status.startsWith("accepted"));

  const trendIcon = sc.trend.includes("📈") ? (
    <TrendingUp className="h-4 w-4 text-green-500" />
  ) : sc.trend.includes("📉") ? (
    <TrendingDown className="h-4 w-4 text-red-500" />
  ) : (
    <Activity className="h-4 w-4 text-muted-foreground" />
  );

  return (
    <div className="mx-auto max-w-7xl space-y-6 p-6">
      {/* -------- Header -------- */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">雙 Agent 控制台</h1>
          <div className="mt-1 text-sm text-muted-foreground">
            Hermes（行政）× 龍蝦（技術）即時狀態 · 自動每 30 秒更新 ·{" "}
            <span className="font-mono">{d.ts}</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button onClick={() => setShowDispatch(true)} className="gap-2">
            <Send className="h-4 w-4" /> 派工給龍蝦
          </Button>
          <Button variant="outline" onClick={() => setShowCoaching(true)} className="gap-2">
            <MessageSquare className="h-4 w-4" /> 教練回饋
          </Button>
          <Button variant="outline" onClick={refresh} className="gap-2">
            <RefreshCw className="h-4 w-4" /> 重新整理
          </Button>
          <ScoreRing score={sc.score} max={sc.max} trend={sc.trend} trendIcon={trendIcon} />
        </div>
      </div>

      {/* -------- 6-signal strip (at-a-glance health) -------- */}
      <SignalStrip breakdown={sc.breakdown} />

      {/* -------- Toast -------- */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 rounded-md border border-border bg-card px-4 py-3 shadow-lg">
          {toast}
        </div>
      )}

      {/* -------- Dispatch modal -------- */}
      {showDispatch && (
        <DispatchModal
          onClose={() => setShowDispatch(false)}
          onDispatched={(tid) => {
            flashToast(`🚀 dispatched ${tid}`);
            setShowDispatch(false);
            refresh();
          }}
        />
      )}

      {/* -------- Coaching modal -------- */}
      {showCoaching && (
        <CoachingModal
          onClose={() => setShowCoaching(false)}
          onCommented={() => {
            flashToast("✅ comment posted");
            refresh();
          }}
        />
      )}

      {/* -------- Scorecard breakdown (visual tiles) -------- */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Activity className="h-4 w-4" /> 6 大訊號明細
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {Object.entries(sc.breakdown).map(([name, tuple]) => (
              <ScoreTile key={name} name={name} emoji={tuple[0]} reason={tuple[1]} />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* -------- §9 Throttle status -------- */}
      {throttle && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Zap className="h-4 w-4" /> 雙 Agent 對話節流（避免過度頻繁打 AI）
              {throttle.enforcement_enabled ? (
                <Badge variant="success">已啟用</Badge>
              ) : (
                <Badge variant="warning">關閉</Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 md:grid-cols-2">
              {Object.entries(throttle.pairs).map(([pair, info]) => {
                const labelMap: Record<string, string> = {
                  hermes_to_openclaw: "Hermes → 龍蝦",
                  openclaw_to_hermes: "龍蝦 → Hermes",
                };
                return (
                  <div key={pair} className="rounded-md border border-border/60 bg-card/50 p-3 text-sm">
                    <div className="flex items-center gap-2">
                      {info.allowed ? (
                        <Badge variant="success">可派工</Badge>
                      ) : (
                        <Badge variant="destructive">需等待</Badge>
                      )}
                      <span className="font-medium">{labelMap[pair] || pair}</span>
                    </div>
                    {info.reason && (
                      <div className="mt-1 text-xs text-muted-foreground">{info.reason}</div>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* -------- Snapshot history chart -------- */}
      {snapshots.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <LineChart className="h-4 w-4" /> 過去分數變化（最近 {Math.min(snapshots.length, 20)} 次紀錄）
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SnapshotSparkline snapshots={snapshots} />
          </CardContent>
        </Card>
      )}

      {/* -------- Middleware chain status -------- */}
      {middleware && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Layers className="h-4 w-4" /> 處理流水線（每次 AI 對話經過的 8 個關卡）
              {middleware.master_enabled ? (
                <Badge variant="success">啟用中</Badge>
              ) : (
                <Badge variant="warning">關閉</Badge>
              )}
              <span className="text-xs text-muted-foreground ml-2">
                {middleware.entries.filter((e) => e.enabled).length}/{middleware.entries.length} 啟用
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <MiddlewareFlow entries={middleware.entries} />
            <div className="mt-4 grid gap-2 md:grid-cols-2 lg:grid-cols-3">
              {middleware.entries.map((e) => (
                <div
                  key={e.name}
                  className="flex items-center gap-2 rounded-md border border-border/60 bg-card/50 p-2 text-sm"
                >
                  <span className="font-mono text-xs text-muted-foreground w-8">
                    #{e.order}
                  </span>
                  {e.enabled ? (
                    <Badge variant="success">啟用</Badge>
                  ) : (
                    <Badge variant="outline">關閉</Badge>
                  )}
                  <span className="flex-1 text-xs">{localizeMiddleware(e.name)}</span>
                  {e.critical && <Badge variant="destructive">嚴重</Badge>}
                </div>
              ))}
            </div>
            {middleware.entries.length === 0 && (
              <div className="text-sm text-muted-foreground">
                尚未註冊 middleware（core.complete_task 第一次被呼叫時會自動 register_defaults）
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* -------- Auto-memory facts (S4) -------- */}
      {autoMemory && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Brain className="h-4 w-4" /> 自動記下的事實（從你的對話抽出來）
              {autoMemory.exists ? (
                <Badge variant="success">{autoMemory.count || 0} 件</Badge>
              ) : (
                <Badge variant="outline">尚未產生</Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {autoMemory.error ? (
              <div className="text-sm text-destructive">{autoMemory.error}</div>
            ) : autoMemory.facts.length === 0 ? (
              <div className="text-sm text-muted-foreground">
                還沒抽出任何事實。每當有 bus 任務完成、AI 會在 30 秒後從對話內容自動萃取
                關於你的事實（偏好、習慣、背景），存到 <span className="font-mono text-xs">{autoMemory.path}</span>。
              </div>
            ) : (
              <div className="space-y-1 max-h-72 overflow-y-auto">
                {autoMemory.facts.map((f) => {
                  return (
                    <div
                      key={f.id}
                      className="flex items-start gap-2 rounded border border-border/60 bg-card/50 p-2 text-sm"
                    >
                      <Badge variant="outline" className="mt-0.5">{localizeCategory(f.category)}</Badge>
                      <div className="min-w-0 flex-1">
                        <div>{f.content}</div>
                        <div className="mt-0.5 text-xs text-muted-foreground">
                          可信度 {(f.confidence * 100).toFixed(0)}% · 來源 {f.source}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* -------- Codex CLI stats -------- */}
      {codexStats && codexStats.exists && (codexStats.total || 0) > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Zap className="h-4 w-4" /> AI 模型呼叫統計（最近 24 小時）
              <Badge variant={(codexStats.fail || 0) === 0 ? "success" : "warning"}>
                {codexStats.ok}/{codexStats.total} 成功
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-6 text-sm">
              <div>
                <div className="text-xs text-muted-foreground">總呼叫</div>
                <div className="text-2xl font-bold">{codexStats.total}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">平均耗時</div>
                <div className="text-2xl font-bold">
                  {codexStats.avg_ms != null
                    ? `${(codexStats.avg_ms / 1000).toFixed(1)}秒`
                    : "—"}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">95% 內</div>
                <div className="text-2xl font-bold">
                  {codexStats.p95_ms != null
                    ? `${(codexStats.p95_ms / 1000).toFixed(1)}秒`
                    : "—"}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">失敗</div>
                <div className="text-2xl font-bold">{codexStats.fail}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">費用</div>
                <div className="text-2xl font-bold text-green-500">$0</div>
                <div className="text-xs text-muted-foreground">（用你訂閱的 codex）</div>
              </div>
            </div>
            <div className="mt-3 grid gap-2 md:grid-cols-2">
              <div>
                <div className="text-xs text-muted-foreground mb-1">用途分類</div>
                <div className="space-y-1 text-xs">
                  {Object.entries(codexStats.by_attempt || {}).map(([k, v]) => {
                    const labelMap: Record<string, string> = {
                      "memory-extract": "抽事實",
                      "dashboard-smoke-test": "面板測試",
                      "subagent:general-purpose": "子代理（通用）",
                      "subagent:bash": "子代理（指令）",
                    };
                    return (
                      <div key={k} className="flex justify-between">
                        <span>{labelMap[k] || k}</span>
                        <span className="font-mono">{v}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
              {Object.keys(codexStats.by_error || {}).length > 0 && (
                <div>
                  <div className="text-xs text-muted-foreground mb-1">錯誤類型</div>
                  <div className="space-y-1 text-xs">
                    {Object.entries(codexStats.by_error || {}).map(([k, v]) => {
                      const errMap: Record<string, string> = {
                        throttled: "被節流擋下",
                        timeout: "逾時",
                        not_found: "找不到 codex",
                        non_zero: "非零退出碼",
                        disabled: "已停用",
                      };
                      return (
                        <div key={k} className="flex justify-between text-destructive/80">
                          <span>{errMap[k] || k}</span>
                          <span className="font-mono">{v}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* -------- Trace spans timeline (S10) -------- */}
      {traces && traces.exists && traces.spans.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Timer className="h-4 w-4" /> 動作耗時追蹤（每次 AI 處理過了哪幾關、各花多久）
              <span className="text-xs text-muted-foreground ml-2">
                最近 {traces.spans.length} 筆 / 累計 {traces.total_lines}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TraceTimeline spans={traces.spans} />
          </CardContent>
        </Card>
      )}

      {/* -------- Sandboxes (S7) -------- */}
      {sandboxes && sandboxes.threads.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <FolderTree className="h-4 w-4" /> 各任務工作區（每個任務有自己的暫存資料夾）
              <span className="text-xs text-muted-foreground ml-2">
                目前 {sandboxes.threads.length} 個 ·{" "}
                <span className="font-mono">{sandboxes.root}</span>
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
              {sandboxes.threads.slice(0, 12).map((t) => (
                <div
                  key={t.thread_id}
                  className="rounded-md border border-border/60 bg-card/50 p-2 text-sm"
                >
                  <div className="font-mono text-xs truncate" title={t.thread_id}>
                    {t.thread_id}
                  </div>
                  <div className="mt-1 flex gap-3 text-xs text-muted-foreground">
                    <span>工作區: {t.workspace_count}</span>
                    <span>上傳: {t.uploads_count}</span>
                    <span>輸出: {t.outputs_count}</span>
                  </div>
                </div>
              ))}
            </div>
            {sandboxes.threads.length > 12 && (
              <div className="mt-2 text-xs text-muted-foreground text-right">
                …還有 {sandboxes.threads.length - 12} 個
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* -------- Recent activity feed -------- */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <History className="h-4 w-4" /> 最近 24h 活動 ({activity.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {activity.length === 0 ? (
            <div className="text-sm text-muted-foreground">無活動</div>
          ) : (
            <div className="space-y-1.5 max-h-96 overflow-y-auto">
              {activity.map((e, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <Badge variant="outline" className="mt-0.5 shrink-0">{localizeKind(e.kind)}</Badge>
                  <div className="min-w-0 flex-1">
                    <div className="truncate">{e.title}</div>
                    {e.subtitle && (
                      <div className="truncate text-xs text-muted-foreground">{e.subtitle}</div>
                    )}
                  </div>
                  <span className="shrink-0 text-xs text-muted-foreground">
                    {timeAgoShort(e.ts)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* -------- Two agents side-by-side -------- */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* -------- Hermes -------- */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <span>🧭</span> Hermes（行政合夥人）
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm">
              <div className="text-muted-foreground">最近一次每日盤點</div>
              <div className="font-mono">
                {d.daily_review?.hermes_last_reviewed || "—"}
                {d.daily_review?.today_done && <Badge variant="success" className="ml-2">今天已跑</Badge>}
              </div>
            </div>
            <div className="text-sm">
              <div className="text-muted-foreground">寫給龍蝦的學習筆記</div>
              <div>
                總計 <span className="font-mono">{d.evolution.total_outbound_hermes_to_openclaw}</span> 篇
                {" · "}本週 <span className="font-mono">{d.evolution.this_week_outbound}</span> 篇
              </div>
            </div>
            <div className="text-sm">
              <div className="text-muted-foreground">教練回饋（替龍蝦想答案）</div>
              <div>
                已預測 <span className="font-mono">{d.coaching.empty_chair_filled}</span> 段對話
              </div>
            </div>
          </CardContent>
        </Card>

        {/* -------- OpenClaw -------- */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <span>🦞</span> OpenClaw（技術合夥人 · 龍蝦）
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm">
              <div className="text-muted-foreground">守門員（Gateway）狀態</div>
              <div>
                {d.openclaw.gateway_state === "running" ? (
                  <Badge variant="success">運行中</Badge>
                ) : (
                  <Badge variant="destructive">{d.openclaw.gateway_state === "down" ? "已停止" : (d.openclaw.gateway_state || "未知")}</Badge>
                )}
                {" "}
                {d.openclaw.codex_app_server_running ? (
                  <Badge variant="success" className="ml-1">Codex 就緒</Badge>
                ) : (
                  <Badge variant="warning" className="ml-1">Codex 未啟動</Badge>
                )}
              </div>
            </div>
            <div className="text-sm">
              <div className="text-muted-foreground">龍蝦寫回給 Hermes 的筆記</div>
              <div>
                總計 <span className="font-mono">{d.evolution.total_inbound_openclaw_to_hermes}</span> 篇
                {" · "}本週 <span className="font-mono">{d.evolution.this_week_inbound}</span> 篇
                {!d.evolution.m2_symmetry_ok && (
                  <Badge variant="destructive" className="ml-2">雙向學習失衡</Badge>
                )}
              </div>
            </div>
            <div className="text-sm">
              <div className="text-muted-foreground">教練回饋待回填</div>
              <div>
                {d.coaching.blanks_openclaw}{" "}
                {d.coaching.blanks_openclaw && d.coaching.blanks_openclaw > 0 ? (
                  <Badge variant="warning">待龍蝦回填</Badge>
                ) : (
                  <Badge variant="success">已完成</Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* -------- Bus tasks -------- */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Network className="h-4 w-4" /> Agent Bus（se-013 finalizer gate）
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <BusPipeline tasks={bus} />
          {busOpen.length > 0 && (
            <div>
              <div className="mb-2 text-sm font-medium">進行中的任務 ({busOpen.length})</div>
              <div className="space-y-2">
                {busOpen.map((t) => (
                  <div
                    key={t.task_id}
                    className="flex items-start gap-3 rounded-md border border-border/60 bg-card/50 p-3"
                  >
                    <Badge variant={statusBadgeVariant(t.status)}>{localizeStatus(t.status)}</Badge>
                    <div className="min-w-0 flex-1">
                      <div className="text-sm">
                        <span className="font-mono text-xs text-muted-foreground">
                          {t.task_id}
                        </span>
                        {" · "}
                        <span>{t.from_agent} → {t.to_agent}</span>
                        {" · "}
                        <span className="text-xs text-muted-foreground">
                          {timeAgoShort(t.created_at)} 前派出
                        </span>
                      </div>
                      <div className="mt-1 text-sm text-foreground/80">{t.goal}</div>
                      <div className="mt-2 flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => closeBusTask(t.task_id, "done")}
                        >
                          標記完成
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => closeBusTask(t.task_id, "fail")}
                        >
                          標記失敗
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => closeBusTask(t.task_id, "keep-alive")}
                        >
                          延長時限
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {busOpen.length === 0 && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              目前沒有未結案任務（收尾守門員顯示乾淨）
            </div>
          )}

          <div>
            <div className="mb-2 text-sm font-medium">最近結案的任務 ({busRecent.length})</div>
            <div className="space-y-1">
              {busRecent.map((t) => (
                <div key={t.task_id} className="flex items-center gap-3 text-sm">
                  <Badge variant={statusBadgeVariant(t.status)}>{localizeStatus(t.status)}</Badge>
                  <span className="font-mono text-xs text-muted-foreground">{t.task_id}</span>
                  <span className="truncate text-foreground/70">{t.goal}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="grid gap-2 border-t border-border/50 pt-3 text-xs text-muted-foreground md:grid-cols-3">
            <div>近 7 天事件分布: <span className="font-mono">{JSON.stringify(d.bus.events_7d)}</span></div>
            <div>近 7 天延長時限次數: <span className="font-mono">{d.bus.keep_alive_7d ?? 0}</span></div>
            <div>近 7 天補學習筆記次數: <span className="font-mono">{d.bus.amend_learning_7d ?? 0}</span></div>
          </div>
        </CardContent>
      </Card>

      {/* -------- HF cards -------- */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <GitBranch className="h-4 w-4" /> 交接卡（雙方互相派工的紀錄）
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {hfPending.length > 0 && (
            <div>
              <div className="mb-2 text-sm font-medium">等回應中 ({hfPending.length} 張)</div>
              <div className="space-y-2">
                {hfPending.map((c) => (
                  <div
                    key={c.file}
                    className="flex items-start gap-3 rounded-md border border-border/60 bg-card/50 p-3"
                  >
                    <Badge variant={hfStatusBadge(c.status)}>{localizeHfStatus(c.status)}</Badge>
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-medium">{c.title}</div>
                      <div className="mt-0.5 text-xs text-muted-foreground">
                        {c.from_agent} → {c.to_agent} · 更新時間 {c.freshness_ts || "—"}
                      </div>
                      <div className="mt-0.5 text-xs text-muted-foreground font-mono">{c.file}</div>
                      <div className="mt-2 flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => hfDecision(c.file, "accept")}
                        >
                          接受
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => hfDecision(c.file, "reject")}
                        >
                          拒絕
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => hfDecision(c.file, "request-clarification")}
                        >
                          請對方澄清
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div>
            <div className="mb-2 text-sm font-medium">
              已收尾 ({hfAccepted.length} 張)
            </div>
            <div className="space-y-1 text-xs text-muted-foreground">
              {hfAccepted.slice(0, 5).map((c) => (
                <div key={c.file} className="flex items-center gap-2">
                  <Badge variant="outline">{localizeHfStatus(c.status)}</Badge>
                  <span className="truncate">{c.title}</span>
                </div>
              ))}
              {hfAccepted.length > 5 && (
                <div className="italic">... 還有 {hfAccepted.length - 5} 張</div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* -------- Next actions -------- */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <MessageSquare className="h-4 w-4" /> 建議下一步
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            {sc.next_actions.map((a, i) => (
              <li key={i} className="flex items-start gap-2">
                <Circle className="mt-0.5 h-3 w-3 flex-shrink-0 fill-primary/40 text-primary" />
                <span>{a}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* -------- Sync bridge detail -------- */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Clock className="h-4 w-4" /> 知識庫同步檢查（讓兩邊看到同樣的 wiki）
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-sm">
          {d.sync_bridge.checks?.map((c) => (
            <div key={c.id} className="flex items-center gap-2">
              {c.ok ? (
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              ) : (
                <AlertCircle className="h-4 w-4 text-destructive" />
              )}
              <span className="font-mono text-xs">{localizeSyncCheck(c.id)}</span>
              <span className="text-xs text-muted-foreground">{c.detail}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

// -------- ScoreRing --------
function ScoreRing({
  score,
  max,
  trend,
  trendIcon,
}: {
  score: number;
  max: number;
  trend: string;
  trendIcon: React.ReactNode;
}) {
  const r = 36;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(1, score / max));
  const dash = c * pct;
  // Color by score band: 0-4 red, 5-7 amber, 8+ emerald
  const stroke =
    score >= 8 ? "#22c55e" : score >= 5 ? "#eab308" : "#ef4444";

  return (
    <div className="flex items-center gap-3">
      <svg width="96" height="96" viewBox="0 0 96 96">
        <circle
          cx="48"
          cy="48"
          r={r}
          fill="none"
          stroke="currentColor"
          strokeOpacity="0.12"
          strokeWidth="8"
        />
        <circle
          cx="48"
          cy="48"
          r={r}
          fill="none"
          stroke={stroke}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={`${dash} ${c - dash}`}
          transform="rotate(-90 48 48)"
          className="transition-all duration-500"
        />
        <text
          x="48"
          y="50"
          textAnchor="middle"
          dominantBaseline="central"
          className="font-bold"
          fontSize="24"
          fill="currentColor"
        >
          {score}
        </text>
        <text
          x="48"
          y="68"
          textAnchor="middle"
          fontSize="9"
          fill="currentColor"
          fillOpacity="0.5"
        >
          / {max}
        </text>
      </svg>
      <div className="text-right max-w-[12rem]">
        <div className="flex items-center justify-end gap-1 text-xs text-muted-foreground">
          {trendIcon}
        </div>
        <div className="mt-1 text-xs text-muted-foreground line-clamp-2">
          {trend}
        </div>
      </div>
    </div>
  );
}

// -------- SignalStrip --------
function SignalStrip({ breakdown }: { breakdown: Record<string, [string, string]> }) {
  const COLORS: Record<string, string> = {
    "🟢": "#22c55e",
    "🟡": "#eab308",
    "🔴": "#ef4444",
  };
  return (
    <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
      {Object.entries(breakdown).map(([name, tuple]) => {
        const [emoji, reason] = tuple;
        const color = COLORS[emoji] || "#737373";
        const label = SIGNAL_LABEL[name] || name;
        return (
          <div
            key={name}
            className="rounded-md border border-border/60 bg-card/50 p-2"
            title={`${label}\n${reason}`}
          >
            <div
              className="h-1 rounded-full mb-1.5"
              style={{ backgroundColor: color }}
            />
            <div className="text-[0.7rem] font-medium truncate">{label}</div>
            <div className="text-[0.65rem] text-muted-foreground truncate">
              {reason}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// -------- ScoreTile (for breakdown grid) --------
function ScoreTile({
  name,
  emoji,
  reason,
}: {
  name: string;
  emoji: string;
  reason: string;
}) {
  const tone =
    emoji === "🟢"
      ? "border-green-500/40 bg-green-500/5"
      : emoji === "🟡"
      ? "border-yellow-500/40 bg-yellow-500/5"
      : emoji === "🔴"
      ? "border-red-500/40 bg-red-500/5"
      : "border-border/60 bg-card/50";
  const label = SIGNAL_LABEL[name] || name;
  return (
    <div
      className={`flex items-start gap-3 rounded-md border p-3 transition-colors ${tone}`}
    >
      <div className="text-2xl">{emoji}</div>
      <div className="min-w-0 flex-1">
        <div className="text-sm font-medium">{label}</div>
        <div className="mt-0.5 text-xs text-muted-foreground">{reason}</div>
      </div>
    </div>
  );
}

// -------- MiddlewareFlow (horizontal pipeline diagram) --------
function MiddlewareFlow({ entries }: { entries: MiddlewareEntry[] }) {
  if (entries.length === 0) return null;
  const sorted = [...entries].sort((a, b) => a.order - b.order);
  return (
    <div className="overflow-x-auto -mx-2 px-2 pb-1">
      <div className="flex items-center gap-1 min-w-max">
        {sorted.map((e, i) => {
          const fill = e.enabled
            ? e.critical
              ? "bg-red-500/20 border-red-500/60 text-red-500"
              : "bg-green-500/15 border-green-500/50 text-green-600"
            : "bg-muted/40 border-border/60 text-muted-foreground line-through";
          const label = localizeMiddleware(e.name);
          return (
            <div key={e.name} className="flex items-center">
              <div
                className={`relative rounded-md border ${fill} px-2.5 py-1.5 text-xs whitespace-nowrap`}
                title={`順序 ${e.order} · 開關 ${e.env_var || "(無)"} · ${
                  e.enabled ? "啟用中" : "關閉"
                }`}
              >
                <span className="absolute -top-1.5 left-1.5 px-1 text-[0.6rem] bg-background border border-border/60 rounded font-mono">
                  {e.order}
                </span>
                <span>{label}</span>
              </div>
              {i < sorted.length - 1 && (
                <span className="text-muted-foreground/40 px-1">→</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// -------- BusPipeline (lifecycle stages with counts) --------
function BusPipeline({ tasks }: { tasks: BusTask[] }) {
  const STAGES: Array<{ id: string; label: string; statuses: string[] }> = [
    { id: "pending", label: "pending", statuses: ["pending"] },
    { id: "ack", label: "ack", statuses: ["ack"] },
    { id: "progress", label: "progress / keep-alive", statuses: ["progress", "keep-alive"] },
    { id: "done", label: "done", statuses: ["done"] },
    { id: "fail", label: "fail / timeout", statuses: ["fail", "timeout"] },
  ];
  const counts = STAGES.map((s) => ({
    ...s,
    count: tasks.filter((t) => s.statuses.includes(t.status)).length,
  }));
  const max = Math.max(...counts.map((c) => c.count), 1);

  return (
    <div className="rounded-md border border-border/60 bg-card/30 p-3">
      <div className="text-xs text-muted-foreground mb-2">Lifecycle pipeline (recent 30)</div>
      <div className="flex items-stretch gap-2">
        {counts.map((s, i) => {
          const intensity = (s.count / max) * 0.8 + 0.2;
          const fill =
            s.id === "done"
              ? `rgba(34, 197, 94, ${intensity})`
              : s.id === "fail"
              ? `rgba(239, 68, 68, ${intensity})`
              : s.id === "progress"
              ? `rgba(59, 130, 246, ${intensity})`
              : s.id === "ack"
              ? `rgba(234, 179, 8, ${intensity})`
              : `rgba(115, 115, 115, ${intensity})`;
          return (
            <div key={s.id} className="flex items-center flex-1">
              <div className="flex-1 rounded-md border border-border/60 px-3 py-2 text-center">
                <div
                  className="rounded text-white font-bold py-2 text-lg"
                  style={{ backgroundColor: fill }}
                >
                  {s.count}
                </div>
                <div className="mt-1 text-[0.7rem] text-muted-foreground font-mono">
                  {s.label}
                </div>
              </div>
              {i < counts.length - 1 && (
                <span className="text-muted-foreground/40 px-1">→</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// -------- Trace Timeline --------
function TraceTimeline({ spans }: { spans: TraceSpan[] }) {
  if (spans.length === 0) return null;

  const HOOK_COLORS: Record<string, string> = {
    before_model: "#3b82f6",
    after_model: "#8b5cf6",
    before_tool: "#f59e0b",
    after_tool: "#10b981",
    on_session_end: "#ef4444",
  };

  const byHook: Record<string, { count: number; total_ms: number; max_ms: number }> = {};
  for (const s of spans) {
    const h = s.hook || "?";
    if (!byHook[h]) byHook[h] = { count: 0, total_ms: 0, max_ms: 0 };
    byHook[h].count += 1;
    byHook[h].total_ms += s.duration_ms;
    byHook[h].max_ms = Math.max(byHook[h].max_ms, s.duration_ms);
  }

  const overallMax = Math.max(...spans.map((s) => s.duration_ms), 1);
  const totalCalls = spans.length;
  const totalTime = spans.reduce((acc, s) => acc + s.duration_ms, 0);

  return (
    <div className="space-y-4">
      {/* Distribution bar — what % of time each hook took */}
      <div>
        <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
          <span>各階段佔用時間分布（{totalCalls} 次呼叫，總計 {totalTime.toFixed(1)} 毫秒）</span>
        </div>
        <div className="flex h-6 rounded overflow-hidden border border-border/40">
          {Object.entries(byHook).map(([hook, stats]) => {
            const pct = (stats.total_ms / Math.max(totalTime, 0.01)) * 100;
            const color = HOOK_COLORS[hook] || "#737373";
            if (pct < 1) return null;
            return (
              <div
                key={hook}
                style={{ width: `${pct}%`, backgroundColor: color }}
                className="flex items-center justify-center text-[0.65rem] text-white font-mono"
                title={`${localizeHook(hook)}: ${stats.total_ms.toFixed(2)}ms (${pct.toFixed(1)}%)`}
              >
                {pct > 5 ? localizeHook(hook) : ""}
              </div>
            );
          })}
        </div>
        <div className="mt-1 flex flex-wrap gap-2 text-[0.65rem]">
          {Object.entries(byHook).map(([hook, stats]) => (
            <div key={hook} className="flex items-center gap-1">
              <span
                className="inline-block w-2 h-2 rounded-sm"
                style={{ backgroundColor: HOOK_COLORS[hook] || "#737373" }}
              />
              <span>{localizeHook(hook)}</span>
              <span className="text-muted-foreground">
                {stats.count} 次 · 平均 {(stats.total_ms / stats.count).toFixed(1)} 毫秒
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent 20 spans as colored bars */}
      <div className="space-y-1">
        <div className="text-xs text-muted-foreground mb-1">最近 20 次動作</div>
        {spans.slice(-20).reverse().map((s, i) => {
          const pct = Math.min(100, (s.duration_ms / overallMax) * 100);
          const color = HOOK_COLORS[s.hook] || "#737373";
          return (
            <div key={i} className="flex items-center gap-2 text-xs">
              <span className="w-28 shrink-0 text-muted-foreground truncate">
                {localizeHook(s.hook)}
              </span>
              <div className="flex-1 relative h-5 rounded bg-background/50 border border-border/40">
                <div
                  className="absolute left-0 top-0 h-full rounded-l opacity-70 transition-all"
                  style={{ width: `${pct}%`, backgroundColor: color }}
                />
                <div className="absolute inset-0 flex items-center px-2 text-[0.7rem] font-mono">
                  {s.duration_ms.toFixed(2)}ms
                </div>
              </div>
              <span
                className="w-28 shrink-0 truncate font-mono text-muted-foreground"
                title={s.thread_id || ""}
              >
                {s.thread_id ? s.thread_id.slice(0, 16) : "-"}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}


// -------- Snapshot Sparkline --------
function SnapshotSparkline({ snapshots }: { snapshots: Snapshot[] }) {
  const dataPoints = [...snapshots].reverse().filter((s) => s.score !== null) as Array<
    Snapshot & { score: number }
  >;
  if (dataPoints.length < 2) {
    return <div className="text-sm text-muted-foreground">需要至少 2 份快照才能畫趨勢</div>;
  }
  const padL = 28;
  const padR = 12;
  const padT = 10;
  const padB = 22;
  const innerW = 600;
  const innerH = 100;
  const width = innerW + padL + padR;
  const height = innerH + padT + padB;
  const max = 10;
  const min = 0;
  const dx = innerW / (dataPoints.length - 1);
  const yFor = (s: number) =>
    padT + innerH - ((s - min) / (max - min)) * innerH;
  const xFor = (i: number) => padL + i * dx;
  const points = dataPoints.map((p, i) => `${xFor(i)},${yFor(p.score)}`);
  const path = "M " + points.join(" L ");
  const areaPath =
    `M ${xFor(0)},${padT + innerH} L ` +
    points.join(" L ") +
    ` L ${xFor(dataPoints.length - 1)},${padT + innerH} Z`;

  const gridLines = [0, 5, 10];
  return (
    <div className="w-full">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-32">
        {/* horizontal gridlines + y-axis labels */}
        {gridLines.map((g) => (
          <g key={g}>
            <line
              x1={padL}
              y1={yFor(g)}
              x2={padL + innerW}
              y2={yFor(g)}
              stroke="currentColor"
              strokeOpacity="0.12"
              strokeDasharray={g === 5 ? "3 3" : ""}
            />
            <text
              x={padL - 4}
              y={yFor(g) + 3}
              textAnchor="end"
              fontSize="9"
              fill="currentColor"
              fillOpacity="0.5"
            >
              {g}
            </text>
          </g>
        ))}
        {/* area fill */}
        <path d={areaPath} fill="currentColor" fillOpacity="0.08" />
        {/* line */}
        <path
          d={path}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
        />
        {/* points colored by score band */}
        {dataPoints.map((p, i) => {
          const fill = p.score >= 8 ? "#22c55e" : p.score >= 5 ? "#eab308" : "#ef4444";
          return (
            <circle key={i} cx={xFor(i)} cy={yFor(p.score)} r="3.5" fill={fill}>
              <title>{`${p.ts}: ${p.score}/10`}</title>
            </circle>
          );
        })}
        {/* x-axis baseline */}
        <line
          x1={padL}
          y1={padT + innerH + 1}
          x2={padL + innerW}
          y2={padT + innerH + 1}
          stroke="currentColor"
          strokeOpacity="0.3"
        />
        <text
          x={padL}
          y={padT + innerH + 14}
          fontSize="9"
          fill="currentColor"
          fillOpacity="0.5"
        >
          oldest
        </text>
        <text
          x={padL + innerW}
          y={padT + innerH + 14}
          textAnchor="end"
          fontSize="9"
          fill="currentColor"
          fillOpacity="0.5"
        >
          latest
        </text>
      </svg>
      <div className="mt-1 flex justify-between text-xs text-muted-foreground font-mono">
        <span>最舊 {dataPoints[0].score}/10</span>
        <span>{dataPoints.length} snapshots</span>
        <span>最新 {dataPoints[dataPoints.length - 1].score}/10</span>
      </div>
    </div>
  );
}

// -------- Coaching Modal --------
function CoachingModal({
  onClose,
  onCommented,
}: {
  onClose: () => void;
  onCommented: () => void;
}) {
  const [data, setData] = useState<{
    markdown: string;
    blanks: number;
    prompts: string[];
    mtime: number;
  } | null>(null);
  const [comment, setComment] = useState("");
  const [section, setSection] = useState("General");
  const [actor, setActor] = useState("brian");
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/dual-agent/coaching")
      .then((r) => r.json())
      .then((d) => {
        if (d.error) setErr(d.error);
        else setData(d);
      });
  }, []);

  async function submit() {
    if (!comment.trim()) {
      setErr("comment 不能空");
      return;
    }
    setSubmitting(true);
    setErr(null);
    try {
      const res = await fetch("/api/dual-agent/coaching/comment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ actor, section, comment: comment.trim() }),
      });
      const j = await res.json();
      if (j.ok) {
        onCommented();
        setComment("");
      } else {
        setErr(j.error || "送出失敗");
      }
    } catch (e) {
      setErr(String(e));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-3xl max-h-[90vh] flex flex-col rounded-lg border border-border bg-card shadow-xl">
        <div className="flex items-center justify-between border-b border-border px-5 py-3">
          <h2 className="text-lg font-semibold">
            教練回饋（針對龍蝦）
            {data && data.blanks > 0 && (
              <Badge variant="warning" className="ml-2">
                {data.blanks} 段待回填
              </Badge>
            )}
          </h2>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4">
          {err && (
            <div className="mb-3 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {err}
            </div>
          )}
          {data ? (
            <>
              <div className="mb-4">
                <div className="mb-1 text-xs text-muted-foreground">提問點 ({data.prompts.length} 個)</div>
                <div className="flex flex-wrap gap-1">
                  {data.prompts.map((p, i) => (
                    <Badge
                      key={i}
                      variant="outline"
                      className="cursor-pointer"
                      onClick={() => {
                        const match = p.match(/Q\d+\.\d+/);
                        if (match) setSection(match[0]);
                      }}
                    >
                      {p.length > 30 ? p.slice(0, 30) + "…" : p}
                    </Badge>
                  ))}
                </div>
              </div>
              <pre className="whitespace-pre-wrap text-xs font-mono leading-relaxed bg-background/50 p-3 rounded border border-border/60 max-h-96 overflow-y-auto">
                {data.markdown.slice(0, 8000)}
                {data.markdown.length > 8000 && "\n\n...（內容過長，完整版存在 wiki 檔案）"}
              </pre>
            </>
          ) : (
            <div className="text-sm text-muted-foreground">載入中…</div>
          )}
        </div>

        <div className="border-t border-border px-5 py-3 space-y-2">
          <div className="text-sm font-medium">快速留言</div>
          <div className="grid grid-cols-2 gap-2">
            <select
              value={actor}
              onChange={(e) => setActor(e.target.value)}
              className="rounded-md border border-input bg-background px-3 py-1.5 text-sm"
            >
              <option value="brian">Brian（你）</option>
              <option value="hermes">Hermes</option>
              <option value="openclaw">龍蝦</option>
            </select>
            <input
              type="text"
              value={section}
              onChange={(e) => setSection(e.target.value)}
              placeholder="哪個段落（例 Q2.1）"
              className="rounded-md border border-input bg-background px-3 py-1.5 text-sm"
            />
          </div>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="一句話回應 / 指令 / 修正…"
            rows={2}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          />
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose} disabled={submitting}>
              關閉
            </Button>
            <Button onClick={submit} disabled={submitting || !comment.trim()}>
              {submitting ? "送出中…" : "加進這個 session"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

// -------- Dispatch Modal --------
function DispatchModal({
  onClose,
  onDispatched,
}: {
  onClose: () => void;
  onDispatched: (taskId: string) => void;
}) {
  const [goal, setGoal] = useState("");
  const [context, setContext] = useState("");
  const [criteria, setCriteria] = useState("");
  const [priority, setPriority] = useState("P2");
  const [deadline, setDeadline] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function submit(force: boolean = false) {
    if (!goal.trim()) {
      setErr("「要做什麼」不能空");
      return;
    }
    setSubmitting(true);
    setErr(null);
    const body = {
      from_agent: "hermes",
      to_agent: "openclaw",
      goal: goal.trim(),
      context: context.trim() || undefined,
      success_criteria: criteria.trim() || undefined,
      priority,
      deadline_minutes: deadline ? parseInt(deadline, 10) : undefined,
    };
    try {
      const url = force
        ? "/api/dual-agent/bus/dispatch?force=true"
        : "/api/dual-agent/bus/dispatch";
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const j = await res.json();
      if (j.ok) {
        onDispatched(j.task_id);
      } else {
        // Better error formatting — if throttled or guardrail-denied, be explicit
        let msg = j.error || "派工失敗";
        if (j.throttled) {
          msg = `⏱️ 被節流擋下：${j.error}`;
        } else if (typeof j.error === "string" && j.error.includes("GUARDRAIL_DENY")) {
          msg = `🛡️ 守門員拒絕：${j.error.replace("GUARDRAIL_DENY: ", "")}`;
        }
        setErr(msg);
      }
    } catch (e) {
      setErr(String(e));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-2xl rounded-lg border border-border bg-card shadow-xl">
        <div className="flex items-center justify-between border-b border-border px-5 py-3">
          <h2 className="text-lg font-semibold">派工給龍蝦（Hermes → OpenClaw）</h2>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X className="h-5 w-5" />
          </button>
        </div>
        <div className="space-y-4 p-5">
          <div>
            <label className="block text-sm font-medium mb-1">要做什麼 *</label>
            <textarea
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="一句話講要做什麼。例：寫本週寫給 Hermes 的學習筆記，主題：龍蝦回信機制"
              rows={2}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">背景資訊（可選）</label>
            <textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="背景資訊、相關檔案、前情提要"
              rows={3}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">完成條件（可選）</label>
            <textarea
              value={criteria}
              onChange={(e) => setCriteria(e.target.value)}
              placeholder="怎麼算做完？例：檔案存在、test 通過、push 完成"
              rows={2}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">急迫程度</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="P0">P0 — 立即</option>
                <option value="P1">P1 — 今天</option>
                <option value="P2">P2 — 本週</option>
                <option value="P3">P3 — 有空</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">截止時間（分鐘，選填）</label>
              <input
                type="number"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                placeholder="例 4320 = 3 天"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              />
            </div>
          </div>
          {err && (
            <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {err}
            </div>
          )}
        </div>
        <div className="flex justify-end gap-2 border-t border-border px-5 py-3">
          <Button variant="outline" onClick={onClose} disabled={submitting}>
            取消
          </Button>
          {err && (err.startsWith("⏱️") || err.startsWith("🛡️")) && (
            <Button
              variant="outline"
              onClick={() => submit(true)}
              disabled={submitting}
              title="繞過節流或守門員拒絕，事後會記錄一筆 bypass log"
            >
              強制送出
            </Button>
          )}
          <Button onClick={() => submit(false)} disabled={submitting}>
            {submitting ? "派工中…" : "派出去"}
          </Button>
        </div>
      </div>
    </div>
  );
}
