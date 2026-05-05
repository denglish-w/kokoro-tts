# Kokoro TTS Web UI

A high-quality Text-to-Speech (TTS) web application built with [Gradio](https://gradio.app/) and powered by the [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) model.

## Project Overview

This project provides a user-friendly interface for generating and streaming speech from text. It leverages the `kokoro` library for fast, high-quality synthesis with support for multiple voices and languages (currently US and UK English).

### Key Technologies
- **Python**: Core logic and scripting.
- **Gradio**: Web interface for interactive use and API access.
- **Kokoro**: TTS engine (KModel and KPipeline).
- **PyTorch**: Underlying deep learning framework.
- **ZeroGPU (via `spaces`)**: Optional GPU acceleration for Hugging Face Spaces.

## Project Structure

- `app.py`: Main application script containing the Gradio interface and TTS logic.
- `en.txt`: A collection of random quotes used for the "Random Quote" feature.
- `gatsby5k.md`, `frankenstein5k.md`: Sample long-form texts for testing synthesis.
- `.venv/`: Python virtual environment containing dependencies.

## Building and Running

### Prerequisites
- Python 3.12+ (as seen in `.venv`)
- [ffmpeg](https://ffmpeg.org/) (usually required for Gradio/Audio processing)

### Installation
If setting up from scratch (assuming `requirements.txt` is missing but dependencies are known):
```bash
python -m venv .venv
source .venv/bin/activate
pip install kokoro gradio torch spaces
```

### Running the App
Execute the main script to start the server:
```bash
python app.py
```
The application will be available at `http://localhost:40001`.

## Development Conventions

- **Language Support**: Uses code `'a'` for American English and `'b'` for British English.
- **Voice Packs**: Voice files are loaded dynamically based on selection (e.g., `af_heart`, `am_michael`).
- **Custom Pronunciation**: Supports Markdown link syntax for phonemes, e.g., `[Kokoro](/kˈOkəɹO/)`.
- **Streaming**: Supports real-time audio streaming using Gradio's streaming output.
- **API**: The app is configured with `api_open=True`, allowing it to be used as a backend for other services.

## TODO / Future Improvements
- [ ] Add explicit `requirements.txt` or `pyproject.toml` for easier setup.
- [ ] Implement multi-language support beyond US/UK English if supported by the model.
- [ ] Add unit tests for synthesis pipelines.
