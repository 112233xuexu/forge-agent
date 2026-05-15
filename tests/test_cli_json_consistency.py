import json

from forge_agent.cli import main


def test_history_show_missing_operation_json_error(capsys, tmp_path):
    exit_code = main([
        "--workspace",
        str(tmp_path / "workspace"),
        "history",
        "show",
        "missing-operation",
        "--json",
    ])

    assert exit_code == 2
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "file_not_found"
    assert "missing-operation" in data["message"]


def test_schedule_pause_missing_task_json_error(capsys, tmp_path):
    exit_code = main([
        "--workspace",
        str(tmp_path / "workspace"),
        "schedule",
        "pause",
        "missing-task",
        "--json",
    ])

    assert exit_code == 2
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "not_found"
    assert "missing-task" in data["message"]


def test_schedule_resume_missing_task_json_error(capsys, tmp_path):
    exit_code = main([
        "--workspace",
        str(tmp_path / "workspace"),
        "schedule",
        "resume",
        "missing-task",
        "--json",
    ])

    assert exit_code == 2
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "not_found"
    assert "missing-task" in data["message"]
