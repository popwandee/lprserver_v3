#!/usr/bin/env python3
"""
Performance Benchmark for LPR Server v3
ทดสอบ performance ของระบบสำหรับการใช้งาน LPR Server
"""

import time
import psutil
import json
import threading
import socket
import base64
import random
import string
from datetime import datetime
from pathlib import Path
import platform

class PerformanceBenchmark:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'benchmarks': {},
            'recommendations': []
        }
    
    def get_system_info(self):
        """เก็บข้อมูลระบบ"""
        self.results['system_info'] = {
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'memory_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'platform': platform.platform(),
            'python_version': platform.python_version()
        }
    
    def benchmark_cpu(self):
        """ทดสอบ CPU performance"""
        print("🔍 ทดสอบ CPU Performance...")
        
        # Single-threaded CPU test
        start_time = time.time()
        for _ in range(1000000):
            pass
        single_thread_time = time.time() - start_time
        
        # Multi-threaded CPU test
        def cpu_worker():
            for _ in range(100000):
                pass
        
        start_time = time.time()
        threads = []
        for _ in range(min(4, psutil.cpu_count())):
            t = threading.Thread(target=cpu_worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        multi_thread_time = time.time() - start_time
        
        # CPU frequency test
        cpu_freq = psutil.cpu_freq()
        current_freq = cpu_freq.current if cpu_freq else 0
        
        self.results['benchmarks']['cpu'] = {
            'single_thread_time': single_thread_time,
            'multi_thread_time': multi_thread_time,
            'current_freq_mhz': current_freq,
            'cpu_percent': psutil.cpu_percent(interval=1)
        }
        
        print(f"   ✅ Single-thread: {single_thread_time:.4f}s")
        print(f"   ✅ Multi-thread: {multi_thread_time:.4f}s")
        print(f"   ✅ CPU Frequency: {current_freq:.0f} MHz")
    
    def benchmark_memory(self):
        """ทดสอบ Memory performance"""
        print("🔍 ทดสอบ Memory Performance...")
        
        # Memory allocation test
        start_time = time.time()
        test_data = []
        try:
            for i in range(100000):
                test_data.append(f"test_string_{i}" * 10)
            allocation_time = time.time() - start_time
            allocation_success = True
        except MemoryError:
            allocation_time = float('inf')
            allocation_success = False
        
        # Memory access test
        if allocation_success:
            start_time = time.time()
            for item in test_data:
                _ = len(item)
            access_time = time.time() - start_time
        else:
            access_time = float('inf')
        
        # Memory cleanup
        if allocation_success:
            start_time = time.time()
            del test_data
            cleanup_time = time.time() - start_time
        else:
            cleanup_time = float('inf')
        
        self.results['benchmarks']['memory'] = {
            'allocation_time': allocation_time,
            'access_time': access_time,
            'cleanup_time': cleanup_time,
            'allocation_success': allocation_success,
            'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2)
        }
        
        print(f"   ✅ Allocation: {allocation_time:.4f}s")
        print(f"   ✅ Access: {access_time:.4f}s")
        print(f"   ✅ Cleanup: {cleanup_time:.4f}s")
    
    def benchmark_disk(self):
        """ทดสอบ Disk performance"""
        print("🔍 ทดสอบ Disk Performance...")
        
        # Write test
        test_file = Path("benchmark_test_write.txt")
        start_time = time.time()
        try:
            with open(test_file, 'w') as f:
                for i in range(10000):
                    f.write(f"Benchmark test line {i}\n")
            write_time = time.time() - start_time
            write_success = True
        except Exception as e:
            write_time = float('inf')
            write_success = False
            print(f"   ❌ Write error: {e}")
        
        # Read test
        if write_success:
            start_time = time.time()
            try:
                with open(test_file, 'r') as f:
                    content = f.read()
                read_time = time.time() - start_time
                read_success = True
            except Exception as e:
                read_time = float('inf')
                read_success = False
                print(f"   ❌ Read error: {e}")
        else:
            read_time = float('inf')
            read_success = False
        
        # Cleanup
        if test_file.exists():
            try:
                test_file.unlink()
            except:
                pass
        
        self.results['benchmarks']['disk'] = {
            'write_time': write_time,
            'read_time': read_time,
            'write_success': write_success,
            'read_success': read_success
        }
        
        print(f"   ✅ Write: {write_time:.4f}s")
        print(f"   ✅ Read: {read_time:.4f}s")
    
    def benchmark_network(self):
        """ทดสอบ Network performance"""
        print("🔍 ทดสอบ Network Performance...")
        
        # Local network test
        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 8765))
            sock.close()
            local_network_time = time.time() - start_time
            local_network_success = result != 0  # Port should be closed for test
        except Exception:
            local_network_time = float('inf')
            local_network_success = False
        
        # Internet connectivity test
        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect(('8.8.8.8', 53))
            sock.close()
            internet_time = time.time() - start_time
            internet_success = True
        except Exception:
            internet_time = float('inf')
            internet_success = False
        
        self.results['benchmarks']['network'] = {
            'local_network_time': local_network_time,
            'internet_time': internet_time,
            'local_network_success': local_network_success,
            'internet_success': internet_success
        }
        
        print(f"   ✅ Local network: {local_network_time:.4f}s")
        print(f"   ✅ Internet: {internet_time:.4f}s")
    
    def benchmark_json_processing(self):
        """ทดสอบ JSON processing performance"""
        print("🔍 ทดสอบ JSON Processing Performance...")
        
        # Create test data
        test_data = {
            'detection_id': 'test_123',
            'camera_id': 'camera_001',
            'checkpoint_id': 'checkpoint_001',
            'timestamp': datetime.now().isoformat(),
            'vehicles_count': 2,
            'plates_count': 2,
            'ocr_results': ['ABC1234', 'XYZ789'],
            'vehicle_detections': [
                {'bbox': [100, 100, 200, 200], 'confidence': 0.95},
                {'bbox': [300, 300, 400, 400], 'confidence': 0.88}
            ],
            'plate_detections': [
                {'bbox': [150, 150, 180, 170], 'confidence': 0.92},
                {'bbox': [350, 350, 380, 370], 'confidence': 0.85}
            ],
            'processing_time_ms': 150,
            'annotated_image': 'base64_encoded_image_data_placeholder',
            'cropped_plates': ['base64_plate1', 'base64_plate2']
        }
        
        # JSON serialization test
        start_time = time.time()
        for _ in range(1000):
            json_str = json.dumps(test_data)
        serialization_time = time.time() - start_time
        
        # JSON deserialization test
        start_time = time.time()
        for _ in range(1000):
            parsed_data = json.loads(json_str)
        deserialization_time = time.time() - start_time
        
        self.results['benchmarks']['json_processing'] = {
            'serialization_time': serialization_time,
            'deserialization_time': deserialization_time,
            'operations_per_second': 1000 / serialization_time
        }
        
        print(f"   ✅ Serialization: {serialization_time:.4f}s (1000 ops)")
        print(f"   ✅ Deserialization: {deserialization_time:.4f}s (1000 ops)")
        print(f"   ✅ Operations/sec: {1000 / serialization_time:.0f}")
    
    def benchmark_base64_processing(self):
        """ทดสอบ Base64 processing performance"""
        print("🔍 ทดสอบ Base64 Processing Performance...")
        
        # Create test image data
        test_image_data = ''.join(random.choices(string.ascii_letters + string.digits, k=10000))
        test_image_bytes = test_image_data.encode('utf-8')
        
        # Base64 encoding test
        start_time = time.time()
        for _ in range(100):
            encoded = base64.b64encode(test_image_bytes)
        encoding_time = time.time() - start_time
        
        # Base64 decoding test
        start_time = time.time()
        for _ in range(100):
            decoded = base64.b64decode(encoded)
        decoding_time = time.time() - start_time
        
        self.results['benchmarks']['base64_processing'] = {
            'encoding_time': encoding_time,
            'decoding_time': decoding_time,
            'data_size_bytes': len(test_image_bytes)
        }
        
        print(f"   ✅ Encoding: {encoding_time:.4f}s (100 ops)")
        print(f"   ✅ Decoding: {decoding_time:.4f}s (100 ops)")
        print(f"   ✅ Data size: {len(test_image_bytes)} bytes")
    
    def benchmark_concurrent_operations(self):
        """ทดสอบ concurrent operations"""
        print("🔍 ทดสอบ Concurrent Operations...")
        
        def worker(worker_id):
            # Simulate LPR processing
            time.sleep(0.01)  # Simulate processing time
            return f"worker_{worker_id}_completed"
        
        # Single-threaded test
        start_time = time.time()
        results = []
        for i in range(10):
            results.append(worker(i))
        single_thread_time = time.time() - start_time
        
        # Multi-threaded test
        start_time = time.time()
        threads = []
        results = []
        for i in range(10):
            t = threading.Thread(target=lambda i=i: results.append(worker(i)))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        multi_thread_time = time.time() - start_time
        
        self.results['benchmarks']['concurrent_operations'] = {
            'single_thread_time': single_thread_time,
            'multi_thread_time': multi_thread_time,
            'speedup_ratio': single_thread_time / multi_thread_time if multi_thread_time > 0 else 0
        }
        
        print(f"   ✅ Single-thread: {single_thread_time:.4f}s")
        print(f"   ✅ Multi-thread: {multi_thread_time:.4f}s")
        print(f"   ✅ Speedup: {single_thread_time / multi_thread_time:.2f}x")
    
    def generate_recommendations(self):
        """สร้างคำแนะนำจากผลการทดสอบ"""
        print("\n🔍 สร้างคำแนะนำ...")
        
        recommendations = []
        benchmarks = self.results['benchmarks']
        
        # CPU recommendations
        cpu = benchmarks.get('cpu', {})
        if cpu.get('single_thread_time', 0) > 0.1:
            recommendations.append("⚠️  CPU performance ต่ำกว่ามาตรฐาน")
        elif cpu.get('single_thread_time', 0) < 0.05:
            recommendations.append("✅ CPU performance ดีเยี่ยม")
        
        # Memory recommendations
        memory = benchmarks.get('memory', {})
        if not memory.get('allocation_success', True):
            recommendations.append("⚠️  Memory allocation ล้มเหลว - ระบบมี RAM น้อยเกินไป")
        elif memory.get('allocation_time', 0) > 1.0:
            recommendations.append("⚠️  Memory allocation ช้า - อาจมีปัญหาเรื่อง RAM")
        
        # Disk recommendations
        disk = benchmarks.get('disk', {})
        if not disk.get('write_success', True):
            recommendations.append("⚠️  Disk write ล้มเหลว - ตรวจสอบ permissions และ disk space")
        elif disk.get('write_time', 0) > 2.0:
            recommendations.append("⚠️  Disk write ช้า - อาจเป็น SSD ที่ช้าหรือ disk ที่มีปัญหา")
        
        # Network recommendations
        network = benchmarks.get('network', {})
        if not network.get('internet_success', True):
            recommendations.append("⚠️  ไม่มีการเชื่อมต่ออินเทอร์เน็ต")
        
        # JSON processing recommendations
        json_bench = benchmarks.get('json_processing', {})
        ops_per_sec = json_bench.get('operations_per_second', 0)
        if ops_per_sec < 1000:
            recommendations.append("⚠️  JSON processing ช้า - อาจมีผลต่อ performance")
        elif ops_per_sec > 5000:
            recommendations.append("✅ JSON processing เร็วมาก")
        
        # Concurrent operations recommendations
        concurrent = benchmarks.get('concurrent_operations', {})
        speedup = concurrent.get('speedup_ratio', 0)
        if speedup < 1.5:
            recommendations.append("⚠️  Concurrent operations ไม่ได้ประโยชน์ - อาจเป็น single-core CPU")
        elif speedup > 3.0:
            recommendations.append("✅ Concurrent operations ทำงานได้ดีเยี่ยม")
        
        self.results['recommendations'] = recommendations
        
        for rec in recommendations:
            print(f"   {rec}")
    
    def save_results(self, filename="performance_benchmark_report.json"):
        """บันทึกผลการทดสอบ"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 บันทึกผลการทดสอบเป็นไฟล์: {filename}")
        except Exception as e:
            print(f"\n❌ ไม่สามารถบันทึกไฟล์ได้: {e}")
    
    def print_summary(self):
        """แสดงสรุปผลการทดสอบ"""
        print("\n" + "="*60)
        print("📊 สรุปผลการทดสอบ Performance Benchmark")
        print("="*60)
        
        benchmarks = self.results['benchmarks']
        
        print(f"\n⚡ Performance Summary:")
        print(f"   CPU: {benchmarks.get('cpu', {}).get('single_thread_time', 0):.4f}s")
        print(f"   Memory: {benchmarks.get('memory', {}).get('allocation_time', 0):.4f}s")
        print(f"   Disk Write: {benchmarks.get('disk', {}).get('write_time', 0):.4f}s")
        print(f"   JSON Processing: {benchmarks.get('json_processing', {}).get('operations_per_second', 0):.0f} ops/sec")
        print(f"   Concurrent Speedup: {benchmarks.get('concurrent_operations', {}).get('speedup_ratio', 0):.2f}x")
        
        # Overall assessment
        issues = len([r for r in self.results['recommendations'] if '⚠️' in r])
        if issues == 0:
            print(f"\n✅ ระบบมี performance ที่ดีสำหรับ LPR Server")
        elif issues <= 2:
            print(f"\n⚠️  ระบบมี performance ที่ยอมรับได้ แต่ควรปรับปรุง {issues} จุด")
        else:
            print(f"\n❌ ระบบมี performance ที่ต่ำ ต้องปรับปรุง {issues} จุด")
    
    def run_all_benchmarks(self):
        """รันการทดสอบทั้งหมด"""
        print("🚀 เริ่มต้น Performance Benchmark สำหรับ LPR Server v3")
        print("="*60)
        
        try:
            self.get_system_info()
            self.benchmark_cpu()
            self.benchmark_memory()
            self.benchmark_disk()
            self.benchmark_network()
            self.benchmark_json_processing()
            self.benchmark_base64_processing()
            self.benchmark_concurrent_operations()
            self.generate_recommendations()
            
            print("\n" + "="*60)
            print("✅ การทดสอบเสร็จสิ้น")
            print("="*60)
            
            self.print_summary()
            self.save_results()
            
        except Exception as e:
            print(f"\n❌ เกิดข้อผิดพลาดในการทดสอบ: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()

if __name__ == "__main__":
    main()

