#!/usr/bin/env python3
"""
FIX FINAL: Perbaiki struktur database Kudos System
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def fix_database():
    """Buat ulang database dengan struktur yang benar"""
    
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kudos_db')
    
    print("="*60)
    print("🔧 FIX KUDOS DATABASE - FINAL")
    print("="*60)
    print(f"📊 Database: {db_url}")
    print("="*60)
    
    # Create engine
    engine = create_engine(db_url)
    
    # Drop semua tabel dengan urutan benar (reverse dependency)
    print("\n📋 Membersihkan tabel lama...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS moderation_log CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS kudos CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.commit()
    print("✅ Tabel lama dihapus")
    
    # Buat tabel dengan SQL langsung (paling aman)
    print("\n📋 Membuat tabel baru...")
    
    with engine.connect() as conn:
        # Create users table
        conn.execute(text("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                department VARCHAR(50),
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create kudos table
        conn.execute(text("""
            CREATE TABLE kudos (
                id SERIAL PRIMARY KEY,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_visible BOOLEAN DEFAULT TRUE,
                moderated_by INTEGER,
                moderated_at TIMESTAMP,
                moderation_reason VARCHAR(200),
                FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (moderated_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """))
        
        # Create moderation_log table
        conn.execute(text("""
            CREATE TABLE moderation_log (
                id SERIAL PRIMARY KEY,
                kudos_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                action VARCHAR(20) NOT NULL,
                reason VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (kudos_id) REFERENCES kudos(id) ON DELETE CASCADE,
                FOREIGN KEY (moderator_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # Create indexes
        conn.execute(text("CREATE INDEX idx_users_username ON users(username)"))
        conn.execute(text("CREATE INDEX idx_users_email ON users(email)"))
        conn.execute(text("CREATE INDEX idx_kudos_sender ON kudos(sender_id)"))
        conn.execute(text("CREATE INDEX idx_kudos_receiver ON kudos(receiver_id)"))
        conn.execute(text("CREATE INDEX idx_kudos_created ON kudos(created_at)"))
        conn.execute(text("CREATE INDEX idx_kudos_visible ON kudos(is_visible)"))
        
        conn.commit()
    
    print("✅ Tabel berhasil dibuat:")
    print("   - users")
    print("   - kudos")
    print("   - moderation_log")
    
    # Insert sample data
    print("\n📝 Menambahkan sample data...")
    
    with engine.connect() as conn:
        # Insert users
        conn.execute(text("""
            INSERT INTO users (username, email, full_name, department, is_admin) VALUES
                ('admin', 'admin@company.com', 'Admin User', 'IT', TRUE),
                ('john.doe', 'john@company.com', 'John Doe', 'Engineering', FALSE),
                ('jane.smith', 'jane@company.com', 'Jane Smith', 'Marketing', FALSE),
                ('budi.santoso', 'budi@company.com', 'Budi Santoso', 'Sales', FALSE),
                ('siti.rahayu', 'siti@company.com', 'Siti Rahayu', 'HR', FALSE)
        """))
        
        # Get user IDs
        result = conn.execute(text("SELECT id, full_name FROM users ORDER BY id"))
        users = result.fetchall()
        
        # Insert sample kudos
        if len(users) >= 5:
            conn.execute(text(f"""
                INSERT INTO kudos (sender_id, receiver_id, message) VALUES
                    ({users[1][0]}, {users[2][0]}, 'Great work on the marketing campaign! 🎉'),
                    ({users[2][0]}, {users[3][0]}, 'Thanks for the excellent sales support!'),
                    ({users[3][0]}, {users[4][0]}, 'Awesome job with the new hire training!'),
                    ({users[1][0]}, {users[4][0]}, 'You are a star! ⭐'),
                    ({users[2][0]}, {users[1][0]}, 'Thanks for the technical help!')
            """))
        
        conn.commit()
    
    print("✅ Sample data ditambahkan:")
    for i, user in enumerate(users):
        print(f"   {i+1}. {user[1]}")
    
    # Verifikasi
    print("\n🔍 Verifikasi database...")
    with engine.connect() as conn:
        # Count users
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        
        # Count kudos
        result = conn.execute(text("SELECT COUNT(*) FROM kudos"))
        kudos_count = result.scalar()
        
        # Show users
        result = conn.execute(text("SELECT id, full_name, email, department FROM users ORDER BY id"))
        users_data = result.fetchall()
    
    print(f"✅ Users: {user_count} records")
    print(f"✅ Kudos: {kudos_count} records")
    
    print("\n👥 User list:")
    for u in users_data:
        print(f"   - ID {u[0]}: {u[1]} ({u[2]}) - {u[3]}")
    
    print("\n" + "="*60)
    print("✅✅✅ DATABASE FIX COMPLETE!")
    print("="*60)
    print("🚀 Silakan restart aplikasi:")
    print("   1. Ctrl+C untuk stop Streamlit")
    print("   2. streamlit run app/main.py")
    print("="*60)

if __name__ == "__main__":
    fix_database()