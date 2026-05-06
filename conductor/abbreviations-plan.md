# Implementation Plan: Custom Abbreviations for Kokoro-TTS

**Objective:**
Extend the text normalization logic in `core/text.py` to properly expand scholarly, Latin, biblical, and manuscript abbreviations found in theological texts like the Word Biblical Commentary.

**Changes:**
1. **Target File:** `core/text.py`
2. **Target Method:** `normalize_text`
3. **Implementation Details:**
   Update the `expansions` dictionary to include a robust set of regex patterns to match the abbreviations:
   * **Latin & General Abbreviations:** `c.`, `cf.`, `e.g.`, `i.e.`, `et al.`, `ibid.`, `vv.`, `v.`, `ff.`, `f.`, `q.v.`, `s.v.`, `viz.`
   * **Language Abbreviations:** `Akkad.`, `Aram.`, `Heb.`, `Gr.`, `Syr.`, `Lat.`
   * **Manuscripts/Terms:** `LXX`, `MT`, `DSS`, `WBC`, `TR`, `FS`
   * **Biblical Books:** `Gen`, `Exod`, `Deut`, `Matt`, `Rom`, `Rev`, `1 Cor`, `2 Sam`
   
   Ensure all new abbreviation patterns correctly handle boundary conditions (e.g., using `(?=\s|$)` for abbreviations ending in a period to avoid matching strings inside other words or sentences incorrectly).

**Verification Steps:**
1. Execute the updated `normalize_text` function on a subset of the target text to ensure the new abbreviations correctly expand into their spoken counterparts.
2. Verify that general use of periods (like ends of sentences) or other text is not incorrectly substituted.
