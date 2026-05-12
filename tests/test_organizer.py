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
    assert result.operation_id is not None
    assert len(result.moved_files) == 1
    assert target.exists()
    assert not invoice.exists()
    assert result.manifest_path is not None
    assert Path(result.manifest_path).exists()
    assert (tmp_path / "workspace" / "organize-manifest.json").exists()
    assert (tmp_path / "workspace" / "operations" / f"organize-{result.operation_id}.json").exists()
    assert (tmp_path / "workspace" / "skills" / "index.jsonl").exists()


def test_organizer_rollback_last_restores_files(tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    invoice = source / "invoice-2026-07-alpha.txt"
    invoice.write_text("Invoice Date: 2026-07-01\nAmount: 33\n", encoding="utf-8")

    organizer = FileOrganizer(tmp_path / "workspace")
    result = organizer.organize_by_month(source, approve=True)
    target = source / "organized" / "2026-07" / invoice.name
    assert target.exists()
    assert not invoice.exists()

    rollback = organizer.rollback_last()

    assert rollback.operation_id == result.operation_id
    assert len(rollback.restored_files) == 1
    assert invoice.exists()
    assert not target.exists()
    assert rollback.manifest_path is not None
    assert Path(rollback.manifest_path).exists()


def test_organizer_rollback_skips_when_original_exists(tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    invoice = source / "receipt-2026-08-train.txt"
    invoice.write_text("Receipt Date: 2026-08-02\nAmount: 12\n", encoding="utf-8")

    organizer = FileOrganizer(tmp_path / "workspace")
    organizer.organize_by_month(source, approve=True)
    invoice.write_text("new file at original path", encoding="utf-8")

    rollback = organizer.rollback_last()

    assert len(rollback.restored_files) == 0
    assert len(rollback.skipped_files) == 1
    assert "original path already exists" in rollback.skipped_files[0]["reason"]
