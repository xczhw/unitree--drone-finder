#!/usr/bin/env python3
"""
模拟UDP数据发布器
用于测试数据记录程序，发送模拟的激光雷达数据

作者: AI Assistant
日期: 2025年
"""

import socket
import struct
import time
import numpy as np
import math

# UDP配置
UDP_IP = "127.0.0.1"
UDP_PORT = 12345

class MockUDPPublisher:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.scan_id = 0
        self.imu_id = 0
        
        print(f"🤖 模拟UDP发布器启动")
        print(f"📡 发送地址: {UDP_IP}:{UDP_PORT}")
        print(f"🎯 模拟激光雷达数据发送中...")
        print("=" * 50)

    def create_mock_scan(self):
        """创建模拟扫描数据"""
        self.scan_id += 1
        timestamp = time.time()
        
        # 模拟一个圆形扫描模式
        num_points = np.random.randint(80, 120)  # 随机点数
        angles = np.linspace(0, 2*np.pi, num_points)
        
        points = []
        for i, angle in enumerate(angles):
            # 模拟距离变化
            distance = 2.0 + 0.5 * math.sin(angle * 3) + np.random.normal(0, 0.1)
            
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            z = 0.1 * math.sin(angle * 5) + np.random.normal(0, 0.02)  # 轻微高度变化
            
            intensity = 200 + 50 * math.sin(angle * 2) + np.random.normal(0, 10)
            intensity = max(0, min(255, intensity))  # 限制范围
            
            point_time = i * 0.0001  # 模拟点的时间偏移
            ring = 0  # 单线激光雷达
            
            points.append([x, y, z, intensity, point_time, ring])
        
        return timestamp, self.scan_id, len(points), points

    def create_mock_imu(self):
        """创建模拟IMU数据"""
        self.imu_id += 1
        timestamp = time.time()
        
        # 模拟四元数 (接近单位四元数)
        quaternion = [0.01, 0.02, 0.01, 0.999]
        
        # 模拟角速度 (rad/s)
        angular_velocity = [0.01, -0.005, 0.02]
        
        # 模拟线性加速度 (m/s²)
        linear_acceleration = [0.1, 0.05, 9.8]  # 包含重力
        
        return timestamp, self.imu_id, quaternion, angular_velocity, linear_acceleration

    def send_scan_message(self):
        """发送扫描消息"""
        timestamp, scan_id, num_points, points = self.create_mock_scan()
        
        # 构建消息
        msg_type = 102  # Scan message type
        
        # 计算消息长度
        point_data_str = "=fffffI"
        point_size = struct.calcsize(point_data_str)
        header_size = 16  # timestamp(8) + id(4) + validPointsNum(4)
        msg_length = header_size + num_points * point_size
        
        # 打包消息
        message = struct.pack("=II", msg_type, msg_length)
        message += struct.pack("=dII", timestamp, scan_id, num_points)
        
        for point in points:
            x, y, z, intensity, point_time, ring = point
            message += struct.pack(point_data_str, x, y, z, intensity, point_time, ring)
        
        # 发送
        self.sock.sendto(message, (UDP_IP, UDP_PORT))
        print(f"📊 发送扫描 #{scan_id}: {num_points}点, 时间戳={timestamp:.6f}")

    def send_imu_message(self):
        """发送IMU消息"""
        timestamp, imu_id, quaternion, angular_velocity, linear_acceleration = self.create_mock_imu()
        
        # 构建消息
        msg_type = 101  # IMU message type
        imu_data_str = "=dI4f3f3f"
        msg_length = struct.calcsize(imu_data_str)
        
        # 打包消息
        message = struct.pack("=II", msg_type, msg_length)
        message += struct.pack(imu_data_str, 
                              timestamp, imu_id,
                              *quaternion,
                              *angular_velocity, 
                              *linear_acceleration)
        
        # 发送
        self.sock.sendto(message, (UDP_IP, UDP_PORT))
        print(f"🧭 发送IMU #{imu_id}: 时间戳={timestamp:.6f}")

    def run(self, duration=60, scan_rate=10, imu_rate=100):
        """
        运行发布器
        
        Args:
            duration: 运行时长(秒)
            scan_rate: 扫描频率(Hz)
            imu_rate: IMU频率(Hz)
        """
        print(f"🚀 开始发送数据 (时长: {duration}秒)")
        print(f"📊 扫描频率: {scan_rate} Hz")
        print(f"🧭 IMU频率: {imu_rate} Hz")
        
        start_time = time.time()
        last_scan_time = 0
        last_imu_time = 0
        
        scan_interval = 1.0 / scan_rate
        imu_interval = 1.0 / imu_rate
        
        try:
            while time.time() - start_time < duration:
                current_time = time.time()
                
                # 发送扫描数据
                if current_time - last_scan_time >= scan_interval:
                    self.send_scan_message()
                    last_scan_time = current_time
                
                # 发送IMU数据
                if current_time - last_imu_time >= imu_interval:
                    self.send_imu_message()
                    last_imu_time = current_time
                
                # 短暂休眠
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            print("\n🛑 用户中断")
        
        print(f"✅ 发送完成! 总扫描: {self.scan_id}, 总IMU: {self.imu_id}")
        self.sock.close()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='模拟UDP数据发布器')
    parser.add_argument('--duration', type=int, default=60, help='运行时长(秒)')
    parser.add_argument('--scan-rate', type=int, default=10, help='扫描频率(Hz)')
    parser.add_argument('--imu-rate', type=int, default=100, help='IMU频率(Hz)')
    
    args = parser.parse_args()
    
    publisher = MockUDPPublisher()
    publisher.run(args.duration, args.scan_rate, args.imu_rate)

if __name__ == "__main__":
    main()