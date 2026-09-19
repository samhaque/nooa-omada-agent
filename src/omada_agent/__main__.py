# SPDX-License-Identifier: Apache-2.0
"""Runnable demo: uv run python -m omada_agent"""

import asyncio

from omada_agent.agent import NetworkOpsAgent


async def main() -> None:
    agent = NetworkOpsAgent()
    report = "AP at site HQ has been flapping offline every few minutes since 09:14 UTC."

    triage = await agent.triage(report)
    print(f"severity={triage.severity} asset={triage.affected_asset}")
    print(f"summary: {triage.summary}\n")

    action = await agent.recommend_action(report)
    print(f"recommended action:\n{action}")


if __name__ == "__main__":
    asyncio.run(main())
