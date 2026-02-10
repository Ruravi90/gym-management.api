import logging
import sys
from app.config import settings

def setup_logging():
    """Setup centralized logging configuration."""
    log_level = logging.INFO
    if settings.ENVIRONMENT == "development":
        log_level = logging.DEBUG
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set levels for noisy libraries
    logging.getLogger("tortoise").setLevel(logging.WARNING)
    logging.getLogger("aiomysql").setLevel(logging.WARNING)
    
    logger = logging.getLogger("app")
    logger.info(f"Logging initialized in {settings.ENVIRONMENT} mode")
    return logger

logger = logging.getLogger("app")
