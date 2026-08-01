import unittest
from unittest.mock import MagicMock, patch
from core.text import scan_for_potential_abbreviations, extract_text_from_pdf, extract_metadata_from_text

class TestPdfAndAbbrev(unittest.TestCase):
    
    # @lat: [[tests#PDF & Abbreviation Scanning#Abbreviation scan counts and exclusions]]
    def test_scan_for_potential_abbreviations(self):
        text = """
        This is a test document talking about XYZACR and DSS, which are scholarly acronyms.
        We also mention MYACR several times (MYACR, MYACR).
        We have XYZACR, XYZACR, XYZACR here.
        However, we should not match common words like THE, AND, BUT or standard sentence ends.
        And we shouldn't match NT or OT because they are in default expansions.
        Wait, what about cf. and e.g.? They are also in default expansions, so they should be skipped.
        But maybe we have new short dotted terms like xyz. or abc.
        Let's see: MYACR should be detected, and xyz. should be detected.
        """
        custom_dict = {"MYACR": "My Acronym"}
        # scan with no custom_dict
        candidates = scan_for_potential_abbreviations(text)
        
        # XYZACR appears 4 times in the sample
        self.assertEqual(candidates.get("XYZACR"), 4)
        # MYACR appears 4 times in the sample (3 in body, 1 near end)
        self.assertEqual(candidates.get("MYACR"), 4)
        # xyz. appears 2 times
        self.assertEqual(candidates.get("xyz."), 2)
        # abc. appears 1 time
        self.assertEqual(candidates.get("abc."), 1)
        
        # NT, OT, cf., e.g. should not be in candidates because they are default expansions
        self.assertNotIn("NT", candidates)
        self.assertNotIn("OT", candidates)
        self.assertNotIn("cf.", candidates)
        
        # If we scan passing custom_dict, MYACR should be skipped
        candidates_with_custom = scan_for_potential_abbreviations(text, custom_dict)
        self.assertNotIn("MYACR", candidates_with_custom)
        
    # @lat: [[tests#PDF & Abbreviation Scanning#PDF text extraction concatenation]]
    @patch('pypdf.PdfReader')
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        # Mocking PdfReader to simulate page text extraction
        mock_reader_instance = MagicMock()
        mock_pdf_reader.return_value = mock_reader_instance
        
        mock_page_1 = MagicMock()
        mock_page_1.extract_text.return_value = "Page 1 Content with WBC."
        mock_page_2 = MagicMock()
        mock_page_2.extract_text.return_value = "Page 2 Content with DSS."
        
        mock_reader_instance.pages = [mock_page_1, mock_page_2]
        
        extracted_text = extract_text_from_pdf("dummy_path.pdf")
        
        self.assertEqual(extracted_text, "Page 1 Content with WBC.\nPage 2 Content with DSS.")
        mock_pdf_reader.assert_called_once_with("dummy_path.pdf")

    # @lat: [[tests#PDF & Abbreviation Scanning#Metadata extraction from text formats]]
    def test_extract_metadata_from_text(self):
        # 1. YAML frontmatter test
        yaml_text = """---
title: "The Great Gatsby"
author: 'F. Scott Fitzgerald'
---
Some body text here.
"""
        meta_yaml = extract_metadata_from_text(yaml_text)
        self.assertEqual(meta_yaml["title"], "The Great Gatsby")
        self.assertEqual(meta_yaml["author"], "F. Scott Fitzgerald")

        # 2. Plain text header test
        plain_text = """
        Title: Common Sense
        Author: Thomas Paine
        
        Some other text.
        """
        meta_plain = extract_metadata_from_text(plain_text)
        self.assertEqual(meta_plain["title"], "Common Sense")
        self.assertEqual(meta_plain["author"], "Thomas Paine")

        # 3. Markdown header test
        md_text = """
        # Mere Christianity
        ## C. S. Lewis
        
        Chapter 1...
        """
        meta_md = extract_metadata_from_text(md_text)
        self.assertEqual(meta_md["title"], "Mere Christianity")
        self.assertEqual(meta_md["author"], "C. S. Lewis")

if __name__ == '__main__':
    unittest.main()
