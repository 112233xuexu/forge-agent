import json

from forge_agent.cli import main


def test_organize_missing_source_json_error(capsys, tmp_path):
    missing = tmp_path / "missing"

    exit_code = main(["--workspace", str(tmp_path / "workspace"), "organize", str(missing), "--json"])

    assert exit_code == 2
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "file_not_found"
    assert "source directory does not exist" in data["message"]


def test_rollback_missing_operation_json_error(capsys, tmp_path):
    exit_code = main(["--workspace", str(tmp_path / "workspace"), "organize-rollback", "--json"])

    assert exit_code == 2
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "file_not_found"
    assert "no previous organize operation found" in data["message"]
