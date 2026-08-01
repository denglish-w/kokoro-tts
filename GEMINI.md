# Kokoro TTS CLI

A high-quality, local-only Text-to-Speech (TTS) command-line tool powered by the [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) model.

## Project Overview

This project provides a command-line tool for generating speech from text or PDF files. It leverages the `kokoro` library for fast, high-quality synthesis with support for multiple voices and languages. There is no server and no web interface — everything runs as a single local process, and the only network traffic is the one-time Hugging Face download of the model and voice packs (cached after first use).

### Key Features
- **Batch Export**: Automatically split long texts (like books) into chapters and export as WAV/MP3 files. Supports resuming interrupted exports and combining chapters into a single file.
- **Secondary Voice**: Alternate between two voices by chapter, e.g. to distinguish a narrator from a second speaker.
- **Custom Pronunciation**: Support for Markdown link syntax for phonemes (e.g., `[Kokoro](/kˈOkəɹO/)`) and a custom `Key: Value` replacement dictionary file.
- **Text Normalization**: Smart handling of years, abbreviations, and auto-skipping of reference/bibliography sections.
- **Hardware Acceleration**: Automatic detection and support for CPU, CUDA-enabled GPUs, and Apple Silicon (MPS).

### Key Technologies
- **Python**: Core logic and scripting.
- **Kokoro**: TTS engine (KModel and KPipeline).
- **PyTorch**: Underlying deep learning framework.

## Project Structure

- `app.py`: Main entry point. Parses args and hands off to the CLI.
- `cli.py`: All CLI logic — argument parsing and the batch synthesis loop.
- `core/`:
  - `engine.py`: TTS engine with lazy model loading, hardware auto-detection, and GPU-to-CPU fallback logic.
  - `text.py`: Text normalization, chapter splitting, reference removal, and the custom pronunciation dictionary parser.
  - `voices.py`: The `CHOICES` map of display labels to voice IDs.
- `sample_texts/`: Sample manuscripts and quotes used for local testing.
- `requirements.txt`: Project dependencies.
- `.venv/`: Python virtual environment.

## Building and Running

### Prerequisites
- Python 3.12+
- [ffmpeg](https://ffmpeg.org/) (required for MP3 export and audio processing)

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

Use `--input` to process a text or PDF file into audio chapters. By default, audio is exported to `~/Documents/Kokoro_Exports`.
```bash
python app.py --input my_book.txt --voice af_heart --speed 1.0
```

Other useful flags:
```bash
python app.py --list-voices                                   # print available voice IDs and exit
python app.py --input my_book.txt --tokenize                  # print phonemes per chapter instead of synthesizing
python app.py --input my_book.txt --combine --format mp3       # combine all chapters into one MP3
python app.py --input my_book.txt --secondary-voice bf_emma    # alternate voices by chapter
python app.py --input my_book.txt --dict pronunciation.txt     # custom pronunciation dictionary file
python app.py --input my_book.txt --no-resume                  # always regenerate, ignoring existing output files
python app.py --input my_book.txt --cpu                        # force CPU even if a GPU is available
```
Run `python app.py --help` for the full flag list.

## Development Conventions

- **Lazy Loading**: Models and voices are loaded on demand during generation to minimize memory footprint and improve startup time.
- **Hardware Detection**: The app automatically selects `cuda`, `mps`, or `cpu`. If a GPU error occurs during generation, it gracefully falls back to CPU. Use `--gpu`/`--cpu` to override.
- **Export Naming**: Combined audio exports use the base filename of the input (e.g., `input.wav`) for better organization.
- **Language Support**: Uses code `'a'` for American English and `'b'` for British English.
- **Chapter Splitting**: Uses regex (default: `^Chapter\s+\d+`) to identify chapter breaks in text files.
- **Resume**: Batch exports skip chapters whose output file already exists, on by default (`--no-resume` to disable).

## TODO / Future Improvements
- [ ] Add unit tests for synthesis pipelines.
- [ ] Implement multi-language support beyond US/UK English.
- [x] Add support for more audio formats (MP3).
- [x] Add resume support for batch exports.
- [x] Remove the web UI and all network-facing surface.
