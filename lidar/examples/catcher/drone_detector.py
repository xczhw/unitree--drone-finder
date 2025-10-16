import numpy as np
import open3d as o3d
import time
import random
from threading import Thread

# 激光雷达原始数据类（存储单帧点云数据）
class LidarPointCloud:
    def __init__(self):
        self.points = None  # 三维坐标 (N, 3) 数组 [x, y, z]
        self.intensities = None  # 反射强度 (N,) 数组
        self.timestamp = None  # 时间戳

# 激光雷达SDK模拟类（实际使用时替换为真实SDK）
class LidarSDK:
    def __init__(self, ip="127.0.0.1", port=5000):
        self.connected = False
        self.ip = ip
        self.port = port
        self.latest_cloud = None  # 存储最新的原始点云数据
        self.running = False
        
    def connect(self):
        """连接到激光雷达"""
        print(f"连接到激光雷达 {self.ip}:{self.port}...")
        # 模拟连接过程
        time.sleep(1)
        self.connected = True
        print("激光雷达连接成功")
        return self.connected
        
    def start_streaming(self):
        """开始获取点云数据"""
        if not self.connected:
            print("请先连接激光雷达")
            return False
            
        self.running = True
        self.thread = Thread(target=self._data_acquisition_loop)
        self.thread.daemon = True
        self.thread.start()
        print("开始获取点云数据...")
        return True
        
    def stop_streaming(self):
        """停止获取点云数据"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        print("已停止获取点云数据")
        
    def get_latest_raw_data(self):
        """获取最新的原始点云数据"""
        return self.latest_cloud
        
    def _data_acquisition_loop(self):
        """数据获取循环（模拟）"""
        while self.running:
            # 生成模拟的原始点云数据（实际使用时替换为真实SDK的数据获取）
            raw_data = self._generate_simulated_raw_data()
            self.latest_cloud = raw_data
            time.sleep(0.1)  # 10Hz的数据率
            
    def _generate_simulated_raw_data(self):
        """生成模拟的原始点云数据（坐标+反射强度）"""
        cloud = LidarPointCloud()
        cloud.timestamp = time.time()
        
        # 生成背景噪声点
        num_background_points = 2000
        x = np.random.uniform(-10, 10, num_background_points)
        y = np.random.uniform(-10, 10, num_background_points)
        z = np.random.uniform(-1, 10, num_background_points)  # 高度范围
        cloud.points = np.column_stack([x, y, z])
        
        # 背景点的反射强度（较低且随机）
        cloud.intensities = np.random.uniform(10, 50, num_background_points)
        
        # 随机决定是否添加无人机点云（30%的概率）
        if random.random() < 1:
            drone_points, drone_intensities = self._generate_drone_raw_data()
            # 合并背景和无人机数据
            cloud.points = np.vstack([cloud.points, drone_points])
            cloud.intensities = np.hstack([cloud.intensities, drone_intensities])
            
        return cloud
        
    def _generate_drone_raw_data(self):
        """生成模拟的四轴无人机原始点云数据"""
        # 无人机主体（一个长方体）
        body_size = [0.3, 0.3, 0.1]  # 无人机主体尺寸
        num_body_points = 50
        
        # 随机位置（在5-15米范围内）
        x_center = random.uniform(5, 15)
        y_center = random.uniform(-5, 5)
        z_center = random.uniform(1, 8)
        
        # 主体点云
        body_x = x_center + np.random.uniform(-body_size[0]/2, body_size[0]/2, num_body_points)
        body_y = y_center + np.random.uniform(-body_size[1]/2, body_size[1]/2, num_body_points)
        body_z = z_center + np.random.uniform(-body_size[2]/2, body_size[2]/2, num_body_points)
        
        # 四个螺旋桨臂
        arm_length = 0.25
        num_arm_points = 20
        
        # 右前臂
        arm1_x = x_center + np.linspace(0, arm_length, num_arm_points)
        arm1_y = y_center + np.linspace(0, arm_length*0.3, num_arm_points)
        arm1_z = z_center + np.random.normal(0, 0.02, num_arm_points)
        
        # 左前臂
        arm2_x = x_center + np.linspace(0, arm_length, num_arm_points)
        arm2_y = y_center - np.linspace(0, arm_length*0.3, num_arm_points)
        arm2_z = z_center + np.random.normal(0, 0.02, num_arm_points)
        
        # 右后臂
        arm3_x = x_center - np.linspace(0, arm_length, num_arm_points)
        arm3_y = y_center + np.linspace(0, arm_length*0.3, num_arm_points)
        arm3_z = z_center + np.random.normal(0, 0.02, num_arm_points)
        
        # 左后臂
        arm4_x = x_center - np.linspace(0, arm_length, num_arm_points)
        arm4_y = y_center - np.linspace(0, arm_length*0.3, num_arm_points)
        arm4_z = z_center + np.random.normal(0, 0.02, num_arm_points)
        
        # 合并所有点
        x = np.concatenate([body_x, arm1_x, arm2_x, arm3_x, arm4_x])
        y = np.concatenate([body_y, arm1_y, arm2_y, arm3_y, arm4_y])
        z = np.concatenate([body_z, arm1_z, arm2_z, arm3_z, arm4_z])
        
        # 无人机的反射强度（通常比背景高）
        intensities = np.random.uniform(80, 200, len(x))
        
        return np.column_stack([x, y, z]), intensities

# 无人机检测器类
class DroneDetector:
    def __init__(self):
        # 检测参数（可根据实际情况调整）
        self.voxel_size = 0.05  # 体素滤波大小
        self.dbscan_eps = 0.3   # DBSCAN聚类半径
        self.dbscan_min_points = 15  # 最小聚类点数
        self.min_intensity = 60  # 无人机反射强度最小值
        self.drone_size_range = {  # 无人机尺寸范围（米）
            'min_x': 0, 'max_x': 0.5,
            'min_y': 0, 'max_y': 0.5,
            'min_z': 0, 'max_z': 0.5,
            'min_points': 50, 'max_points': 300
        }
        
    def raw_data_to_point_cloud(self, raw_data):
        """将原始点数据转换为Open3D点云对象"""
        if raw_data is None or raw_data.points is None:
            return None
            
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(raw_data.points)
        
        # 如果有反射强度，将其存储为颜色信息（用于可视化）
        if raw_data.intensities is not None:
            # 归一化反射强度到[0,1]范围，作为灰度值
            normalized_intensity = (raw_data.intensities - raw_data.intensities.min()) / \
                                 (raw_data.intensities.max() - raw_data.intensities.min() + 1e-6)
            # 转换为RGB（这里用灰度表示）
            colors = np.column_stack([normalized_intensity, normalized_intensity, normalized_intensity])
            pcd.colors = o3d.utility.Vector3dVector(colors)
            
        return pcd
        
    def preprocess_point_cloud(self, pcd, intensities=None):
        """预处理点云数据"""
        # 体素滤波降采样
        down_pcd = pcd.voxel_down_sample(voxel_size=self.voxel_size)
        #o3d.visualization.draw_geometries([down_pcd])

        # 如果有反射强度信息，过滤低强度点（可能是噪声）
        if intensities is not None and len(intensities) == len(pcd.points):
            # 找到降采样后保留的点的索引
            # 注意：这里是简化处理，实际需要更精确的索引映射
            if len(down_pcd.points) < len(pcd.points):
                # 简单随机保留相同比例的高强度点（实际应用需改进）
                high_intensity_mask = intensities > self.min_intensity
                high_intensity_indices = np.where(high_intensity_mask)[0]
                down_pcd = pcd.select_by_index(high_intensity_indices)
        
        # 移除离群点
        cl, ind = down_pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
        filtered_pcd = down_pcd.select_by_index(ind)
        #o3d.visualization.draw_geometries([filtered_pcd])
        #return filtered_pcd
        return pcd
        
    def detect_drones(self, raw_data):
        """从原始数据中检测无人机"""
        if raw_data is None or raw_data.points is None or len(raw_data.points) == 0:
            return [], None
        
        # 转换为Open3D点云
        pcd = self.raw_data_to_point_cloud(raw_data)
        #o3d.visualization.draw_geometries([pcd])
        # 预处理
        processed_pcd = self.preprocess_point_cloud(pcd, raw_data.intensities)
        #o3d.visualization.draw_geometries([processed_pcd])
        if len(processed_pcd.points) < 10:
            return [], processed_pcd
        
        # 使用DBSCAN进行聚类
        with o3d.utility.VerbosityContextManager(
                o3d.utility.VerbosityLevel.Error) as cm:
            labels = np.array(
                processed_pcd.cluster_dbscan(eps=self.dbscan_eps, min_points=self.dbscan_min_points, print_progress=False))
        
        max_label = labels.max()
        print(f"检测到 {max_label + 1} 个聚类")
        
        # 提取每个聚类并判断是否为无人机
        drone_clusters = []
        for label in range(max_label + 1):
            cluster_indices = np.where(labels == label)[0]
            cluster_pcd = processed_pcd.select_by_index(cluster_indices)
            
            # 分析聚类特征
            if self._is_drone(cluster_pcd):
                drone_clusters.append(cluster_pcd)
        
        return drone_clusters, processed_pcd
        
    def _is_drone(self, cluster_pcd):
        """判断聚类是否为无人机"""
        # 获取点云边界框
        bbox = cluster_pcd.get_axis_aligned_bounding_box()
        min_bound = bbox.min_bound
        max_bound = bbox.max_bound
        
        # 计算尺寸
        size_x = max_bound[0] - min_bound[0]
        size_y = max_bound[1] - min_bound[1]
        size_z = max_bound[2] - min_bound[2]
        num_points = len(cluster_pcd.points)
        
        # 检查是否在无人机尺寸范围内
        if (self.drone_size_range['min_x'] <= size_x <= self.drone_size_range['max_x'] and
            self.drone_size_range['min_y'] <= size_y <= self.drone_size_range['max_y'] and
            self.drone_size_range['min_z'] <= size_z <= self.drone_size_range['max_z'] and
            self.drone_size_range['min_points'] <= num_points <= self.drone_size_range['max_points']):
            return True
        
        return False

# 可视化器类
class Visualizer:
    def __init__(self):
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name="激光雷达无人机检测系统")
        
        # 初始化几何对象
        self.pcd_background = o3d.geometry.PointCloud()
        self.pcd_drones = []  # 存储无人机点云列表
        self.bboxes = []      # 存储边界框列表（修复：初始化边界框列表）
        self.coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
            size=10.0, origin=[0, 0, 0]
        )
        
        # 初始添加几何对象到可视化器
        self.vis.add_geometry(self.coordinate_frame)
        self.vis.add_geometry(self.pcd_background)  # 修复：初始添加背景点云，避免首次移除错误
        
    def update_visualization(self, background_pcd, drone_clusters):
        """更新可视化内容"""
        # 清除之前的点云
        self.vis.remove_geometry(self.pcd_background, reset_bounding_box=False)
        
        # 移除所有无人机点云
        for drone_pcd in self.pcd_drones:
            self.vis.remove_geometry(drone_pcd, reset_bounding_box=False)
        
        # 移除所有边界框（修复：独立循环，避免重复移除）
        for bbox in self.bboxes:
            self.vis.remove_geometry(bbox, reset_bounding_box=False)
        
        # 更新背景点云
        self.pcd_background = background_pcd
        # 如果没有颜色信息，设置为灰色
        if not self.pcd_background.has_colors():
            self.pcd_background.paint_uniform_color([0.5, 0.5, 0.5])
        self.vis.add_geometry(self.pcd_background, reset_bounding_box=False)
        
        # 更新无人机点云（红色）和边界框
        self.pcd_drones = []  # 清空旧数据
        self.bboxes = []      # 清空旧边界框
        for cluster in drone_clusters:
            drone_pcd = cluster
            drone_pcd.paint_uniform_color([1.0, 0.0, 0.0])  # 红色标识无人机
            self.vis.add_geometry(drone_pcd, reset_bounding_box=False)
            self.pcd_drones.append(drone_pcd)
            
            # 添加轴对齐边界框
            bbox = drone_pcd.get_axis_aligned_bounding_box()
            bbox.color = (1, 0, 0)  # 红色边界框
            self.vis.add_geometry(bbox, reset_bounding_box=False)
            self.bboxes.append(bbox)
        
        # 更新视图
        self.vis.poll_events()   # 处理交互事件（如鼠标操作）
        self.vis.update_renderer()  # 重新渲染画面
        
    def close(self):
        """关闭可视化窗口"""
        self.vis.destroy_window()

# 主程序
def main():
    # 初始化组件
    lidar = LidarSDK()
    detector = DroneDetector()
    visualizer = Visualizer()
    
    try:
        # 连接激光雷达并开始获取数据
        if not lidar.connect():
            print("无法连接到激光雷达，程序退出")
            return
            
        if not lidar.start_streaming():
            print("无法开始获取点云数据，程序退出")
            return
            
        print("无人机检测系统启动，按Ctrl+C退出...")
        
        # 主循环
        while True:
            # 获取最新原始点云数据
            raw_data = lidar.get_latest_raw_data()
            if raw_data is None:
                time.sleep(0.1)
                continue
                
            # 检测无人机
            drones, processed_pcd = detector.detect_drones(raw_data)
            
            # 显示检测结果
            if drones:
                print(f"检测到 {len(drones)} 架无人机!")
            else:
                print("未检测到无人机")
                
            # 更新可视化
            visualizer.update_visualization(processed_pcd, drones)
            
            time.sleep(0.1)  # 控制检测频率
            
    except KeyboardInterrupt:
        print("\n用户中断程序")
    finally:
        # 清理资源
        lidar.stop_streaming()
        visualizer.close()
        print("程序已退出")

if __name__ == "__main__":
    main()
    