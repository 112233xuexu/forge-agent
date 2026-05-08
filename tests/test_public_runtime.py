from forge_agent import ForgeRuntime, __version__


def test_version():
    assert __version__ == "1.0.0rc10"


def test_runtime_accepts_goal(tmp_path):
    runtime = ForgeRuntime(tmp_path)
    result = runtime.do("write release notes", source="test")
    assert result.status == "accepted"
    assert result.goal == "write release notes"
    assert (tmp_path / "tasks.jsonl").exists()
