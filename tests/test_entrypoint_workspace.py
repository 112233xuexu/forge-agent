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
        "enabled": True,
        "bounded": True,
        "limit": 5,
        "include_sensitive": False,
        "sensitive_requires_explicit_recall": True,
    }
    assert store.show(public.id).last_used_at is not None
    assert store.show(sensitive.id).last_used_at is None


def test_ask_no_memory_disables_memory_metadata(monkeypatch, capsys, tmp_path):
    store = MemoryStore(tmp_path)
    public = store.add("Invoices should be organized by month only after preview", room="invoices")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "forge-agent",
            "--workspace",
            str(tmp_path),
            "ask",
            "--no-memory",
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
    assert data["metadata"]["memory_used"] == []
    assert data["metadata"]["memory_policy"]["enabled"] is False
    assert store.show(public.id).last_used_at is None


def test_ask_memory_limit_controls_recall_count(monkeypatch, capsys, tmp_path):
    store = MemoryStore(tmp_path)
    first = store.add("Invoices should be organized by month only after preview", room="invoices")
    second = store.add("Invoices need approval before file movement", room="invoices")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "forge-agent",
            "--workspace",
            str(tmp_path),
            "ask",
            "--memory-limit",
            "1",
            "organize",
            "invoices",
            "approval",
            "--json",
        ],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    memory_used = data["metadata"]["memory_used"]
    assert len(memory_used) == 1
    assert memory_used[0]["id"] in {first.id, second.id}
    assert data["metadata"]["memory_policy"]["limit"] == 1


def test_ask_include_sensitive_memory_requires_explicit_flag(monkeypatch, capsys, tmp_path):
    store = MemoryStore(tmp_path)
    public = store.add("Invoices should be organized by month only after preview", room="invoices")
    sensitive = store.add("Sensitive invoice secret is available only by explicit opt in", safety="sensitive")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "forge-agent",
            "--workspace",
            str(tmp_path),
            "ask",
            "--include-sensitive-memory",
            "organize",
            "invoice",
            "secret",
            "--json",
        ],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    memory_used = data["metadata"]["memory_used"]
    assert {item["id"] for item in memory_used} == {public.id, sensitive.id}
    assert {item["safety"] for item in memory_used} == {"normal", "sensitive"}
    assert data["metadata"]["memory_policy"]["include_sensitive"] is True
    assert store.show(public.id).last_used_at is not None
    assert store.show(sensitive.id).last_used_at is not None


def test_ask_include_sensitive_memory_is_ignored_when_memory_disabled(monkeypatch, capsys, tmp_path):
    store = MemoryStore(tmp_path)
    sensitive = store.add("Sensitive invoice secret", safety="sensitive")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "forge-agent",
            "--workspace",
            str(tmp_path),
            "ask",
            "--no-memory",
            "--include-sensitive-memory",
            "invoice",
            "secret",
            "--json",
        ],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["metadata"]["memory_used"] == []
    assert data["metadata"]["memory_policy"]["enabled"] is False
    assert data["metadata"]["memory_policy"]["include_sensitive"] is False
    assert store.show(sensitive.id).last_used_at is None


def test_ask_invalid_memory_limit_json_error(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "forge-agent",
            "--workspace",
            str(tmp_path),
            "ask",
            "--memory-limit",
            "not-a-number",
            "organize",
            "invoices",
            "--json",
        ],
    )

    exit_code = cli_entrypoint()

    assert exit_code == 2
    data = json.loads(capsys.readouterr().err)
    assert data["error"] == "invalid_memory_limit"
    assert "memory-limit" in data["message"]
