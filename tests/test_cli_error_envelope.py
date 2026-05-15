import json

from forge_agent.cli import main


def test_json_error_envelope_includes_ok_false(capsys, tmp_path):
    exit_code = main([
        "--workspace",
        str(tmp_path / "workspace"),
        "organize",
        str(tmp_path / "missing"),
        "--json",
    ])

    assert exit_code == 2
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["ok"] is False
    assert data["error"] == "file_not_found"
    assert "source directory does not exist" in data["message"]


def test_approval_json_error_envelope_includes_ok_false(capsys, tmp_path):
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
    assert data["ok"] is False
    assert data["error"] == "not_found"
    assert "missing-approval" in data["message"]
