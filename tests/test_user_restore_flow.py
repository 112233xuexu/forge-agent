import json
import sys

from forge_agent.entrypoint import cli_entrypoint
from forge_agent.user_restore_flow import maybe_run_restore_goal


def test_restore_goal_ignores_unrelated_text(tmp_path):
    assert maybe_run_restore_goal("summarize notes", workspace=tmp_path, mode="preview") is None


def test_do_preview_restore_goal_human(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "do", "--preview", "--human", "undo", "last", "organize"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Status: planned" in output
    assert "restore the latest" in output.lower()


def test_do_execute_restore_goal_restores_files(monkeypatch, capsys, tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    original = source / "invoice-2026-04.txt"
    original.write_text("invoice 2026-04", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "do", "--execute", "organize", "folder", str(source)])
    assert cli_entrypoint() == 0
    capsys.readouterr()
    moved = source / "organized" / "2026-04" / "invoice-2026-04.txt"
    assert moved.exists()
    assert not original.exists()

    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "do", "--execute", "undo", "last", "organize"])
    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "completed"
    assert data["rollback_result"]["restored_files"]
    assert original.exists()
    assert not moved.exists()
