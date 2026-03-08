#!/usr/bin/env python3
"""
Fix database setup with proper table order
"""

import os
import sys
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database():
    """Setup database dengan urutan yang benar"""
    
    load_dotenv()
    
    # Database URL
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kudos_db')
    
    try:
        from sqlalchemy import create_engine, text, MetaData
        from sqlalchemy.exc import ProgrammingError
        
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Koneksi ke database berhasil")
        
        # Drop existing tables if they exist (in correct order - reverse dependencies)
        logger.info("Membersihkan tabel yang ada...")
        with engine.connect() as conn:
            # Disable foreign key checks temporarily
            conn.execute(text("DROP TABLE IF EXISTS moderation_log CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS kudos CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            conn.commit()
        
        logger.info("✅ Tabel lama dihapus")
        
        # Import models AFTER cleaning
        from app.modules.kudos_system import Base, User, Kudos, ModerationLog
        
        # Create tables in correct order (SQLAlchemy will handle dependencies)
        logger.info("Membuat tabel baru...")
        Base.metadata.create_all(engine)
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            logger.info(f"✅ Tabel terbuat: {', '.join(tables)}")
        
        # Initialize KudosSystem
        from app.modules.kudos_system import KudosSystem
        kudos = KudosSystem(db_url)
        
        # Create sample users
        logger.info("📝 Membuat sample users...")
        
        sample_users = [
            ("admin", "admin@company.com", "Admin User", "IT", True),
            ("john.doe", "john@company.com", "John Doe", "Engineering", False),
            ("jane.smith", "jane@company.com", "Jane Smith", "Marketing", False),
            ("budi.santoso", "budi@company.com", "Budi Santoso", "Sales", False),
            ("siti.rahayu", "siti@company.com", "Siti Rahayu", "HR", False),
        ]
        
        for username, email, full_name, dept, is_admin in sample_users:
            try:
                user = kudos.create_user(username, email, full_name, dept, is_admin)
                logger.info(f"  ✅ User: {username} (ID: {user.id})")
            except Exception as e:
                logger.warning(f"  ⚠️  {username}: {e}")
        
        # Create sample kudos
        logger.info("📝 Membuat sample kudos...")
        
        # Get user IDs
        users = kudos.get_users_list()
        if len(users) >= 2:
            try:
                kudos.send_kudos(
                    sender_id=users[1]['id'],  # John
                    receiver_id=users[2]['id'],  # Jane
                    message="Great work on the marketing campaign! 🎉"
                )
                logger.info("  ✅ Kudos: John → Jane")
                
                kudos.send_kudos(
                    sender_id=users[2]['id'],  # Jane
                    receiver_id=users[3]['id'],  # Budi
                    message="Thanks for the excellent sales support!"
                )
                logger.info("  ✅ Kudos: Jane → Budi")
                
                kudos.send_kudos(
                    sender_id=users[3]['id'],  # Budi
                    receiver_id=users[4]['id'],  # Siti
                    message="Awesome job with the new hire training!"
                )
                logger.info("  ✅ Kudos: Budi → Siti")
            except Exception as e:
                logger.warning(f"  ⚠️  Error creating kudos: {e}")
        
        print("\n" + "="*60)
        print("✅✅✅ DATABASE BERHASIL DIPERBAIKI!")
        print("="*60)
        print(f"📊 Database: {db_url}")
        print(f"📋 Tabel: {', '.join(tables)}")
        print(f"👥 Users: {len(users)} sample users")
        print("\n🚀 Jalankan aplikasi:")
        print("   streamlit run app/main.py")
        print("="*60)
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        print("\n💡 Pastikan semua dependencies terinstall:")
        print("   pip install psycopg2-binary sqlalchemy python-dotenv")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Pastikan PostgreSQL running: pg_isready")
        print("2. Cek koneksi: psql -U postgres -h localhost -d postgres")
        print("3. Buat database: createdb -U postgres kudos_db")

if __name__ == "__main__":
    print("="*60)
    print("🔧 FIX DATABASE KUDOS SYSTEM")
    print("="*60)
    fix_database()