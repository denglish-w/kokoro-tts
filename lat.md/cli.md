# CLI

The command line is the only front end: [[cli.py#run_cli]] drives batch export of a text/PDF file into per-chapter audio, sharing [[core/engine.py#generate_first]] and the [[text-pipeline|text preprocessing pipeline]] with no other entry point.

## Batch Export and Resume

[[cli.py#run_cli]] writes chapters to disk incrementally and can resume a synthesis run that was interrupted partway through.

It writes each chapter to disk incrementally rather than holding the whole book in memory, and `--resume` (on by default) skips regenerating any chapter whose output file already exists (checked in-loop, not up front) — needed because full-book synthesis can take a long time. `--no-resume` always regenerates.

## Secondary Voice Alternation

When `--secondary-voice` is set, [[cli.py#run_cli]] alternates between the primary and secondary voice by chapter index parity (`idx % 2`) — used to distinguish a narrator voice from a second voice across a long book, or simply to add variety.

## Combine vs Separate Audio Files

`--combine` buffers all chapter audio arrays in memory and concatenates them into one file at the end instead of writing each chapter to its own file; this trades peak memory usage for a single continuous audio file.

## Custom Dictionary Auto-Discovery

If `--dict` is not passed, [[cli.py#run_cli]] looks for a sibling file named `<input-basename>.custom_dict.txt` next to `--input` and loads it automatically, so per-manuscript dictionaries don't need to be specified on every run.

An explicit `--dict` always takes priority over the auto-detected sibling file. The convention only replaces the extension: `txt_files/book.txt` looks for `txt_files/book.custom_dict.txt`, parsed the same way as an explicitly-passed dictionary via [[core/text.py#parse_custom_dict]].
