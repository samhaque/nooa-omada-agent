# Deployment notes

## No auth on the LLM

The OpenAI-compatible client still requires a non-empty `api_key` string to
set the `Authorization` header; NIM behind Kourier with no auth ignores it.
`NEMOTRON_API_KEY` defaults to `not-needed`.

## Thinking toggle

Qwen-coder-family chat templates take `enable_thinking` as a boolean in
`chat_template_kwargs`, not a reasoning-effort string, set via
`NEMOTRON_ENABLE_THINKING` in `.env`, forwarded as `extra_body` on every call.

## Serverless cold starts

KServe serverless scales to zero. The first request after idle may take
longer than NOOA's default HTTP timeout, raise `http_config` on the client
(see `nooa.unifiedllm.http_config.HttpConfig`) if you see timeouts on cold
start rather than treating it as a broken route.

## Trust model on the Omada side

`omada-controller-mcp`'s `call_operation` can reach every cataloged
operation, including destructive ones (reboot, config changes), using that
server's own session. See
[its README's trust-model section](https://github.com/samhaque/omada-controller-mcp#security)
and [`docs/SECURITY.md`](https://github.com/samhaque/omada-controller-mcp/blob/main/docs/SECURITY.md)
before pointing this agent at a production controller.
