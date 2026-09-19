# Deployment notes

## No auth on the LLM

The OpenAI-compatible client still requires a non-empty `api_key` string to
set the `Authorization` header; NIM behind Kourier with no auth ignores it.
`NEMOTRON_API_KEY` defaults to `not-needed`.

## Thinking toggle and max_tokens

Qwen-coder-family chat templates take `enable_thinking` as a boolean in
`chat_template_kwargs`, not a reasoning-effort string, set via
`NEMOTRON_ENABLE_THINKING` in `.env`, forwarded as `extra_body` on every call.

**Confirmed not honored by LM Studio** (checked 2026-09-19, local server):
`enable_thinking: false` had no effect, the model still spent its whole
`max_tokens` budget on `reasoning_content` and returned nothing. Probed
directly:

```bash
curl -s http://localhost:1234/v1/chat/completions -d '{
  "model": "<id>", "messages": [{"role": "user", "content": "Say OK."}],
  "max_tokens": 50, "chat_template_kwargs": {"enable_thinking": false}
}'
# -> content: "", reasoning_content: "...", finish_reason: "length"
```

So the real lever is `NEMOTRON_MAX_TOKENS` (default 16384, see
`.env.example`), not the thinking toggle, on servers that ignore it. Without
enough headroom, nooa raises `GenerationError: Empty response: the model
used all available output tokens on reasoning and had none left for a tool
call.` If you hit that with the default already set, raise
`NEMOTRON_MAX_TOKENS` further.

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
