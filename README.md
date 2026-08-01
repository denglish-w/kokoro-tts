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

## CLI Flags

| Flag | Default | Description |
| --- | --- | --- |
| `--input` | — | Input text/PDF file for batch processing |
| `--output-dir` | `~/Documents/Kokoro_Exports` | Directory to save audio chapters |
| `--regex` | `^Chapter\s+\d+` | Regex for splitting chapters |
| `--voice` | `am_michael` | Voice ID to use |
| `--secondary-voice` | none | Secondary voice ID; alternates with `--voice` by chapter index |
| `--speed` | `1.0` | Playback speed |
| `--gpu` | auto-detect | Force use of GPU |
| `--cpu` | auto-detect | Force use of CPU |
| `--list-voices` | off | List available voice IDs and exit |
| `--tokenize` | off | Print phonemes for each chapter instead of synthesizing audio |
| `--scan-abbrev` | off | Scan for unrecognized abbreviations and prompt interactively to expand them |
| `--dict` | none | Path to a custom pronunciation dictionary file (`Key: Value` per line) |
| `--title` | none | Manual override for Title metadata (used in filenames) |
| `--author` | none | Manual override for Author metadata (used in filenames) |
| `--format` | `mp3` | Output audio format (`wav` or `mp3`) |
| `--bitrate` | `192k` | MP3 bitrate (e.g. `192k`, `64k`, `32k`) |
| `--combine` | off | Combine all chapters into a single audio file |
| `--resume` / `--no-resume` | on | Skip chapters whose output file already exists |
| `--skip-chapters-regex` | none | Chapters whose title matches this regex will not be generated |
| `--skip-references` / `--no-skip-references` | on | Heuristically remove long bibliography/reference lists before generation |
| `--strip-outlines` / `--no-strip-outlines` | on | Strip repeated chapter outlines |
| `--skip-discussion` / `--no-skip-discussion` | on | Skip Discussion and Response sections |
| `--strip-grid` / `--no-strip-grid` | on | Strip flattened grid matrices |
| `--skip-citations` / `--no-skip-citations` | on | Skip parenthetical scripture citations |
| `--split-columns` | off | Split double-column layout PDFs horizontally |
| `--format-epigraphs` / `--no-format-epigraphs` | on | Format epigraphs and quotes block |
| `--format-bullets` / `--no-format-bullets` | on | Format bullet points list to sequences |
| `--expand-citations` | off | Expand inline scripture reference abbreviations to spoken text |
| `--clean-placeholders` / `--no-clean-placeholders` | on | Clean template placeholders to generic words |
| `--replace-em-dashes` / `--no-replace-em-dashes` | on | Replace em dashes with pauses (comma) |

Run `python app.py --help` to see this list from the CLI itself.

See [GEMINI.md](GEMINI.md) for detailed architecture and development guidelines.
