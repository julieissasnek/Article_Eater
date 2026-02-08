"""
Article Eater Configuration Module
==================================

Centralized configuration for deployment flexibility.
"""

from .pdf_storage import (
    get_config,
    find_pdf,
    find_pdf_by_zotero_key,
    get_upload_path,
    list_zotero_pdfs,
    prepare_server_migration,
    PDFStorageConfig,
    LOCAL_CONFIG,
    SERVER_CONFIG,
)

__all__ = [
    'get_config',
    'find_pdf',
    'find_pdf_by_zotero_key',
    'get_upload_path',
    'list_zotero_pdfs',
    'prepare_server_migration',
    'PDFStorageConfig',
    'LOCAL_CONFIG',
    'SERVER_CONFIG',
]
