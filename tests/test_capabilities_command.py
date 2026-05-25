import json
import sys

from forge_agent.entrypoint import cli_entrypoint


def test_capabilities_human_output(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path), "capabilities"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Forge Agent can currently help with:" in output
    assert "summarize-notes" in output
    assert "rewrite-text" in output


def test_capabilities_json_output(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["forge-agent", "--workspace", str(tmp_path), "capabilities", "--json"])

    exit_code = cli_entrypoint()

    assert exit_code == 0
    data = json.loads(capsys.readouterr().out)
    names = [item["name"] for item in data["capabilities"]]
    assert names == ["draft-follow-up", "rewrite-text", "summarize-notes", "translate-text"]
