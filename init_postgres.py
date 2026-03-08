#!/usr/bin/env python3
"""
Inisialisasi database PostgreSQL untuk Kudos System
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app.modules.kudos_system import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Inisialisasi database PostgreSQL"""
    
    # Load environment
    load_dotenv()
    
    # Database URL
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kudos_db')
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Koneksi ke PostgreSQL berhasil")
        
        # Create tables
        Base.metadata.create_all(engine)
        logger.info("✅ Tabel-tabel berhasil dibuat")
        
        # Create sample data
        from app.modules.kudos_system import KudosSystem
        kudos = KudosSystem(db_url)
        
        # Cek apakah sudah ada user
        if not kudos.get_users_list():
            # Create sample users
            users = [
                ("admin", "admin@company.com", "Admin User", "IT", True),
                ("john.doe", "john@company.com", "John Doe", "Engineering", False),
                ("jane.smith", "jane@company.com", "Jane Smith", "Marketing", False),
                ("budi", "budi@company.com", "Budi Santoso", "Sales", False),
                ("siti", "siti@company.com", "Siti Rahayu", "HR", False),
            ]
            
            for username, email, full_name, dept, is_admin in users:
                try:
                    kudos.create_user(username, email, full_name, dept, is_admin)
                    logger.info(f"  ✅ User {username} created")
                except Exception as e:
                    logger.warning(f"  ⚠️  User {username} mungkin sudah ada: {e}")
            
            logger.info("✅ Sample users created")
        
        print("\n" + "="*50)
        print("✅✅✅ DATABASE POSTGRESQL SIAP DIGUNAKAN!")
        print("="*50)
        print(f"📊 Database: {db_url}")
        print("🚀 Silakan jalankan: streamlit run app/main.py")
        print("="*50)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print("\n💡 Tips:")
        print("1. Pastikan PostgreSQL running: brew services list | grep postgres")
        print("2. Cek koneksi: psql -U postgres -h localhost -d postgres")
        print("3. Buat database: createdb -U postgres kudos_db")

if __name__ == "__main__":
    init_database()