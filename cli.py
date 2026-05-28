import os
import argparse
import soundfile as sf
from tqdm import tqdm
import logging
from core.engine import generate_first
from core.text import split_text_into_chapters, extract_text_from_pdf, scan_for_potential_abbreviations, clean_filename, extract_metadata_from_pdf, extract_metadata_from_text

logger = logging.getLogger(__name__)

def run_cli(args):
    logger.info(f"Reading {args.input}...")
    try:
        if args.input.lower().endswith('.pdf'):
            text = extract_text_from_pdf(args.input)
        else:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
    except FileNotFoundError:
        logger.error(f"Input file not found: {args.input}")
        return
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return

    custom_dict = {}
    if args.scan_abbrev:
        logger.info("Scanning for unrecognized potential abbreviations...")
        candidates = scan_for_potential_abbreviations(text)
        if candidates:
            print("\n=== Unrecognized Potential Abbreviations ===")
            print("Found the following potential abbreviations/acronyms.")
            print("Enter an expansion for each, or press Enter to skip.\n")
            for word, count in candidates.items():
                try:
                    ans = input(f"'{word}' (appears {count} times) -> expansion: ").strip()
                    if ans:
                        custom_dict[word] = ans
                except (KeyboardInterrupt, EOFError):
                    print("\nAborting interactive scan. Continuing with current abbreviations...")
                    break
            print("\n============================================\n")
        else:
            logger.info("No unrecognized abbreviations found.")

    # Try to extract metadata for naming
    author = args.author
    title_meta = args.title
    
    if not author or not title_meta:
        if args.input.lower().endswith('.pdf'):
            meta = extract_metadata_from_pdf(args.input)
        else:
            meta = extract_metadata_from_text(text)
        
        if not author and meta.get("author"):
            author = meta["author"]
        if not title_meta and meta.get("title"):
            title_meta = meta["title"]

    meta_parts = []
    if author:
        meta_parts.append(clean_filename(author))
    if title_meta:
        meta_parts.append(clean_filename(title_meta))
        
    if meta_parts:
        base_name = " - ".join(meta_parts)
    else:
        base_name = os.path.splitext(os.path.basename(args.input))[0]

    import time
    total_start_time = time.time()
    chapters = split_text_into_chapters(text, args.regex, custom_dict=custom_dict)
    logger.info(f"Found {len(chapters)} chapters. Starting synthesis...")

    output_dir = os.path.expanduser(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    total_duration = 0.0
    for title_key, chapter_text in tqdm(chapters, desc="Generating Chapters"):
        chapter_start = time.time()
        audio_data, _ = generate_first(chapter_text, args.voice, args.speed, use_gpu=args.gpu, custom_dict=custom_dict)
        chapter_elapsed = time.time() - chapter_start
        
        if audio_data:
            sample_rate, audio_np = audio_data
            duration = len(audio_np) / sample_rate
            total_duration += duration
            
            speed_ratio = duration / chapter_elapsed if chapter_elapsed > 0 else 0
            char_rate = len(chapter_text) / chapter_elapsed if chapter_elapsed > 0 else 0
            
            logger.info(f"Synthesized '{title_key}' ({len(chapter_text)} chars) in {chapter_elapsed:.2f}s | "
                        f"Audio: {duration:.2f}s ({speed_ratio:.2fx} RT speed, {char_rate:.1f} chars/s)")
            
            # Dynamically rename based upon author/title
            if title_key == "Full_Audio":
                filename = f"{base_name}.wav"
            else:
                filename = f"{base_name} - {title_key}.wav"
            output_path = os.path.join(output_dir, filename)
            sf.write(output_path, audio_np, sample_rate)
            logger.debug(f"Saved {output_path}")

    total_elapsed = time.time() - total_start_time
    m, s = divmod(total_elapsed, 60)
    h, m = divmod(m, 60)
    time_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}" if h > 0 else f"{int(m):02d}:{int(s):02d}"
    
    avg_speed_ratio = total_duration / total_elapsed if total_elapsed > 0 else 0
    logger.info(f"Done! Synthesized {len(chapters)} chapters in {time_str} ({total_elapsed:.2f}s) | "
                f"Total Audio: {total_duration:.2f}s ({avg_speed_ratio:.2fx} average RT speed)")

def parse_args():
    parser = argparse.ArgumentParser(description='Kokoro-TTS CLI')
    parser.add_argument('--input', type=str, help='Input text/PDF file for batch processing')
    parser.add_argument('--output-dir', type=str, default='~/Documents/Kokoro_Exports', help='Directory to save audio chapters')
    parser.add_argument('--regex', type=str, default=r'^Chapter\s+\d+', help='Regex for splitting chapters')
    parser.add_argument('--voice', type=str, default='am_michael', help='Voice ID to use')
    parser.add_argument('--speed', type=float, default=1.0, help='Playback speed')
    parser.add_argument('--gpu', action='store_true', help='Force use of GPU')
    parser.add_argument('--scan-abbrev', action='store_true', help='Scan for unrecognized abbreviations and prompt interactively to expand them')
    parser.add_argument('--title', type=str, help='Manual override for Title metadata (used in filenames)')
    parser.add_argument('--author', type=str, help='Manual override for Author metadata (used in filenames)')
    
    return parser.parse_known_args()
