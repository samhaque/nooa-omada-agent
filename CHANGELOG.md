# Changelog

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- Loosened the `nooa` dependency pin from `>=0.1.0` to `>=0.0.10` to match what's actually published on PyPI; the old pin made `uv sync` unsatisfiable on a clean clone.

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
