"""
PDF Storage Configuration
=========================

This module defines where Article Eater looks for PDF files.
Designed for easy migration from local development to server deployment.

MIGRATION TO SERVER:
--------------------
1. Set environment variables before starting the server:

   export AE_PDF_STORAGE_MODE=server
   export AE_PDF_PRIMARY_PATH=/srv/article_eater/pdfs
   export AE_PDF_ZOTERO_PATH=/srv/article_eater/zotero_import

2. Or edit the SERVER_CONFIG below directly.

3. Upload PDFs to the server paths, or use the upload endpoint.

Date: January 23, 2026
Version: V22.0.0 (Post-Quinean)
"""

import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)
AE_ROOT = Path(__file__).resolve().parents[2]
_AF_DATA_CANDIDATES = [
    AE_ROOT.parent / "Article_Finder_v3_2_3" / "data",
    Path.home() / "REPOS" / "Article_Finder_v3_2_3" / "data",
]


def _default_af_data_path() -> Path:
    for candidate in _AF_DATA_CANDIDATES:
        if candidate.exists():
            return candidate
    return _AF_DATA_CANDIDATES[0]


@dataclass
class PDFStorageConfig:
    """Configuration for PDF storage locations."""
    mode: str  # 'local' or 'server'
    primary_path: Path  # Main PDF storage (uploads go here)
    search_paths: List[Path]  # All paths to search for PDFs
    zotero_storage_path: Optional[Path]  # Zotero's local storage


# =============================================================================
# LOCAL DEVELOPMENT CONFIG (Professor Kirsh's machine)
# =============================================================================
LOCAL_CONFIG = PDFStorageConfig(
    mode='local',
    primary_path=AE_ROOT / 'data' / 'pdfs',
    search_paths=[
        # 1. Article Eater uploaded PDFs
        AE_ROOT / 'data' / 'pdfs',
        # 2. Article Finder's PDF collection
        _default_af_data_path(),
        # 3. Zotero's local storage (PDFs stored by attachment key)
        Path.home() / 'Zotero' / 'storage',
    ],
    zotero_storage_path=Path.home() / 'Zotero' / 'storage'
)


# =============================================================================
# SERVER DEPLOYMENT CONFIG (future)
# =============================================================================
SERVER_CONFIG = PDFStorageConfig(
    mode='server',
    primary_path=Path('/srv/article_eater/pdfs'),
    search_paths=[
        # 1. Primary server storage
        Path('/srv/article_eater/pdfs'),
        # 2. Imported from Zotero (bulk upload)
        Path('/srv/article_eater/zotero_import'),
        # 3. Legacy/migrated PDFs
        Path('/srv/article_eater/legacy'),
    ],
    zotero_storage_path=None  # No local Zotero on server
)


# =============================================================================
# ACTIVE CONFIGURATION
# =============================================================================

def get_config() -> PDFStorageConfig:
    """
    Get the active PDF storage configuration.

    Override with environment variables:
    - AE_PDF_STORAGE_MODE: 'local' or 'server'
    - AE_PDF_PRIMARY_PATH: Primary storage path
    - AE_PDF_SEARCH_PATHS: Colon-separated list of search paths
    - AE_PDF_ZOTERO_PATH: Zotero storage path (local only)
    """
    mode = os.environ.get('AE_PDF_STORAGE_MODE', 'local')

    if mode == 'server':
        config = SERVER_CONFIG
    else:
        config = LOCAL_CONFIG

    # Allow environment variable overrides
    if os.environ.get('AE_PDF_PRIMARY_PATH'):
        config.primary_path = Path(os.environ['AE_PDF_PRIMARY_PATH'])

    if os.environ.get('AE_PDF_SEARCH_PATHS'):
        paths = os.environ['AE_PDF_SEARCH_PATHS'].split(':')
        config.search_paths = [Path(p) for p in paths if p]

    if os.environ.get('AE_PDF_ZOTERO_PATH'):
        config.zotero_storage_path = Path(os.environ['AE_PDF_ZOTERO_PATH'])

    logger.info(f"PDF Storage Mode: {config.mode}")
    logger.info(f"PDF Primary Path: {config.primary_path}")
    logger.info(f"PDF Search Paths: {config.search_paths}")

    return config


def find_pdf(filename: str, zotero_key: Optional[str] = None) -> Optional[Path]:
    """
    Find a PDF file across all configured storage locations.

    Args:
        filename: The PDF filename to find
        zotero_key: Optional Zotero attachment key (8-char) for Zotero storage lookup

    Returns:
        Path to the PDF if found, None otherwise
    """
    config = get_config()

    # If we have a Zotero key, check Zotero storage first
    if zotero_key and config.zotero_storage_path:
        zotero_path = config.zotero_storage_path / zotero_key
        if zotero_path.exists():
            # Zotero stores files in {key}/{filename} structure
            for pdf in zotero_path.glob('*.pdf'):
                return pdf

    # Search all configured paths
    for search_path in config.search_paths:
        if not search_path.exists():
            continue

        # Direct match
        direct = search_path / filename
        if direct.exists():
            return direct

        # Search subdirectories (for Zotero-style storage)
        for pdf in search_path.glob(f'**/{filename}'):
            return pdf

        # Fuzzy match - filename without path
        base_name = Path(filename).name
        for pdf in search_path.glob(f'**/{base_name}'):
            return pdf

    return None


def find_pdf_by_zotero_key(zotero_key: str) -> Optional[Path]:
    """
    Find a PDF in Zotero's local storage by its attachment key.

    Zotero stores files as: ~/Zotero/storage/{8-char-key}/{filename}.pdf

    Args:
        zotero_key: The 8-character Zotero attachment key

    Returns:
        Path to the PDF if found, None otherwise
    """
    config = get_config()

    if not config.zotero_storage_path:
        return None

    zotero_dir = config.zotero_storage_path / zotero_key
    if not zotero_dir.exists():
        return None

    # Find the PDF in this directory
    pdfs = list(zotero_dir.glob('*.pdf'))
    if pdfs:
        return pdfs[0]

    return None


def get_upload_path() -> Path:
    """Get the path where uploaded PDFs should be stored."""
    config = get_config()
    config.primary_path.mkdir(parents=True, exist_ok=True)
    return config.primary_path


# =============================================================================
# MIGRATION UTILITIES
# =============================================================================

def list_zotero_pdfs() -> List[dict]:
    """
    List all PDFs in Zotero's local storage.
    Useful for migration planning.
    """
    config = get_config()

    if not config.zotero_storage_path or not config.zotero_storage_path.exists():
        return []

    pdfs = []
    for key_dir in config.zotero_storage_path.iterdir():
        if key_dir.is_dir() and len(key_dir.name) == 8:  # Zotero uses 8-char keys
            for pdf in key_dir.glob('*.pdf'):
                pdfs.append({
                    'zotero_key': key_dir.name,
                    'filename': pdf.name,
                    'path': str(pdf),
                    'size_bytes': pdf.stat().st_size
                })

    return pdfs


def prepare_server_migration() -> dict:
    """
    Generate a migration report for moving to server deployment.

    Returns:
        Dictionary with migration info and commands
    """
    config = get_config()
    zotero_pdfs = list_zotero_pdfs()

    total_size = sum(p['size_bytes'] for p in zotero_pdfs)

    return {
        'current_mode': config.mode,
        'zotero_pdfs_count': len(zotero_pdfs),
        'zotero_pdfs_size_mb': round(total_size / (1024 * 1024), 2),
        'migration_steps': [
            '1. Copy PDFs to server:',
            f'   rsync -av {config.zotero_storage_path}/ user@server:/srv/article_eater/zotero_import/',
            '',
            '2. Set environment variables on server:',
            '   export AE_PDF_STORAGE_MODE=server',
            '   export AE_PDF_PRIMARY_PATH=/srv/article_eater/pdfs',
            '',
            '3. Restart Article Eater server',
            '',
            '4. Verify with: curl http://server:8080/api/v1/annotator/pdf-config',
        ],
        'zotero_pdfs': zotero_pdfs[:10]  # First 10 as sample
    }
