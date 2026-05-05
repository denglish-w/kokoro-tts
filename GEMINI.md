# Kokoro TTS Web UI & CLI

A high-quality Text-to-Speech (TTS) application built with [Gradio](https://gradio.app/) and powered by the [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) model.

## Project Overview

This project provides a user-friendly interface and a command-line tool for generating and streaming speech from text. It leverages the `kokoro` library for fast, high-quality synthesis with support for multiple voices and languages.

### Key Features
- **Web UI**: Interactive Gradio interface for real-time synthesis and streaming.
- **CLI Mode**: Batch process text files into audio chapters from the command line.
- **Batch Export**: Automatically split long texts (like books) into chapters and export as WAV files or ZIP.
- **Custom Pronunciation**: Support for Markdown link syntax for phonemes (e.g., `[Kokoro](/kˈOkəɹO/)`) and a custom replacement dictionary.
- **Text Normalization**: Smart handling of years, abbreviations, and auto-skipping of reference/bibliography sections.
- **Hardware Acceleration**: Support for both CPU and CUDA-enabled GPUs.

### Key Technologies
- **Python**: Core logic and scripting.
- **Gradio**: Web interface for interactive use.
- **Kokoro**: TTS engine (KModel and KPipeline).
- **PyTorch**: Underlying deep learning framework.
- **ZeroGPU (via `spaces`)**: Optional GPU acceleration for Hugging Face Spaces.

## Project Structure

- `app.py`: Main entry point. Supports launching the Web UI or CLI.
- `cli.py`: Logic for the Command-Line Interface.
- `ui/`:
  - `app.py`: Gradio UI definition and frontend logic.
- `core/`:
  - `engine.py`: TTS generation engine, model loading, and pipeline management.
  - `text.py`: Text normalization, chapter splitting, and reference removal.
- `en.txt`: A collection of random quotes for the "Random Quote" feature.
- `gatsby5k.md`, `frankenstein5k.md`: Sample long-form texts for testing.
- `requirements.txt`: Project dependencies.
- `.venv/`: Python virtual environment.

## Building and Running

### Prerequisites
- Python 3.12+
- [ffmpeg](https://ffmpeg.org/) (required for audio processing)

### Installation
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

#### Web UI Mode
Execute the main script without arguments to start the Gradio server:
```bash
python app.py
```
The application will be available at `http://localhost:40001` (or as configured by `KOKORO_PORT`).

#### CLI Mode
Use the `--input` flag to process a text file into audio chapters:
```bash
python app.py --input my_book.txt --output-dir audio_output --voice af_heart --speed 1.0
```

## Development Conventions

- **Language Support**: Uses code `'a'` for American English and `'b'` for British English.
- **Voice Packs**: 20+ voices available (e.g., `af_heart`, `am_michael`, `bf_emma`).
- **Phonemes**: Supports `[text](/phonemes/)` syntax for precise control.
- **Streaming**: Supports real-time audio streaming in the Web UI.

## TODO / Future Improvements
- [ ] Add unit tests for synthesis pipelines and text normalization.
- [ ] Implement multi-language support beyond US/UK English.
- [ ] Add support for more audio formats (MP3, OGG).
- [x] Add explicit `requirements.txt`.
