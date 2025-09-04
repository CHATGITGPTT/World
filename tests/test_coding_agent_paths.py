from pathlib import Path
import sys, pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from agents.coding_agent import CodingAgent


def test_create_project_returns_strings(tmp_path: Path):
    d = tmp_path / "demo"
    d.mkdir()
    (d / "a.txt").write_text("x")
    agent = CodingAgent()
    out = agent._create_project(d)
    assert all(isinstance(p, str) for p in out["files_created"])
