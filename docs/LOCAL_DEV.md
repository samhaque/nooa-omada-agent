# Running Nemotron locally with LM Studio

For dev/testing without cluster access. No KServe, no Kourier, just LM
Studio's local OpenAI-compatible server standing in for the NIM.

## Model and quant used

[`lmstudio-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF`](https://huggingface.co/lmstudio-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF),
`Q4_K_M` quant, ~24.5GB. Verified on a MacBook Pro (M-series, 48GB unified
memory). Model card: [nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16)
(original weights). Hybrid Mamba-2/MoE, ~31B total params, ~3B active per
token.

## Fast download

Hugging Face defaults to Xet storage now, fast out of the box (~200-270MB/s
seen). Don't bother with `hf_transfer`/`HF_HUB_ENABLE_HF_TRANSFER`,
deprecated, no-op, just throws a warning.

```bash
uvx --from huggingface_hub python3 -c "
import os
os.environ['HF_XET_NUM_CONCURRENT_RANGE_GET'] = '64'
from huggingface_hub import hf_hub_download
hf_hub_download(
    repo_id='lmstudio-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF',
    filename='NVIDIA-Nemotron-3.5-Lightning-30B-A3B-Q4_K_M.gguf',
    local_dir=os.path.expanduser('~/.lmstudio/models/lmstudio-community/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF'),
)
"
```

`HF_XET_NUM_CONCURRENT_RANGE_GET` (default 16) bumped to 64: more parallel
chunk fetches. Downloading straight into LM Studio's own cache layout
(`~/.lmstudio/models/<publisher>/<repo>/`) means LM Studio detects the file
as already present on next launch, no re-download through its UI. Runs via
`uvx`, no global/user pip install.

Skip `HF_XET_HIGH_PERFORMANCE=1` under 64GB RAM, its buffer sizing wants
that much, can thrash instead of help on less.

## LM Studio setup

1. Load the model in LM Studio (My Models, or search "nemotron-3.5-lightning"
   if downloading through the UI instead of the command above).
2. Developer tab → Start Server. Default `http://localhost:1234/v1`.
3. Get the exact model id LM Studio reports (not always the same string as
   the repo name):

   ```bash
   curl -s http://localhost:1234/v1/models | python3 -m json.tool
   ```

## Wiring `.env`

```
NEMOTRON_BASE_URL=http://localhost:1234/v1
NEMOTRON_MODEL_NAME=<id from the /v1/models response>
NEMOTRON_API_KEY=not-needed
NEMOTRON_MAX_TOKENS=16384
```

Then:

```bash
uv run python -m omada_agent
```

## Known gotcha: `enable_thinking` is ignored

Confirmed by direct probe (2026-09-19) that LM Studio's local server does
not honor `chat_template_kwargs.enable_thinking: false`, the model always
emits `reasoning_content` regardless of `NEMOTRON_ENABLE_THINKING`:

```bash
curl -s http://localhost:1234/v1/chat/completions -d '{
  "model": "<id>", "messages": [{"role": "user", "content": "Say OK."}],
  "max_tokens": 50, "chat_template_kwargs": {"enable_thinking": false}
}'
# -> content: "", reasoning_content: "...", finish_reason: "length"
```

So `NEMOTRON_MAX_TOKENS` (default 16384) is what actually keeps
`recommend_action` from failing with `GenerationError: Empty response... used
all available output tokens on reasoning`, not the thinking toggle. See
[`DEPLOYMENT.md`](DEPLOYMENT.md#thinking-toggle-and-max_tokens) for the
cluster/NIM-side version of this note.

## Also needed: an `omada-controller-mcp` checkout

Sibling directory (`../omada-controller-mcp`) or `OMADA_MCP_DIR` pointed at
one. Without a real controller reachable it falls back to a bundled API
spec snapshot, enough to exercise the tool-calling loop, but `list_sites`/
`list_devices` will error (`ConnectError`) since those hit the live API, not
just the catalog.
