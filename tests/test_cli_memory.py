import json

from forge_agent.cli import main


def test_memory_cli_add_list_show_search_forget_json(capsys, tmp_path):
    workspace = tmp_path / "workspace"

    exit_code = main([
        "--workspace",
        str(workspace),
        "memory",
        "add",
        "Forge remembers visibly",
        "--scope",
        "project",
        "--room",
        "roadmap",
        "--json",
    ])
    assert exit_code == 0
    created = json.loads(capsys.readouterr().out)
    assert created["ok"] is True
    memory_id = created["memory"]["id"]
    assert created["memory"]["content"] == "Forge remembers visibly"

    exit_code = main(["--workspace", str(workspace), "memory", "list", "--json"])
    assert exit_code == 0
    listed = json.loads(capsys.readouterr().out)
    assert listed["ok"] is True
    assert [item["id"] for item in listed["memories"]] == [memory_id]

    exit_code = main(["--workspace", str(workspace), "memory", "show", memory_id, "--json"])
    assert exit_code == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["ok"] is True
    assert shown["memory"]["id"] == memory_id

    exit_code = main(["--workspace", str(workspace), "memory", "search", "visibly", "--json"])
    assert exit_code == 0
    searched = json.loads(capsys.readouterr().out)
    assert searched["ok"] is True
    assert [item["id"] for item in searched["memories"]] == [memory_id]

    exit_code = main(["--workspace", str(workspace), "memory", "forget", memory_id, "--json"])
    assert exit_code == 0
    forgotten = json.loads(capsys.readouterr().out)
    assert forgotten["ok"] is True
    assert forgotten["memory"]["status"] == "forgotten"

    exit_code = main(["--workspace", str(workspace), "memory", "list", "--json"])
    assert exit_code == 0
    listed_after_forget = json.loads(capsys.readouterr().out)
    assert listed_after_forget["memories"] == []


def test_memory_cli_quarantine_restore_and_export_json(capsys, tmp_path):
    workspace = tmp_path / "workspace"

    exit_code = main([
        "--workspace",
        str(workspace),
        "memory",
        "add",
        "Sensitive memory should be governable",
        "--safety",
        "sensitive",
        "--json",
    ])
    assert exit_code == 0
    created = json.loads(capsys.readouterr().out)
    memory_id = created["memory"]["id"]

    exit_code = main(["--workspace", str(workspace), "memory", "quarantine", memory_id, "--json"])
    assert exit_code == 0
    quarantined = json.loads(capsys.readouterr().out)
    assert quarantined["ok"] is True
    assert quarantined["memory"]["status"] == "quarantined"

    exit_code = main(["--workspace", str(workspace), "memory", "restore", memory_id, "--json"])
    assert exit_code == 0
    restored = json.loads(capsys.readouterr().out)
    assert restored["ok"] is True
    assert restored["memory"]["status"] == "active"

    exit_code = main(["--workspace", str(workspace), "memory", "export", "--json"])
    assert exit_code == 0
    exported = json.loads(capsys.readouterr().out)
    assert exported["ok"] is True
    assert exported["export"]["version"] == 1
    assert exported["export"]["doctor"]["sensitive"] == 1
    assert exported["export"]["memories"][0]["id"] == memory_id


def test_memory_cli_missing_memory_json_error(capsys, tmp_path):
    exit_code = main([
        "--workspace",
        str(tmp_path / "workspace"),
        "memory",
        "show",
        "mem_missing",
        "--json",
    ])

    assert exit_code == 2
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is False
    assert data["error"] == "not_found"
    assert "mem_missing" in data["message"]


def test_memory_cli_doctor_and_palace_json(capsys, tmp_path):
    workspace = tmp_path / "workspace"

    exit_code = main(["--workspace", str(workspace), "memory", "doctor", "--json"])
    assert exit_code == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["ok"] is True
    assert doctor["doctor"]["active"] == 0
    assert doctor["doctor"]["sensitive"] == 0

    exit_code = main(["--workspace", str(workspace), "memory", "palace", "--json"])
    assert exit_code == 0
    palace = json.loads(capsys.readouterr().out)
    assert palace["ok"] is True
    assert palace["palace"]["version"] == 1
    assert palace["palace"]["policy"]["restore_requires_explicit_command"] is True
