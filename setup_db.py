#!/usr/bin/env python3
"""
Setup database untuk Kudos System
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_install_deps():
    """Cek dan install dependencies yang diperlukan"""
    try:
        import psycopg2
        logger.info("✅ psycopg2 sudah terinstall")
        return True
    except ImportError:
        logger.warning("⚠️ psycopg2 belum terinstall")
        print("\n📦 Install psycopg2 dengan perintah:")
        print("   pip install psycopg2-binary")
        print("\nAtau jalankan:")
        print("   pip install -r requirements.txt")
        return False

def check_postgres_running():
    """Cek apakah PostgreSQL running"""
    import subprocess
    
    try:
        # Cek dengan pg_isready
        result = subprocess.run(['pg_isready'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ PostgreSQL running")
            return True
        else:
            logger.error("❌ PostgreSQL tidak running")
            return False
    except FileNotFoundError:
        logger.error("❌ PostgreSQL tidak ditemukan di PATH")
        return False

def init_database():
    """Inisialisasi database"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Database URL
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kudos_db')
    
    try:
        # Import setelah psycopg2 terinstall
        from sqlalchemy import create_engine, text
        from app.modules.kudos_system import Base, KudosSystem
        
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Koneksi ke database berhasil")
        
        # Create tables
        Base.metadata.create_all(engine)
        logger.info("✅ Tabel berhasil dibuat")
        
        # Initialize KudosSystem
        kudos = KudosSystem(db_url)
        
        # Check if users exist
        users = kudos.get_users_list()
        if not users:
            logger.info("📝 Membuat sample users...")
            
            # Create sample users
            sample_users = [
                ("admin", "admin@company.com", "Admin User", "IT", True),
                ("john.doe", "john@company.com", "John Doe", "Engineering", False),
                ("jane.smith", "jane@company.com", "Jane Smith", "Marketing", False),
                ("budi.santoso", "budi@company.com", "Budi Santoso", "Sales", False),
                ("siti.rahayu", "siti@company.com", "Siti Rahayu", "HR", False),
            ]
            
            for username, email, full_name, dept, is_admin in sample_users:
                try:
                    kudos.create_user(username, email, full_name, dept, is_admin)
                    logger.info(f"  ✅ User: {username}")
                except Exception as e:
                    logger.warning(f"  ⚠️  {username}: {e}")
            
            logger.info("✅ Sample users created")
        
        print("\n" + "="*60)
        print("✅✅✅ DATABASE SIAP DIGUNAKAN!")
        print("="*60)
        print(f"📊 Database: {db_url}")
        print("\n🚀 Jalankan aplikasi:")
        print("   streamlit run app/main.py")
        print("="*60)
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        print("\n💡 Install dependencies dulu:")
        print("   pip install psycopg2-binary sqlalchemy python-dotenv")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print("\n💡 Tips:")
        print("1. Pastikan PostgreSQL running: pg_isready")
        print("2. Cek koneksi: psql -U postgres -h localhost -d postgres")
        print("3. Buat database: createdb -U postgres kudos_db")

def main():
    print("="*60)
    print("🔧 SETUP DATABASE KUDOS SYSTEM")
    print("="*60)
    
    # Step 1: Check dependencies
    if not check_and_install_deps():
        return
    
    # Step 2: Check PostgreSQL
    if not check_postgres_running():
        print("\n💡 Jalankan PostgreSQL:")
        print("   brew services start postgresql    # macOS")
        print("   sudo systemctl start postgresql   # Linux")
        print("   # Atau jalankan Postgres.app dari GUI")
        return
    
    # Step 3: Initialize database
    init_database()

if __name__ == "__main__":
    main()