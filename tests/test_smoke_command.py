import json
import sys

from forge_agent.entrypoint import cli_entrypoint


def test_smoke_human_output(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "smoke"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Forge Agent smoke check" in output
    assert "Passed: True" in output
    assert "ok: capabilities_available" in output
    assert "ok: user_flow_demo_passed" in output


def test_smoke_json_output(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "smoke", "--json"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["passed"] is True
    assert data["checks"]["capabilities_available"] is True
    assert data["checks"]["user_flow_demo_passed"] is True
    assert data["capability_count"] >= 8
    assert data["demo"]["passed"] is True
