# Architecture

Kokoro TTS is a local-only CLI: one synthesis engine driven by a single batch-export front end, with no server or network surface beyond fetching the model/voices from Hugging Face. Everything routes through [[core/engine.py#generate_first]] and [[core/text.py#normalize_text]].

## Entry Point Routing

`app.py` parses args via [[cli.py#parse_args]], resolves a bare file-path positional argument to `--input` if needed, and calls [[cli.py#run_cli]]. With no input resolved, it prints help and exits instead of doing any work.

## Lazy Loading

Only the `KModel` weights are truly lazy-loaded on first use; `KPipeline` instances are created eagerly at import time since they're cheap.

[[core/engine.py#get_model]] caches one `KModel` instance per hardware target (GPU vs CPU) in the module-level `models` dict. `KPipeline` instances (`model=False`) are built eagerly for both language codes at import time, so "lazy loading" here specifically refers to the heavy model weights, not the pipelines themselves.

## Hardware Detection and GPU Fallback

`DEVICE` is auto-detected once at import (`cuda` > `mps` > `cpu`); generation falls back from GPU to CPU on any error instead of failing.

[[core/engine.py#generate_first]] attempts GPU synthesis via [[core/engine.py#forward_gpu]] and catches any exception, falling back to a CPU `KModel` and logging a warning rather than failing the request. `--gpu`/`--cpu` override auto-detection.

## Voice Packs and Language Routing

Voice IDs like `af_heart` encode language, gender, and name; the first character routes phonemization to one of two language pipelines.

The first character of the voice ID selects which of the two pipelines (`pipelines['a']` for American English, `pipelines['b']` for British English) handles phonemization. [[core/voices.py#CHOICES]] maps display labels (flag/gender emoji) to these IDs; `python app.py --list-voices` prints them.

## Hardcoded Pronunciation Overrides (G2P Lexicon Golds)

Some words are consistently mispronounced by Kokoro's grapheme-to-phoneme model and are patched directly into each pipeline's lexicon at import time, separate from the user-facing custom dictionary.

Each pipeline's `g2p.lexicon.golds` dict is seeded once at import (e.g. `kokoro` and `breathed`), with per-language IPA spellings for `pipelines['a']` vs `pipelines['b']`. Unlike [[text-pipeline#Text Processing Pipeline#Custom Pronunciation Dictionary|the custom pronunciation dictionary]], these overrides are code-level fixes for words that are wrong for every user and every input, not per-run substitutions.
