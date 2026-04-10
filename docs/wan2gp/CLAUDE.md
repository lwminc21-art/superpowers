# WanGP — AI Agent Guidelines

## Project Overview

WanGP is an open-source AI video/image/audio generation framework optimised for low-VRAM GPUs. It wraps multiple model architectures (Wan, HunyuanVideo, LTX-2, Flux, Qwen, etc.) behind a Gradio web interface and a headless CLI. The project also ships **Deepy**, an on-device AI agent that orchestrates multi-step media workflows.

## Key Entry Points

| File / Dir | Purpose |
|---|---|
| `wgp.py` | Main Gradio web application |
| `shared/api.py` | Python API for third-party integration |
| `shared/deepy/` | Deepy agent (controller, engine, tools, CLI) |
| `plugins/` | User-installable plugin packages |
| `preprocessing/` | Pre-generation helpers (masking, pose, depth, …) |
| `postprocessing/` | Post-generation helpers (upscaling, audio merge, …) |
| `models/` | Model loaders and architecture definitions |
| `shared/utils/` | Shared utilities (file I/O, video/audio, prompts) |
| `docs/` | Full documentation (see below) |

## Documentation Map

- `docs/INSTALLATION.md` — setup on NVIDIA / AMD
- `docs/PLUGINS.md` — plugin authoring guide
- `docs/API.md` — Python API reference
- `docs/DEEPY.md` — Deepy agent guide
- `docs/CLI.md` — headless CLI usage
- `docs/MODELS.md` — supported models and checkpoints
- `docs/LORAS.md` — LoRA usage

## Plugin System

Plugins live in `plugins/<plugin-name>/` and must contain:
- `__init__.py` (can be empty)
- `plugin.py` with a class inheriting `WAN2GPPlugin` from `shared.utils.plugins`

Key `WAN2GPPlugin` hooks:
- `setup_ui()` — declare required globals/components, register tabs
- `on_tab_select(state)` / `on_tab_deselect(state)` — tab lifecycle
- `create_config_ui()` — build Gradio components

GPU resource management uses `acquire_GPU_ressources` / `release_GPU_ressources` from `shared.utils.process_locks`.

See `plugins/wan2gp-sample/plugin.py` for a complete working example.

## Python API (shared/api.py)

```python
from pathlib import Path
from shared.api import init

session = init(root=Path("/path/to/wangp"), cli_args=["--profile", "4"])
job = session.submit_task(settings_dict)   # settings exported from web UI
for event in job.events.iter(timeout=0.2):
    ...  # event.kind: "progress" | "preview" | "stream"
result = job.result()   # result.success, result.generated_files
```

Any product using this API must disclose it uses WanGP in its UI and docs.

## Deepy Agent (shared/deepy/)

| File | Role |
|---|---|
| `controller.py` | Orchestrates tool calls and conversation loop |
| `engine.py` | LLM inference (Qwen3.5VL via vllm or GGUF) |
| `tool_settings.py` | Tool template definitions |
| `video_tools.py` | Video/image/audio generation tools |
| `vision.py` | Image/video inspection |
| `transcription.py` | Audio transcription |
| `cli.py` | Headless Deepy CLI |
| `settings/` | Default Deepy configuration |

Deepy requires a Qwen3.5VL Abliterated model as its Prompt Enhancer base.

## Coding Conventions

- Python 3.10+; no mandatory type annotations in existing code but new code should aim for them
- Gradio components are constructed inside `setup_ui()` / tab constructor methods
- Use `shared.utils.utils` helpers for media I/O — do not reimplement
- GPU resources must always be released in a `try/finally` block
- Avoid blocking the Gradio event loop; long operations should use background threads or asyncio
- Existing code uses `fr` (French) variable names in some places — preserve them as-is when editing

## Running Locally

```bash
# CPU / NVIDIA
python wgp.py

# With specific attention backend
python wgp.py --attention sdpa --profile 4

# Headless generation
python wgp.py --headless --settings path/to/settings.json
```

## Testing

There is no automated test suite. Verify changes manually:
1. Launch `python wgp.py`
2. Load the relevant model
3. Generate a short clip / image to confirm the feature works
4. Check the Deepy tab if your change touches `shared/deepy/`
