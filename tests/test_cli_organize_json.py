import json

from forge_agent.cli import main


def test_organize_cli_json_includes_skipped_files(tmp_path, capsys):
    source = tmp_path / "invoices"
    source.mkdir()
    invoice = source / "invoice-2026-11-alpha.txt"
    invoice.write_text("Invoice Date: 2026-11-03\nAmount: 10\n", encoding="utf-8")

    target_dir = source / "organized" / "2026-11"
    target_dir.mkdir(parents=True)
    target = target_dir / invoice.name
    target.write_text("existing organized file", encoding="utf-8")

    exit_code = main([
        "--workspace",
        str(tmp_path / "workspace"),
        "organize",
        str(source),
        "--approve",
        "--json",
    ])

    assert exit_code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)

    assert data["mode"] == "approved"
    assert data["moved_files"] == []
    assert len(data["skipped_files"]) == 1
    assert data["skipped_files"][0]["source"] == str(invoice)
    assert data["skipped_files"][0]["destination"] == str(target)
    assert data["skipped_files"][0]["reason"] == "destination already exists"

    assert invoice.exists()
    assert target.read_text(encoding="utf-8") == "existing organized file"
