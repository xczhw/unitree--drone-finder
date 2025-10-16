#!/usr/bin/env python3
"""
Unitree激光雷达数据记录器
基于UDP接收雷达数据并保存为NPZ格式文件，方便Python加载和处理

作者: AI Assistant
日期: 2025年
"""

import socket
import struct
import numpy as np
import os
import time
from datetime import datetime
import argparse

# IP and Port
UDP_IP = "0.0.0.0"
UDP_PORT = 12345

# Point Type
class PointUnitree:
    def __init__(self, x, y, z, intensity, time, ring):
        self.x = x
        self.y = y
        self.z = z
        self.intensity = intensity
        self.time = time
        self.ring = ring

# Scan Type
class ScanUnitree:
    def __init__(self, stamp, id, validPointsNum, points):
        self.stamp = stamp
        self.id = id
        self.validPointsNum = validPointsNum
        self.points = points

# IMU Type
class IMUUnitree:
    def __init__(self, stamp, id, quaternion, angular_velocity, linear_acceleration):
        self.stamp = stamp
        self.id = id
        self.quaternion = quaternion
        self.angular_velocity = angular_velocity
        self.linear_acceleration = linear_acceleration

class LidarDataRecorder:
    def __init__(self, output_dir="data", max_scans=1000, max_duration=60):
        """
        初始化数据记录器
        
        Args:
            output_dir: 输出目录
            max_scans: 最大记录扫描数量
            max_duration: 最大记录时长(秒)
        """
        self.output_dir = output_dir
        self.max_scans = max_scans
        self.max_duration = max_duration
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 数据存储列表
        self.scan_data = []
        self.imu_data = []
        
        # 统计信息
        self.scan_count = 0
        self.imu_count = 0
        self.start_time = None
        
        # 创建UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        
        # 计算结构体大小
        self.imuDataStr = "=dI4f3f3f"
        self.imuDataSize = struct.calcsize(self.imuDataStr)
        self.pointDataStr = "=fffffI"
        self.pointSize = struct.calcsize(self.pointDataStr)
        self.scanDataStr = "=dII" + 120 * "fffffI"
        self.scanDataSize = struct.calcsize(self.scanDataStr)
        
        print(f"📡 UDP数据记录器已启动")
        print(f"📁 输出目录: {os.path.abspath(output_dir)}")
        print(f"📊 最大记录: {max_scans}帧扫描, {max_duration}秒")
        print(f"🔧 数据结构大小: 点={self.pointSize}字节, 扫描={self.scanDataSize}字节, IMU={self.imuDataSize}字节")
        print(f"🎯 监听地址: {UDP_IP}:{UDP_PORT}")
        print("=" * 60)

    def process_scan_message(self, data):
        """处理扫描消息"""
        length = struct.unpack("=I", data[4:8])[0]
        stamp = struct.unpack("=d", data[8:16])[0]
        id = struct.unpack("=I", data[16:20])[0]
        validPointsNum = struct.unpack("=I", data[20:24])[0]
        
        # 解析点云数据
        points = []
        pointStartAddr = 24
        for i in range(validPointsNum):
            pointData = struct.unpack(self.pointDataStr, data[pointStartAddr: pointStartAddr+self.pointSize])
            pointStartAddr = pointStartAddr + self.pointSize
            point = PointUnitree(*pointData)
            points.append([point.x, point.y, point.z, point.intensity, point.time, point.ring])
        
        # 转换为numpy数组
        points_array = np.array(points, dtype=np.float32)
        
        # 存储扫描数据
        scan_info = {
            'timestamp': stamp,
            'scan_id': id,
            'valid_points': validPointsNum,
            'points': points_array,
            'system_time': time.time()
        }
        
        self.scan_data.append(scan_info)
        self.scan_count += 1
        
        print(f"📊 扫描 #{self.scan_count}: ID={id}, 点数={validPointsNum}, 时间戳={stamp:.6f}")
        
        return scan_info

    def process_imu_message(self, data):
        """处理IMU消息"""
        length = struct.unpack("=I", data[4:8])[0]
        imuData = struct.unpack(self.imuDataStr, data[8:8+self.imuDataSize])
        
        # 存储IMU数据
        imu_info = {
            'timestamp': imuData[0],
            'imu_id': imuData[1],
            'quaternion': np.array(imuData[2:6], dtype=np.float32),
            'angular_velocity': np.array(imuData[6:9], dtype=np.float32),
            'linear_acceleration': np.array(imuData[9:12], dtype=np.float32),
            'system_time': time.time()
        }
        
        self.imu_data.append(imu_info)
        self.imu_count += 1
        
        print(f"🧭 IMU #{self.imu_count}: ID={imu_info['imu_id']}, 时间戳={imu_info['timestamp']:.6f}")
        
        return imu_info

    def save_data(self, filename_prefix=None):
        """保存数据到NPZ文件"""
        if not self.scan_data and not self.imu_data:
            print("⚠️  没有数据可保存")
            return None
            
        # 生成文件名
        if filename_prefix is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_prefix = f"lidar_data_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename_prefix}.npz")
        
        # 准备保存的数据
        save_dict = {
            'recording_info': {
                'start_time': self.start_time,
                'end_time': time.time(),
                'scan_count': self.scan_count,
                'imu_count': self.imu_count,
                'duration': time.time() - self.start_time if self.start_time else 0
            }
        }
        
        # 处理扫描数据
        if self.scan_data:
            scan_timestamps = np.array([s['timestamp'] for s in self.scan_data])
            scan_ids = np.array([s['scan_id'] for s in self.scan_data])
            scan_valid_points = np.array([s['valid_points'] for s in self.scan_data])
            scan_system_times = np.array([s['system_time'] for s in self.scan_data])
            
            # 合并所有点云数据
            all_points = []
            scan_indices = []  # 记录每个点属于哪个扫描
            
            for i, scan in enumerate(self.scan_data):
                points = scan['points']
                all_points.append(points)
                scan_indices.extend([i] * len(points))
            
            if all_points:
                all_points = np.vstack(all_points)
                scan_indices = np.array(scan_indices)
                
                save_dict.update({
                    'scan_timestamps': scan_timestamps,
                    'scan_ids': scan_ids,
                    'scan_valid_points': scan_valid_points,
                    'scan_system_times': scan_system_times,
                    'points': all_points,  # [N, 6] - x,y,z,intensity,time,ring
                    'point_scan_indices': scan_indices  # 每个点属于哪个扫描
                })
        
        # 处理IMU数据
        if self.imu_data:
            imu_timestamps = np.array([i['timestamp'] for i in self.imu_data])
            imu_ids = np.array([i['imu_id'] for i in self.imu_data])
            imu_system_times = np.array([i['system_time'] for i in self.imu_data])
            imu_quaternions = np.array([i['quaternion'] for i in self.imu_data])
            imu_angular_velocities = np.array([i['angular_velocity'] for i in self.imu_data])
            imu_linear_accelerations = np.array([i['linear_acceleration'] for i in self.imu_data])
            
            save_dict.update({
                'imu_timestamps': imu_timestamps,
                'imu_ids': imu_ids,
                'imu_system_times': imu_system_times,
                'imu_quaternions': imu_quaternions,
                'imu_angular_velocities': imu_angular_velocities,
                'imu_linear_accelerations': imu_linear_accelerations
            })
        
        # 保存到NPZ文件
        np.savez_compressed(filepath, **save_dict)
        
        print(f"💾 数据已保存到: {filepath}")
        print(f"📊 包含: {self.scan_count}帧扫描, {self.imu_count}个IMU数据")
        
        return filepath

    def record(self):
        """开始记录数据"""
        print("🚀 开始记录数据...")
        self.start_time = time.time()
        
        try:
            while True:
                # 检查停止条件
                if self.scan_count >= self.max_scans:
                    print(f"✅ 达到最大扫描数量 ({self.max_scans})")
                    break
                    
                if time.time() - self.start_time >= self.max_duration:
                    print(f"✅ 达到最大记录时长 ({self.max_duration}秒)")
                    break
                
                # 接收数据
                try:
                    data, addr = self.sock.recvfrom(10000)
                except socket.timeout:
                    continue
                
                # 解析消息类型
                msgType = struct.unpack("=I", data[:4])[0]
                
                if msgType == 101:  # IMU Message
                    self.process_imu_message(data)
                elif msgType == 102:  # Scan Message
                    self.process_scan_message(data)
                else:
                    print(f"⚠️  未知消息类型: {msgType}")
                    
        except KeyboardInterrupt:
            print("\n🛑 用户中断记录")
        except Exception as e:
            print(f"❌ 记录过程中出错: {e}")
        finally:
            self.sock.close()
            
        # 保存数据
        saved_file = self.save_data()
        return saved_file

def load_lidar_data(filepath):
    """
    加载保存的激光雷达数据
    
    Args:
        filepath: NPZ文件路径
        
    Returns:
        dict: 包含所有数据的字典
    """
    print(f"📂 加载数据文件: {filepath}")
    
    data = np.load(filepath, allow_pickle=True)
    
    # 提取信息
    info = data['recording_info'].item()
    print(f"📊 记录信息:")
    print(f"   时长: {info['duration']:.2f}秒")
    print(f"   扫描帧数: {info['scan_count']}")
    print(f"   IMU数据: {info['imu_count']}")
    
    if 'points' in data:
        points = data['points']
        print(f"   总点数: {len(points)}")
        print(f"   点云字段: x, y, z, intensity, time, ring")
    
    return {key: data[key] for key in data.files}

def main():
    parser = argparse.ArgumentParser(description='Unitree激光雷达数据记录器')
    parser.add_argument('--output-dir', default='../data', help='输出目录 (默认: ../data)')
    parser.add_argument('--max-scans', type=int, default=1000, help='最大记录扫描数 (默认: 1000)')
    parser.add_argument('--max-duration', type=int, default=60, help='最大记录时长(秒) (默认: 60)')
    parser.add_argument('--load', type=str, help='加载并显示指定NPZ文件的信息')
    
    args = parser.parse_args()
    
    if args.load:
        # 加载模式
        load_lidar_data(args.load)
    else:
        # 记录模式
        recorder = LidarDataRecorder(
            output_dir=args.output_dir,
            max_scans=args.max_scans,
            max_duration=args.max_duration
        )
        
        saved_file = recorder.record()
        
        if saved_file:
            print("\n" + "="*60)
            print("🎉 记录完成!")
            print(f"📁 文件位置: {saved_file}")
            print("\n💡 使用方法:")
            print(f"   python {__file__} --load {saved_file}")
            print("\n🐍 Python加载示例:")
            print("   import numpy as np")
            print(f"   data = np.load('{saved_file}', allow_pickle=True)")
            print("   points = data['points']  # 点云数据 [N, 6]")
            print("   scan_timestamps = data['scan_timestamps']  # 扫描时间戳")

if __name__ == "__main__":
    main()