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

logger = logging.getLogger(__name__)

from cli import parse_args, run_cli
from ui.app import create_ui, theme, custom_css

if __name__ == '__main__':
    args, unknown = parse_args()
    
    if args.input:
        logger.info("Starting in CLI mode...")
        run_cli(args)
    else:
        logger.info("Starting in Web UI mode...")
        app = create_ui()
        
        # Get configuration from environment variables
        port = int(os.environ.get("KOKORO_PORT", 40001))
        host = os.environ.get("KOKORO_HOST", "0.0.0.0")
        api_open = os.environ.get("KOKORO_API_OPEN", "True").lower() == "true"
        
        logger.info(f"Launching Gradio UI on {host}:{port}")
        app.queue(api_open=api_open).launch(
            server_name=host, 
            server_port=port,
            theme=theme,
            css=custom_css
        )
