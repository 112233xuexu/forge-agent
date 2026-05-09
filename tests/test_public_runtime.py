from forge_agent import ForgeRuntime, __version__
from forge_agent.approvals import ApprovalLedger
from forge_agent.file_organizer_demo import run_file_organizer_demo


def test_version():
    assert __version__ == "1.0.0rc10"


def test_runtime_init_creates_workspace(tmp_path):
    runtime = ForgeRuntime(tmp_path)
    status = runtime.init_workspace()
    assert status.ready is True
    assert status.skill_store_exists is True
    assert (tmp_path / "config.json").exists()
    assert (tmp_path / "tasks.jsonl").exists()
    assert (tmp_path / "skills" / "index.jsonl").exists()


def test_runtime_accepts_goal_and_creates_skill(tmp_path):
    runtime = ForgeRuntime(tmp_path)
    result = runtime.do("write release notes", source="test")
    assert result.status == "accepted"
    assert result.goal == "write release notes"
    assert result.evidence["skill"]["created_for_goal"] is True
    assert (tmp_path / "tasks.jsonl").exists()
    assert runtime.list_skills()[0].name == "Write Release Notes"


def test_runtime_reuses_existing_skill(tmp_path):
    runtime = ForgeRuntime(tmp_path)
    first = runtime.do("write release notes")
    second = runtime.do("write release notes for v1")
    assert first.evidence["skill"]["skill_id"] == second.evidence["skill"]["skill_id"]
    assert second.evidence["skill"]["created_for_goal"] is False


def test_runtime_lists_tasks_newest_first(tmp_path):
    runtime = ForgeRuntime(tmp_path)
    first = runtime.do("first task")
    second = runtime.do("second task")
    tasks = runtime.list_tasks()
    assert [task.task_id for task in tasks] == [second.task_id, first.task_id]


def test_doctor_reports_missing_workspace(tmp_path):
    runtime = ForgeRuntime(tmp_path / "missing")
    status = runtime.doctor()
    assert status.ready is False
    assert status.task_count == 0
    assert status.skill_count == 0
    assert "forge-agent init" in " ".join(status.messages)


def test_approval_ledger_records_decision(tmp_path):
    ledger = ApprovalLedger(tmp_path)
    item = ledger.request(action="move demo files", risk="file_move", explanation="demo approval")
    decided = ledger.decide(item.approval_id, "approved")
    assert decided.status == "approved"
    assert ledger.list()[0].approval_id == item.approval_id


def test_file_organizer_demo_proves_reuse(tmp_path):
    result = run_file_organizer_demo(tmp_path / "demo")
    assert result.created_skill is True
    assert result.reuse_proven is True
    assert len(result.moved_files) == 5
    assert result.manifest_path.endswith("manifest.json")
