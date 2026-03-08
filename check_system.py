#!/usr/bin/env python3
"""
Script untuk memeriksa kompatibilitas sistem sebelum instalasi
Versi: Menggunakan importlib.metadata (Python 3.8+ native)
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """Periksa versi Python"""
    version = sys.version_info
    print(f"📊 Python version: {sys.version}")
    if version.major == 3 and version.minor >= 8:
        print("✅ Python 3.8+ OK")
        return True
    else:
        print("❌ Butuh Python 3.8 atau lebih baru")
        return False

def check_virtual_env():
    """Periksa apakah virtual environment aktif"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print(f"✅ Virtual environment aktif: {sys.prefix}")
        return True
    else:
        print("❌ Virtual environment TIDAK aktif")
        return False

def check_requirements_file():
    """Periksa requirements.txt dan cek paket yang sudah terinstall"""
    try:
        # Baca requirements.txt
        req_file = Path('requirements.txt')
        if not req_file.exists():
            print("❌ requirements.txt tidak ditemukan")
            return False
        
        with open(req_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"\n📋 Memeriksa {len(requirements)} paket di requirements.txt...")
        
        # Cek paket yang sudah terinstall dengan pip list
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=freeze'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Gagal mendapatkan daftar paket terinstall")
            return False
        
        installed_packages = {}
        for line in result.stdout.split('\n'):
            if '==' in line:
                name, version = line.split('==', 1)
                installed_packages[name.lower()] = version
        
        # Cek setiap requirement
        all_found = True
        for req in requirements:
            # Handle paket dengan versi spesifik (contoh: streamlit==1.32.0)
            if '==' in req:
                name, version = req.split('==', 1)
                name_lower = name.lower()
                if name_lower in installed_packages:
                    installed_version = installed_packages[name_lower]
                    if installed_version == version:
                        print(f"  ✅ {name}=={version} (sesuai)")
                    else:
                        print(f"  ⚠️  {name} (butuh: {version}, terinstall: {installed_version})")
                        all_found = False
                else:
                    print(f"  ⚠️  {req} (belum terinstall)")
                    all_found = False
            else:
                # Paket tanpa versi spesifik
                name_lower = req.lower()
                if name_lower in installed_packages:
                    print(f"  ✅ {req} (terinstall: {installed_packages[name_lower]})")
                else:
                    print(f"  ⚠️  {req} (belum terinstall)")
                    all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error membaca requirements: {e}")
        return False

def check_postgres():
    """Periksa PostgreSQL"""
    try:
        # Cek dengan perintah psql
        result = subprocess.run(['which', 'psql'], capture_output=True, text=True)
        if result.returncode == 0:
            psql_path = result.stdout.strip()
            print(f"✅ PostgreSQL ditemukan di: {psql_path}")
            
            # Cek versi
            version_result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
            if version_result.returncode == 0:
                print(f"   Versi: {version_result.stdout.strip()}")
            
            # Cek apakah service running
            pg_isready = subprocess.run(['pg_isready'], capture_output=True, text=True)
            if pg_isready.returncode == 0:
                print("✅ PostgreSQL service running")
            else:
                print("⚠️  PostgreSQL terinstall tapi service mungkin tidak running")
            
            return True
        else:
            print("❌ PostgreSQL tidak ditemukan di PATH")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL tidak terinstall")
        return False

def check_disk_space():
    """Periksa ruang disk"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_mb = free // (1024 * 1024)
        free_gb = free // (1024 * 1024 * 1024)
        
        print(f"💾 Ruang disk tersedia: {free_mb} MB ({free_gb} GB)")
        
        if free_gb > 2:
            print("✅ Ruang disk sangat cukup (>2GB)")
            return True
        elif free_gb > 1:
            print("⚠️  Ruang disk cukup (1-2GB)")
            return True
        else:
            print("❌ Ruang disk terbatas (<1GB)")
            return False
    except Exception as e:
        print(f"❌ Gagal cek disk space: {e}")
        return False

def check_port_5432():
    """Periksa apakah port 5432 sudah dipakai"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5432))
        if result == 0:
            print("⚠️  Port 5432 (PostgreSQL) sudah digunakan")
            
            # Coba cek proses yang menggunakan port 5432
            if sys.platform == 'darwin' or sys.platform == 'linux':
                lsof = subprocess.run(['lsof', '-i', ':5432'], capture_output=True, text=True)
                if lsof.stdout:
                    print(f"   Proses: {lsof.stdout.split(chr(10))[1] if lsof.stdout else 'Unknown'}")
            return False
        else:
            print("✅ Port 5432 tersedia")
            return True
    except:
        print("✅ Port 5432 tersedia (asumsi)")
        return True

def check_ram():
    """Periksa RAM yang tersedia"""
    try:
        if sys.platform == 'darwin':  # macOS
            result = subprocess.run(['sysctl', 'hw.memsize'], capture_output=True, text=True)
            if result.returncode == 0:
                mem_bytes = int(result.stdout.split(':')[1].strip())
                mem_gb = mem_bytes / (1024**3)
                print(f"💿 RAM: {mem_gb:.1f} GB")
                
                if mem_gb >= 4:
                    print("✅ RAM cukup untuk menjalankan aplikasi")
                    return True
                else:
                    print("⚠️  RAM terbatas (<4GB), mungkin akan lambat")
                    return True
        else:
            print("ℹ️  Tidak bisa cek RAM (gunakan asumsi)")
            return True
    except:
        print("ℹ️  Tidak bisa cek RAM (gunakan asumsi)")
        return True

def main():
    print("="*60)
    print("🔍 SISTEM CHECKER UNTUK CUSTOMER ANALYTICS")
    print("="*60)
    print(f"📍 Direktori: {os.getcwd()}")
    print(f"🐍 Python: {sys.executable}")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_env),
        ("RAM", check_ram),
        ("Disk Space", check_disk_space),
        ("Port 5432", check_port_5432),
        ("PostgreSQL", check_postgres),
        ("Requirements Check", check_requirements_file),
    ]
    
    results = []
    print("\n📋 MEMULAI PENGECEKAN...\n")
    
    for name, func in checks:
        print(f"▶️  {name}")
        try:
            result = func()
            results.append(result)
            print("")  # Baris kosong untuk spacing
        except Exception as e:
            print(f"❌ Error: {e}\n")
            results.append(False)
    
    print("="*60)
    print("📊 RINGKASAN HASIL")
    print("="*60)
    
    all_passed = True
    for i, (name, _) in enumerate(checks):
        status = "✅" if results[i] else "❌"
        print(f"{status} {name}")
        if not results[i]:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✅✅✅ SEMUA CEK BERHASIL! Siap untuk instalasi.")
        print("\n📦 Untuk install semua dependency:")
        print("   pip install -r requirements.txt")
        print("\n🚀 Untuk menjalankan aplikasi:")
        print("   streamlit run app/main.py")
    else:
        print("\n⚠️  Ada beberapa masalah yang perlu diperbaiki:")
        for i, (name, _) in enumerate(checks):
            if not results[i]:
                if name == "Requirements Check":
                    print(f"  • {name}: Jalankan 'pip install -r requirements.txt'")
                elif name == "PostgreSQL":
                    print(f"  • {name}: Install PostgreSQL atau pastikan service berjalan")
                elif name == "Port 5432":
                    print(f"  • {name}: Port 5432 sudah dipakai, hentikan aplikasi lain")
                elif name == "Virtual Environment":
                    print(f"  • {name}: Aktifkan virtual environment dengan 'source venv/bin/activate'")
                else:
                    print(f"  • {name}: Perlu perbaikan")
    
    print("="*60)

if __name__ == "__main__":
    main()