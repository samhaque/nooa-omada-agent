# SPDX-License-Identifier: Apache-2.0
"""Assert-based self-check for agent.py's pure logic. No network, no subprocess.

Importing omada_agent.agent runs `build_llm()` at class-definition time
(NetworkOpsAgent(Agent, llm=build_llm())), so NEMOTRON_BASE_URL must be set
to *something* before import, even though nothing here calls the model.

Run: uv run python tests/test_agent_paths.py
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

os.environ.setdefault("NEMOTRON_BASE_URL", "http://example.internal/v1")

from pydantic import ValidationError  # noqa: E402

from omada_agent import agent  # noqa: E402


def test_repo_paths_resolve_correctly():
    assert agent._REPO_ROOT == Path(__file__).resolve().parent.parent
    assert agent._MCP_CONFIG == agent._REPO_ROOT / ".mcp.json"
    assert agent._DEFAULT_OMADA_MCP_DIR == agent._REPO_ROOT.parent / "omada-controller-mcp"


def test_incident_triage_rejects_invalid_severity():
    try:
        agent.IncidentTriage(severity="catastrophic", affected_asset="AP-1", summary="x")
    except ValidationError:
        pass
    else:
        raise AssertionError("expected ValidationError for an out-of-Literal severity")


def test_incident_triage_accepts_valid_severity():
    triage = agent.IncidentTriage(severity="high", affected_asset="AP-1", summary="flapping")
    assert triage.severity == "high"


def test_resolve_omada_mcp_dir_rejects_wrong_directory():
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["OMADA_MCP_DIR"] = tmp
        try:
            agent._resolve_omada_mcp_dir()
        except RuntimeError as exc:
            assert "doesn't look like an omada-controller-mcp checkout" in str(exc)
        else:
            raise AssertionError(
                "expected RuntimeError for a directory with no matching pyproject.toml"
            )
        finally:
            os.environ.pop("OMADA_MCP_DIR", None)


def test_resolve_omada_mcp_dir_accepts_matching_pyproject():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "pyproject.toml").write_text('[project]\nname = "omada-controller-mcp"\n')
        os.environ["OMADA_MCP_DIR"] = tmp
        try:
            resolved = agent._resolve_omada_mcp_dir()
            assert resolved == Path(tmp).resolve()
        finally:
            os.environ.pop("OMADA_MCP_DIR", None)


if __name__ == "__main__":
    test_repo_paths_resolve_correctly()
    test_incident_triage_rejects_invalid_severity()
    test_incident_triage_accepts_valid_severity()
    test_resolve_omada_mcp_dir_rejects_wrong_directory()
    test_resolve_omada_mcp_dir_accepts_matching_pyproject()
    print("OK: all agent path/validation checks passed")
