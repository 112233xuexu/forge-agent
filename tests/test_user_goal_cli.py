import json
import sys

from forge_agent.entrypoint import cli_entrypoint
from forge_agent.user_goal_store import UserGoalStore


def test_do_default_keeps_legacy_task_record(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path), "do", "summarize", "notes"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "accepted"
    assert data["evidence"]["next_step"] == "planning"


def test_do_preview_uses_user_goal_runner(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        ["forge-agent", "--workspace", str(tmp_path), "do", "--preview", "Summarize", "these", "notes:", "ship", "update"],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "planned"
    assert data["mode"] == "preview"
    assert data["plan"]["steps"][0]["tool_name"] == "summarize_notes"


def test_do_preview_human_output(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        ["forge-agent", "--workspace", str(tmp_path), "do", "--preview", "--human", "Summarize", "these", "notes:", "ship", "update"],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Forge Agent" in output
    assert "Status: planned" in output
    assert "Goal:" in output
    assert "Matched playbook:" in output


def test_do_explain_returns_plain_plan(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        ["forge-agent", "--workspace", str(tmp_path), "do", "--explain", "Rewrite", '"Need approval"', "in", "a", "warmer", "tone"],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "explained"
    assert data["mode"] == "explain"
    assert "I made a plan" in data["text"]


def test_do_execute_runs_safe_local_plan(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        ["forge-agent", "--workspace", str(tmp_path), "do", "--execute", "Summarize", "these", "notes:", "ship", "update"],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "completed"
    assert data["mode"] == "execute"
    assert data["execution"]["status"] == "completed"


def test_do_execute_persists_learning_state(monkeypatch, capsys, tmp_path):
    for value in ["one", "two"]:
        monkeypatch.setattr(
            sys,
            "argv",
            ["forge-agent", "--workspace", str(tmp_path), "do", "--execute", "Summarize", "these", "notes:", value],
        )
        assert cli_entrypoint() == 0
        capsys.readouterr()

    store = UserGoalStore(tmp_path / "state.db")
    try:
        assert store.to_status() == {"skill_count": 1, "trace_count": 2}
    finally:
        store.close()
