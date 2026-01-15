"""
Logger configuration for the application.
"""

import logging
import sys

# Configure logging with standard format and stdout handler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Export a default logger instance
logger: logging.Logger = logging.getLogger("app")
