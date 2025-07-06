import argparse

from folder_sync import FolderSync
from log import setup_logger

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='One-way sync two folders.')
    parser.add_argument('source', help='Source folder')
    parser.add_argument('target', help='Target folder')
    parser.add_argument('log_folder', help='Log folder')
    args = parser.parse_args()

    logger = setup_logger(args.log_folder, args.source)
    logger.info(f'Starting sync: {args.source} -> {args.target}')
    syncer = FolderSync(args.source, args.target, logger)
    syncer.sync()
    logger.info('Sync complete.')
