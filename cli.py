import os
import argparse
import logging

logger = logging.getLogger(__name__)

def run_cli(args):
    import soundfile as sf
    from tqdm import tqdm
    from core.engine import generate_first
    from core.text import (
        split_text_into_chapters,
        extract_text_from_pdf,
        scan_for_potential_abbreviations,
        clean_filename,
        extract_metadata_from_pdf,
        extract_metadata_from_text
    )

    if args.format.lower() == 'mp3':
        import shutil
        if not shutil.which('ffmpeg'):
            logger.error("Error: ffmpeg is not installed or not in the system PATH. Please install ffmpeg to use MP3 format.")
            return

    logger.info(f"Reading {args.input}...")
    try:
        if args.input.lower().endswith('.pdf'):
            text = extract_text_from_pdf(args.input, split_columns=args.split_columns)
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
    chapters = split_text_into_chapters(
        text, 
        args.regex, 
        custom_dict=custom_dict, 
        strip_chapter_outlines=args.strip_outlines, 
        skip_discussion_questions=args.skip_discussion,
        strip_grid_matrices=args.strip_grid,
        skip_scripture_citations=args.skip_citations,
        format_epigraphs=args.format_epigraphs,
        format_bullet_lists=args.format_bullets,
        expand_scripture_citations=args.expand_citations,
        clean_template_placeholders=args.clean_placeholders,
        replace_em_dashes=args.replace_em_dashes
    )
    logger.info(f"Found {len(chapters)} chapters. Starting synthesis...")

    output_dir = os.path.expanduser(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    total_duration = 0.0
    for title_key, chapter_text in tqdm(chapters, desc="Generating Chapters"):
        chapter_start = time.time()
        audio_data, _ = generate_first(
            chapter_text, 
            args.voice, 
            args.speed, 
            use_gpu=args.gpu, 
            custom_dict=custom_dict,
            replace_em_dashes=args.replace_em_dashes,
            clean_template_placeholders=args.clean_placeholders
        )
        chapter_elapsed = time.time() - chapter_start
        
        if audio_data:
            sample_rate, audio_np = audio_data
            duration = len(audio_np) / sample_rate
            total_duration += duration
            
            speed_ratio = duration / chapter_elapsed if chapter_elapsed > 0 else 0
            char_rate = len(chapter_text) / chapter_elapsed if chapter_elapsed > 0 else 0
            
            logger.info(f"Synthesized '{title_key}' ({len(chapter_text)} chars) in {chapter_elapsed:.2f}s | "
                        f"Audio: {duration:.2f}s ({speed_ratio:.2f}x RT speed, {char_rate:.1f} chars/s)")
            
            # Dynamically rename based upon author/title
            if title_key == "Full_Audio":
                filename = f"{base_name}.wav"
            else:
                filename = f"{base_name} - {title_key}.wav"
            output_path = os.path.join(output_dir, filename)
            sf.write(output_path, audio_np, sample_rate)
            
            if args.format.lower() == 'mp3':
                import subprocess
                mp3_path = output_path.replace('.wav', '.mp3')
                logger.debug(f"Converting '{filename}' to MP3...")
                subprocess.run(['ffmpeg', '-y', '-i', output_path, '-b:a', args.bitrate, mp3_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(mp3_path):
                    os.remove(output_path)
                    logger.debug(f"Saved {mp3_path}")
                else:
                    logger.error(f"Failed to convert '{filename}' to MP3 (is ffmpeg installed?)")
            else:
                logger.debug(f"Saved {output_path}")

    total_elapsed = time.time() - total_start_time
    m, s = divmod(total_elapsed, 60)
    h, m = divmod(m, 60)
    time_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}" if h > 0 else f"{int(m):02d}:{int(s):02d}"
    
    avg_speed_ratio = total_duration / total_elapsed if total_elapsed > 0 else 0
    logger.info(f"Done! Synthesized {len(chapters)} chapters in {time_str} ({total_elapsed:.2f}s) | "
                f"Total Audio: {total_duration:.2f}s ({avg_speed_ratio:.2f}x average RT speed)")

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
    parser.add_argument('--format', type=str, choices=['wav', 'mp3'], default='wav', help='Output audio format')
    parser.add_argument('--bitrate', type=str, default='192k', help='MP3 bitrate (e.g. 192k, 64k, 32k)')
    parser.add_argument('--strip-outlines', action='store_true', default=True, help='Strip repeated chapter outlines')
    parser.add_argument('--no-strip-outlines', action='store_false', dest='strip_outlines', help='Do not strip repeated chapter outlines')
    parser.add_argument('--skip-discussion', action='store_true', default=True, help='Skip Discussion and Response sections')
    parser.add_argument('--no-skip-discussion', action='store_false', dest='skip_discussion', help='Do not skip Discussion and Response sections')
    parser.add_argument('--strip-grid', action='store_true', default=True, help='Strip flattened grid matrices')
    parser.add_argument('--no-strip-grid', action='store_false', dest='strip_grid', help='Do not strip flattened grid matrices')
    parser.add_argument('--skip-citations', action='store_true', default=True, help='Skip parenthetical scripture citations')
    parser.add_argument('--no-skip-citations', action='store_false', dest='skip_citations', help='Do not skip parenthetical scripture citations')
    parser.add_argument('--split-columns', action='store_true', default=False, help='Split double-column layout PDFs horizontally')
    parser.add_argument('--format-epigraphs', action='store_true', default=True, help='Format epigraphs and quotes block')
    parser.add_argument('--no-format-epigraphs', action='store_false', dest='format_epigraphs', help='Do not format epigraphs and quotes')
    parser.add_argument('--format-bullets', action='store_true', default=True, help='Format bullet points list to sequences')
    parser.add_argument('--no-format-bullets', action='store_false', dest='format_bullets', help='Do not format bullet points list to sequences')
    parser.add_argument('--expand-citations', action='store_true', default=False, help='Expand inline scripture reference abbreviations to spoken text')
    parser.add_argument('--clean-placeholders', action='store_true', default=True, help='Clean template placeholders to generic words')
    parser.add_argument('--no-clean-placeholders', action='store_false', dest='clean_placeholders', help='Do not clean template placeholders')
    parser.add_argument('--replace-em-dashes', action='store_true', default=True, help='Replace em dashes with pauses (comma)')
    parser.add_argument('--no-replace-em-dashes', action='store_false', dest='replace_em_dashes', help='Do not replace em dashes with pauses')
    
    return parser.parse_known_args()
