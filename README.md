# sync-folder

**sync-folder** is a Python utility for one-way synchronization of two folders. It copies new and updated files from a source folder to a target folder. If a file is deleted from the source, it is moved (with its folder structure preserved) to a `Deleted` folder inside the target.

## Features

- One-way sync: source → target
- Only copies files that are new or have changed (using SHA-256 hash comparison)
- Moves files deleted from source to a `Deleted` folder in the target, preserving directory structure
- Removes empty directories from the target
- Rotating log files for sync operations

## Usage

### Requirements

- Python 3.11+
- No external dependencies

### Example

```bash
python main.py /path/to/source /path/to/target /path/to/logs