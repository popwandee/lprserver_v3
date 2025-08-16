#!/usr/bin/env python3
"""
Quick System Check for LPR Server v3
ตรวจสอบระบบแบบรวดเร็วเพื่อประเมินความพร้อมในการใช้งาน LPR Server
"""

import os
import sys
import platform
import psutil
import subprocess
from pathlib import Path

def check_python_version():
    """ตรวจสอบ Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"❌ Python {version.major}.{version.minor}.{version.micro} (ต้องการ 3.8+)"

def check_memory():
    """ตรวจสอบ RAM"""
    memory = psutil.virtual_memory()
    total_gb = memory.total / (1024**3)
    available_gb = memory.available / (1024**3)
    
    if total_gb >= 4:
        return True, f"✅ RAM: {total_gb:.1f} GB (Available: {available_gb:.1f} GB)"
    else:
        return False, f"❌ RAM: {total_gb:.1f} GB (ต้องการอย่างน้อย 4 GB)"

def check_cpu():
    """ตรวจสอบ CPU"""
    cores = psutil.cpu_count(logical=False)
    if cores >= 2:
        return True, f"✅ CPU: {cores} cores"
    else:
        return False, f"❌ CPU: {cores} cores (ต้องการอย่างน้อย 2 cores)"

def check_disk_space():
    """ตรวจสอบพื้นที่ disk"""
    try:
        current_dir = Path.cwd()
        usage = psutil.disk_usage(current_dir)
        free_gb = usage.free / (1024**3)
        
        if free_gb >= 10:
            return True, f"✅ Disk space: {free_gb:.1f} GB available"
        else:
            return False, f"❌ Disk space: {free_gb:.1f} GB (ต้องการอย่างน้อย 10 GB)"
    except:
        return False, "❌ ไม่สามารถตรวจสอบ disk space ได้"

def check_required_packages():
    """ตรวจสอบ Python packages ที่จำเป็น"""
    required = ['flask', 'flask_socketio', 'psutil', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if not missing:
        return True, f"✅ Required packages: {len(required)} installed"
    else:
        return False, f"❌ Missing packages: {', '.join(missing)}"

def check_network_connectivity():
    """ตรวจสอบการเชื่อมต่อเครือข่าย"""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True, "✅ Internet connectivity available"
    except:
        return False, "❌ No internet connectivity"

def check_port_availability():
    """ตรวจสอบ port ที่จำเป็น"""
    ports = [8765, 5000]  # WebSocket port, Flask port
    available_ports = []
    occupied_ports = []
    
    for port in ports:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result != 0:  # Port is available
                available_ports.append(port)
            else:
                occupied_ports.append(port)
        except:
            occupied_ports.append(port)
    
    if not occupied_ports:
        return True, f"✅ Required ports available: {available_ports}"
    else:
        return False, f"❌ Ports in use: {occupied_ports}"

def check_file_permissions():
    """ตรวจสอบ file permissions"""
    important_files = ['websocket_server.py', 'config.py', 'requirements.txt']
    existing_files = []
    missing_files = []
    
    for file in important_files:
        if Path(file).exists():
            existing_files.append(file)
        else:
            missing_files.append(file)
    
    if not missing_files:
        return True, f"✅ Important files: {len(existing_files)} found"
    else:
        return False, f"❌ Missing files: {', '.join(missing_files)}"

def check_directory_structure():
    """ตรวจสอบ directory structure"""
    required_dirs = ['logs', 'storage', 'templates']
    existing_dirs = []
    missing_dirs = []
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            existing_dirs.append(dir_name)
        else:
            missing_dirs.append(dir_name)
    
    if not missing_dirs:
        return True, f"✅ Required directories: {len(existing_dirs)} found"
    else:
        return False, f"❌ Missing directories: {', '.join(missing_dirs)}"

def run_quick_check():
    """รันการตรวจสอบแบบรวดเร็ว"""
    print("🚀 Quick System Check for LPR Server v3")
    print("="*50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Memory (RAM)", check_memory),
        ("CPU Cores", check_cpu),
        ("Disk Space", check_disk_space),
        ("Required Packages", check_required_packages),
        ("Network Connectivity", check_network_connectivity),
        ("Port Availability", check_port_availability),
        ("File Permissions", check_file_permissions),
        ("Directory Structure", check_directory_structure)
    ]
    
    results = []
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}...")
        success, message = check_func()
        print(f"   {message}")
        results.append((check_name, success, message))
        if success:
            passed += 1
    
    # Summary
    print("\n" + "="*50)
    print("📊 QUICK CHECK SUMMARY")
    print("="*50)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ระบบพร้อมใช้งาน LPR Server!")
        print("💡 สามารถรันคำสั่งต่อไปนี้ได้:")
        print("   python websocket_server.py")
        print("   python test_edge_communication.py")
    elif passed >= total * 0.8:  # 80% or more
        print("\n⚠️  ระบบเกือบพร้อมใช้งาน")
        print("💡 ควรแก้ไขปัญหาที่พบก่อนใช้งาน")
    else:
        print("\n❌ ระบบไม่พร้อมใช้งาน")
        print("💡 ต้องแก้ไขปัญหาหลายจุดก่อนใช้งาน")
    
    # Failed checks
    failed_checks = [r for r in results if not r[1]]
    if failed_checks:
        print(f"\n🔧 Issues to fix:")
        for i, (name, success, message) in enumerate(failed_checks, 1):
            print(f"   {i}. {name}: {message}")
    
    return passed == total

def main():
    """Main function"""
    try:
        success = run_quick_check()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  การตรวจสอบถูกยกเลิก")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

