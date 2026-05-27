import json
import subprocess
import sys


def test_ui_handoff_example_runs():
    completed = subprocess.run(
        [sys.executable, "examples/ui_handoff.py"],
        check=True,
        capture_output=True,
        text=True,
    )

    decoder = json.JSONDecoder()
    first, offset = decoder.raw_decode(completed.stdout)
    second, _ = decoder.raw_decode(completed.stdout[offset:].lstrip())

    assert first["schema_version"] == "desktop.v1"
    assert first["kind"] == "desktop_response"
    assert first["status"] == "planned"
    assert first["needs_confirmation"] is True
    assert first["next_actions"] == ["execute"]
    assert second["schema_version"] == "desktop.v1"
    assert second["status"] == "completed"
    assert second["needs_confirmation"] is False
