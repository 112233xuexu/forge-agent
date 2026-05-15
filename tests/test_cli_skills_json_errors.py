import json

from forge_agent.cli import main


def test_skills_show_missing_json_error(capsys, tmp_path):
    exit_code = main([
        "--workspace",
        str(tmp_path / "workspace"),
        "skills",
        "--json",
        "show",
        "missing-skill",
    ])

    assert exit_code == 2
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "not_found"
    assert "missing-skill" in data["message"]


def test_skills_promote_missing_json_error(capsys, tmp_path):
    exit_code = main([
        "--workspace",
        str(tmp_path / "workspace"),
        "skills",
        "--json",
        "promote",
        "missing-skill",
    ])

    assert exit_code == 2
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error"] == "not_found"
    assert "missing-skill" in data["message"]
