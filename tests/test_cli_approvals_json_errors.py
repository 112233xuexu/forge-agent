import json

from forge_agent.cli import main


def test_approvals_decide_missing_json_error(capsys, tmp_path):
    exit_code = main([
        "--workspace",
        str(tmp_path / "workspace"),
        "approvals",
        "decide",
        "missing-approval",
        "--decision",
        "approved",
        "--json",
    ])

    assert exit_code == 2
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "not_found"
    assert "missing-approval" in data["message"]
