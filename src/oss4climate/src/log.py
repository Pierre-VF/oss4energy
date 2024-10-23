"""
Module for logging
"""

import logging


def log_info(msg: str):
    print(msg)
    logging.info(msg)


def log_warning(msg: str):
    print(msg)
    logging.warning(msg)
