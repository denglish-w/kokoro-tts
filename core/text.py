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

def normalize_text(text, custom_dict=None, skip_references=True, replace_em_dashes=True, clean_template_placeholders=True):
    # Auto-skip reference sections first
    if skip_references:
        text = remove_reference_sections(text)

    # Standardize line endings and whitespace
    text = text.replace('\r\n', '\n').strip()
    
    # Remove footnote markers like [1], [12], (1), ^1
    text = re.sub(r'\[\d+\]|\(\d+\)|\^\d+', '', text)
    
    # Clean template placeholders first if requested
    if clean_template_placeholders:
        text = clean_placeholders(text)
    
    # Replace em dashes with pauses (comma) if requested
    if replace_em_dashes:
        text = text.replace('—', ', ').replace('--', ', ')
    
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

def strip_discussion_sections(text):
    """
    Strips out 'Discussion and Response' or 'Discussion Questions' sections.
    Stops skipping if it encounters a major, unindented section header (e.g., 'Conclusion').
    """
    lines = text.split('\n')
    out_lines = []
    i = 0
    skipping = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if not skipping:
            if re.match(r'^\s*(discussion\s+and\s+response|discussion\s+questions)\b', stripped, re.IGNORECASE):
                skipping = True
                i += 1
                continue
            out_lines.append(line)
            i += 1
        else:
            # Stop skipping if we hit a major header
            is_unindented = len(line) > 0 and not line.startswith(' ') and not line.startswith('\t')
            is_header_like = is_unindented and len(stripped) < 50 and not re.match(r'^(\d+[\.\)]|•|\*)', stripped)
            
            if is_header_like:
                skipping = False
                out_lines.append(line)
                i += 1
            else:
                i += 1
                
    return '\n'.join(out_lines).strip()

def do_strip_chapter_outlines(chapter_text, chapter_titles):
    """
    Strips the repeated table of contents / outlines at the beginning of a chapter.
    """
    lines = chapter_text.split('\n')
    out_lines = []
    i = 0
    
    def normalize_for_match(s):
        s = s.lower().strip()
        s = s.replace('An ', '').replace('A ', '')
        s = s.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
        return s
        
    normalized_titles = {normalize_for_match(t) for t in chapter_titles}
    
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()
        
        is_indented = line.startswith(' ') or line.startswith('\t')
        
        if is_indented and normalized_titles and normalize_for_match(stripped_line) in normalized_titles and i < 25:
            # Found a match, skip all contiguous matching lines or empty lines
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                if not next_stripped:
                    i += 1
                    continue
                is_next_indented = next_line.startswith(' ') or next_line.startswith('\t')
                if is_next_indented and normalize_for_match(next_stripped) in normalized_titles:
                    i += 1
                else:
                    break
            continue
        else:
            out_lines.append(line)
            i += 1
            
    return '\n'.join(out_lines).strip()

def strip_scripture_citations(text):
    """
    Strips out parenthetical scripture citations (e.g. (John 3:16)).
    """
    books_pattern = r'\b(Gen|Exod|Lev|Num|Deut|Josh|Judg|Ruth|Sam|Kings?|Kgs|Chr|Chron|Ezra|Neh|Esth|Job|Ps|Pss|Psalm|Psalms|Prov|Proverbs|Eccl|Ecclesiastes|Cant|Song|Isa|Isaiah|Jer|Jeremiah|Lam|Lamentations|Ezek|Ezekiel|Dan|Daniel|Hos|Hosea|Joel|Amos|Obad|Obadiah|Jonah|Mic|Micah|Nah|Nahum|Hab|Habakkuk|Zeph|Zephaniah|Hag|Haggai|Zech|Zechariah|Mal|Malachi|Matt|Matthew|Mark|Luke|John|Acts|Rom|Romans?|Cor|Corinthians|Gal|Galatians|Eph|Ephesians|Phil|Philippians|Col|Colossians|Thess|Thessalonians|Tim|Timothy|Titus|Philem|Philemon|Heb|Hebrews|James|Pet|Peter|Jude|Rev|Revelation)\.?'
    citation_regex = re.compile(
        rf'\(\s*[1-3]?\s*{books_pattern}\s*[^)]*\d+\s*:\s*\d+[^)]*\)',
        re.IGNORECASE
    )
    return citation_regex.sub('', text)

def title_case_heading(s):
    small_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'yet', 'is', 'with', 'from', 'into'}
    words = s.split()
    if not words:
        return s
    result = []
    for idx, word in enumerate(words):
        clean_word = re.sub(r'^\W+|\W+$', '', word).lower()
        if clean_word in small_words and idx > 0 and idx < len(words) - 1:
            result.append(word.lower())
        else:
            first_alpha = re.search(r'[A-Za-z]', word)
            if first_alpha:
                pos = first_alpha.start()
                capitalized = word[:pos] + word[pos].upper() + word[pos+1:].lower()
                result.append(capitalized)
            else:
                result.append(word.capitalize())
    return ' '.join(result)

def format_epigraphs_logic(text):
    lines = text.split('\n')
    out_lines = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped and not stripped.startswith('—') and not stripped.startswith('--') and not stripped.startswith('–'):
            quote_lines = []
            j = i
            while j < n and lines[j].strip() and not lines[j].strip().startswith('—') and not lines[j].strip().startswith('--') and not lines[j].strip().startswith('–'):
                quote_lines.append(lines[j].strip())
                j += 1
            
            attr_idx = j
            while attr_idx < n and not lines[attr_idx].strip():
                attr_idx += 1
                
            if attr_idx < n:
                attr_stripped = lines[attr_idx].strip()
                match = re.match(r'^(—|--|–)\s*(.+)$', attr_stripped)
                if match:
                    author = match.group(2).strip()
                    quote_content = " ".join(quote_lines)
                    rewritten = f'... Quote by {author}: "{quote_content}" ...'
                    out_lines.append("")
                    out_lines.append(rewritten)
                    out_lines.append("")
                    i = attr_idx + 1
                    continue
                    
        out_lines.append(line)
        i += 1
    return "\n".join(out_lines)

def format_bullet_lists_logic(text):
    lines = text.split('\n')
    out_lines = []
    i = 0
    n = len(lines)
    sequence_words = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth", "Tenth"]
    
    while i < n:
        line = lines[i]
        is_bullet = False
        bullet_char = ""
        bullet_match = re.match(r'^(\s*)([•\*\-])(\s+)(.*)$', line)
        if bullet_match:
            bullet_char = bullet_match.group(2)
            content = bullet_match.group(4).strip()
            if content and not all(c == bullet_char for c in content):
                is_bullet = True
                
        if is_bullet:
            bullet_lines = []
            j = i
            while j < n:
                curr_line = lines[j]
                curr_match = re.match(r'^(\s*)([•\*\-])(\s+)(.*)$', curr_line)
                if curr_match:
                    curr_char = curr_match.group(2)
                    curr_content = curr_match.group(4).strip()
                    if curr_content and not all(c == curr_char for c in curr_content):
                        bullet_lines.append((curr_line, curr_match.group(1), curr_match.group(3), curr_content))
                        j += 1
                        continue
                break
                
            if len(bullet_lines) > 1:
                for idx, (orig_line, indent, spaces, content) in enumerate(bullet_lines):
                    if idx < len(sequence_words):
                        word = sequence_words[idx]
                    else:
                        word = f"Number {idx + 1}"
                    new_line = f"{indent}{word}, {content}"
                    out_lines.append(new_line)
                i = j
                continue
            else:
                out_lines.append(line)
                i += 1
                continue
        else:
            out_lines.append(line)
            i += 1
            
    return "\n".join(out_lines)

def expand_scripture_citations_logic(text):
    books_pattern = r'\b(?:Gen|Exod|Lev|Num|Deut|Josh|Judg|Ruth|Sam|Kings?|Kgs|Chr|Chron|Ezra|Neh|Esth|Job|Ps|Pss|Psalm|Psalms|Prov|Proverbs|Eccl|Ecclesiastes|Cant|Song|Isa|Isaiah|Jer|Jeremiah|Lam|Lamentations|Ezek|Ezekiel|Dan|Daniel|Hos|Hosea|Joel|Amos|Obad|Obadiah|Jonah|Mic|Micah|Nah|Nahum|Hab|Habakkuk|Zeph|Zechariah|Zech|Mal|Malachi|Matt|Matthew|Mark|Luke|John|Acts|Rom|Romans?|Cor|Corinthians|Gal|Galatians|Eph|Ephesians|Phil|Philippians|Col|Colossians|Thess|Thessalonians|Tim|Timothy|Titus|Philem|Philemon|Heb|Hebrews|James|Pet|Peter|Jude|Rev|Revelation)\b'
    citation_regex = re.compile(
        rf'\(\s*([1-3]?\s*{books_pattern}\.?\s*\d+\s*:\s*\d+[^)]*)\)',
        re.IGNORECASE
    )
    
    SCRIPTURE_BOOKS = {
        'gen': 'Genesis', 'exod': 'Exodus', 'lev': 'Leviticus', 'num': 'Numbers', 'deut': 'Deuteronomy',
        'josh': 'Joshua', 'judg': 'Judges', 'ruth': 'Ruth', '1 sam': 'First Samuel', '2 sam': 'Second Samuel',
        '1 kgs': 'First Kings', '2 kgs': 'Second Kings', '1 chr': 'First Chronicles', '2 chr': 'Second Chronicles',
        'ezra': 'Ezra', 'neh': 'Nehemiah', 'esth': 'Esther', 'job': 'Job', 'ps': 'Psalm', 'pss': 'Psalms',
        'prov': 'Proverbs', 'eccl': 'Ecclesiastes', 'cant': 'Song of Solomon', 'isa': 'Isaiah', 'jer': 'Jeremiah',
        'lam': 'Lamentations', 'ezek': 'Ezekiel', 'dan': 'Daniel', 'hos': 'Hosea', 'joel': 'Joel', 'amos': 'Amos',
        'obad': 'Obadiah', 'jonah': 'Jonah', 'mic': 'Micah', 'nah': 'Nahum', 'hab': 'Habakkuk', 'zeph': 'Zephaniah',
        'hag': 'Haggai', 'zech': 'Zechariah', 'mal': 'Malachi', 'matt': 'Matthew', 'mark': 'Mark', 'luke': 'Luke',
        'john': 'John', 'acts': 'Acts', 'rom': 'Romans', '1 cor': 'First Corinthians', '2 cor': 'Second Corinthians',
        'gal': 'Galatians', 'eph': 'Ephesians', 'phil': 'Philippians', 'col': 'Colossians',
        '1 thess': 'First Thessalonians', '2 thess': 'Second Thessalonians', '1 tim': 'First Timothy',
        '2 tim': 'Second Timothy', 'titus': 'Titus', 'philem': 'Philemon', 'heb': 'Hebrews', 'james': 'James',
        '1 pet': 'First Peter', '2 pet': 'Second Peter', '1 john': 'First John', '2 john': 'Second John',
        '3 john': 'Third John', 'jude': 'Jude', 'rev': 'Revelation'
    }

    def replacer(match):
        citation_content = match.group(1)
        parts = citation_content.split(';')
        expansions = []
        for part in parts:
            part_stripped = part.strip()
            part_match = re.match(r'^([1-3]?\s*[A-Za-z]+)\.?\s*(\d+)\s*:\s*(\d+)(?:[\u2013\u2014-]\s*(\d+))?$', part_stripped)
            if part_match:
                book = part_match.group(1).strip()
                chapter = part_match.group(2)
                verse_start = part_match.group(3)
                verse_end = part_match.group(4)
                
                book_clean = re.sub(r'\s+', ' ', book).lower()
                book_full = SCRIPTURE_BOOKS.get(book_clean, book)
                
                chapter_text = f"chapter {chapter}"
                if verse_end:
                    verses_text = f"verses {verse_start} to {verse_end}"
                else:
                    verses_text = f"verse {verse_start}"
                
                expansions.append(f"{book_full} {chapter_text}, {verses_text}")
            else:
                expansions.append(part_stripped)
        
        if len(expansions) > 1:
            expanded_str = ", ".join(expansions[:-1]) + ", and " + expansions[-1]
        else:
            expanded_str = expansions[0]
            
        return f"({expanded_str})"

    return citation_regex.sub(replacer, text)

def clean_placeholders(text):
    PLACEHOLDER_REPLACEMENTS = {
        r'\[specific person\]': 'that person',
        r'\[someone\]': 'someone',
        r'\[particular person\]': 'that person',
        r'\[spouse/close friend\]': 'your spouse or close friend',
        r'\[something\]': 'something',
        r'\[specific choices\]': 'your choices',
        r'\[specific choice\]': 'your choice',
        r'\[choice\]': 'your choice',
        r'\[specific desire\(s\)\]': 'your desires',
        r'\[specific desire\]': 'your desire',
        r'\[ruling desires\]': 'your desires',
        r'\[specific emotion\]': 'your feelings',
        r'\[particular emotion\]': 'your feelings',
        r'\[situation\]': 'the situation',
        r'\[particular difficult situation\]': 'the situation',
        r'\[specific truth\]': 'the truth',
        r'\[attributes of God or insight from Scripture\]': "God's attributes",
        r'\[music, TV, books\]': 'music, TV, or books',
        r'\[statement\]': 'your statement',
        r'\[key aspect of created, fallen, redeemed, newly created\]': 'a key aspect of your identity',
        r'\[specific number\]': 'a specific number',
        r'\[specific Scripture\]': 'Scripture',
        r'\[particular belief\]': 'your belief',
        r'\[specific voices, whether relationships, media, etc\.\]': 'specific voices',
        r'\[specific pursuits\]': 'your pursuits',
    }
    
    for pattern, replacement in PLACEHOLDER_REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
    text = text.replace('[', '').replace(']', '')
    return text

def normalize_chapter_header(chapter_text):
    """
    Normalizes chapter titles like 'CHAPTER 12\n\nTitle' to 'Chapter 12: Title'.
    """
    lines = chapter_text.split('\n')
    if len(lines) >= 3:
        first_non_empty = -1
        second_non_empty = -1
        for idx, line in enumerate(lines):
            if line.strip():
                if first_non_empty == -1:
                    first_non_empty = idx
                elif second_non_empty == -1:
                    second_non_empty = idx
                    break
        
        if first_non_empty != -1 and second_non_empty != -1:
            first_line = lines[first_non_empty].strip()
            second_line = lines[second_non_empty].strip()
            
            if re.match(r'^(chapter|part)\s+\d+$', first_line, re.IGNORECASE):
                prefix = first_line.capitalize()
                title_parts = second_line.split(':')
                title_cased_parts = [title_case_heading(p.strip()) for p in title_parts]
                cleaned_title = ' — '.join(title_cased_parts)
                combined_header = f"{prefix}: {cleaned_title}"
                new_lines = []
                for idx, line in enumerate(lines):
                    if idx == first_non_empty:
                        new_lines.append(combined_header)
                    elif idx == second_non_empty:
                        continue
                    else:
                        new_lines.append(line)
                return '\n'.join(new_lines)
    return chapter_text

def strip_grid_matrices_logic(text):
    """
    Strips the flattened grid matrices (OCR table garble).
    """
    lines = text.split('\n')
    out_lines = []
    i = 0
    skipping = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if not skipping:
            if i + 2 < len(lines) and \
               "Cognition: Thought and Belief" in lines[i] and \
               "Affection: Desire and Feeling" in lines[i+1] and \
               "Volition: Will and Choice" in lines[i+2]:
                skipping = True
                i += 3
                continue
            out_lines.append(line)
            i += 1
        else:
            is_unindented = len(line) > 0 and not line.startswith(' ') and not line.startswith('\t')
            is_heading = is_unindented and (
                "reading" in stripped.lower() or 
                "reflecting" in stripped.lower() or 
                "relating" in stripped.lower() or 
                "renewal" in stripped.lower() or 
                "helping" in stripped.lower()
            )
            if is_heading:
                skipping = False
                out_lines.append(line)
                i += 1
            else:
                i += 1
    return '\n'.join(out_lines)

def split_text_into_chapters(text, chapter_regex, custom_dict=None, skip_references=True, skip_chapters_regex=None, strip_chapter_outlines=True, skip_discussion_questions=True, strip_grid_matrices=True, skip_scripture_citations=True, format_epigraphs=True, format_bullet_lists=True, expand_scripture_citations=False, clean_template_placeholders=True, replace_em_dashes=True):
    text = normalize_text(text, custom_dict, skip_references=skip_references, replace_em_dashes=False, clean_template_placeholders=clean_template_placeholders)
    
    if skip_scripture_citations:
        text = strip_scripture_citations(text)
    elif expand_scripture_citations:
        text = expand_scripture_citations_logic(text)
        
    if format_epigraphs:
        text = format_epigraphs_logic(text)
        
    if replace_em_dashes:
        text = text.replace('—', ', ').replace('--', ', ')
        
    if format_bullet_lists:
        text = format_bullet_lists_logic(text)
    
    # Strip brackets fallback if template placeholder cleaning was disabled
    if not clean_template_placeholders:
        text = text.replace('[', '').replace(']', '')
    
    # Extract chapter titles for stripping outlines if requested
    chapter_titles = set()
    if strip_chapter_outlines and chapter_regex.strip():
        try:
            matches = list(re.finditer(chapter_regex, text, flags=re.MULTILINE | re.IGNORECASE))
            for i in range(len(matches)):
                start = matches[i].start()
                end = matches[i+1].start() if i + 1 < len(matches) else len(text)
                chapter_content = text[start:end].strip()
                content_lines = [line.strip() for line in chapter_content.split('\n') if line.strip()]
                # content_lines[0] is the match (e.g., "12" or "CHAPTER 12")
                # content_lines[1] is the actual title line
                if len(content_lines) > 1:
                    title_candidate = content_lines[1]
                    if len(title_candidate) > 2 and len(title_candidate) < 100:
                        chapter_titles.add(title_candidate)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error extracting chapter titles: {e}")

    chapters = []
    if not chapter_regex.strip():
        processed_text = text
        if strip_grid_matrices:
            processed_text = strip_grid_matrices_logic(processed_text)
        if skip_discussion_questions:
            processed_text = strip_discussion_sections(processed_text)
        chapters.append(("Full_Audio", processed_text))
    else:
        matches = list(re.finditer(chapter_regex, text, flags=re.MULTILINE | re.IGNORECASE))
        if not matches:
            processed_text = text
            if strip_grid_matrices:
                processed_text = strip_grid_matrices_logic(processed_text)
            if skip_discussion_questions:
                processed_text = strip_discussion_sections(processed_text)
            chapters.append(("Full_Audio", processed_text))
        else:
            if matches[0].start() > 0:
                intro = text[:matches[0].start()].strip()
                if intro:
                    if strip_grid_matrices:
                        intro = strip_grid_matrices_logic(intro)
                    if skip_discussion_questions:
                        intro = strip_discussion_sections(intro)
                    chapters.append(("00_Intro", intro))
            
            for i in range(len(matches)):
                start = matches[i].start()
                end = matches[i+1].start() if i + 1 < len(matches) else len(text)
                chapter_text = text[start:end].strip()
                
                if strip_chapter_outlines and chapter_titles:
                    chapter_text = do_strip_chapter_outlines(chapter_text, chapter_titles)
                if strip_grid_matrices:
                    chapter_text = strip_grid_matrices_logic(chapter_text)
                if skip_discussion_questions:
                    chapter_text = strip_discussion_sections(chapter_text)
                
                chapter_text = normalize_chapter_header(chapter_text)
                
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

def extract_text_from_pdf(pdf_path, split_columns=False):
    """
    Extracts text page-by-page from a PDF file.
    Supports splitting double-column layout PDFs by using a coordinate-based visitor.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pypdf is not installed. Please run 'pip install pypdf' to use PDF features.")
        
    reader = PdfReader(pdf_path)
    text_parts = []
    for page in reader.pages:
        if split_columns:
            mb = page.mediabox
            width = mb.right - mb.left
            midpoint = mb.left + (width / 2)
            
            parts_left = []
            parts_right = []
            
            def visitor(text, cm, tm, fontDict, fontSize):
                # tm[4] is the horizontal offset (X coordinate)
                if tm and len(tm) > 4:
                    x = tm[4]
                    if x < midpoint:
                        parts_left.append(text)
                    else:
                        parts_right.append(text)
            
            page.extract_text(visitor_text=visitor)
            text = "".join(parts_left) + "\n" + "".join(parts_right)
        else:
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
