import re
from num2words import num2words

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
    
    # We no longer aggressively remove standalone numbers because they are often used 
    # as chapter headings (e.g. 1, 2, 3) in text files.
    # text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
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
    
    # Expand abbreviations (case-sensitive, whole-word only)
    expansions = {
        r'\bNT\b': 'New Testament',
        r'\bOT\b': 'Old Testament',
    }
    
    for pattern, replacement in expansions.items():
        text = re.sub(pattern, replacement, text)
        
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
