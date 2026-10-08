"""
MAIRA-∞ Entry Point

Handles application startup, argument parsing, and environment setup.
"""

import sys
import argparse
import asyncio
import logging
from pathlib import Path
from typing import NoReturn

from maira.app import MAIRAApplication

def setup_logging(debug: bool = False) -> None:
    """Configure application logging."""
    level = logging.DEBUG if debug else logging.INFO
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # File handler (logs directory)
    logs_dir = Path.home() / ".maira" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(logs_dir / "maira.log")
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter with timestamp
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MAIRA-∞ - Limitless AI Desktop Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  maira                    # Start normally
  maira --dev             # Development mode
  maira --debug           # Debug logging
  maira --offline         # Offline mode (Ollama only)
        """
    )
    
    parser.add_argument("--dev", action="store_true", help="Enable development mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--offline", action="store_true", help="Start in offline mode (local LLM only)")
    parser.add_argument("--config", type=Path, help="Custom config file path")
    parser.add_argument("--data-dir", type=Path, help="Custom data directory")
    
    return parser.parse_args()

def main() -> NoReturn:
    """Main entry point."""
    args = parse_args()
    
    # Setup logging first
    setup_logging(debug=args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting MAIRA v12.7.3")
    logger.info(f"Python {sys.version}")
    logger.info(f"Arguments: {vars(args)}")
    
    try:
        # Create and run application
        app = MAIRAApplication(
            dev_mode=args.dev,
            offline_mode=args.offline,
            config_path=args.config,
            data_dir=args.data_dir
        )
        
        exit_code = app.run()
        logger.info(f"Application exited with code {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()