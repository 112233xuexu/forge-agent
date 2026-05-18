import json
import sys

from forge_agent.entrypoint import cli_entrypoint
from forge_agent.memory import MemoryStore


def test_ask_supports_workspace_before_command(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "forge-agent",
            "--workspace",
            str(tmp_path),
            "ask",
            "organize",
            "my",
            "receipts",
            "--json",
        ],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["intent"] == "organize_files"
    assert data["next_step"] == "preview organize plan"


def test_ask_supports_workspace_equals_before_command(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "forge-agent",
            f"--workspace={tmp_path}",
            "ask",
            "make",
            "a",
            "project",
            "status",
            "ppt",
            "--json",
        ],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["intent"] == "make_ppt"


def test_ask_attaches_bounded_memory_metadata(monkeypatch, capsys, tmp_path):
    store = MemoryStore(tmp_path)
    public = store.add("Invoices should be organized by month only after preview", room="invoices")
    sensitive = store.add("Sensitive invoice secret should not be injected", safety="sensitive")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "forge-agent",
            "--workspace",
            str(tmp_path),
            "ask",
            "organize",
            "invoices",
            "by",
            "month",
            "--json",
        ],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    memory_used = data["metadata"]["memory_used"]
    assert [item["id"] for item in memory_used] == [public.id]
    assert memory_used[0]["score"] > 0
    assert memory_used[0]["reasons"]
    assert data["metadata"]["memory_policy"] == {
        "bounded": True,
        "limit": 5,
        "include_sensitive": False,
        "sensitive_requires_explicit_recall": True,
    }
    assert store.show(public.id).last_used_at is not None
    assert store.show(sensitive.id).last_used_at is None
