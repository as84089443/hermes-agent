import importlib.util
import sys
import time
from pathlib import Path

import pytest


def load_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "slack_mcp_boss_mode.py"
    spec = importlib.util.spec_from_file_location("slack_mcp_boss_mode_test", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_extract_and_strip_session_metadata():
    mod = load_module()
    raw = "結論：已整理第一版。\n\n下一步：補更多細節。\n\nsession_id: 20260415_111749_5b3706\n"
    assert mod.extract_session_id(raw) == "20260415_111749_5b3706"
    assert mod.strip_session_metadata(raw) == "結論：已整理第一版。\n\n下一步：補更多細節。"


def test_run_lane_agent_resumes_existing_session(monkeypatch):
    mod = load_module()
    calls = {}

    class DummyProc:
        returncode = 0
        stdout = "結論：收到你的補充，我已調整。\n\nsession_id: sess_123\n"
        stderr = ""

    def fake_run(cmd, capture_output, text, timeout, cwd):
        calls["cmd"] = cmd
        return DummyProc()

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    result = mod.run_lane_agent(
        {"lane_id": "lane-1", "source_text": "原始交辦", "session_id": "sess_prev"},
        followup_text="我補充一下方向",
    )

    prompt = mod.build_execution_agent_prompt({"lane_id": "lane-1", "source_text": "原始交辦"}, followup_text="我補充一下方向")

    assert "--resume" in calls["cmd"]
    assert "sess_prev" in calls["cmd"]
    assert result["session_id"] == "sess_123"
    assert "session_id:" not in result["output"]
    assert "不要每次都硬切『結論 / 現況 / 下一步』三個標題" in prompt


def test_run_queue_once_clears_active_on_system_exit(monkeypatch):
    mod = load_module()
    mod.save_state({"execution_queue": {"pending": ["lane-missing"], "active": None, "history": []}})

    def boom(_lane_id):
        raise SystemExit("missing lane")

    monkeypatch.setattr(mod, "execute_lane", boom)

    result = mod.run_queue_once()
    state = mod.load_state()
    queue = state["execution_queue"]

    assert result["ok"] is False
    assert result["action"] == "error"
    assert queue["active"] is None
    assert queue["last_result"]["status"] == "error"
    assert queue["history"][-1]["status"] == "error"


def test_claim_top_level_task_is_idempotent():
    mod = load_module()
    mod.save_state({})

    assert mod.claim_top_level_task("C1", "100.01") is True
    assert mod.claim_top_level_task("C1", "100.01") is False

    state = mod.load_state()
    lane_state = state["thread_lane"]["C1"]
    assert lane_state["in_flight_top_level_ts"] == ["100.01"]

    mod.release_top_level_task("C1", "100.01", processed=True)
    state = mod.load_state()
    lane_state = state["thread_lane"]["C1"]
    assert lane_state["in_flight_top_level_ts"] == []
    assert lane_state["processed_top_level_ts"] == ["100.01"]
    assert mod.claim_top_level_task("C1", "100.01") is False


def test_reconcile_stale_lanes_marks_only_nonterminal_old_lanes():
    mod = load_module()
    old = time.time() - 7200
    mod.save_state(
        {
            "lane_registry": {
                "lane-old": {"lane_id": "lane-old", "status": "executing", "last_updated_at": old},
                "lane-terminal": {"lane_id": "lane-terminal", "status": "agent_replied", "last_updated_at": old},
                "lane-fresh": {"lane_id": "lane-fresh", "status": "triaging", "last_updated_at": time.time()},
            }
        }
    )

    result = mod.reconcile_stale_lanes(max_age_seconds=1800)
    state = mod.load_state()

    assert result["count"] == 1
    assert result["stale_lanes"] == ["lane-old"]
    assert state["lane_registry"]["lane-old"]["status"] == "stale"
    assert state["lane_registry"]["lane-old"]["stale_reason"] == "inactive_for_1800s"
    assert state["lane_registry"]["lane-terminal"]["status"] == "agent_replied"
    assert state["lane_registry"]["lane-fresh"]["status"] == "triaging"


def test_queue_status_reports_stale_lane_count():
    mod = load_module()
    mod.save_state(
        {
            "execution_queue": {"pending": [], "active": None, "history": [], "last_result": None},
            "lane_registry": {
                "lane-1": {"status": "stale"},
                "lane-2": {"status": "executing"},
                "lane-3": {"status": "stale"},
            },
        }
    )

    status = mod.queue_status()

    assert status["stale_lane_count"] == 2


def test_advance_lane_no_longer_posts_intermediate_thread_updates(monkeypatch):
    mod = load_module()
    mod.save_state(
        {
            "lane_registry": {
                "lane-1": {
                    "lane_id": "lane-1",
                    "channel_id": "C1",
                    "channel_name": "一般",
                    "thread_ts": "123.45",
                    "source_ts": "123.45",
                    "status": "kickoff_sent",
                }
            }
        }
    )

    thread_posts = []
    parent_posts = []

    def fake_reply(channel_id, thread_ts, text):
        thread_posts.append({"channel_id": channel_id, "thread_ts": thread_ts, "text": text})
        return {"ts": f"reply-{len(thread_posts)}"}

    def fake_post(channel_id, text):
        parent_posts.append({"channel_id": channel_id, "text": text})
        return {"ts": "parent-1"}

    monkeypatch.setattr(mod, "reply_thread", fake_reply)
    monkeypatch.setattr(mod, "post_message", fake_post)

    result = mod.advance_lane(
        {"id": "C1", "name": "一般"},
        {"ts": "123.45", "text": "這是我們攝影棚的宣傳計畫"},
        {"lane_id": "lane-1", "thread_ts": "123.45", "source_ts": "123.45", "channel_id": "C1", "channel_name": "一般"},
    )

    assert result["lane"]["status"] == "executing"
    assert len(thread_posts) == 0
    assert len(parent_posts) == 0
    assert result["reply"] is None
    assert result["execution_reply"] is None
    assert result["parent_summary"] is None


def test_watch_once_top_level_starts_lane_without_kickoff_chatter(monkeypatch):
    mod = load_module()
    mod.save_state({})

    monkeypatch.setattr(mod, "detect_new_lane_reply", lambda user_token, channel: None)
    monkeypatch.setattr(mod, "detect_new_top_level_task", lambda user_token, channel: {"ts": "200.01", "text": "新交辦"})
    monkeypatch.setattr(mod, "claim_top_level_task", lambda channel_id, ts: True)
    monkeypatch.setattr(mod, "release_top_level_task", lambda channel_id, ts, processed: None)
    monkeypatch.setattr(mod, "register_lane", lambda channel, source_message, kickoff_reply=None: {"lane_id": "lane-2", "thread_ts": "200.01", "source_ts": "200.01", "channel_id": channel["id"], "channel_name": channel["name"]})
    monkeypatch.setattr(mod, "advance_lane", lambda channel, source_message, lane_entry: {"lane": {**lane_entry, "status": "executing"}, "reply": None, "execution_reply": None, "parent_summary": None})
    monkeypatch.setattr(mod, "enqueue_lane", lambda lane_id: None)
    monkeypatch.setattr(mod, "run_queue_once", lambda: {"ok": True, "action": "executed", "result": {"lane": {"lane_id": "lane-2", "status": "agent_replied"}, "reply": {"ts": "final-1"}}})
    monkeypatch.setattr(mod, "update_lane", lambda lane_id, **fields: {"lane_id": lane_id, **fields})

    result = mod.watch_once("token", {"id": "C1", "name": "一般"})

    assert result["action"] == "thread_kickoff"
    assert result["reply"] is None
    assert result["reply_ts"] is None
    assert result["agent_reply"] == {"ts": "final-1"}


def test_watch_once_prefers_thread_reply_and_executes_same_lane(monkeypatch):
    mod = load_module()
    mod.save_state(
        {
            "lane_registry": {
                "lane-1": {
                    "lane_id": "lane-1",
                    "channel_id": "C1",
                    "channel_name": "一般",
                    "source_ts": "111.01",
                    "thread_ts": "111.01",
                    "status": "agent_replied",
                }
            }
        }
    )

    monkeypatch.setattr(
        mod,
        "detect_new_lane_reply",
        lambda user_token, channel: {
            "lane": {"lane_id": "lane-1", "source_ts": "111.01"},
            "message": {"ts": "111.02", "text": "我補充一下新想法"},
            "latest_seen": "111.02",
        },
    )
    monkeypatch.setattr(mod, "detect_new_top_level_task", lambda user_token, channel: None)

    executed = {}

    def fake_execute(lane_id, followup_text=None, followup_ts=None):
        executed.update({"lane_id": lane_id, "followup_text": followup_text, "followup_ts": followup_ts})
        return {"reply": {"ts": "reply-2"}}

    monkeypatch.setattr(mod, "execute_lane", fake_execute)
    monkeypatch.setattr(mod, "update_lane", lambda lane_id, **fields: {"lane_id": lane_id, **fields})

    result = mod.watch_once("token", {"id": "C1", "name": "一般"})

    assert result["action"] == "thread_reply"
    assert executed["lane_id"] == "lane-1"
    assert executed["followup_text"] == "我補充一下新想法"
    assert executed["followup_ts"] == "111.02"


def test_transition_lane_updates_status_and_posts_reply(monkeypatch):
    mod = load_module()
    mod.save_state(
        {
            "lane_registry": {
                "lane-1": {
                    "lane_id": "lane-1",
                    "channel_id": "C1",
                    "thread_ts": "123.45",
                    "source_ts": "123.45",
                    "status": "agent_replied",
                }
            }
        }
    )

    posted = {}

    def fake_reply(channel_id, thread_ts, text):
        posted.update({"channel_id": channel_id, "thread_ts": thread_ts, "text": text})
        return {"ts": "999.01"}

    monkeypatch.setattr(mod, "reply_thread", fake_reply)

    result = mod.transition_lane("lane-1", status="completed", note="已完成交付")

    assert result["lane"]["status"] == "completed"
    assert result["lane"]["governance_note"] == "已完成交付"
    assert result["lane"]["governance_reply_ts"] == "999.01"
    assert posted["channel_id"] == "C1"
    assert posted["thread_ts"] == "123.45"
    assert "已完成主要執行" in posted["text"]
    assert "已完成交付" in posted["text"]


def test_transition_lane_rejects_unknown_status():
    mod = load_module()
    mod.save_state(
        {"lane_registry": {"lane-1": {"lane_id": "lane-1", "channel_id": "C1", "thread_ts": "1", "source_ts": "1", "status": "agent_replied"}}}
    )

    with pytest.raises(SystemExit):
        mod.transition_lane("lane-1", status="weird")
