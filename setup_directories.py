#!/usr/bin/env python3
"""
Setup script untuk membuat semua direktori yang diperlukan
"""

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_directories():
    """Buat semua direktori yang diperlukan untuk aplikasi"""
    
    base_dir = Path.cwd()
    
    # Struktur direktori yang diperlukan
    directories = [
        "data",
        "data/emails",
        "data/orders",
        "data/logs",
        "data/uploads",
        "data/exports",
        "data/backups",
        "app",
        "app/modules",
        "tests",
        "docs",
    ]
    
    logger.info("📁 Membuat struktur direktori...")
    
    for dir_path in directories:
        full_path = base_dir / dir_path
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"  ✅ {dir_path}")
        except Exception as e:
            logger.error(f"  ❌ {dir_path}: {e}")
    
    # Buat sample files jika belum ada
    emails_dir = base_dir / "data/emails"
    sample_files = [
        "order_ORD-001.pdf",
        "order_ORD-002.pdf", 
        "order_ORD-003.pdf"
    ]
    
    for sample in sample_files:
        sample_path = emails_dir / sample
        if not sample_path.exists():
            sample_path.touch()
            logger.info(f"  📄 Created sample: {sample}")
    
    # Buat .gitkeep files untuk empty directories
    for dir_path in directories:
        gitkeep = base_dir / dir_path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
    
    logger.info("\n✅ Struktur direktori siap!")
    logger.info(f"📂 Base directory: {base_dir}")
    
    # List semua direktori
    print("\n📋 Direktori yang tersedia:")
    for dir_path in sorted(directories):
        full_path = base_dir / dir_path
        if full_path.exists():
            file_count = len(list(full_path.glob("*")))
            print(f"  • {dir_path}/ ({file_count} files)")

if __name__ == "__main__":
    setup_directories()