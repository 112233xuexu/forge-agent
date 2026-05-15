import json
from pathlib import Path

from forge_agent.organizer import FileOrganizer


def test_rollback_preserves_organize_skipped_files_in_manifest(tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()

    blocked_invoice = source / "invoice-2026-10-blocked.txt"
    blocked_invoice.write_text("Invoice Date: 2026-10-03\nAmount: 10\n", encoding="utf-8")
    blocked_target_dir = source / "organized" / "2026-10"
    blocked_target_dir.mkdir(parents=True)
    blocked_target = blocked_target_dir / blocked_invoice.name
    blocked_target.write_text("existing organized file", encoding="utf-8")

    movable_invoice = source / "invoice-2026-11-move.txt"
    movable_invoice.write_text("Invoice Date: 2026-11-03\nAmount: 20\n", encoding="utf-8")

    organizer = FileOrganizer(tmp_path / "workspace")
    result = organizer.organize_by_month(source, approve=True)

    assert len(result.moved_files) == 1
    assert len(result.skipped_files) == 1
    assert result.manifest_path is not None

    rollback = organizer.rollback_last()

    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["skipped_files"] == result.skipped_files
    assert manifest["rollback_skipped_files"] == rollback.skipped_files
    assert "rolled_back_at" in manifest
