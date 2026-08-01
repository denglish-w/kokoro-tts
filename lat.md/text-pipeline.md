# Text Processing Pipeline

Long-form manuscripts need heavy preprocessing before TTS: references dropped, citations spoken aloud, OCR garble stripped, chapter outlines removed.

All of it lives in [[core/text.py#normalize_text]] and [[core/text.py#split_text_into_chapters]], applied to sermon books, commentaries, and OCR'd PDFs before they reach the synthesis engine.

## Normalization Order Matters

[[core/text.py#normalize_text]] applies transforms in a fixed order, and that order matters for correctness.

The sequence is: reference-section removal, quote/em-dash normalization, footnote-marker stripping, template-placeholder cleaning, year-to-words conversion, then the custom dictionary, then [[core/text.py#DEFAULT_EXPANSIONS]]. Expansions apply longest-pattern-first (sorted by regex string length descending) so multi-word abbreviations like "Hist. eccl." match before shorter overlapping ones like "Eccl".

## Reference/Bibliography Auto-Skip

[[core/text.py#remove_reference_sections]] is a line-scanning heuristic, not a fixed section boundary.

It starts skipping at a short, unindented line matching `abbreviations?|bibliography|works cited|references`, and stops skipping at a later short, unindented, blank-preceded line that doesn't match that pattern, or at a roman-numeral list item (e.g. "II. ") — treated as the start of the next real section.

## Chapter Splitting Pipeline

[[core/text.py#split_text_into_chapters]] runs a fixed sequence of transforms per chapter before slicing text at `chapter_regex` matches.

The sequence is: scripture citation stripping/expansion, epigraph formatting, em-dash replacement, bullet-list formatting, chapter-outline stripping, grid-matrix stripping, discussion-section stripping, then header normalization — producing ordered `(title, text)` tuples. An optional `skip_chapters_regex` filters out whole chapters (e.g. bibliography chapters) by title after splitting.

## Chapter Outline Stripping

Many source books repeat a table-of-contents-style outline at the top of every chapter; this strips it.

Chapter titles are harvested from the second non-empty line following each `chapter_regex` match, during the same pass that locates chapter boundaries. [[core/text.py#do_strip_chapter_outlines]] then removes any indented block within the first 25 lines of a chapter whose (case/article-insensitive) text matches one of those harvested titles.

## Discussion Section Skipping

[[core/text.py#strip_discussion_sections]] drops "Discussion and Response" / "Discussion Questions" blocks from chapters.

It resumes normal output at the next short, unindented, non-list-item line — used as a proxy for "the next major heading".

## Grid Matrix Stripping (OCR Table Garble)

[[core/text.py#strip_grid_matrices_logic]] is hardcoded to one specific book's flattened OCR table layout.

It starts skipping when it finds the three-line sequence "Cognition: Thought and Belief" / "Affection: Desire and Feeling" / "Volition: Will and Choice", and resumes at a heading containing "reading", "reflecting", "relating", "renewal", or "helping".

## Scripture Citation Handling

Two mutually exclusive modes, selected by `skip_scripture_citations` vs `expand_scripture_citations`.

[[core/text.py#strip_scripture_citations]] deletes parenthetical citations like "(John 3:16)" outright; [[core/text.py#expand_scripture_citations_logic]] instead rewrites them to spoken form ("(John chapter 3, verse 16)") via a book-abbreviation lookup table, joining multiple citations in one parenthetical with commas and a trailing "and".

## Epigraph and Bullet List Formatting

Visual formatting that doesn't read aloud (attributed quote blocks, bullet glyphs) gets rewritten into spoken prose.

[[core/text.py#format_epigraphs_logic]] detects an attributed quote block (lines followed by an em/en-dash-prefixed attribution line) and rewrites it as `... Quote by X: "..." ...`. [[core/text.py#format_bullet_lists_logic]] converts bullet lists (`•`, `*`, `-`) into spoken sequence words (First, Second, ... then "Number N").

## Template Placeholder Cleaning

[[core/text.py#clean_placeholders]] replaces counseling-book bracketed placeholders with generic spoken substitutes.

Known placeholders like `[specific person]` or `[situation]` map to fixed substitutes; any remaining bracket characters are then stripped outright — this project's source texts are drawn from pastoral counseling books that use fill-in-the-blank bracket templates.

## Custom Pronunciation Dictionary

User-supplied `{phrase: replacement}` pairs override default pronunciation before any built-in expansions run.

Pairs are parsed from "Key: Value" lines by [[core/text.py#parse_custom_dict]] and applied case-insensitively before [[core/text.py#DEFAULT_EXPANSIONS]], sorted longest-key-first so multi-word keys aren't partially shadowed by shorter ones matching first.

## Abbreviation Scanning

[[core/text.py#scan_for_potential_abbreviations]] flags acronyms and abbreviations not already covered, so users can supply expansions before synthesis.

It flags all-caps acronyms and short dotted abbreviations not already covered by `DEFAULT_EXPANSIONS` or the custom dictionary, using a system dictionary file (falling back to a small hardcoded common-word list via [[core/text.py#is_normal_word]]) to exclude ordinary words. Surfaced via the CLI's `--scan-abbrev` interactive prompt and the UI's Scan button.

## Metadata Extraction and Filename Generation

Title/author metadata drives output filenames, extracted from several possible sources in priority order.

[[core/text.py#extract_metadata_from_text]] and [[core/text.py#extract_metadata_from_pdf]] pull title/author from YAML frontmatter, "Title:"/"Author:" lines, markdown headers, or PDF document properties. Both CLI and UI export paths use the result (falling back to manual overrides, then to the input filename) via [[core/text.py#clean_filename]] to name output as `Author - Title[ - Chapter].wav`.

## Coordinate-Based PDF Column Splitting

Double-column academic PDFs need geometric reassembly, not just linear text extraction, to stay in reading order.

[[core/text.py#extract_text_from_pdf]]'s `split_columns` mode uses a `pypdf` visitor callback keyed on each text run's transform-matrix X-offset relative to the page midpoint, emitting all of the left column then all of the right column instead of interleaving lines across columns.
