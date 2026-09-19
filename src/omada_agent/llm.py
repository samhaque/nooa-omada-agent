# SPDX-License-Identifier: Apache-2.0
"""Builds the NOOA LLM client for a self-hosted Nemotron Lightning 30B A3B NIM.

The NIM is deployed as a KServe InferenceService (serverless, Knative/Kourier
routed) inside the firewall, with no auth in front of it. litellm needs the
"openai/" routing prefix to treat api_base as a plain OpenAI-compatible Chat
Completions endpoint instead of trying to resolve a known provider by name.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from nooa.unifiedllm.registry import get_llm_client

load_dotenv(override=False)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"0", "false", "no", "off", ""}


def build_llm():
    """Return a configured UnifiedLLM client for the on-prem Nemotron NIM.

    Raises RuntimeError if NEMOTRON_BASE_URL is unset — there is no public
    fallback for an on-prem, firewalled endpoint.
    """
    base_url = os.getenv("NEMOTRON_BASE_URL")
    if not base_url:
        raise RuntimeError(
            "NEMOTRON_BASE_URL is required (Kourier route to the KServe "
            "InferenceService, e.g. http://<svc>.<ns>.svc.cluster.local/v1). "
            "Copy .env.example to .env and set it."
        )

    model_name = os.getenv("NEMOTRON_MODEL_NAME", "nvidia/nemotron-lightning-30b-a3b")
    enable_thinking = _env_bool("NEMOTRON_ENABLE_THINKING", True)
    max_tokens = int(os.getenv("NEMOTRON_MAX_TOKENS", "16384"))

    return get_llm_client(
        f"openai/{model_name}",
        api_base=base_url,
        api_key=os.getenv("NEMOTRON_API_KEY", "not-needed"),
        # Qwen-coder chat template: thinking is a request-time toggle, not a
        # reasoning-effort level. Some servers (LM Studio, at least as of
        # 2026-09) don't honor it and always emit reasoning tokens, so
        # max_tokens needs real headroom on top of whatever the tool-call
        # response itself needs, or the model burns its whole budget on
        # <think> and never emits the call.
        extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}},
        max_tokens=max_tokens,
    )
