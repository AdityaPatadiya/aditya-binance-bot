import logging
import os
import sys
from datetime import datetime


def setup_logger():
    """Configure multi-handler logging system"""
    logger = logging.getLogger('trading_bot')
    logger.setLevel(logging.DEBUG)

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime(r"%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/bot_{timestamp}.log"
    file_handler = logging.FileHandler(log_file, mode='a')

    console_handler = logging.StreamHandler(sys.stdout)

    file_format = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_format = logging.Formatter(
        '%(levelname)-8s %(message)s'
    )

    # set formatters
    file_handler.setFormatter(file_format)
    console_handler.setFormatter(console_format)

    # set levels
    file_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)

    # add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger

logger = setup_logger()
