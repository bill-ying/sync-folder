import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger(log_folder, source):
    os.makedirs(log_folder, exist_ok=True)
    base_name = os.path.basename(os.path.normpath(source))
    log_file = os.path.join(log_folder, f'{base_name}.log')
    logger = logging.getLogger('folder_sync')
    logger.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(log_file, when='D', interval=7, backupCount=4)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger