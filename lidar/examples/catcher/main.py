#!/usr/bin/env python3
"""
Unitree 雷达一键启动程序
自动启动数据发布器和目标检测器
"""

import subprocess
import time
import signal
import sys
import os
import threading
from pathlib import Path

class LidarSystem:
    def __init__(self):
        self.publisher_process = None
        self.detector_process = None
        self.running = False
        
        # 路径配置
        self.sdk_root = Path(__file__).parent.parent.parent
        self.publisher_path = self.sdk_root / "bin" / "unilidar_publisher_udp"
        self.detector_path = Path(__file__).parent / "simple_drone_detector.py"
        
        # 设备配置
        self.serial_device = "/dev/ttyUSB0"
        self.udp_ip = "127.0.0.1"
        self.udp_port = "12345"
        
    def check_prerequisites(self):
        """检查运行前提条件"""
        print("🔍 检查系统前提条件...")
        
        # 检查发布器程序
        if not self.publisher_path.exists():
            print(f"❌ 发布器程序不存在: {self.publisher_path}")
            print("请先编译 C++ 程序:")
            print("cd /home/xczhw/Documents/sdk/unitree_lidar_sdk")
            print("mkdir -p build && cd build")
            print("cmake .. && make -j4")
            return False
            
        # 检查检测器程序
        if not self.detector_path.exists():
            print(f"❌ 检测器程序不存在: {self.detector_path}")
            return False
            
        # 检查串口设备
        if not os.path.exists(self.serial_device):
            print(f"❌ 串口设备不存在: {self.serial_device}")
            print("请检查雷达硬件连接")
            return False
            
        # 检查串口权限
        try:
            with open(self.serial_device, 'rb'):
                pass
        except PermissionError:
            print(f"❌ 没有串口访问权限: {self.serial_device}")
            print("请运行: sudo usermod -a -G dialout $USER")
            print("然后重新登录")
            return False
        except:
            pass  # 设备可能被占用，但权限正常
            
        print("✅ 所有前提条件检查通过")
        return True
        
    def start_publisher(self):
        """启动数据发布器"""
        print(f"🚀 启动数据发布器...")
        print(f"   设备: {self.serial_device}")
        print(f"   UDP: {self.udp_ip}:{self.udp_port}")
        
        try:
            cmd = [str(self.publisher_path), self.serial_device, self.udp_ip, self.udp_port]
            self.publisher_process = subprocess.Popen(
                cmd,
                cwd=str(self.sdk_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 等待发布器初始化
            print("⏳ 等待发布器初始化...")
            time.sleep(3)
            
            # 检查进程是否正常运行
            if self.publisher_process.poll() is None:
                print("✅ 数据发布器启动成功")
                return True
            else:
                print("❌ 数据发布器启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动发布器时出错: {e}")
            return False
            
    def start_detector(self):
        """启动目标检测器"""
        print("🎯 启动目标检测器...")
        
        try:
            cmd = ["python3", str(self.detector_path)]
            self.detector_process = subprocess.Popen(
                cmd,
                cwd=str(self.detector_path.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            print("✅ 目标检测器启动成功")
            return True
            
        except Exception as e:
            print(f"❌ 启动检测器时出错: {e}")
            return False
            
    def monitor_processes(self):
        """监控进程输出"""
        def monitor_publisher():
            if self.publisher_process:
                for line in iter(self.publisher_process.stdout.readline, ''):
                    if self.running:
                        print(f"[发布器] {line.strip()}")
                    else:
                        break
                        
        def monitor_detector():
            if self.detector_process:
                for line in iter(self.detector_process.stdout.readline, ''):
                    if self.running:
                        print(f"[检测器] {line.strip()}")
                    else:
                        break
        
        # 启动监控线程
        if self.publisher_process:
            threading.Thread(target=monitor_publisher, daemon=True).start()
        if self.detector_process:
            threading.Thread(target=monitor_detector, daemon=True).start()
            
    def stop_all(self):
        """停止所有进程"""
        print("\n🛑 正在停止所有进程...")
        self.running = False
        
        if self.detector_process:
            try:
                self.detector_process.terminate()
                self.detector_process.wait(timeout=5)
                print("✅ 检测器已停止")
            except:
                self.detector_process.kill()
                print("⚠️ 强制停止检测器")
                
        if self.publisher_process:
            try:
                self.publisher_process.terminate()
                self.publisher_process.wait(timeout=5)
                print("✅ 发布器已停止")
            except:
                self.publisher_process.kill()
                print("⚠️ 强制停止发布器")
                
    def run(self):
        """运行主程序"""
        print("=" * 60)
        print("🚁 Unitree 雷达目标检测系统")
        print("=" * 60)
        
        # 检查前提条件
        if not self.check_prerequisites():
            return False
            
        # 设置信号处理
        def signal_handler(signum, frame):
            self.stop_all()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # 启动发布器
            if not self.start_publisher():
                return False
                
            # 启动检测器
            if not self.start_detector():
                self.stop_all()
                return False
                
            self.running = True
            
            # 开始监控
            print("\n📊 系统运行中...")
            print("按 Ctrl+C 退出")
            print("-" * 60)
            
            self.monitor_processes()
            
            # 主循环
            while self.running:
                # 检查进程状态
                if self.publisher_process and self.publisher_process.poll() is not None:
                    print("❌ 发布器进程意外退出")
                    break
                    
                if self.detector_process and self.detector_process.poll() is not None:
                    print("❌ 检测器进程意外退出")
                    break
                    
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 用户中断")
        except Exception as e:
            print(f"\n❌ 运行时错误: {e}")
        finally:
            self.stop_all()
            
        return True

def show_help():
    """显示帮助信息"""
    print("""
使用方法:
    python3 main.py [选项]

选项:
    -h, --help     显示此帮助信息
    --device PATH  指定串口设备 (默认: /dev/ttyUSB0)
    --ip IP        指定UDP IP地址 (默认: 127.0.0.1)
    --port PORT    指定UDP端口 (默认: 12345)

示例:
    python3 main.py                           # 使用默认设置
    python3 main.py --device /dev/ttyUSB1     # 使用不同串口
    python3 main.py --port 12346              # 使用不同端口

系统要求:
    1. 雷达硬件连接到串口
    2. 用户在 dialout 组中
    3. 已编译 C++ 发布器程序
    4. 已安装 Python 依赖 (numpy)
""")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unitree 雷达一键启动程序")
    parser.add_argument("--device", default="/dev/ttyUSB0", help="串口设备路径")
    parser.add_argument("--ip", default="127.0.0.1", help="UDP IP地址")
    parser.add_argument("--port", default="12345", help="UDP端口")
    
    args = parser.parse_args()
    
    # 创建系统实例
    system = LidarSystem()
    system.serial_device = args.device
    system.udp_ip = args.ip
    system.udp_port = args.port
    
    # 运行系统
    success = system.run()
    
    if success:
        print("\n✅ 程序正常退出")
    else:
        print("\n❌ 程序异常退出")
        sys.exit(1)

if __name__ == "__main__":
    main()