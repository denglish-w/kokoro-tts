# Implementation Plan: Raymond Brown Abbreviations for Kokoro-TTS

**Objective:**
Extend the text normalization logic in `core/text.py` to properly expand additional scholarly and manuscript abbreviations found in the `rb_introduction_john.txt` text.

**Changes:**
1. **Target File:** `core/text.py`
2. **Target Method:** `normalize_text` (specifically the `expansions` dictionary)
3. **Implementation Details:**
   Add the following regex patterns and their expansions:
   * **General & Scholarly:** `A.D.` -> `Anno Domini`, `A.T.` -> `A. T.`, `art. cit.` -> `article cited`, `abbr.` -> `abbreviation`, `vs.` -> `verse`, `vss.` -> `verses`
   * **Manuscripts:** `P66` -> `Papyrus 66`, `P75` -> `Papyrus 75`
   * **Other:** `SB` -> `La Sainte Bible`

   Ensure lookaheads `(?=\s|$)` for abbreviations ending in periods to prevent incorrect expansions.

**Verification Steps:**
1. Create a temporary script `test_rb_abbreviations.py` with sample text covering these new abbreviations.
2. Execute the script to verify the abbreviations expand correctly.
3. Remove the temporary script once verified.
