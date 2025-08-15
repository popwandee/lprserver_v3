#!/usr/bin/env python3
"""
System Check Runner for LPR Server v3
รันการตรวจสอบระบบทั้งหมดและสร้างรายงานสรุป
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_script(script_name, description):
    """รัน script และแสดงผล"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Script ทำงานสำเร็จ")
            print(result.stdout)
            if result.stderr:
                print("⚠️  Warnings:")
                print(result.stderr)
            return True
        else:
            print("❌ Script ทำงานล้มเหลว")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Script {script_name} ใช้เวลานานเกินไป")
        return False
    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์ {script_name}")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def check_script_exists(script_name):
    """ตรวจสอบว่า script มีอยู่หรือไม่"""
    return Path(script_name).exists()

def generate_summary_report(results):
    """สร้างรายงานสรุป"""
    print(f"\n{'='*60}")
    print("📊 รายงานสรุปการตรวจสอบระบบ")
    print(f"{'='*60}")
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    
    print(f"\n📈 สรุปผลการตรวจสอบ:")
    print(f"   ✅ ผ่าน: {passed_checks}/{total_checks}")
    print(f"   ❌ ล้มเหลว: {total_checks - passed_checks}/{total_checks}")
    print(f"   📊 อัตราความสำเร็จ: {(passed_checks/total_checks)*100:.1f}%")
    
    # แสดงผลแต่ละ script
    print(f"\n🔍 ผลการตรวจสอบแต่ละส่วน:")
    for script_name, success in results.items():
        status = "✅ ผ่าน" if success else "❌ ล้มเหลว"
        print(f"   {script_name}: {status}")
    
    # คำแนะนำ
    print(f"\n💡 คำแนะนำ:")
    if passed_checks == total_checks:
        print("   🎉 ระบบพร้อมใช้งาน LPR Server อย่างสมบูรณ์!")
        print("   💡 สามารถเริ่มต้นใช้งานได้ทันที")
    elif passed_checks >= total_checks * 0.8:
        print("   ⚠️  ระบบเกือบพร้อมใช้งาน")
        print("   💡 ควรแก้ไขปัญหาที่พบก่อนใช้งาน")
    else:
        print("   ❌ ระบบไม่พร้อมใช้งาน")
        print("   💡 ต้องแก้ไขปัญหาหลายจุดก่อนใช้งาน")
    
    # ขั้นตอนต่อไป
    print(f"\n🔄 ขั้นตอนต่อไป:")
    if passed_checks == total_checks:
        print("   1. รัน WebSocket server: python websocket_server.py")
        print("   2. ทดสอบการเชื่อมต่อ: python test_edge_communication.py")
        print("   3. เริ่มต้นใช้งาน LPR Server")
    else:
        print("   1. ตรวจสอบรายงาน JSON ที่สร้างขึ้น")
        print("   2. แก้ไขปัญหาที่พบ")
        print("   3. รันการตรวจสอบอีกครั้ง")
    
    return passed_checks == total_checks

def save_final_report(results):
    """บันทึกรายงานสุดท้าย"""
    final_report = {
        'timestamp': datetime.now().isoformat(),
        'total_checks': len(results),
        'passed_checks': sum(1 for result in results.values() if result),
        'results': results,
        'system_ready': all(results.values())
    }
    
    try:
        with open('final_system_check_report.json', 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 บันทึกรายงานสุดท้าย: final_system_check_report.json")
    except Exception as e:
        print(f"\n❌ ไม่สามารถบันทึกรายงานได้: {e}")

def main():
    """Main function"""
    print("🚀 System Check Runner for LPR Server v3")
    print("="*60)
    print("🔍 ตรวจสอบระบบทั้งหมดเพื่อความพร้อมในการใช้งาน LPR Server")
    print("="*60)
    
    # ตรวจสอบ scripts ที่มีอยู่
    scripts_to_run = [
        ('quick_system_check.py', 'Quick System Check'),
        ('check_system_specs.py', 'Detailed System Specifications'),
        ('performance_benchmark.py', 'Performance Benchmark')
    ]
    
    available_scripts = []
    for script_name, description in scripts_to_run:
        if check_script_exists(script_name):
            available_scripts.append((script_name, description))
        else:
            print(f"⚠️  ไม่พบไฟล์ {script_name}")
    
    if not available_scripts:
        print("❌ ไม่พบ script ใดๆ สำหรับการตรวจสอบ")
        return
    
    print(f"\n📋 Scripts ที่จะรัน ({len(available_scripts)} scripts):")
    for script_name, description in available_scripts:
        print(f"   • {script_name} - {description}")
    
    # รัน scripts
    results = {}
    for script_name, description in available_scripts:
        success = run_script(script_name, description)
        results[script_name] = success
    
    # สร้างรายงานสรุป
    system_ready = generate_summary_report(results)
    
    # บันทึกรายงานสุดท้าย
    save_final_report(results)
    
    # สรุป
    print(f"\n{'='*60}")
    print("🏁 การตรวจสอบระบบเสร็จสิ้น")
    print(f"{'='*60}")
    
    if system_ready:
        print("🎉 ระบบพร้อมใช้งาน LPR Server!")
        print("💡 สามารถเริ่มต้นใช้งานได้ทันที")
        sys.exit(0)
    else:
        print("⚠️  ระบบไม่พร้อมใช้งาน")
        print("💡 ตรวจสอบรายงานและแก้ไขปัญหาที่พบ")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  การตรวจสอบถูกยกเลิก")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        sys.exit(1)

