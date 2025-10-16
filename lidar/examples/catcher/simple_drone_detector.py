#!/usr/bin/env python3
"""
简化版无人机检测器 - 不依赖open3d
使用真实雷达数据进行目标检测
"""

import numpy as np
import time
import math
from lidar_udp_receiver import LidarUDPReceiver
from config import DetectionConfig

class SimpleDroneDetector:
    def __init__(self):
        self.min_cluster_size = 5  # 最小聚类点数
        self.max_cluster_size = 100  # 最大聚类点数
        self.cluster_distance = 0.5  # 聚类距离阈值
        self.min_height = 0.5  # 最小高度
        self.max_height = 10.0  # 最大高度

    def detect_objects(self, points):
        """
        检测点云中的目标对象
        """
        if points is None or len(points) == 0:
            return []

        # 过滤高度范围
        valid_points = []
        for point in points:
            if self.min_height <= point[2] <= self.max_height:
                valid_points.append(point)

        if len(valid_points) < self.min_cluster_size:
            return []

        # 简单聚类算法
        clusters = self.simple_clustering(valid_points)

        # 分析聚类特征
        detected_objects = []
        for cluster in clusters:
            if self.min_cluster_size <= len(cluster) <= self.max_cluster_size:
                obj_info = self.analyze_cluster(cluster)
                if obj_info:
                    detected_objects.append(obj_info)

        return detected_objects

    def simple_clustering(self, points):
        """
        简单的基于距离的聚类
        """
        if len(points) == 0:
            return []

        clusters = []
        used = set()

        for i, point in enumerate(points):
            if i in used:
                continue

            cluster = [point]
            used.add(i)

            # 递归查找邻近点
            queue = [i]
            while queue:
                current_idx = queue.pop(0)
                current_point = points[current_idx]

                for j, other_point in enumerate(points):
                    if j in used:
                        continue

                    if self.calculate_distance(current_point, other_point) < DetectionConfig.CLUSTERING_DISTANCE:
                        cluster.append(other_point)
                        used.add(j)
                        queue.append(j)

            clusters.append(cluster)

        return clusters

    def calculate_distance(self, p1, p2):
        """计算两点间距离"""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

    def analyze_cluster(self, cluster):
        """
        分析聚类特征
        """
        if len(cluster) < DetectionConfig.MIN_POINTS_PER_CLUSTER:
            return None

        # 计算聚类中心
        center_x = sum(p[0] for p in cluster) / len(cluster)
        center_y = sum(p[1] for p in cluster) / len(cluster)
        center_z = sum(p[2] for p in cluster) / len(cluster)

        # 计算聚类尺寸
        min_x = min(p[0] for p in cluster)
        max_x = max(p[0] for p in cluster)
        min_y = min(p[1] for p in cluster)
        max_y = max(p[1] for p in cluster)
        min_z = min(p[2] for p in cluster)
        max_z = max(p[2] for p in cluster)

        size_x = max_x - min_x
        size_y = max_y - min_y
        size_z = max_z - min_z

        # 计算距离
        distance = math.sqrt(center_x**2 + center_y**2)

        # 使用配置文件中的无人机判断逻辑
        is_drone_like = (
            DetectionConfig.DRONE_SIZE_MIN <= size_x <= DetectionConfig.DRONE_SIZE_MAX_XY and
            DetectionConfig.DRONE_SIZE_MIN <= size_y <= DetectionConfig.DRONE_SIZE_MAX_XY and
            DetectionConfig.DRONE_SIZE_MIN <= size_z <= DetectionConfig.DRONE_SIZE_MAX_Z and
            DetectionConfig.DETECTION_DISTANCE_MIN <= distance <= DetectionConfig.DETECTION_DISTANCE_MAX and
            center_z >= DetectionConfig.MIN_HEIGHT
        )

        return {
            'center': (center_x, center_y, center_z),
            'size': (size_x, size_y, size_z),
            'distance': distance,
            'point_count': len(cluster),
            'is_drone_like': is_drone_like,
            'confidence': self.calculate_confidence(cluster, size_x, size_y, size_z)
        }

    def calculate_confidence(self, cluster, size_x, size_y, size_z):
        """计算检测置信度"""
        # 基于点数的置信度
        point_confidence = min(len(cluster) / 20.0, 1.0)

        # 基于尺寸的置信度（接近正方形的物体置信度更高）
        aspect_ratio = max(size_x, size_y) / (min(size_x, size_y) + 0.01)
        size_confidence = max(0, 1.0 - abs(aspect_ratio - 1.0))

        return (point_confidence + size_confidence) / 2.0

def main():
    print("启动简化版无人机检测器...")
    print("连接到雷达数据流...")

    # 创建雷达接收器
    receiver = LidarUDPReceiver()
    detector = SimpleDroneDetector()

    # 连接并开始接收数据
    if not receiver.connect():
        print("连接失败")
        return

    if not receiver.start_streaming():
        print("启动数据流失败")
        return

    print("开始检测，按 Ctrl+C 退出...")

    try:
        while True:
            # 获取最新点云数据
            point_cloud = receiver.get_latest_raw_data()

            if point_cloud and point_cloud.points is not None:
                # 检测目标
                detected_objects = detector.detect_objects(point_cloud.points)

                # 过滤结果：根据配置显示目标
                filtered_targets = []
                if detected_objects:
                    for obj in detected_objects:
                        # 根据配置决定是否显示
                        show_target = False

                        if obj['is_drone_like'] and obj['confidence'] >= DetectionConfig.CONFIDENCE_THRESHOLD:
                            show_target = True
                        elif DetectionConfig.SHOW_NON_DRONE_TARGETS and not obj['is_drone_like']:
                            show_target = True
                        elif DetectionConfig.SHOW_LOW_CONFIDENCE and obj['confidence'] < DetectionConfig.CONFIDENCE_THRESHOLD:
                            show_target = True

                        if show_target:
                            filtered_targets.append(obj)

                # 输出结果
                if filtered_targets:
                    print(f"\n时间: {point_cloud.timestamp:.3f}")
                    print(f"检测到 {len(filtered_targets)} 个目标:")

                    for i, obj in enumerate(filtered_targets):
                        center = obj['center']
                        size = obj['size']
                        distance = obj['distance']
                        confidence = obj['confidence']
                        is_drone = obj['is_drone_like']

                        status = "可能是无人机" if is_drone else "其他目标"
                        print(f"  目标 {i+1}: {status}")
                        print(f"    位置: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
                        print(f"    尺寸: {size[0]:.2f}×{size[1]:.2f}×{size[2]:.2f}m")
                        print(f"    距离: {distance:.2f}m")
                        print(f"    置信度: {confidence:.2f}")
                        print(f"    点数: {obj['point_count']}")
                elif not DetectionConfig.QUIET_MODE:
                    print(f"时间: {point_cloud.timestamp:.3f} - 未检测到目标")

            time.sleep(DetectionConfig.DETECTION_INTERVAL)  # 检测间隔

    except KeyboardInterrupt:
        print("\n检测已停止")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        receiver.stop_streaming()

if __name__ == "__main__":
    main()