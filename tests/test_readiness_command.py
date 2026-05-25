import json
import sys

from forge_agent.entrypoint import cli_entrypoint


def test_readiness_human_output_from_repo_root(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "readiness"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Forge Agent readiness: ready" in output
    assert "ok: README.md" in output
    assert "ok: docs/CAPABILITIES.md" in output


def test_readiness_json_output_from_repo_root(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "readiness", "--json"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ready"] is True
    names = [item["name"] for item in data["checks"]]
    assert "README.md" in names
    assert "docs/CAPABILITIES.md" in names


def test_readiness_reports_missing_files(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["forge-agent", "readiness", "--json"])

    exit_code = cli_entrypoint()

    assert exit_code == 1
    data = json.loads(capsys.readouterr().out)
    assert data["ready"] is False
    assert any(not item["ok"] for item in data["checks"])
