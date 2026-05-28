import re
from num2words import num2words

# Default abbreviation expansions (case-sensitive regex patterns to text expansions)
DEFAULT_EXPANSIONS = {
    # Scholarly / General
    r'\bNT\b': 'New Testament',
    r'\bOT\b': 'Old Testament',
    r'\bN\.T\.(?=\s|[.,;:]|$)': 'New Testament',
    r'\bO\.T\.(?=\s|[.,;:]|$)': 'Old Testament',
    r'\bLXX\b': 'Septuagint',
    r'\bMT\b': 'Masoretic Text',
    r'\bDSS\b': 'Dead Sea Scrolls',
    r'\bWBC\b': 'Word Biblical Commentary',
    r'\bTR\b': 'Textus Receptus',
    r'\bFS\b': 'Festschrift',
    r'\bCE\b': 'Common Era',
    r'\bBCE\b': 'Before Common Era',
    r'\bC\.E\.(?=\s|[.,;:]|$)': 'Common Era',
    r'\bB\.C\.E\.(?=\s|[.,;:]|$)': 'Before Common Era',
    r'\bB\.C\.(?=\s|[.,;:]|$)': 'Before Christ',
    r'\bA\.D\.(?=\s|[.,;:]|$)': 'Anno Domini',
    r'\bA\.T\.(?=\s|[.,;:]|$)': 'A. T.',
    r'\bNTL\b': 'New Testament Library',
    r'\bart\.\s+cit\.(?=\s|[.,;:]|$)': 'article cited',
    r'\babbr\.(?=\s|[.,;:]|$)': 'abbreviation',
    
    # Latin / Common (with boundary lookahead for periods)
    r'\bc\.(?=\s|[.,;:]|$)': 'circa',
    r'\bca\.(?=\s|[.,;:]|$)': 'circa',
    r'\bcf\.(?=\s|[.,;:]|$)': 'compare',
    r'\be\.g\.(?=\s|[.,;:]|$)': 'for example',
    r'\bi\.e\.(?=\s|[.,;:]|$)': 'that is',
    r'\bet al\.(?=\s|[.,;:]|$)': 'and others',
    r'\bibid\.(?=\s|[.,;:]|$)': 'in the same place',
    r'\bvv\.(?=\s|[.,;:]|$)': 'verses',
    r'\bv\.(?=\s|[.,;:]|$)': 'verse',
    r'\bvs\.(?=\s|[.,;:]|$)': 'verse',
    r'\bvss\.(?=\s|[.,;:]|$)': 'verses',
    r'\bff\.(?=\s|[.,;:]|$)': 'following',
    r'\bf\.(?=\s|[.,;:]|$)': 'following',
    r'\bq\.v\.(?=\s|[.,;:]|$)': 'which see',
    r'\bs\.v\.(?=\s|[.,;:]|$)': 'under the word',
    r'\bviz\.(?=\s|[.,;:]|$)': 'namely',
    r'\bch\.(?=\s|[.,;:]|$)': 'chapter',
    r'\bchs\.(?=\s|[.,;:]|$)': 'chapters',
    r'\bpp\.(?=\s|[.,;:]|$)': 'pages',
    r'\bvol\.(?=\s|[.,;:]|$)': 'volume',
    r'\bvols\.(?=\s|[.,;:]|$)': 'volumes',
    r'\bed\.(?=\s|[.,;:]|$)': 'edition',
    
    # Languages
    r'\bAkkad\.(?=\s|[.,;:]|$)': 'Akkadian',
    r'\bAram\.(?=\s|[.,;:]|$)': 'Aramaic',
    r'\bHeb\.(?=\s|[.,;:]|$)': 'Hebrew',
    r'\bGr\.(?=\s|[.,;:]|$)': 'Greek',
    r'\bSyr\.(?=\s|[.,;:]|$)': 'Syriac',
    r'\bLat\.(?=\s|[.,;:]|$)': 'Latin',
    
    # Biblical Books
    r'\bGen\b': 'Genesis',
    r'\bExod\b': 'Exodus',
    r'\bLev\b': 'Leviticus',
    r'\bNum\b': 'Numbers',
    r'\bDeut\b': 'Deuteronomy',
    r'\bJosh\b': 'Joshua',
    r'\bJudg\b': 'Judges',
    r'\bRuth\b': 'Ruth',
    r'\b1\s+Sam\b': 'First Samuel',
    r'\b2\s+Sam\b': 'Second Samuel',
    r'\b1\s+Kgs\b': 'First Kings',
    r'\b2\s+Kgs\b': 'Second Kings',
    r'\b1\s+Chr\b': 'First Chronicles',
    r'\b2\s+Chr\b': 'Second Chronicles',
    r'\bEzra\b': 'Ezra',
    r'\bNeh\b': 'Nehemiah',
    r'\bEsth\b': 'Esther',
    r'\bJob\b': 'Job',
    r'\bPs\.(?=\s|[.,;:]|$)': 'Psalm',
    r'\bPss\.(?=\s|[.,;:]|$)': 'Psalms',
    r'\bProv\.(?=\s|[.,;:]|$)': 'Proverbs',
    r'\bEccl\b': 'Ecclesiastes',
    r'\bCant\b': 'Song of Solomon',
    r'\bIsa\.(?=\s|[.,;:]|$)': 'Isaiah',
    r'\bJer\.(?=\s|[.,;:]|$)': 'Jeremiah',
    r'\bLam\b': 'Lamentations',
    r'\bEzek\b': 'Ezekiel',
    r'\bDan\.(?=\s|[.,;:]|$)': 'Daniel',
    r'\bHos\b': 'Hosea',
    r'\bJoel\b': 'Joel',
    r'\bAmos\b': 'Amos',
    r'\bObad\b': 'Obadiah',
    r'\bJonah\b': 'Jonah',
    r'\bMic\b': 'Micah',
    r'\bNah\b': 'Nahum',
    r'\bHab\b': 'Habakkuk',
    r'\bZeph\b': 'Zephaniah',
    r'\bHag\b': 'Haggai',
    r'\bZech\b': 'Zechariah',
    r'\bMal\b': 'Malachi',
    r'\bMatt\b': 'Matthew',
    r'\bMark\b': 'Mark',
    r'\bLuke\b': 'Luke',
    r'\bJohn\b': 'John',
    r'\bActs\b': 'Acts',
    r'\bRom\b': 'Romans',
    r'\b1\s+Cor\b': 'First Corinthians',
    r'\b2\s+Cor\b': 'Second Corinthians',
    r'\bGal\.(?=\s|[.,;:]|$)': 'Galatians',
    r'\bEph\b': 'Ephesians',
    r'\bPhil\b': 'Philippians',
    r'\bCol\b': 'Colossians',
    r'\b1\s+Thess\b': 'First Thessalonians',
    r'\b2\s+Thess\b': 'Second Thessalonians',
    r'\b1\s+Tim\b': 'First Timothy',
    r'\b2\s+Tim\b': 'Second Timothy',
    r'\bTitus\b': 'Titus',
    r'\bPhilem\b': 'Philemon',
    r'\bHeb\b': 'Hebrews',
    r'\bJames\b': 'James',
    r'\b1\s+Pet\b': 'First Peter',
    r'\b2\s+Pet\b': 'Second Peter',
    r'\b1\s+John\b': 'First John',
    r'\b2\s+John\b': 'Second John',
    r'\b3\s+John\b': 'Third John',
    r'\bJude\b': 'Jude',
    r'\bRev\b': 'Revelation',
    r'\bEcclus\b': 'Ecclesiasticus',
    r'\bWisd\.(?=\s|[.,;:]|$)': 'Wisdom',
    
    # Historical / Patristic
    r'\bAdv\.\s+Haer\.(?=\s|[.,;:]|$)': 'Adversus Haereses',
    r'\bHaer\.(?=\s|[.,;:]|$)': 'Against Heresies',
    r'\bHist\.\s+eccl\.(?=\s|[.,;:]|$)': 'Historia Ecclesiastica',
    r'\bH\.\s*E\.(?=\s|[.,;:]|$)': 'Historia Ecclesiastica',
    r'\bAg\.\s+Ap\.(?=\s|[.,;:]|$)': 'Against Apion',
    r'\bAnt\.(?=\s|[.,;:]|$)': 'Antiquities of the Jews',
    r'\bLegat\.(?=\s|[.,;:]|$)': 'Legatio ad Gaium',
    r'\bPan\.(?=\s|[.,;:]|$)': 'Panegyricus',
    r'\bDom\.(?=\s|[.,;:]|$)': 'Domitian',
    r'\bIgn\.(?=\s|[.,;:]|$)': 'Ignatius',
    r'\bSmyrn\.(?=\s|[.,;:]|$)': 'Smyrnaeans',
    r'\bb\.\s+Sanhedrin(?=\s|[.,;:]|$)': 'Babylonian Sanhedrin',
    
    # Mishnah
    r'\bm\.\s+Šabb\.(?=\s|[.,;:]|$)': 'Mishnah Shabbat',
    r'\bm\.\s+Kelim(?=\s|[.,;:]|$)': 'Mishnah Kelim',
    r'\bm\.\s+Sukkah(?=\s|[.,;:]|$)': 'Mishnah Sukkah',
    r'\bm\.(?=\s|[.,;:]|$)': 'Mishnah',
    
    # Manuscripts
    r'𝔓52': 'Papyrus 52',
    r'\bP52\b': 'Papyrus 52',
    r'\bP66\b': 'Papyrus 66',
    r'\bP75\b': 'Papyrus 75',
    
    # Other
    r'\bSB\b': 'La Sainte Bible',
    
    # Symbols
    r'§': ' section ',
}

def remove_reference_sections(text):
    lines = text.split('\n')
    out_lines = []
    skipping = False
    skip_regex = re.compile(r'\b(abbreviations?|bibliograph(y|ies)|works cited|references)\b', re.IGNORECASE)
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            if not skipping:
                out_lines.append(line)
            continue
            
        if not skipping:
            is_unindented = not line.startswith(' ')
            is_short = len(stripped) < 100
            
            if is_short and is_unindented and skip_regex.search(stripped):
                skipping = True
                continue
        else:
            is_unindented = not line.startswith(' ')
            is_short = len(stripped) < 80
            prev_blank = i > 0 and not lines[i-1].strip()
            is_roman = re.match(r'^[IVXLCDM]+\.\s+', stripped)
            
            if (is_short and is_unindented and prev_blank and not skip_regex.search(stripped)) or is_roman:
                skipping = False
                
        if not skipping:
            out_lines.append(line)
            
    return '\n'.join(out_lines)

def normalize_text(text, custom_dict=None, skip_references=True):
    # Auto-skip reference sections first
    if skip_references:
        text = remove_reference_sections(text)

    # Standardize line endings and whitespace
    text = text.replace('\r\n', '\n').strip()
    
    # Remove footnote markers like [1], [12], (1), ^1
    text = re.sub(r'\[\d+\]|\(\d+\)|\^\d+', '', text)
    
    # Normalize 4-digit years (1000-2099) to read as "sixteen forty-five"
    def year_to_words(match):
        year = int(match.group(0))
        return num2words(year, to='year')
    
    text = re.sub(r'\b(1[0-9]{3}|20[0-9]{2})\b', year_to_words, text)
    
    # Apply custom dictionary replacements FIRST
    if custom_dict:
        # Sort by length descending so longer phrases match before shorter ones
        for k in sorted(custom_dict.keys(), key=len, reverse=True):
            # Case insensitive exact match (using word boundaries if alphanumeric)
            pattern = rf'\b{re.escape(k)}\b' if k.replace(' ', '').isalnum() else re.escape(k)
            text = re.sub(pattern, custom_dict[k], text, flags=re.IGNORECASE)
    
    # Apply expansions sorted by pattern length descending
    # to ensure longer patterns (like 'Hist. eccl.') match before shorter ones ('Eccl')
    sorted_patterns = sorted(DEFAULT_EXPANSIONS.keys(), key=len, reverse=True)
    for pattern in sorted_patterns:
        text = re.sub(pattern, DEFAULT_EXPANSIONS[pattern], text, flags=re.IGNORECASE)
        
    return text

def split_text_into_chapters(text, chapter_regex, custom_dict=None, skip_references=True, skip_chapters_regex=None):
    text = normalize_text(text, custom_dict, skip_references=skip_references)
    chapters = []
    if not chapter_regex.strip():
        chapters.append(("Full_Audio", text))
    else:
        matches = list(re.finditer(chapter_regex, text, flags=re.MULTILINE | re.IGNORECASE))
        if not matches:
            chapters.append(("Full_Audio", text))
        else:
            if matches[0].start() > 0:
                intro = text[:matches[0].start()].strip()
                if intro:
                    chapters.append(("00_Intro", intro))
            
            for i in range(len(matches)):
                start = matches[i].start()
                end = matches[i+1].start() if i + 1 < len(matches) else len(text)
                chapter_text = text[start:end].strip()
                
                title = matches[i].group(0).strip()
                title = re.sub(r'[\\/*?:"<>|]', "", title)
                title = title.replace(" ", "_")
                chapters.append((f"{i+1:02d}_{title}", chapter_text))
                
    # Filter out chapters if skip_chapters_regex is provided
    if skip_chapters_regex and skip_chapters_regex.strip():
        try:
            skip_pattern = re.compile(skip_chapters_regex, re.IGNORECASE)
            chapters = [(title, content) for title, content in chapters if not skip_pattern.search(title)]
        except re.error:
            pass # ignore invalid skip regex

    return chapters

def extract_text_from_pdf(pdf_path):
    """
    Extracts text page-by-page from a PDF file.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pypdf is not installed. Please run 'pip install pypdf' to use PDF features.")
        
    reader = PdfReader(pdf_path)
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n".join(text_parts)

def clean_filename(name):
    """
    Sanitizes a string to make it safe for filenames.
    """
    import re
    # Remove characters that are illegal in Windows/macOS/Linux filenames
    cleaned = re.sub(r'[\\/*?:"<>|\x00]', "", name)
    cleaned = re.sub(r'\s+', " ", cleaned)
    return cleaned.strip()

def extract_metadata_from_pdf(pdf_path):
    """
    Extracts metadata (title, author) from a PDF file.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        return {}
        
    try:
        reader = PdfReader(pdf_path)
        meta = reader.metadata
        if not meta:
            return {}
        
        # Get standard properties
        title = meta.title
        author = meta.author
        
        # Fallback to key access if title/author properties are empty
        if not title and '/Title' in meta:
            title = meta['/Title']
        if not author and '/Author' in meta:
            author = meta['/Author']
            
        return {
            "title": title.strip() if title else None,
            "author": author.strip() if author else None
        }
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Error reading PDF metadata: {e}")
        return {}

def extract_metadata_from_text(text):
    """
    Extracts metadata (title, author) from a text/markdown file's content.
    Supports YAML frontmatter and key-value lines like 'Title: ...' and 'Author: ...'.
    """
    meta = {"title": None, "author": None}
    if not text:
        return meta
        
    # 1. Try to parse YAML-like frontmatter
    stripped_text = text.lstrip()
    if stripped_text.startswith("---"):
        parts = stripped_text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            for line in frontmatter.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip().lower()
                    val = val.strip().strip('"').strip("'").strip()
                    if key in ["title", "author"]:
                        meta[key] = val

    # 2. If frontmatter didn't find both, try to match Title: and Author: at the top of the file
    lines = text.splitlines()[:50]
    for line in lines:
        if not meta["title"]:
            title_match = re.match(r'^\s*title\s*:\s*(.+)$', line, re.IGNORECASE)
            if title_match:
                meta["title"] = title_match.group(1).strip().strip('"').strip("'").strip()
        if not meta["author"]:
            author_match = re.match(r'^\s*author\s*:\s*(.+)$', line, re.IGNORECASE)
            if author_match:
                meta["author"] = author_match.group(1).strip().strip('"').strip("'").strip()

    # 3. Try markdown headers if still missing
    for line in lines[:5]:
        stripped = line.strip()
        if not meta["title"] and stripped.startswith("# "):
            meta["title"] = stripped[2:].strip()
        elif not meta["author"] and stripped.startswith("## ") and ("by" in stripped.lower() or len(stripped) < 40):
            meta["author"] = stripped[3:].strip()
            if meta["author"].lower().startswith("by "):
                meta["author"] = meta["author"][3:].strip()

    return meta

_DICT_WORDS = None
FALLBACK_COMMON_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
    'life', 'word', 'god', 'wise', 'hope', 'ways', 'men', 'man', 'said', 'may', 'into', 'than', 'then', 'now', 'will', 'was', 'were', 'has', 'had', 'been', 'is', 'am',
    'are', 'would', 'should', 'could', 'did', 'do', 'does', 'done', 'doing', 'go', 'goes', 'went', 'gone', 'going', 'here', 'there', 'where', 'when', 'why', 'how',
    'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can',
    'will', 'just', 'should', 'now'
}

def _get_dict_words():
    global _DICT_WORDS
    if _DICT_WORDS is not None:
        return _DICT_WORDS
    
    import os
    _DICT_WORDS = set()
    for path in ['/usr/share/dict/words', '/etc/dictionaries-common/words', '/usr/dict/words']:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        _DICT_WORDS.add(line.strip().lower())
                break
            except Exception:
                pass
    return _DICT_WORDS

def is_normal_word(word):
    w = word.lower().rstrip('.')
    dict_words = _get_dict_words()
    if dict_words:
        return w in dict_words
    return w in FALLBACK_COMMON_WORDS

def scan_for_potential_abbreviations(text, custom_dict=None):
    """
    Scans the text for potential abbreviations and acronyms that:
    1. Are not in the default expansions dictionary.
    2. Are not in the custom_dict (if provided).
    Returns a dictionary of {abbreviation: count} sorted by frequency descending.
    """
    # 1) Acronyms: All-caps words of length 2-6
    acronym_pattern = re.compile(r'\b[A-Z]{2,6}\b')
    # 2) Words ending with a period (1-4 letters) followed by space, e.g., "cf. ", "vol. "
    abbrev_pattern = re.compile(r'\b[A-Za-z]{1,4}\.(?=\s)')
    
    found_candidates = {}
    
    # Find all acronyms
    for match in acronym_pattern.finditer(text):
        word = match.group(0)
        if word not in found_candidates:
            found_candidates[word] = 0
        found_candidates[word] += 1
        
    # Find short dotted words
    for match in abbrev_pattern.finditer(text):
        word = match.group(0)
        if word not in found_candidates:
            found_candidates[word] = 0
        found_candidates[word] += 1
        
    # Exclude common words, standard parts of sentences, and normal English words
    EXCLUDE_WORDS = {
        'A', 'I', 'THE', 'AND', 'BUT', 'FOR', 'HIS', 'HER', 'ITS', 'OUR', 'YOU', 'THEY', 'WHO', 'WHOM',
        'WAS', 'WERE', 'ARE', 'HAS', 'HAD', 'HAVE', 'CAN', 'MAY', 'NOT', 'YES', 'NO', 'SO', 'IF', 'OR',
        'IN', 'ON', 'AT', 'TO', 'OF', 'BY', 'WITH', 'FROM', 'UP', 'DOWN', 'OUT', 'OFF', 'OVER', 'UNDER',
        'A.', 'I.', 'HE.', 'SHE.', 'IT.', 'THE.', 'AND.', 'BUT.', 'SO.', 'IF.', 'OR.', 'IN.', 'ON.', 'AT.', 'TO.', 'OF.'
    }
    
    refined_candidates = {}
    for word, count in found_candidates.items():
        upper_word = word.upper()
        if upper_word in EXCLUDE_WORDS or word in EXCLUDE_WORDS or is_normal_word(word):
            continue
            
        # Check if already expanded by DEFAULT_EXPANSIONS
        is_already_expanded = False
        for pattern_str in DEFAULT_EXPANSIONS:
            try:
                # Compile default expansion regex and check if it matches the candidate
                if re.search(pattern_str, word, flags=re.IGNORECASE):
                    is_already_expanded = True
                    break
            except re.error:
                pass
                
        if custom_dict:
            for k in custom_dict:
                if re.search(rf'\b{re.escape(k)}\b', word, flags=re.IGNORECASE):
                    is_already_expanded = True
                    break
                    
        if not is_already_expanded:
            refined_candidates[word] = count
            
    # Sort candidates by count descending
    return dict(sorted(refined_candidates.items(), key=lambda x: x[1], reverse=True))
