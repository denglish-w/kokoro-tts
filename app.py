import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Silence phonemizer warnings
logging.getLogger("phonemizer").setLevel(logging.ERROR)

import warnings
warnings.filterwarnings("ignore", message="An output with one or more elements was resized since it had shape")

logger = logging.getLogger(__name__)

from cli import parse_args

if __name__ == '__main__':
    args, unknown = parse_args()

    if args.list_voices:
        from core.voices import CHOICES
        for label, voice_id in CHOICES.items():
            print(f"{voice_id:15s} {label}")
        sys.exit(0)

    # Fallback: if --input is not set, look for any existing file in the unknown positional arguments
    if not args.input and unknown:
        for arg in unknown:
            clean_arg = arg.strip('\'"')
            if os.path.isfile(clean_arg):
                args.input = clean_arg
                break

    if not args.input:
        from cli import build_parser
        build_parser().print_help()
        sys.exit(1)

    logger.info(f"Starting synthesis with input: {args.input}")
    from cli import run_cli
    run_cli(args)
