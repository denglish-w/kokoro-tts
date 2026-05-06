import os
import argparse
import soundfile as sf
from tqdm import tqdm
import logging
from core.engine import generate_first
from core.text import split_text_into_chapters

logger = logging.getLogger(__name__)

def run_cli(args):
    logger.info(f"Reading {args.input}...")
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        logger.error(f"Input file not found: {args.input}")
        return

    chapters = split_text_into_chapters(text, args.regex)
    logger.info(f"Found {len(chapters)} chapters. Starting synthesis...")

    os.makedirs(args.output_dir, exist_ok=True)

    for title, chapter_text in tqdm(chapters, desc="Generating Chapters"):
        audio_data, _ = generate_first(chapter_text, args.voice, args.speed, use_gpu=args.gpu)
        if audio_data:
            sample_rate, audio_np = audio_data
            filename = f"{title}.wav"
            output_path = os.path.join(args.output_dir, filename)
            sf.write(output_path, audio_np, sample_rate)
            logger.debug(f"Saved {output_path}")

    logger.info(f"Done! Audio files saved to {args.output_dir}")

def parse_args():
    parser = argparse.ArgumentParser(description='Kokoro-TTS CLI')
    parser.add_argument('--input', type=str, help='Input text file for batch processing')
    parser.add_argument('--output-dir', type=str, default='/mnt/c/Users/DavidEnglish/Documents/Kokoro_Exports', help='Directory to save audio chapters')
    parser.add_argument('--regex', type=str, default=r'^Chapter\s+\d+', help='Regex for splitting chapters')
    parser.add_argument('--voice', type=str, default='af_heart', help='Voice ID to use')
    parser.add_argument('--speed', type=float, default=1.0, help='Playback speed')
    parser.add_argument('--gpu', action='store_true', help='Force use of GPU')
    
    return parser.parse_known_args()
