from core.text import split_text_into_chapters
with open('john_sheffield_introduction.txt', 'r') as f:
    text = f.read()
chapters = split_text_into_chapters(text, r'^(Part\s+[IVXLCDM]+|\d+)\s*$')
print(f"Number of chapters: {len(chapters)}")
for title, _ in chapters:
    print(title)
