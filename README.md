# Kokoro TTS

High-quality Text-to-Speech using Kokoro-82M. Runs entirely locally as a CLI — no server, no web UI, no network access beyond fetching the model/voices from Hugging Face on first use.

## Quick Start

1. **Install**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run**:
   ```bash
   python app.py --input book.txt
   ```
3. **List available voices**:
   ```bash
   python app.py --list-voices
   ```

## Key Features
- **Fast**: Lazy loading and hardware acceleration (CUDA/MPS/CPU, auto-detected).
- **Flexible**: Export as WAV or MP3, combine chapters into one file, resume interrupted runs.
- **Smart**: Automatic chapter splitting and reference skipping.

See [GEMINI.md](GEMINI.md) for detailed architecture and development guidelines.
