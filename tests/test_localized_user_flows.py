import json
import sys

from forge_agent.entrypoint import cli_entrypoint
from forge_agent.user_file_flow import maybe_run_file_goal
from forge_agent.user_restore_flow import maybe_run_restore_goal


def test_localized_file_goal_requires_folder(tmp_path):
    result = maybe_run_file_goal("\u5e2e\u6211\u6574\u7406\u53d1\u7968\u6587\u4ef6", workspace=tmp_path, mode="preview")

    assert result is not None
    assert result.status == "input_required"
    assert result.missing_inputs == ["source_folder"]


def test_do_preview_localized_file_goal_json(monkeypatch, capsys, tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    (source / "invoice-2026-07.txt").write_text("invoice 2026-07", encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "do", "--preview", "\u6574\u7406", "\u6587\u4ef6\u5939", str(source)])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["status"] == "planned"
    assert data["source"] == str(source)
    assert len(data["organize_result"]["planned_moves"]) == 1


def test_localized_restore_goal_is_detected(tmp_path):
    result = maybe_run_restore_goal("\u64a4\u9500\u4e0a\u6b21\u6587\u4ef6\u6574\u7406", workspace=tmp_path, mode="preview")

    assert result is not None
    assert result.status == "planned"
