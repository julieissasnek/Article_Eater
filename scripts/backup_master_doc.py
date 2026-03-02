#!/usr/bin/env python3
"""
Backup MASTER_DOC and maintain rolling history.

Creates timestamped backups with SHA-256 hashes.
Keeps last 10 backups, rotates oldest.
"""

import argparse
import hashlib
import shutil
import tarfile
from pathlib import Path
from datetime import datetime
import json

MASTER_DOC = Path("/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/MASTER_DOC_CMR_2026-02-25.md")
PARTS_DIR = Path("/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/master_doc_parts")
BACKUP_DIR = Path("/sessions/keen-busy-turing/mnt/REPOS/Article_Eater_PostQuinean_v1/docs/backups")
BACKUP_MANIFEST = BACKUP_DIR / "BACKUP_MANIFEST.json"
MAX_BACKUPS = 10

def compute_hash(filepath):
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def load_manifest():
    """Load backup manifest."""
    if BACKUP_MANIFEST.exists():
        with open(BACKUP_MANIFEST, 'r') as f:
            return json.load(f)
    return {'backups': []}

def save_manifest(manifest):
    """Save backup manifest."""
    with open(BACKUP_MANIFEST, 'w') as f:
        json.dump(manifest, f, indent=2)

def backup_master_doc():
    """Backup the master document."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Create timestamped backup
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    backup_file = BACKUP_DIR / f"MASTER_DOC_CMR_BACKUP_{timestamp}.md"

    # Check if file already exists (shouldn't happen, but be safe)
    if backup_file.exists():
        print(f"Backup already exists: {backup_file}")
        return None

    # Copy the master doc
    shutil.copy2(MASTER_DOC, backup_file)

    # Compute hash
    file_hash = compute_hash(backup_file)
    hash_file = backup_file.with_suffix('.sha256')

    with open(hash_file, 'w') as f:
        f.write(f"{file_hash}  {backup_file.name}\n")

    # Get file size
    size_bytes = backup_file.stat().st_size
    size_lines = len(backup_file.read_text(encoding='utf-8').splitlines())

    print(f"Backed up {size_lines:,} lines ({size_bytes:,} bytes) to:")
    print(f"  {backup_file.name}")
    print(f"  SHA-256: {file_hash}")

    # Update manifest
    manifest = load_manifest()
    manifest['backups'].append({
        'filename': backup_file.name,
        'timestamp': datetime.now().isoformat(),
        'sha256': file_hash,
        'size_bytes': size_bytes,
        'size_lines': size_lines,
    })

    # Keep only last MAX_BACKUPS
    while len(manifest['backups']) > MAX_BACKUPS:
        old_backup = manifest['backups'].pop(0)
        old_file = BACKUP_DIR / old_backup['filename']
        old_hash = old_file.with_suffix('.sha256')

        if old_file.exists():
            old_file.unlink()
            print(f"  Rotated out: {old_backup['filename']}")

        if old_hash.exists():
            old_hash.unlink()

    save_manifest(manifest)

    return backup_file

def backup_parts(include_manifest=True):
    """Backup the parts directory as tarball."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
    tar_file = BACKUP_DIR / f"MASTER_DOC_PARTS_BACKUP_{timestamp}.tar.gz"

    # Create tarball
    with tarfile.open(tar_file, 'w:gz') as tar:
        tar.add(PARTS_DIR, arcname='master_doc_parts')

    size_bytes = tar_file.stat().st_size
    file_hash = compute_hash(tar_file)

    hash_file = tar_file.with_suffix('.sha256')
    with open(hash_file, 'w') as f:
        f.write(f"{file_hash}  {tar_file.name}\n")

    print(f"Backed up parts directory ({size_bytes:,} bytes) to:")
    print(f"  {tar_file.name}")
    print(f"  SHA-256: {file_hash}")

    return tar_file

def main():
    parser = argparse.ArgumentParser(description='Backup MASTER_DOC')
    parser.add_argument('--parts', action='store_true',
                       help='Also backup the parts directory as tarball')
    args = parser.parse_args()

    print("Creating backup...")
    backup_file = backup_master_doc()

    if args.parts:
        print("\nBacking up parts directory...")
        backup_parts()

    print(f"\nManifest: {BACKUP_MANIFEST}")
    print("Done.")

if __name__ == '__main__':
    main()
