#!/usr/bin/env python3
"""
Seed database with sample users
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.modules.kudos_system import KudosSystem
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

def seed():
    print("="*60)
    print("🌱 SEEDING DATABASE")
    print("="*60)
    
    # Initialize
    k = KudosSystem()
    
    # Sample users
    users = [
        ('admin', 'admin@company.com', 'Admin User', 'IT', True),
        ('john.doe', 'john@company.com', 'John Doe', 'Engineering', False),
        ('jane.smith', 'jane@company.com', 'Jane Smith', 'Marketing', False),
        ('budi.santoso', 'budi@company.com', 'Budi Santoso', 'Sales', False),
        ('siti.rahayu', 'siti@company.com', 'Siti Rahayu', 'HR', False),
    ]
    
    # Insert users
    print("\n📝 Adding users...")
    for username, email, full_name, dept, is_admin in users:
        try:
            user = k.create_user(username, email, full_name, dept, is_admin)
            print(f"   ✅ {full_name} (ID: {user.id})")
        except Exception as e:
            print(f"   ⚠️ {full_name}: {e}")
    
    # Verify
    print("\n📊 Verifying...")
    users_list = k.get_users_list()
    print(f"   ✅ Total users: {len(users_list)}")
    
    print("\n👥 Users in database:")
    for u in users_list:
        print(f"   - {u['full_name']} (ID: {u['id']})")
    
    print("\n" + "="*60)
    print("✅✅✅ SEEDING COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    seed()
