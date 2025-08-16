#!/usr/bin/env python3
"""
System Specification Checker for LPR Server v3
ตรวจสอบ spec ของเครื่อง local machine เพื่อความพร้อมในการใช้งาน LPR Server
"""

import os
import sys
import platform
import psutil
import subprocess
import json
import socket
import time
from datetime import datetime
from pathlib import Path

class SystemSpecChecker:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'hardware_specs': {},
            'software_specs': {},
            'network_specs': {},
            'storage_specs': {},
            'performance_tests': {},
            'recommendations': []
        }
    
    def check_system_info(self):
        """ตรวจสอบข้อมูลระบบพื้นฐาน"""
        print("🔍 ตรวจสอบข้อมูลระบบพื้นฐาน...")
        
        self.results['system_info'] = {
            'os_name': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'architecture': platform.architecture()[0],
            'machine': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_version': sys.version,
            'python_executable': sys.executable
        }
        
        print(f"   ✅ OS: {self.results['system_info']['os_name']} {self.results['system_info']['os_version']}")
        print(f"   ✅ Architecture: {self.results['system_info']['architecture']}")
        print(f"   ✅ Python: {self.results['system_info']['python_version'].split()[0]}")
    
    def check_hardware_specs(self):
        """ตรวจสอบ spec ของ hardware"""
        print("\n🔍 ตรวจสอบ Hardware Specifications...")
        
        # CPU Information
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
        
        # Memory Information
        memory = psutil.virtual_memory()
        memory_info = {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'percent_used': memory.percent,
            'percent_available': 100 - memory.percent
        }
        
        # Disk Information
        disk_info = {}
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.device] = {
                    'mountpoint': partition.mountpoint,
                    'filesystem': partition.fstype,
                    'total_gb': round(usage.total / (1024**3), 2),
                    'used_gb': round(usage.used / (1024**3), 2),
                    'free_gb': round(usage.free / (1024**3), 2),
                    'percent_used': round((usage.used / usage.total) * 100, 2)
                }
            except PermissionError:
                continue
        
        self.results['hardware_specs'] = {
            'cpu': cpu_info,
            'memory': memory_info,
            'disks': disk_info
        }
        
        print(f"   ✅ CPU: {cpu_info['physical_cores']} physical cores, {cpu_info['logical_cores']} logical cores")
        print(f"   ✅ Memory: {memory_info['total_gb']} GB total, {memory_info['available_gb']} GB available")
        print(f"   ✅ Disks: {len(disk_info)} partitions found")
    
    def check_software_specs(self):
        """ตรวจสอบ software และ dependencies"""
        print("\n🔍 ตรวจสอบ Software Specifications...")
        
        # Check Python packages
        required_packages = [
            'flask', 'flask_socketio', 'flask_sqlalchemy', 'psutil',
            'requests', 'eventlet', 'python_socketio', 'python_engineio'
        ]
        
        installed_packages = {}
        missing_packages = []
        
        for package in required_packages:
            try:
                import importlib
                module = importlib.import_module(package.replace('-', '_'))
                version = getattr(module, '__version__', 'unknown')
                installed_packages[package] = version
            except ImportError:
                missing_packages.append(package)
        
        # Check system services
        services_status = {}
        services_to_check = ['nginx', 'apache2', 'postgresql', 'mysql', 'redis']
        
        for service in services_to_check:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], 
                                      capture_output=True, text=True, timeout=5)
                services_status[service] = result.stdout.strip()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                services_status[service] = 'not_found'
        
        # Check Docker
        docker_available = False
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            docker_available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        self.results['software_specs'] = {
            'python_packages': installed_packages,
            'missing_packages': missing_packages,
            'system_services': services_status,
            'docker_available': docker_available
        }
        
        print(f"   ✅ Python packages: {len(installed_packages)} installed, {len(missing_packages)} missing")
        print(f"   ✅ Docker: {'Available' if docker_available else 'Not available'}")
    
    def check_network_specs(self):
        """ตรวจสอบ network specifications"""
        print("\n🔍 ตรวจสอบ Network Specifications...")
        
        # Network interfaces
        network_interfaces = {}
        for interface, addresses in psutil.net_if_addrs().items():
            for addr in addresses:
                if addr.family == socket.AF_INET:  # IPv4
                    network_interfaces[interface] = {
                        'ip': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    }
                    break
        
        # Network connections
        try:
            connections = psutil.net_connections()
            active_connections = len([conn for conn in connections if conn.status == 'ESTABLISHED'])
        except PermissionError:
            active_connections = 'permission_denied'
        
        # Port availability check
        ports_to_check = [80, 443, 5000, 8765, 3306, 5432]
        port_status = {}
        
        for port in ports_to_check:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                port_status[port] = 'open' if result == 0 else 'closed'
            except Exception:
                port_status[port] = 'error'
        
        # Internet connectivity
        internet_available = False
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            internet_available = True
        except OSError:
            pass
        
        self.results['network_specs'] = {
            'interfaces': network_interfaces,
            'active_connections': active_connections,
            'port_status': port_status,
            'internet_available': internet_available
        }
        
        print(f"   ✅ Network interfaces: {len(network_interfaces)} found")
        print(f"   ✅ Internet connectivity: {'Available' if internet_available else 'Not available'}")
        print(f"   ✅ Port 8765 (WebSocket): {port_status.get(8765, 'unknown')}")
    
    def check_storage_specs(self):
        """ตรวจสอบ storage specifications"""
        print("\n🔍 ตรวจสอบ Storage Specifications...")
        
        # Check storage directories
        storage_paths = {
            'logs': 'logs/',
            'storage': 'storage/',
            'database': 'database/',
            'templates': 'templates/',
            'static': 'web/static/'
        }
        
        storage_status = {}
        for name, path in storage_paths.items():
            full_path = Path(path)
            storage_status[name] = {
                'exists': full_path.exists(),
                'is_dir': full_path.is_dir() if full_path.exists() else False,
                'writable': os.access(full_path, os.W_OK) if full_path.exists() else False,
                'path': str(full_path.absolute())
            }
        
        # Check file permissions
        file_permissions = {}
        important_files = [
            'websocket_server.py',
            'config.py',
            'requirements.txt',
            'run.py'
        ]
        
        for file in important_files:
            file_path = Path(file)
            file_permissions[file] = {
                'exists': file_path.exists(),
                'readable': os.access(file_path, os.R_OK) if file_path.exists() else False,
                'executable': os.access(file_path, os.X_OK) if file_path.exists() else False
            }
        
        self.results['storage_specs'] = {
            'directories': storage_status,
            'files': file_permissions
        }
        
        print(f"   ✅ Storage directories: {len([s for s in storage_status.values() if s['exists']])} found")
        print(f"   ✅ Important files: {len([f for f in file_permissions.values() if f['exists']])} found")
    
    def run_performance_tests(self):
        """ทดสอบ performance ของระบบ"""
        print("\n🔍 ทดสอบ Performance...")
        
        # CPU performance test
        start_time = time.time()
        for _ in range(1000000):
            pass
        cpu_test_time = time.time() - start_time
        
        # Memory performance test
        try:
            test_data = []
            for i in range(100000):
                test_data.append(f"test_string_{i}")
            memory_test_success = True
        except MemoryError:
            memory_test_success = False
        
        # Disk write test
        try:
            test_file = Path("temp_performance_test.txt")
            with open(test_file, 'w') as f:
                f.write("Performance test data" * 1000)
            test_file.unlink()  # Clean up
            disk_test_success = True
        except Exception:
            disk_test_success = False
        
        self.results['performance_tests'] = {
            'cpu_test_time': cpu_test_time,
            'memory_test_success': memory_test_success,
            'disk_test_success': disk_test_success
        }
        
        print(f"   ✅ CPU test: {cpu_test_time:.4f} seconds")
        print(f"   ✅ Memory test: {'Passed' if memory_test_success else 'Failed'}")
        print(f"   ✅ Disk test: {'Passed' if disk_test_success else 'Failed'}")
    
    def generate_recommendations(self):
        """สร้างคำแนะนำสำหรับการปรับปรุงระบบ"""
        print("\n🔍 สร้างคำแนะนำ...")
        
        recommendations = []
        
        # CPU recommendations
        cpu_cores = self.results['hardware_specs']['cpu']['physical_cores']
        if cpu_cores < 2:
            recommendations.append("⚠️  ควรใช้ CPU อย่างน้อย 2 cores สำหรับ production")
        elif cpu_cores >= 4:
            recommendations.append("✅ CPU cores เพียงพอสำหรับ production")
        
        # Memory recommendations
        memory_gb = self.results['hardware_specs']['memory']['total_gb']
        if memory_gb < 4:
            recommendations.append("⚠️  ควรใช้ RAM อย่างน้อย 4 GB สำหรับ production")
        elif memory_gb >= 8:
            recommendations.append("✅ RAM เพียงพอสำหรับ production")
        
        # Storage recommendations
        for device, info in self.results['hardware_specs']['disks'].items():
            if info['free_gb'] < 10:
                recommendations.append(f"⚠️  Disk {device} มีพื้นที่ว่างน้อย (เหลือ {info['free_gb']} GB)")
        
        # Software recommendations
        if self.results['software_specs']['missing_packages']:
            recommendations.append(f"⚠️  ติดตั้ง packages ที่ขาด: {', '.join(self.results['software_specs']['missing_packages'])}")
        
        # Network recommendations
        if not self.results['network_specs']['internet_available']:
            recommendations.append("⚠️  ไม่มีการเชื่อมต่ออินเทอร์เน็ต")
        
        if self.results['network_specs']['port_status'].get(8765) == 'open':
            recommendations.append("⚠️  Port 8765 ถูกใช้งานอยู่แล้ว")
        
        # Performance recommendations
        if self.results['performance_tests']['cpu_test_time'] > 0.1:
            recommendations.append("⚠️  CPU performance ต่ำกว่ามาตรฐาน")
        
        if not self.results['performance_tests']['memory_test_success']:
            recommendations.append("⚠️  Memory performance มีปัญหา")
        
        if not self.results['performance_tests']['disk_test_success']:
            recommendations.append("⚠️  Disk performance มีปัญหา")
        
        self.results['recommendations'] = recommendations
        
        for rec in recommendations:
            print(f"   {rec}")
    
    def save_results(self, filename="system_specs_report.json"):
        """บันทึกผลการตรวจสอบเป็นไฟล์ JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 บันทึกผลการตรวจสอบเป็นไฟล์: {filename}")
        except Exception as e:
            print(f"\n❌ ไม่สามารถบันทึกไฟล์ได้: {e}")
    
    def print_summary(self):
        """แสดงสรุปผลการตรวจสอบ"""
        print("\n" + "="*60)
        print("📊 สรุปผลการตรวจสอบ System Specifications")
        print("="*60)
        
        # System Info
        sys_info = self.results['system_info']
        print(f"\n🖥️  ระบบ: {sys_info['os_name']} {sys_info['os_version']}")
        print(f"🏗️  Architecture: {sys_info['architecture']}")
        print(f"🐍 Python: {sys_info['python_version'].split()[0]}")
        
        # Hardware
        hw = self.results['hardware_specs']
        print(f"\n💻 Hardware:")
        print(f"   CPU: {hw['cpu']['physical_cores']} cores ({hw['cpu']['logical_cores']} threads)")
        print(f"   RAM: {hw['memory']['total_gb']} GB ({hw['memory']['available_gb']} GB available)")
        print(f"   Storage: {len(hw['disks'])} partitions")
        
        # Software
        sw = self.results['software_specs']
        print(f"\n📦 Software:")
        print(f"   Python packages: {len(sw['python_packages'])} installed")
        print(f"   Missing packages: {len(sw['missing_packages'])}")
        print(f"   Docker: {'Available' if sw['docker_available'] else 'Not available'}")
        
        # Network
        net = self.results['network_specs']
        print(f"\n🌐 Network:")
        print(f"   Interfaces: {len(net['interfaces'])}")
        print(f"   Internet: {'Available' if net['internet_available'] else 'Not available'}")
        print(f"   WebSocket port (8765): {net['port_status'].get(8765, 'unknown')}")
        
        # Performance
        perf = self.results['performance_tests']
        print(f"\n⚡ Performance:")
        print(f"   CPU test: {perf['cpu_test_time']:.4f}s")
        print(f"   Memory test: {'Passed' if perf['memory_test_success'] else 'Failed'}")
        print(f"   Disk test: {'Passed' if perf['disk_test_success'] else 'Failed'}")
        
        # Recommendations
        print(f"\n💡 คำแนะนำ ({len(self.results['recommendations'])} items):")
        for i, rec in enumerate(self.results['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        # Overall assessment
        critical_issues = len([r for r in self.results['recommendations'] if '⚠️' in r])
        if critical_issues == 0:
            print(f"\n✅ ระบบพร้อมใช้งาน LPR Server")
        elif critical_issues <= 3:
            print(f"\n⚠️  ระบบพร้อมใช้งาน แต่ควรปรับปรุง {critical_issues} จุด")
        else:
            print(f"\n❌ ระบบไม่พร้อมใช้งาน ต้องปรับปรุง {critical_issues} จุด")
    
    def run_all_checks(self):
        """รันการตรวจสอบทั้งหมด"""
        print("🚀 เริ่มต้นตรวจสอบ System Specifications สำหรับ LPR Server v3")
        print("="*60)
        
        try:
            self.check_system_info()
            self.check_hardware_specs()
            self.check_software_specs()
            self.check_network_specs()
            self.check_storage_specs()
            self.run_performance_tests()
            self.generate_recommendations()
            
            print("\n" + "="*60)
            print("✅ การตรวจสอบเสร็จสิ้น")
            print("="*60)
            
            self.print_summary()
            self.save_results()
            
        except Exception as e:
            print(f"\n❌ เกิดข้อผิดพลาดในการตรวจสอบ: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    checker = SystemSpecChecker()
    checker.run_all_checks()

if __name__ == "__main__":
    main()

