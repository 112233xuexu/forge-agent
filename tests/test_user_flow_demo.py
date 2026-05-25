import json
import sys

from forge_agent.entrypoint import cli_entrypoint
from forge_agent.user_flow_demo import run_user_flow_demo


def test_run_user_flow_demo_roundtrip(tmp_path):
    result = run_user_flow_demo(tmp_path / "demo")

    assert result.preview["status"] == "planned"
    assert result.execute["status"] == "completed"
    assert result.restore["status"] == "completed"
    assert len(result.audit) == 4


def test_user_flow_demo_json_command(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "demo", "--kind", "user-flow", "--json"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["preview"]["status"] == "planned"
    assert data["execute"]["status"] == "completed"
    assert data["restore"]["status"] == "completed"


def test_user_flow_demo_human_command(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "demo", "--kind", "user-flow"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "ordinary-user demo: user flow" in output
    assert "Preview: planned" in output
    assert "Execute: completed" in output
    assert "Restore: completed" in output
