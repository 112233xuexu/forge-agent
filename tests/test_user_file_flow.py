import json
import sys

from forge_agent.entrypoint import cli_entrypoint
from forge_agent.user_file_flow import maybe_run_file_goal


def test_file_goal_requires_folder(tmp_path):
    result = maybe_run_file_goal("organize invoices by month", workspace=tmp_path, mode="preview")

    assert result is not None
    assert result.status == "input_required"
    assert result.missing_inputs == ["source_folder"]


def test_do_preview_file_goal_human(monkeypatch, capsys, tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    (source / "invoice-2026-01.txt").write_text("invoice 2026-01", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        ["forge-agent", "--workspace", str(tmp_path / ".forge"), "do", "--preview", "--human", "organize", "folder", str(source)],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Status: planned" in output
    assert "Planned moves: 1" in output
    assert (source / "invoice-2026-01.txt").exists()


def test_do_preview_file_goal_json(monkeypatch, capsys, tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    (source / "receipt-2026-02.txt").write_text("receipt 2026-02", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "do", "--preview", "organize", "folder", str(source)])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "planned"
    assert data["organize_result"]["mode"] == "dry-run"
    assert len(data["organize_result"]["planned_moves"]) == 1


def test_do_execute_file_goal_moves_file(monkeypatch, capsys, tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    original = source / "invoice-2026-03.txt"
    original.write_text("invoice 2026-03", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "do", "--execute", "organize", "folder", str(source)])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "completed"
    assert data["organize_result"]["mode"] == "approved"
    assert not original.exists()
    assert (source / "organized" / "2026-03" / "invoice-2026-03.txt").exists()
