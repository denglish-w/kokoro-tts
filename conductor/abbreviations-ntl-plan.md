# Implementation Plan: NTL Abbreviations for Kokoro-TTS

**Objective:**
Extend the text normalization logic in `core/text.py` to properly expand additional scholarly, biblical, and historical abbreviations found in the `john_ntl.txt` text (New Testament Library).

**Changes:**
1. **Target File:** `core/text.py`
2. **Target Method:** `normalize_text` (specifically the `expansions` dictionary)
3. **Implementation Details:**
   Add the following regex patterns and their expansions:
   * **General & Scholarly:** `ca.` -> `circa`, `C.E.` -> `Common Era`, `chs.` -> `chapters`
   * **Histories & Patristics:** `Hist. eccl.` -> `Historia Ecclesiastica`, `Ag. Ap.` -> `Against Apion`, `Ant.` -> `Antiquities of the Jews`, `Haer.` -> `Against Heresies`, `Legat.` -> `Legatio ad Gaium`, `Pan.` -> `Panegyricus`, `Dom.` -> `Domitian`
   * **Ignatius' Letters:** `Ign.` -> `Ignatius`, `Smyrn.` -> `Smyrnaeans`
   * **Mishnah references:** `m.\s+Šabb\.` -> `Mishnah Shabbat`, `m.\s+Kelim` -> `Mishnah Kelim`, `m.\s+Sukkah` -> `Mishnah Sukkah`, `m\.(?=\s|$)` -> `Mishnah`
   * **Manuscripts:** `𝔓52` -> `Papyrus 52`, `P52` -> `Papyrus 52`
   * **Series:** `NTL` -> `New Testament Library`

**Verification Steps:**
1. Create a temporary script `test_ntl_abbreviations.py` with sample text covering these new abbreviations.
2. Execute the script to verify the abbreviations expand correctly.
3. Remove the temporary script once verified.
