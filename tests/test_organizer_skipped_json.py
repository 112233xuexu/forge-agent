import json
from pathlib import Path

from forge_agent.organizer import FileOrganizer


def test_organizer_skipped_files_are_in_result_and_manifest(tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    invoice = source / "invoice-2026-10-alpha.txt"
    invoice.write_text("Invoice Date: 2026-10-03\nAmount: 10\n", encoding="utf-8")

    target_dir = source / "organized" / "2026-10"
    target_dir.mkdir(parents=True)
    target = target_dir / invoice.name
    target.write_text("existing organized file", encoding="utf-8")

    organizer = FileOrganizer(tmp_path / "workspace")
    result = organizer.organize_by_month(source, approve=True)

    assert len(result.moved_files) == 0
    assert len(result.skipped_files) == 1
    assert result.skipped_files[0]["source"] == str(invoice)
    assert result.skipped_files[0]["destination"] == str(target)
    assert result.skipped_files[0]["reason"] == "destination already exists"
    assert result.to_dict()["skipped_files"] == result.skipped_files

    assert invoice.exists()
    assert target.read_text(encoding="utf-8") == "existing organized file"

    assert result.manifest_path is not None
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest["moved_files"] == []
    assert manifest["skipped_files"] == result.skipped_files

    latest_manifest = json.loads((tmp_path / "workspace" / "organize-manifest.json").read_text(encoding="utf-8"))
    assert latest_manifest["skipped_files"] == result.skipped_files
