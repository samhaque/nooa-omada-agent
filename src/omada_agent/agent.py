# SPDX-License-Identifier: Apache-2.0
"""NOOA agent that manages a TP-Link Omada SDN controller via MCP.

Mirrors the NOOA quickstart MCP pattern (see NVIDIA-NeMo/labs-OO-Agents
examples/quickstart/11_mcp.py): an MCPTool connects to an external MCP
server as a subprocess and exposes its tools to the agent, alongside one
PredictStrategy method for a typed single-shot call and one CodeActStrategy
method for a multi-step tool-using loop.

The MCP server is omada-controller-mcp (github.com/samhaque/omada-controller-mcp),
expected to live in a sibling directory — see OMADA_MCP_DIR below.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from nooa import Agent, strategy
from nooa.mcp import MCPManager, MCPTool
from nooa.strategies import CodeActStrategy, PredictStrategy
from pydantic import BaseModel, Field

from omada_agent.llm import build_llm

Severity = Literal["low", "medium", "high", "critical"]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MCP_CONFIG = _REPO_ROOT / ".mcp.json"
_DEFAULT_OMADA_MCP_DIR = _REPO_ROOT.parent / "omada-controller-mcp"


def _resolve_omada_mcp_dir() -> Path:
    """Resolve and validate the omada-controller-mcp checkout to launch.

    OMADA_MCP_DIR is attacker-influenced in principle (any process that can
    set env vars for this one), and it flows straight into a subprocess
    argv (`uv run --directory <dir> run omada-mcp`). Refuse to launch
    against a directory that isn't actually that project.
    """
    omada_dir = Path(os.getenv("OMADA_MCP_DIR") or _DEFAULT_OMADA_MCP_DIR).resolve()
    pyproject = omada_dir / "pyproject.toml"
    if not pyproject.is_file() or '"omada-controller-mcp"' not in pyproject.read_text():
        raise RuntimeError(
            f"OMADA_MCP_DIR ({omada_dir}) doesn't look like an omada-controller-mcp "
            "checkout (missing or mismatched pyproject.toml)."
        )
    return omada_dir


class IncidentTriage(BaseModel):
    severity: Severity = Field(description="Impact severity of the network incident.")
    affected_asset: str = Field(
        description="Site, device, or client name from the controller, if any."
    )
    summary: str = Field(description="One-sentence summary of the incident.")


class NetworkOpsAgent(Agent, llm=build_llm()):
    """You are an on-call assistant for a TP-Link Omada SDN network.

    Use the omada tool's list_sites/list_devices for common questions, or
    search_operations to find any other operation the controller supports,
    then get_operation_schema before calling an unfamiliar one with
    call_operation.
    """

    omada: MCPTool

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Each MCPTool owns connection state (a subprocess + session), so
        # keep it per agent instance rather than sharing across agents.
        # args is always passed explicitly (not left to .mcp.json's own
        # args) so the OMADA_MCP_DIR validation above is what actually
        # decides the launched path; .mcp.json stays there for other MCP
        # clients (e.g. Claude Code) reading it directly.
        omada_dir = _resolve_omada_mcp_dir()
        self.omada = MCPManager.create_from_server(
            "omada",
            mcp_file=_MCP_CONFIG,
            args=["--directory", str(omada_dir), "run", "omada-mcp"],
        )

    # PredictStrategy: single-shot typed classification.
    @strategy(PredictStrategy())
    async def triage(self, report: str) -> IncidentTriage:
        """Classify an incoming network incident report."""
        ...

    # CodeActStrategy (default): can call the omada MCP tools itself,
    # iterate, and decide when it has enough to answer.
    @strategy(CodeActStrategy())
    async def recommend_action(self, report: str) -> str:
        """Investigate a network incident via the omada tools and recommend a next action."""
        ...
