# Implementation Plan: Sheffield Abbreviations for Kokoro-TTS

**Objective:**
Extend the text normalization logic in `core/text.py` to properly expand additional scholarly, biblical, and historical abbreviations found in the `john_sheffield_introduction.txt` text.

**Changes:**
1. **Target File:** `core/text.py`
2. **Target Method:** `normalize_text` (specifically the `expansions` dictionary)
3. **Implementation Details:**
   Add the following regex patterns and their expansions:
   * **General & Scholarly:** `N.T.` -> `New Testament`, `O.T.` -> `Old Testament`, `CE` -> `Common Era`, `BCE` -> `Before Common Era`, `ch.` -> `chapter`, `pp.` -> `pages`, `vol.` -> `volume`, `vols.` -> `volumes`, `ed.` -> `edition`
   * **Biblical & Apocryphal Books:** `Isa.` -> `Isaiah`, `Jer.` -> `Jeremiah`, `Dan.` -> `Daniel`, `Prov.` -> `Proverbs`, `Ps.` -> `Psalm`, `Gal.` -> `Galatians`, `Ecclus` -> `Ecclesiasticus`, `Wisd.` -> `Wisdom`
   * **Historical & Patristic Works:** `Adv. Haer.` -> `Adversus Haereses`, `H. E.` -> `Historia Ecclesiastica`
   * **Talmudic Tractates:** `b.\s+Sanhedrin` -> `Babylonian Sanhedrin` (to handle cases like `b. Sanhedrin`)

   Care will be taken to use lookaheads `(?=\s|$)` for abbreviations ending in periods to prevent incorrect expansions inside other words or when followed by punctuation not handled by the boundary.

**Verification Steps:**
1. Create a temporary script `test_sheffield_abbreviations.py` with sample text covering these new abbreviations.
2. Execute the script to verify the abbreviations expand correctly and don't match substrings.
3. Remove the temporary script once verified.