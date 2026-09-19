# nooa-omada-agent

A [NOOA](https://github.com/NVIDIA-NeMo/labs-OO-Agents) agent that manages a
TP-Link Omada SDN network: it talks to
[omada-controller-mcp](https://github.com/samhaque/omada-controller-mcp) over
MCP for the actual controller calls (sites, devices, the full Omada API
surface), and to a self-hosted **Nemotron Lightning 30B A3B** NIM for the
model. The NIM is reachable at an on-prem URL with no auth, deployed as an
OpenShift **KServe** `InferenceService` (serverless) and fronted by
**Kourier** (Knative's networking layer).

Background: NOOA is NVIDIA's "agent is a Python object" framework — see
[arXiv:2607.20709](https://arxiv.org/abs/2607.20709). Its `CodeActStrategy`
loop drives the model with a tool-calling contract (`execute_python` /
`return_result`); NOOA's chat-completion client already has a fallback parser
for `<tool_call>` XML output (`unifiedllm.py: _extract_xml_tool_calls`), which
is the tool-call format Qwen-coder-style models emit — relevant since the
served model uses that chat template. No extra glue code needed for that part.

## Layout

```
src/omada_agent/
  llm.py     # builds the UnifiedLLM client from NEMOTRON_* env vars
  agent.py   # NetworkOpsAgent: MCPTool wired to omada-controller-mcp, Predict + CodeAct methods
  __main__.py
.mcp.json    # tells NOOA's MCPManager how to launch the omada MCP server
tests/test_llm_config.py   # assert-based, no network — validates env parsing
```

## Setup

Needs a checkout of
[omada-controller-mcp](https://github.com/samhaque/omada-controller-mcp) as a
sibling directory (`../omada-controller-mcp`), or point `OMADA_MCP_DIR` at
wherever yours lives. That repo has its own setup for talking to a real
controller (`OMADA_CLIENT_ID`/`OMADA_CLIENT_SECRET`); without one reachable it
falls back to a bundled API spec snapshot, which is enough to exercise the
agent's tool-calling loop without a live controller.

```sh
uv sync --extra mcp
cp .env.example .env
# edit .env: set NEMOTRON_BASE_URL to your cluster's Kourier route
```

`NEMOTRON_BASE_URL` is required — there's no public fallback for a
firewalled, on-prem endpoint. It's whatever `curl` can already reach from
inside the network boundary, e.g.:

- In-cluster: `http://nemotron-lightning-predictor.<namespace>.svc.cluster.local/v1`
- Via the Kourier-fronted OpenShift route: `https://nemotron-lightning-predictor-<namespace>.apps.<cluster-domain>/v1`

Confirm connectivity and the exact served model name before running the agent
— NIM's `/models` response is the source of truth, not the marketing name:

```sh
curl -s "$NEMOTRON_BASE_URL/models" | python3 -m json.tool
```

Set `NEMOTRON_MODEL_NAME` in `.env` to the `id` field from that response if it
doesn't match the default in `.env.example`.

## Run

```sh
uv run python -m omada_agent
```

Launches `omada-controller-mcp` as a subprocess over stdio, triages a sample
network incident, then asks the agent to investigate using the omada tools
and recommend a next action.

## Verify without a live endpoint

```sh
python tests/test_llm_config.py
```

Checks env-var validation and client construction (routing prefix, thinking
toggle, api_key passthrough) with no network call — useful before you have
cluster or controller access, or in CI.

## Notes on this deployment shape

- **No auth on the LLM**: the OpenAI-compatible client still requires a
  non-empty `api_key` string to set the `Authorization` header; NIM behind
  Kourier with no auth ignores it. `NEMOTRON_API_KEY` defaults to
  `not-needed`.
- **Thinking toggle**: Qwen-coder-family chat templates take
  `enable_thinking` as a boolean in `chat_template_kwargs`, not a
  reasoning-effort string — set via `NEMOTRON_ENABLE_THINKING` in `.env`,
  forwarded as `extra_body` on every call.
- **Serverless cold starts**: KServe serverless scales to zero. The first
  request after idle may take longer than NOOA's default HTTP timeout;
  raise `http_config` on the client (see `nooa.unifiedllm.http_config.HttpConfig`)
  if you see timeouts on cold start rather than treating it as a broken route.
- **Trust model on the Omada side**: `omada-controller-mcp`'s `call_operation`
  can reach every cataloged operation, including destructive ones (reboot,
  config changes), using that server's own session — see its README's
  trust-model section before pointing this agent at a production controller.
