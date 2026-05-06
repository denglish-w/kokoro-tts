# Kokoro TTS

High-quality Text-to-Speech using Kokoro-82M.

## Quick Start

1. **Install**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run Web UI**:
   ```bash
   python app.py
   ```
3. **Run CLI**:
   ```bash
   python app.py --input book.txt
   ```

## Key Features
- **Fast**: Lazy loading and hardware acceleration (CUDA/MPS).
- **Flexible**: Export as WAV or MP3.
- **Smart**: Automatic chapter splitting and reference skipping.

See [GEMINI.md](GEMINI.md) for detailed architecture and development guidelines.
