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


class IncidentTriage(BaseModel):
    severity: Severity = Field(description="Impact severity of the network incident.")
    affected_asset: str = Field(description="Site, device, or client name from the controller, if any.")
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
        omada_dir = os.getenv("OMADA_MCP_DIR", str(_DEFAULT_OMADA_MCP_DIR))
        self.omada = MCPManager.create_from_server(
            "omada",
            mcp_file=_MCP_CONFIG,
            args=["--directory", omada_dir, "run", "omada-mcp"],
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
