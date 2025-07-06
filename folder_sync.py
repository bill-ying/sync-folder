import os
import shutil
import hashlib

class FolderSync:
    def __init__(self, source, target, logger):
        self.source = source
        self.target = target
        self.logger = logger
        self.deleted_root = os.path.join(self.target, 'Deleted')

    def __file_hash(self, path, chunk_size=65536):
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def __build_hash_map(self, root_dir):
        hash_map = {}
        for root, _, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                try:
                    h = self.__file_hash(file_path)
                    hash_map[h] = rel_path
                except Exception as e:
                    self.logger.error(f'Failed to hash {file_path}: {e}')
        return hash_map

    def __move_or_copy_files(self, source_hashes, target_hashes):
        for h, src_rel_path in source_hashes.items():
            src_file = os.path.join(self.source, src_rel_path)
            dst_file = os.path.join(self.target, src_rel_path)

            if h in target_hashes:
                tgt_rel_path = target_hashes[h]
                old_tgt_file = os.path.join(self.target, tgt_rel_path)
                if tgt_rel_path != src_rel_path:
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    try:
                        shutil.move(old_tgt_file, dst_file)
                        self.logger.info(f'Moved in target: {old_tgt_file} -> {dst_file}')
                    except Exception as e:
                        self.logger.error(f'Failed to move {old_tgt_file} to {dst_file}: {e}')
            else:
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                try:
                    shutil.copyfile(src_file, dst_file)
                    self.logger.info(f'Copied: {src_file} -> {dst_file}')
                except Exception as e:
                    self.logger.error(f'Failed to copy {src_file} to {dst_file}: {e}')

    def __move_deleted_files(self, source_hashes):
        for root, dirs, files in os.walk(self.target):
            if os.path.commonpath([root, self.deleted_root]) == self.deleted_root:
                continue
            rel_path = os.path.relpath(root, self.target)
            src_root = os.path.join(self.source, rel_path)
            for file in files:
                dst_file = os.path.join(root, file)
                rel_file_path = os.path.relpath(dst_file, self.target)
                if rel_file_path not in source_hashes.values():
                    deleted_file = os.path.join(self.deleted_root, rel_path, file)
                    os.makedirs(os.path.dirname(deleted_file), exist_ok=True)
                    try:
                        shutil.move(dst_file, deleted_file)
                        self.logger.info(f'Moved deleted file: {dst_file} -> {deleted_file}')
                    except Exception as e:
                        self.logger.error(f'Failed to move deleted file {dst_file}: {e}')
            # Only remove empty directory if it does not exist in source
            if root != self.target and not os.listdir(root) and not os.path.exists(src_root):
                try:
                    os.rmdir(root)
                    self.logger.info(f'Removed empty directory: {root}')
                except Exception as e:
                    self.logger.error(f'Failed to remove directory {root}: {e}')

    def sync(self):
        source_hashes = self.__build_hash_map(self.source)
        target_hashes = self.__build_hash_map(self.target)
        self.__move_or_copy_files(source_hashes, target_hashes)
        self.__move_deleted_files(source_hashes)
