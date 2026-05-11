from pathlib import Path

from forge_agent.organizer import FileOrganizer


def test_organizer_dry_run_does_not_move_files(tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    invoice = source / "invoice-2026-04-alpha.txt"
    invoice.write_text("Invoice Date: 2026-04-03\nAmount: 10\n", encoding="utf-8")
    note = source / "note.txt"
    note.write_text("hello", encoding="utf-8")

    organizer = FileOrganizer(tmp_path / "workspace")
    result = organizer.organize_by_month(source)

    assert result.mode == "dry-run"
    assert result.approved is False
    assert len(result.planned_moves) == 1
    assert invoice.exists()
    assert note.exists()
    assert not (source / "organized" / "2026-04" / invoice.name).exists()
    assert (tmp_path / "workspace" / "approvals.jsonl").exists()


def test_organizer_approved_moves_files_and_writes_manifest(tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    invoice = source / "receipt-2026-05-coffee.txt"
    invoice.write_text("Receipt Date: 2026-05-08\nAmount: 7\n", encoding="utf-8")

    organizer = FileOrganizer(tmp_path / "workspace")
    result = organizer.organize_by_month(source, approve=True)

    target = source / "organized" / "2026-05" / invoice.name
    assert result.mode == "approved"
    assert result.approved is True
    assert len(result.moved_files) == 1
    assert target.exists()
    assert not invoice.exists()
    assert result.manifest_path is not None
    assert Path(result.manifest_path).exists()
    assert (tmp_path / "workspace" / "skills" / "index.jsonl").exists()
