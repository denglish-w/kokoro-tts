# Claude Context for Kokoro TTS

This file provides context for Claude to assist with the Kokoro TTS project.

## Development Environment
- **Language**: Python 3.12+
- **Core Library**: `kokoro` (KModel, KPipeline)
- **UI Framework**: Gradio
- **Hardware**: CUDA, MPS, or CPU (Auto-detected)

## Architecture Overview
- `app.py`: Entry point, handles CLI/UI routing.
- `core/engine.py`: The heart of synthesis. Uses `get_model()` for lazy loading and hardware fallback.
- `core/text.py`: Normalization and chapter regex logic.
- `ui/app.py`: Gradio interface, `BrowserState` for settings, and export logic.

## Key Patterns
- **Lazy Loading**: `pipelines` and `models` are populated on demand.
- **Hardware Fallback**: Always check `DEVICE` and use `get_model(use_gpu)` to handle potential GPU errors.
- **Pathing**: Default export path is set to `/mnt/c/Users/DavidEnglish/Documents/Kokoro_Exports` (WSL/Windows).

## Common Tasks
- **Adding a Voice**: Update `CHOICES` in `ui/app.py`.
- **Modifying Normalization**: Edit `normalize_text` in `core/text.py`.
- **Extending CLI**: Update `parse_args` in `cli.py`.
