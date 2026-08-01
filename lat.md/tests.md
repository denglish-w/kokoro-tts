---
lat:
  require-code-mention: true
---
# Tests

Unit test specifications for the pure-function text-preprocessing transforms in [[core/text.py#normalize_text|core/text.py]], which don't require the Kokoro model to be loaded and so can be tested as plain string-in/string-out functions.

## Text Preprocessors

Formatting and normalization helpers tested against fixed input/output string pairs in `tests/test_preprocessors.py`.

### Title case heading

[[core/text.py#title_case_heading]] must correctly downcase small words (articles, short prepositions) except at the start or end of the string, while still capitalizing the first letter after leading punctuation.

### Chapter header normalization

[[core/text.py#normalize_chapter_header]] must merge a "CHAPTER 12" line plus a following ALL-CAPS title line into a single "Chapter 12: Title Case" header, joining any colon-separated sub-title with an em dash.

### Epigraph formatting

[[core/text.py#format_epigraphs_logic]] must detect a multi-line quote followed by an em/en-dash attribution line and rewrite it into a single spoken `... Quote by X: "..." ...` line.

### Bullet list formatting

[[core/text.py#format_bullet_lists_logic]] must convert a run of bullet-marked lines into spoken sequence words (First, Second, ...) while preserving the original indentation.

### Scripture citation expansion

[[core/text.py#expand_scripture_citations_logic]] must expand parenthetical citations — including multi-reference and verse-range citations — into fully spoken book/chapter/verse phrases, joined with commas and a trailing "and".

### Template placeholder cleaning

[[core/text.py#clean_placeholders]] must replace known bracketed counseling placeholders with generic spoken substitutes and strip any remaining bracket characters, including ones not in the known-placeholder list.

### Custom pronunciation dictionary parsing

[[core/text.py#parse_custom_dict]] must parse `Key: Value` lines into a dict, ignore blank and colonless lines, split only on the first colon so values may contain their own, and return `None` for blank/empty input.

## PDF & Abbreviation Scanning

Tests in `tests/test_pdf_and_abbrev.py` covering abbreviation detection, PDF text extraction, and metadata parsing.

### Abbreviation scan counts and exclusions

[[core/text.py#scan_for_potential_abbreviations]] must count acronym and dotted-abbreviation occurrences correctly, exclude anything already covered by [[core/text.py#DEFAULT_EXPANSIONS]], and additionally exclude anything covered by a passed-in `custom_dict`.

### PDF text extraction concatenation

[[core/text.py#extract_text_from_pdf]] must concatenate extracted text from each `PdfReader` page in order, joined by newlines.

### Metadata extraction from text formats

[[core/text.py#extract_metadata_from_text]] must recover title/author from YAML frontmatter, plain "Title:"/"Author:" lines, and markdown "# Title" / "## Author" headers, in that priority order.
