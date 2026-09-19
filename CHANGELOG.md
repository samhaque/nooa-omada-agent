# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- Loosened the `nooa` dependency pin from `>=0.1.0` to `>=0.0.10` to match what's actually published on PyPI; the old pin made `uv sync` unsatisfiable on a clean clone.
- Pinned `mcp<2`: `nooa` 0.0.10's MCP client passes a `timedelta` as `read_timeout_seconds`, which `mcp>=2.0`'s `anyio.fail_after()` no longer accepts (`TypeError: unsupported operand type(s) for +: 'float' and 'datetime.timedelta'`), breaking every MCP tool connection.
- `_resolve_omada_mcp_dir()` (and the old inline lookup it replaced) treated `OMADA_MCP_DIR=` (present but empty, e.g. from a `.env` template) as an explicit override instead of falling back to the sibling-directory default, since `os.getenv(name, default)` only applies `default` when the key is entirely absent. Now uses `os.getenv(name) or default`.
- `load_dotenv(override=True)` → `override=False` in `llm.py`, so a stray `.env` value no longer silently clobbers a real env var (e.g. injected by k8s).
- Added `NEMOTRON_MAX_TOKENS` (default 16384). The `NEMOTRON_ENABLE_THINKING` toggle isn't honored by every server (confirmed not honored by LM Studio's local OpenAI-compatible endpoint as of 2026-09-19: `enable_thinking: false` still returned an empty `content` with the whole budget spent on `reasoning_content`), so `max_tokens` needs real headroom or `recommend_action` fails with `GenerationError: Empty response... used all available output tokens on reasoning`.

### Added
- CI: lint (`ruff`), format check, tests, dependency scan (`pip-audit`).
- Contributor docs (`CONTRIBUTING.md`), issue/PR templates, `CODEOWNERS`.
- `docs/DEPLOYMENT.md` covering the on-prem NIM deployment shape (no-auth endpoint, thinking toggle, serverless cold starts).

## [0.2.0] - 2026-09-19

### Changed
- Repurposed from a generic NOOA sample into a network-ops agent for `omada-controller-mcp`: `NetworkOpsAgent` wires an `MCPTool` to the Omada MCP server (launched as a stdio subprocess) alongside a `PredictStrategy` triage method and a `CodeActStrategy` investigate-and-recommend method.

## [0.1.0] - 2026-09-19

### Added
- NOOA sample agent (`llm.py`) building a `UnifiedLLM` client for a self-hosted Nemotron Lightning 30B A3B NIM, served behind an OpenShift KServe `InferenceService` fronted by Kourier.
- Env-driven config: `NEMOTRON_BASE_URL` (required, no public fallback), `NEMOTRON_MODEL_NAME`, `NEMOTRON_API_KEY`, `NEMOTRON_ENABLE_THINKING`.
- Assert-based test suite (`tests/test_llm_config.py`) validating env parsing with no network calls.
- Apache-2.0 license.

[Unreleased]: https://github.com/samhaque/nooa-omada-agent/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/samhaque/nooa-omada-agent/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/samhaque/nooa-omada-agent/releases/tag/v0.1.0
