#!/usr/bin/env python3
"""
Debug script untuk Kudos System
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.modules.kudos_system import KudosSystem
import logging
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_kudos():
    """Debug kudos system connection"""
    
    print("="*60)
    print("🔍 DEBUGGING KUDOS SYSTEM")
    print("="*60)
    
    # 1. Cek environment variables
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/kudos_db')
    print(f"\n1. Database URL: {db_url}")
    
    # 2. Test raw connection
    print("\n2. Testing raw database connection...")
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("   ✅ Raw connection OK")
            
            # Cek tabel
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema='public'
            """))
            tables = [row[0] for row in result]
            print(f"   📋 Tables: {', '.join(tables)}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
    
    # 3. Test KudosSystem
    print("\n3. Testing KudosSystem...")
    try:
        kudos = KudosSystem(db_url)
        print("   ✅ KudosSystem initialized")
        
        # Test get_users_list
        users = kudos.get_users_list()
        print(f"   📊 Users found: {len(users)}")
        
        if users:
            print("\n   👥 User list:")
            for u in users:
                print(f"      - ID {u['id']}: {u['full_name']} ({u['email']}) - {u['department']}")
        else:
            print("   ⚠️  No users found - database needs seeding")
            
    except Exception as e:
        print(f"   ❌ KudosSystem error: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Recommendations
    print("\n" + "="*60)
    print("📋 RECOMMENDATIONS:")
    print("="*60)
    
    if 'users' in locals() and len(users) == 0:
        print("✅ Run seed script: python seed_kudos_db.py")
    
    print("✅ Refresh browser after fixing")
    print("="*60)

if __name__ == "__main__":
    debug_kudos()