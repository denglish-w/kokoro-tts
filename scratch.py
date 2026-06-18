import os
from core.text import split_text_into_chapters

with open('txt_files/The-Dynamic-Heart-In-Daily-Life.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Split the text using chapter regex. The chapters are labeled like "CHAPTER 12"
chapters = split_text_into_chapters(
    text,
    chapter_regex=r'^CHAPTER\s+\d+\s*$',
    format_epigraphs=True,
    format_bullet_lists=True,
    expand_scripture_citations=True,
    clean_template_placeholders=True,
    replace_em_dashes=True
)

print(f"Total Chapters found: {len(chapters)}")
# Find Chapter 12
chapter_12 = None
for title, content in chapters:
    if "12" in title or "12_" in title:
        chapter_12 = (title, content)
        break

if chapter_12:
    title, content = chapter_12
    print(f"\n=== Found Chapter 12: {title} ===")
    
    # Let's inspect the start of Chapter 12 (Heading & Epigraph)
    print("\n--- Start of Chapter 12 Content (first 750 chars) ---")
    print(content[:750])
    
    # Let's check if the table matrix starting with 'Cognition: Thought and Belief' was stripped successfully
    print("\n--- Check if grid matrix is stripped ---")
    if "Cognition: Thought and Belief" in content:
        print("WARNING: Grid matrix is STILL PRESENT!")
    else:
        print("SUCCESS: Grid matrix was successfully stripped!")
        
    # Let's check bullet formatting in 'Questions to Ask'
    print("\n--- Search for bullet formatting ---")
    pos = content.find("First, ")
    if pos != -1:
        print(f"SUCCESS: Found sequence transitions: '{content[pos:pos+120]}...'")
    else:
        print("WARNING: 'First, ' sequence transition not found!")
        
    # Let's check template placeholder cleaning
    print("\n--- Search for placeholders ---")
    if "[specific" in content or "[spouse" in content or "[situation" in content:
        print("WARNING: Template placeholders are still present!")
    else:
        # Check if the replaced word is present
        pos_place = content.find("A key moment for you was")
        if pos_place != -1:
            print(f"SUCCESS: Placeholder clean output check: '{content[pos_place:pos_place+120]}...'")
        else:
            print("Placeholder check: Replaced target phrase not found, but brackets are stripped.")
else:
    print("Chapter 12 not found. Printing all chapter titles:")
    for title, _ in chapters:
        print(title)
