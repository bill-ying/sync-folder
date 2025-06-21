import os
import shutil
import logging
import hashlib
from logging.handlers import TimedRotatingFileHandler

class FolderSync:
    def __init__(self, source, target, logger):
        self.source = source
        self.target = target
        self.logger = logger
        self.deleted_root = os.path.join(self.target, 'Deleted')

    def file_hash(self, path, chunk_size=65536):
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def move_deleted_files(self):
        for root, dirs, files in os.walk(self.target):
            if os.path.commonpath([root, self.deleted_root]) == self.deleted_root:
                continue
            rel_path = os.path.relpath(root, self.target)
            src_root = os.path.join(self.source, rel_path)
            for file in files:
                dst_file = os.path.join(root, file)
                src_file = os.path.join(src_root, file)
                if not os.path.exists(src_file):
                    deleted_file = os.path.join(self.deleted_root, rel_path, file)
                    os.makedirs(os.path.dirname(deleted_file), exist_ok=True)
                    shutil.move(dst_file, deleted_file)
                    self.logger.info(f'Moved deleted file: {dst_file} -> {deleted_file}')
            if root != self.target and not os.listdir(root):
                os.rmdir(root)
                self.logger.info(f'Removed empty directory: {root}')

    def sync(self):
        for root, dirs, files in os.walk(self.source):
            rel_path = os.path.relpath(root, self.source)
            target_root = os.path.join(self.target, rel_path)
            os.makedirs(target_root, exist_ok=True)
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_root, file)
                copy_needed = False
                if not os.path.exists(dst_file):
                    copy_needed = True
                else:
                    try:
                        if self.file_hash(src_file) != self.file_hash(dst_file):
                            copy_needed = True
                    except Exception as e:
                        self.logger.error(f'Failed to compare {src_file} and {dst_file}: {e}')
                        continue
                if copy_needed:
                    try:
                        shutil.copyfile(src_file, dst_file)
                        self.logger.info(f'Copied: {src_file} -> {dst_file}')
                    except Exception as e:
                        self.logger.error(f'Failed to copy {src_file} to {dst_file}: {e}')
        self.move_deleted_files()

def setup_logger(log_folder, source):
    os.makedirs(log_folder, exist_ok=True)
    base_name = os.path.basename(os.path.normpath(source))
    log_file = os.path.join(log_folder, f'{base_name}.log')
    logger = logging.getLogger('folder_sync')
    logger.setLevel(logging.INFO)
    handler = TimedRotatingFileHandler(log_file, when='D', interval=7, backupCount=4)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
