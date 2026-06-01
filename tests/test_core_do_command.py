from argparse import Namespace
import json

from forge_agent.commands.core import handle_do
from forge_agent.runtime import ForgeRuntime


def test_handle_do_file_goal_missing_source_returns_input_required(tmp_path, capsys):
    runtime = ForgeRuntime(tmp_path / "workspace")
    args = Namespace(goal=["organize", "my", "invoices"], preview=True, explain=False, execute=False, human=False)

    code = handle_do(args, runtime)

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 2
    assert payload["status"] == "input_required"
    assert payload["missing_inputs"] == ["source_folder"]
