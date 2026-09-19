# SPDX-License-Identifier: Apache-2.0
"""Assert-based self-check for llm.build_llm(). No network calls.

Run: uv run python tests/test_llm_config.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from omada_agent.llm import build_llm  # noqa: E402


def _clear_env():
    for key in ("NEMOTRON_BASE_URL", "NEMOTRON_MODEL_NAME", "NEMOTRON_API_KEY", "NEMOTRON_ENABLE_THINKING"):
        os.environ.pop(key, None)


def test_missing_base_url_raises():
    _clear_env()
    try:
        build_llm()
    except RuntimeError as exc:
        assert "NEMOTRON_BASE_URL" in str(exc)
    else:
        raise AssertionError("expected RuntimeError when NEMOTRON_BASE_URL is unset")


def test_defaults_and_routing_prefix():
    _clear_env()
    os.environ["NEMOTRON_BASE_URL"] = "http://nemotron-lightning-predictor.ml.svc.cluster.local/v1"
    llm = build_llm()
    assert llm.model == "openai/nvidia/nemotron-lightning-30b-a3b"
    assert llm.config["api_base"] == "http://nemotron-lightning-predictor.ml.svc.cluster.local/v1"
    assert llm.config["api_key"] == "not-needed"
    assert llm.config["extra_body"]["chat_template_kwargs"]["enable_thinking"] is True


def test_thinking_toggle_off():
    _clear_env()
    os.environ["NEMOTRON_BASE_URL"] = "http://example.internal/v1"
    os.environ["NEMOTRON_ENABLE_THINKING"] = "false"
    llm = build_llm()
    assert llm.config["extra_body"]["chat_template_kwargs"]["enable_thinking"] is False


def test_custom_model_name():
    _clear_env()
    os.environ["NEMOTRON_BASE_URL"] = "http://example.internal/v1"
    os.environ["NEMOTRON_MODEL_NAME"] = "nvidia/custom-nemotron"
    llm = build_llm()
    assert llm.model == "openai/nvidia/custom-nemotron"


if __name__ == "__main__":
    test_missing_base_url_raises()
    test_defaults_and_routing_prefix()
    test_thinking_toggle_off()
    test_custom_model_name()
    print("OK: all llm config checks passed")
