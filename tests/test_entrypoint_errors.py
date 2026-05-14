import sys

import forge_agent.entrypoint as entrypoint


def test_cli_entrypoint_handles_oserror(monkeypatch, capsys):
    def raise_oserror():
        raise OSError("permission denied for demo folder")

    monkeypatch.setattr(sys, "argv", ["forge-agent", "organize", "/blocked"])
    monkeypatch.setattr(entrypoint, "legacy_cli_entrypoint", raise_oserror)

    exit_code = entrypoint.cli_entrypoint()

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Forge Agent file error" in captured.err
    assert "permission denied for demo folder" in captured.err
