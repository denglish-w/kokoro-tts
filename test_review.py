from core.text import normalize_text

texts = [
    "He did a good job.",
    "Don't leave a mark on the CD-ROM.",
    "I need some num lock.",
    "John F. Kennedy",
    "Batman vs. Superman",
    "He acts well.",
    "She has volume 1 of the new edition."
]

for t in texts:
    print(f"Original: {t}")
    print(f"Normalized: {normalize_text(t)}")
    print()
