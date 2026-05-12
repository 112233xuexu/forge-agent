from forge_agent.content_packs import ContentPack
from forge_agent.history import OperationHistory
from forge_agent.organizer import FileOrganizer
from forge_agent.scheduler import ScheduleStore


def test_history_lists_organize_operations(tmp_path):
    source = tmp_path / "invoices"
    source.mkdir()
    invoice = source / "invoice-2026-10-alpha.txt"
    invoice.write_text("Invoice Date: 2026-10-01\n", encoding="utf-8")
    organizer = FileOrganizer(tmp_path / "workspace")
    result = organizer.organize_by_month(source, approve=True)

    history = OperationHistory(tmp_path / "workspace")
    entries = history.list()
    shown = history.show(result.operation_id)

    assert entries
    assert entries[0].operation_id == result.operation_id
    assert shown["operation_id"] == result.operation_id


def test_schedule_store_add_pause_resume(tmp_path):
    store = ScheduleStore(tmp_path / "workspace")
    task = store.add("forge-agent organize ~/Downloads", "every day 9am")
    assert task.status == "active"
    assert store.list()[0].command == "forge-agent organize ~/Downloads"

    paused = store.set_status(task.task_id[:8], "paused")
    assert paused.status == "paused"
    resumed = store.set_status(task.task_id[:8], "active")
    assert resumed.status == "active"


def test_content_pack_generates_artifacts(tmp_path):
    pack = ContentPack(tmp_path / "workspace")
    ppt = pack.make_ppt_outline("Forge Agent product update")
    report = pack.make_report("Forge Agent validation")
    news = pack.make_news_brief("AI agents")
    storyboard = pack.make_storyboard("Forge Agent demo")

    for artifact in [ppt, report, news, storyboard]:
        assert artifact.path
        assert artifact.kind in {"ppt", "report", "news", "storyboard"}

    assert (tmp_path / "workspace" / "artifacts" / "index.jsonl").exists()
