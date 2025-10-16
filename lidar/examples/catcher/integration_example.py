"""
集成示例：如何在 drone_detector.py 中使用 LidarUDPReceiver

这个文件展示了如何修改 drone_detector.py 中的 LidarSDK 类，
用真实的 UDP 数据接收器替代模拟数据生成器。
"""

from lidar_udp_receiver import LidarUDPReceiver, LidarPointCloud
import time
from threading import Thread


class RealLidarSDK:
    """
    真实的激光雷达 SDK 类，使用 UDP 接收器获取数据
    用于替代 drone_detector.py 中的 LidarSDK 类
    """
    
    def __init__(self, ip="0.0.0.0", port=12345):
        """
        初始化真实的激光雷达 SDK
        
        Args:
            ip: UDP 监听 IP 地址
            port: UDP 监听端口
        """
        self.connected = False
        self.ip = ip
        self.port = port
        self.latest_cloud = None
        self.running = False
        
        # 创建 UDP 接收器
        self.udp_receiver = LidarUDPReceiver(ip, port)
        
    def connect(self):
        """连接到激光雷达"""
        print(f"连接到激光雷达 UDP 接收器 {self.ip}:{self.port}...")
        
        # 连接 UDP 接收器
        if self.udp_receiver.connect():
            self.connected = True
            print("激光雷达 UDP 连接成功")
            return True
        else:
            print("激光雷达 UDP 连接失败")
            return False
        
    def start_streaming(self):
        """开始获取点云数据"""
        if not self.connected:
            print("请先连接激光雷达")
            return False
            
        # 启动 UDP 接收器
        if self.udp_receiver.start_streaming():
            self.running = True
            self.thread = Thread(target=self._data_sync_loop)
            self.thread.daemon = True
            self.thread.start()
            print("开始获取真实点云数据...")
            return True
        else:
            print("启动数据流失败")
            return False
        
    def stop_streaming(self):
        """停止获取点云数据"""
        self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join()
        
        # 停止 UDP 接收器
        self.udp_receiver.stop_streaming()
        print("已停止获取点云数据")
        
    def get_latest_raw_data(self):
        """获取最新的原始点云数据"""
        return self.latest_cloud
        
    def _data_sync_loop(self):
        """数据同步循环，从 UDP 接收器获取数据"""
        while self.running:
            # 从 UDP 接收器获取最新数据
            raw_data = self.udp_receiver.get_latest_raw_data()
            if raw_data is not None:
                self.latest_cloud = raw_data
            time.sleep(0.01)  # 100Hz 同步频率


def modify_drone_detector_example():
    """
    展示如何修改 drone_detector.py 中的代码
    """
    print("=== 如何在 drone_detector.py 中集成 UDP 接收器 ===")
    print()
    
    print("1. 导入新的模块:")
    print("   from lidar_udp_receiver import LidarUDPReceiver")
    print()
    
    print("2. 替换 LidarSDK 类的实现:")
    print("   将 drone_detector.py 中的 LidarSDK 类替换为 RealLidarSDK 类")
    print("   或者直接修改 LidarSDK 类的 _generate_simulated_raw_data 方法")
    print()
    
    print("3. 修改 _generate_simulated_raw_data 方法:")
    print("""
    # 在 LidarSDK 类中添加 UDP 接收器
    def __init__(self, ip="0.0.0.0", port=12345):
        # ... 原有代码 ...
        self.udp_receiver = LidarUDPReceiver(ip, port)
        self.udp_receiver.connect()
        self.udp_receiver.start_streaming()
    
    def _generate_simulated_raw_data(self):
        '''获取真实的 UDP 激光雷达数据'''
        return self.udp_receiver.get_latest_raw_data()
    """)
    print()
    
    print("4. 确保在程序退出时清理资源:")
    print("""
    def stop_streaming(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        self.udp_receiver.stop_streaming()  # 添加这行
    """)


def test_integration():
    """测试集成功能"""
    print("=== 测试 UDP 接收器集成 ===")
    
    # 创建真实的激光雷达 SDK
    lidar_sdk = RealLidarSDK()
    
    try:
        # 连接并开始数据流
        if lidar_sdk.connect():
            if lidar_sdk.start_streaming():
                print("等待数据...")
                
                # 模拟获取数据的过程
                for i in range(10):
                    raw_data = lidar_sdk.get_latest_raw_data()
                    if raw_data is not None:
                        print(f"第 {i+1} 次获取数据:")
                        print(f"  时间戳: {raw_data.timestamp}")
                        print(f"  点数: {len(raw_data.points) if raw_data.points is not None else 0}")
                        if raw_data.intensities is not None:
                            print(f"  强度范围: {raw_data.intensities.min():.2f} - {raw_data.intensities.max():.2f}")
                    else:
                        print(f"第 {i+1} 次: 暂无数据")
                    
                    time.sleep(1.0)
            else:
                print("启动数据流失败")
        else:
            print("连接失败")
            
    except KeyboardInterrupt:
        print("\n用户中断")
    finally:
        lidar_sdk.stop_streaming()


if __name__ == "__main__":
    print("Unitree Lidar UDP 接收器集成示例")
    print("=" * 50)
    print()
    
    # 显示集成说明
    modify_drone_detector_example()
    print()
    
    # 询问是否进行测试
    response = input("是否要测试 UDP 接收器功能？(y/n): ").lower().strip()
    if response in ['y', 'yes', '是']:
        test_integration()
    else:
        print("跳过测试，程序结束。")