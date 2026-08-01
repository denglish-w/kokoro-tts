import unittest
from core.text import (
    title_case_heading,
    normalize_chapter_header,
    format_epigraphs_logic,
    format_bullet_lists_logic,
    expand_scripture_citations_logic,
    clean_placeholders,
    parse_custom_dict
)

class TestPreprocessors(unittest.TestCase):
    
    # @lat: [[tests#Text Preprocessors#Title case heading]]
    def test_title_case_heading(self):
        self.assertEqual(title_case_heading("RELATE: LOOKING TO JESUS, THE AUTHOR AND FINISHER OF FAITH"),
                         "Relate: Looking to Jesus, the Author and Finisher of Faith")
        self.assertEqual(title_case_heading("OTHERS AND INFLUENCE"),
                         "Others and Influence")
        self.assertEqual(title_case_heading(""), "")
        
    # @lat: [[tests#Text Preprocessors#Chapter header normalization]]
    def test_normalize_chapter_header(self):
        chapter_text = "CHAPTER 12\n\nRELATE: LOOKING TO JESUS, THE AUTHOR AND FINISHER OF FAITH\n\nSome body text."
        expected = "Chapter 12: Relate — Looking to Jesus, the Author and Finisher of Faith\n\n\nSome body text."
        self.assertEqual(normalize_chapter_header(chapter_text), expected)
        
    # @lat: [[tests#Text Preprocessors#Epigraph formatting]]
    def test_format_epigraphs_logic(self):
        text = """If faith is the sole condition of the Divine act of grace
which makes the beginning of the new life,
then it alone can be also the condition of every furthering
of that life.

— Franklin Weidner

Next paragraph starts here."""
        
        expected = '\n... Quote by Franklin Weidner: "If faith is the sole condition of the Divine act of grace which makes the beginning of the new life, then it alone can be also the condition of every furthering of that life." ...\n\n\nNext paragraph starts here.'
        self.assertEqual(format_epigraphs_logic(text), expected)
        
    # @lat: [[tests#Text Preprocessors#Bullet list formatting]]
    def test_format_bullet_lists_logic(self):
        text = """Questions to Ask:
    •      What do you think this situation shows?
    •      What do you believe would be better?"""
        
        expected = """Questions to Ask:
    First, What do you think this situation shows?
    Second, What do you believe would be better?"""
        self.assertEqual(format_bullet_lists_logic(text), expected)
        
    # @lat: [[tests#Text Preprocessors#Scripture citation expansion]]
    def test_expand_scripture_citations_logic(self):
        self.assertEqual(
            expand_scripture_citations_logic("(Eph. 4:26–32; Col. 3:8; James 1:19)"),
            "(Ephesians chapter 4, verses 26 to 32, Colossians chapter 3, verse 8, and James chapter 1, verse 19)"
        )
        self.assertEqual(
            expand_scripture_citations_logic("Reference (Rom. 10:17) in text"),
            "Reference (Romans chapter 10, verse 17) in text"
        )
        self.assertEqual(
            expand_scripture_citations_logic("Look at (1 Pet. 1:14)"),
            "Look at (First Peter chapter 1, verse 14)"
        )
        
    # @lat: [[tests#Text Preprocessors#Template placeholder cleaning]]
    def test_clean_placeholders(self):
        self.assertEqual(
            clean_placeholders("A key moment for you was when you [situation]; in response, you chose to [choice]."),
            "A key moment for you was when you the situation; in response, you chose to your choice."
        )
        self.assertEqual(
            clean_placeholders("What do you think is motivating [specific person] to treat you like that?"),
            "What do you think is motivating that person to treat you like that?"
        )
        self.assertEqual(
            clean_placeholders("And [Jesus] said..."),
            "And Jesus said..."
        )

    # @lat: [[tests#Text Preprocessors#Custom pronunciation dictionary parsing]]
    def test_parse_custom_dict(self):
        self.assertEqual(
            parse_custom_dict("Jon: John\nNT: New Testament"),
            {"Jon": "John", "NT": "New Testament"}
        )
        self.assertEqual(
            parse_custom_dict("Jon: John\n\nno colon here\n"),
            {"Jon": "John"}
        )
        self.assertEqual(
            parse_custom_dict("Time: 3:45 PM"),
            {"Time": "3:45 PM"}
        )
        self.assertIsNone(parse_custom_dict(""))
        self.assertIsNone(parse_custom_dict("   \n  "))
        self.assertIsNone(parse_custom_dict(None))

if __name__ == '__main__':
    unittest.main()
