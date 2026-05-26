import json
import sys

from forge_agent.entrypoint import cli_entrypoint
from forge_agent.user_flow_demo import run_user_flow_demo


def test_user_flow_demo_includes_localized_checks(tmp_path):
    result = run_user_flow_demo(tmp_path / "demo")

    assert result.passed is True
    assert result.checks["localized_preview_status_planned"] is True
    assert result.checks["localized_restore_status_planned"] is True
    assert len(result.audit) == 9


def test_user_flow_demo_json_includes_localized_checks(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path / ".forge"), "demo", "--kind", "user-flow", "--json"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["checks"]["localized_preview_status_planned"] is True
    assert data["checks"]["localized_restore_status_planned"] is True
