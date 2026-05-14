import json
import sys

from forge_agent.entrypoint import cli_entrypoint


def test_ask_supports_workspace_before_command(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "forge-agent",
            "--workspace",
            str(tmp_path),
            "ask",
            "organize",
            "my",
            "receipts",
            "--json",
        ],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["intent"] == "organize_files"
    assert data["next_step"] == "preview organize plan"


def test_ask_supports_workspace_equals_before_command(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "forge-agent",
            f"--workspace={tmp_path}",
            "ask",
            "make",
            "a",
            "project",
            "status",
            "ppt",
            "--json",
        ],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["intent"] == "make_ppt"
