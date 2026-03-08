#!/usr/bin/env python3
"""
Debug final untuk masalah database Kudos System
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.modules.kudos_system import KudosSystem
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def debug_final():
    """Debug semua kemungkinan masalah database"""
    
    print("="*70)
    print("🔍 FINAL DATABASE DEBUGGING")
    print("="*70)
    
    # 1. Cek file .env
    print("\n1. 📁 Checking .env file...")
    env_file = Path('.env')
    if env_file.exists():
        print(f"   ✅ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            print(f"   📄 Content: {content[:100]}...")
    else:
        print("   ❌ .env file NOT FOUND!")
        print("   Creating default .env...")
        with open('.env', 'w') as f:
            f.write("DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kudos_db")
        print("   ✅ .env created")
    
    # 2. Cek environment variable
    print("\n2. 🌍 Checking environment variables...")
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        print(f"   ✅ DATABASE_URL found: {db_url}")
    else:
        db_url = 'postgresql://postgres:postgres@localhost:5432/kudos_db'
        print(f"   ⚠️ Using default: {db_url}")
    
    # 3. Test koneksi PostgreSQL
    print("\n3. 🐘 Testing PostgreSQL connection...")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).scalar()
            print(f"   ✅ Connected to PostgreSQL")
            print(f"   📊 Version: {result[:50]}...")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n   💡 Tips:")
        print("   - Is PostgreSQL running? 'pg_isready'")
        print("   - Check credentials in .env")
        return False
    
    # 4. Cek database dan tabel
    print("\n4. 📊 Checking database and tables...")
    with engine.connect() as conn:
        # List databases
        dbs = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false")).fetchall()
        print(f"   📋 Available databases: {', '.join([db[0] for db in dbs if db[0] not in ['postgres', 'template0', 'template1']])}")
        
        # Connect to kudos_db
        conn.execute(text("SET search_path TO public"))
        
        # List tables
        tables = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
        """)).fetchall()
        
        if tables:
            print(f"   ✅ Tables found: {', '.join([t[0] for t in tables])}")
        else:
            print("   ❌ No tables found in public schema!")
    
    # 5. Cek data users
    print("\n5. 👥 Checking users data...")
    try:
        with engine.connect() as conn:
            # Try to query users
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"   ✅ Users table exists with {count} records")
            
            if count > 0:
                users = conn.execute(text("SELECT id, full_name, email FROM users")).fetchall()
                print("\n   👤 Users in database:")
                for u in users:
                    print(f"      - ID {u[0]}: {u[1]} ({u[2]})")
            else:
                print("   ⚠️ Users table is EMPTY!")
                
    except Exception as e:
        print(f"   ❌ Error accessing users table: {e}")
    
    # 6. Test KudosSystem langsung
    print("\n6. 🔧 Testing KudosSystem class...")
    try:
        k = KudosSystem(db_url)
        print("   ✅ KudosSystem initialized")
        
        users = k.get_users_list()
        print(f"   📊 KudosSystem.get_users_list() returned {len(users)} users")
        
        if users:
            print("\n   👥 Users from KudosSystem:")
            for u in users:
                print(f"      - {u['full_name']} (ID: {u['id']})")
        else:
            print("   ❌ KudosSystem returned 0 users!")
            
            # Try to create a test user
            print("\n   🔧 Attempting to create test user...")
            try:
                test_user = k.create_user(
                    username="test_user",
                    email="test@example.com", 
                    full_name="Test User",
                    department="Testing"
                )
                print(f"   ✅ Test user created with ID: {test_user.id}")
                
                # Try again
                users = k.get_users_list()
                print(f"   📊 Now found {len(users)} users")
                
            except Exception as e:
                print(f"   ❌ Failed to create test user: {e}")
                
    except Exception as e:
        print(f"   ❌ KudosSystem error: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. Recommendations
    print("\n" + "="*70)
    print("📋 RECOMMENDATIONS:")
    print("="*70)
    
    print("\n👉 If database has no tables, run:")
    print("   python fix_kudos_db_final.py")
    
    print("\n👉 If database has tables but no users, run:")
    print("   python seed_database.py")
    
    print("\n👉 If connection errors, check PostgreSQL:")
    print("   pg_isready")
    print("   psql -U postgres -d kudos_db -c 'SELECT 1'")
    
    print("\n👉 To reset everything:")
    print("   dropdb -U postgres kudos_db")
    print("   createdb -U postgres kudos_db")
    print("   python fix_kudos_db_final.py")
    
    print("="*70)

if __name__ == "__main__":
    debug_final()