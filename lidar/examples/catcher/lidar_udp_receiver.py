"""
Unitree Lidar UDP Data Receiver
基于 UDP 协议接收和解析 Unitree 激光雷达数据的封装模块

作者: Assistant
日期: 2024
用途: 替代 drone_detector.py 中的 _generate_simulated_raw_data 函数
"""

import socket
import struct
import numpy as np
import time
import threading
from typing import Optional, Tuple, List


class PointUnitree:
    """Unitree 激光雷达点数据结构"""
    def __init__(self, x: float, y: float, z: float, intensity: float, time: float, ring: int):
        self.x = x
        self.y = y
        self.z = z
        self.intensity = intensity
        self.time = time
        self.ring = ring


class ScanUnitree:
    """Unitree 激光雷达扫描数据结构"""
    def __init__(self, stamp: float, id: int, validPointsNum: int, points: List[PointUnitree]):
        self.stamp = stamp
        self.id = id
        self.validPointsNum = validPointsNum
        self.points = points


class IMUUnitree:
    """Unitree IMU 数据结构"""
    def __init__(self, stamp: float, id: int, quaternion: Tuple[float, ...],
                 angular_velocity: Tuple[float, ...], linear_acceleration: Tuple[float, ...]):
        self.stamp = stamp
        self.id = id
        self.quaternion = quaternion
        self.angular_velocity = angular_velocity
        self.linear_acceleration = linear_acceleration


class LidarPointCloud:
    """激光雷达点云数据类（与 drone_detector.py 兼容）"""
    def __init__(self):
        self.points = None  # 三维坐标 (N, 3) 数组 [x, y, z]
        self.intensities = None  # 反射强度 (N,) 数组
        self.timestamp = None  # 时间戳


class LidarUDPReceiver:
    """
    Unitree 激光雷达 UDP 数据接收器

    功能:
    - 接收 UDP 激光雷达数据
    - 解析点云和 IMU 数据
    - 转换为标准格式供其他模块使用
    """

    def __init__(self, udp_ip: str = "0.0.0.0", udp_port: int = 12345):
        """
        初始化 UDP 接收器

        Args:
            udp_ip: UDP 监听 IP 地址
            udp_port: UDP 监听端口
        """
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.socket = None
        self.running = False
        self.thread = None

        # 数据存储
        self.latest_scan = None
        self.latest_imu = None
        self.latest_point_cloud = None
        self.data_lock = threading.Lock()

        # 数据结构大小计算
        self.imu_data_str = "=dI4f3f3f"
        self.imu_data_size = struct.calcsize(self.imu_data_str)
        self.point_data_str = "=fffffI"
        self.point_size = struct.calcsize(self.point_data_str)

        print(f"LidarUDPReceiver 初始化完成")
        print(f"监听地址: {self.udp_ip}:{self.udp_port}")
        print(f"数据结构大小: point={self.point_size}, imu={self.imu_data_size}")

    def connect(self) -> bool:
        """
        连接到 UDP 端口

        Returns:
            bool: 连接是否成功
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.udp_ip, self.udp_port))
            self.socket.settimeout(1.0)  # 设置超时，便于优雅退出
            print(f"UDP 套接字绑定成功: {self.udp_ip}:{self.udp_port}")
            return True
        except Exception as e:
            print(f"UDP 连接失败: {e}")
            return False

    def start_streaming(self) -> bool:
        """
        开始接收数据流

        Returns:
            bool: 启动是否成功
        """
        if self.socket is None:
            print("请先调用 connect() 方法")
            return False

        self.running = True
        self.thread = threading.Thread(target=self._data_receiving_loop)
        self.thread.daemon = True
        self.thread.start()
        print("开始接收激光雷达数据...")
        return True

    def stop_streaming(self):
        """停止接收数据流"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        if self.socket:
            self.socket.close()
        print("已停止接收激光雷达数据")

    def get_latest_raw_data(self) -> Optional[LidarPointCloud]:
        """
        获取最新的原始点云数据（与 drone_detector.py 兼容的接口）

        Returns:
            LidarPointCloud: 最新的点云数据，如果没有数据则返回 None
        """
        with self.data_lock:
            return self.latest_point_cloud

    def get_latest_scan(self) -> Optional[ScanUnitree]:
        """获取最新的扫描数据"""
        with self.data_lock:
            return self.latest_scan

    def get_latest_imu(self) -> Optional[IMUUnitree]:
        """获取最新的 IMU 数据"""
        with self.data_lock:
            return self.latest_imu

    def _data_receiving_loop(self):
        """数据接收循环"""
        while self.running:
            try:
                # 接收 UDP 数据
                data, addr = self.socket.recvfrom(10000)
                # print(f"收到数据来自 {addr[0]}:{addr[1]}")

                # 解析消息类型
                msg_type = struct.unpack("=I", data[:4])[0]

                if msg_type == 101:  # IMU 消息
                    self._parse_imu_message(data)
                elif msg_type == 102:  # 点云扫描消息
                    self._parse_scan_message(data)
                else:
                    print(f"未知消息类型: {msg_type}")

            except socket.timeout:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                if self.running:  # 只有在运行时才报告错误
                    print(f"数据接收错误: {e}")
                break

    def _parse_imu_message(self, data: bytes):
        """解析 IMU 消息"""
        try:
            length = struct.unpack("=I", data[4:8])[0]
            imu_data = struct.unpack(self.imu_data_str, data[8:8+self.imu_data_size])

            imu_msg = IMUUnitree(
                stamp=imu_data[0],
                id=imu_data[1],
                quaternion=imu_data[2:6],
                angular_velocity=imu_data[6:9],
                linear_acceleration=imu_data[9:12]
            )

            with self.data_lock:
                self.latest_imu = imu_msg

        except Exception as e:
            print(f"IMU 消息解析错误: {e}")

    def _parse_scan_message(self, data: bytes):
        """解析点云扫描消息"""
        try:
            length = struct.unpack("=I", data[4:8])[0]
            stamp = struct.unpack("=d", data[8:16])[0]
            id = struct.unpack("=I", data[16:20])[0]
            valid_points_num = struct.unpack("=I", data[20:24])[0]

            # 解析点云数据
            scan_points = []
            point_start_addr = 24

            for i in range(valid_points_num):
                point_data = struct.unpack(
                    self.point_data_str,
                    data[point_start_addr:point_start_addr + self.point_size]
                )
                point_start_addr += self.point_size
                point = PointUnitree(*point_data)
                scan_points.append(point)

            scan_msg = ScanUnitree(stamp, id, valid_points_num, scan_points)

            # 转换为 LidarPointCloud 格式
            point_cloud = self._convert_to_point_cloud(scan_msg)

            with self.data_lock:
                self.latest_scan = scan_msg
                self.latest_point_cloud = point_cloud

        except Exception as e:
            print(f"扫描消息解析错误: {e}")

    def _convert_to_point_cloud(self, scan_msg: ScanUnitree) -> LidarPointCloud:
        """
        将 ScanUnitree 转换为 LidarPointCloud 格式

        Args:
            scan_msg: 扫描消息

        Returns:
            LidarPointCloud: 转换后的点云数据
        """
        cloud = LidarPointCloud()
        cloud.timestamp = scan_msg.stamp

        if scan_msg.validPointsNum > 0:
            # 提取坐标和强度
            points = []
            intensities = []

            for point in scan_msg.points:
                points.append([point.x, point.y, point.z])
                intensities.append(point.intensity)

            cloud.points = np.array(points, dtype=np.float32)
            cloud.intensities = np.array(intensities, dtype=np.float32)
        else:
            cloud.points = np.empty((0, 3), dtype=np.float32)
            cloud.intensities = np.empty(0, dtype=np.float32)

        return cloud


def create_lidar_receiver(udp_ip: str = "0.0.0.0", udp_port: int = 12345) -> LidarUDPReceiver:
    """
    创建激光雷达 UDP 接收器的工厂函数

    Args:
        udp_ip: UDP 监听 IP 地址
        udp_port: UDP 监听端口

    Returns:
        LidarUDPReceiver: 配置好的接收器实例
    """
    return LidarUDPReceiver(udp_ip, udp_port)


# 示例使用代码
if __name__ == "__main__":
    # 创建接收器
    receiver = create_lidar_receiver()

    # 连接并开始接收
    if receiver.connect():
        receiver.start_streaming()

        try:
            print("开始接收数据，按 Ctrl+C 退出...")
            while True:
                # 获取最新数据
                point_cloud = receiver.get_latest_raw_data()
                if point_cloud is not None:
                    print(f"时间戳: {point_cloud.timestamp:.3f}, "
                          f"点数: {len(point_cloud.points) if point_cloud.points is not None else 0}")

                time.sleep(1.0)

        except KeyboardInterrupt:
            print("\n正在退出...")
        finally:
            receiver.stop_streaming()
    else:
        print("连接失败")