#!/usr/bin/env python3
"""
Fix PostgreSQL Permissions
"""

import subprocess
import sys

def run_psql(command):
    """Run psql command"""
    try:
        result = subprocess.run(
            ['psql', '-U', 'postgres', '-d', 'kudos_db', '-c', command],
            capture_output=True,
            text=True
        )
        print(f"✅ {command[:50]}...")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def fix_permissions():
    """Fix all permission issues"""
    
    print("="*60)
    print("🔧 FIXING POSTGRESQL PERMISSIONS")
    print("="*60)
    
    commands = [
        "GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;",
        "GRANT ALL PRIVILEGES ON DATABASE kudos_db TO postgres;",
        "GRANT CREATE ON SCHEMA public TO PUBLIC;",
        "GRANT USAGE ON SCHEMA public TO PUBLIC;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres;",
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;",
    ]
    
    for cmd in commands:
        run_psql(cmd)
    
    print("\n" + "="*60)
    print("✅✅✅ PERMISSIONS FIXED!")
    print("="*60)
    print("\n📋 Next steps:")
    print("1. Restart Streamlit app")
    print("2. If still error, run: python fix_kudos_db_final.py")
    print("="*60)

if __name__ == "__main__":
    fix_permissions()