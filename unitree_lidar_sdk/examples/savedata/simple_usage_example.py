#!/usr/bin/env python3
"""
简单的激光雷达数据使用示例
演示如何在你的Python项目中加载和使用保存的激光雷达数据

作者: AI Assistant
日期: 2025年
"""

import numpy as np
import os

def load_lidar_data(npz_file):
    """
    加载激光雷达数据
    
    Args:
        npz_file: NPZ文件路径
        
    Returns:
        dict: 包含点云和IMU数据的字典
    """
    print(f"📂 加载数据: {npz_file}")
    
    data = np.load(npz_file, allow_pickle=True)
    
    # 提取点云数据
    points = data['points']  # [N, 6] - x, y, z, intensity, time, ring
    scan_timestamps = data['scan_timestamps']
    scan_ids = data['scan_ids']
    
    # 提取IMU数据
    imu_timestamps = data['imu_timestamps']
    imu_quaternions = data['imu_quaternions']
    imu_angular_velocities = data['imu_angular_velocities']
    imu_linear_accelerations = data['imu_linear_accelerations']
    
    print(f"✅ 成功加载 {len(points)} 个点, {len(scan_timestamps)} 帧扫描, {len(imu_timestamps)} 个IMU数据")
    
    return {
        'points': points,
        'scan_timestamps': scan_timestamps,
        'scan_ids': scan_ids,
        'imu_timestamps': imu_timestamps,
        'imu_quaternions': imu_quaternions,
        'imu_angular_velocities': imu_angular_velocities,
        'imu_linear_accelerations': imu_linear_accelerations
    }

def basic_point_cloud_processing(points):
    """
    基本的点云处理示例
    
    Args:
        points: 点云数据 [N, 6]
    """
    print("\n🔧 基本点云处理:")
    
    # 分离坐标和属性
    xyz = points[:, :3]  # x, y, z坐标
    intensity = points[:, 3]  # 强度
    time = points[:, 4]  # 时间
    ring = points[:, 5]  # 环数
    
    print(f"   点云形状: {xyz.shape}")
    print(f"   坐标范围: X[{xyz[:, 0].min():.2f}, {xyz[:, 0].max():.2f}]")
    print(f"            Y[{xyz[:, 1].min():.2f}, {xyz[:, 1].max():.2f}]")
    print(f"            Z[{xyz[:, 2].min():.2f}, {xyz[:, 2].max():.2f}]")
    
    # 计算距离
    distances = np.sqrt(np.sum(xyz**2, axis=1))
    print(f"   距离范围: [{distances.min():.2f}, {distances.max():.2f}] 米")
    print(f"   平均距离: {distances.mean():.2f} 米")
    
    # 强度统计
    print(f"   强度范围: [{intensity.min():.0f}, {intensity.max():.0f}]")
    print(f"   平均强度: {intensity.mean():.1f}")
    
    return xyz, intensity, distances

def filter_points_by_distance(points, min_dist=0.5, max_dist=10.0):
    """
    根据距离过滤点云
    
    Args:
        points: 点云数据 [N, 6]
        min_dist: 最小距离
        max_dist: 最大距离
        
    Returns:
        filtered_points: 过滤后的点云
    """
    xyz = points[:, :3]
    distances = np.sqrt(np.sum(xyz**2, axis=1))
    
    # 距离过滤
    mask = (distances >= min_dist) & (distances <= max_dist)
    filtered_points = points[mask]
    
    print(f"🔍 距离过滤 [{min_dist}, {max_dist}]米:")
    print(f"   原始点数: {len(points)}")
    print(f"   过滤后: {len(filtered_points)} ({len(filtered_points)/len(points)*100:.1f}%)")
    
    return filtered_points

def filter_points_by_intensity(points, min_intensity=100):
    """
    根据强度过滤点云
    
    Args:
        points: 点云数据 [N, 6]
        min_intensity: 最小强度阈值
        
    Returns:
        filtered_points: 过滤后的点云
    """
    intensity = points[:, 3]
    mask = intensity >= min_intensity
    filtered_points = points[mask]
    
    print(f"💡 强度过滤 (>={min_intensity}):")
    print(f"   原始点数: {len(points)}")
    print(f"   过滤后: {len(filtered_points)} ({len(filtered_points)/len(points)*100:.1f}%)")
    
    return filtered_points

def extract_scan_by_id(data, scan_id):
    """
    提取特定ID的扫描数据
    
    Args:
        data: 完整数据字典
        scan_id: 扫描ID
        
    Returns:
        scan_points: 该扫描的点云数据
    """
    scan_ids = data['scan_ids']
    point_scan_indices = data['point_scan_indices'] if 'point_scan_indices' in data else None
    
    if point_scan_indices is not None:
        # 找到对应扫描的索引
        scan_index = np.where(scan_ids == scan_id)[0]
        if len(scan_index) > 0:
            scan_index = scan_index[0]
            mask = point_scan_indices == scan_index
            scan_points = data['points'][mask]
            
            print(f"📊 扫描 ID {scan_id}:")
            print(f"   点数: {len(scan_points)}")
            print(f"   时间戳: {data['scan_timestamps'][scan_index]:.6f}")
            
            return scan_points
    
    print(f"❌ 未找到扫描 ID {scan_id}")
    return None

def main():
    # 查找最新的数据文件
    data_dir = "../data"
    if not os.path.exists(data_dir):
        print(f"❌ 数据目录不存在: {data_dir}")
        return
    
    npz_files = [f for f in os.listdir(data_dir) if f.endswith('.npz')]
    if not npz_files:
        print(f"❌ 在 {data_dir} 中没有找到NPZ文件")
        print("💡 请先运行数据记录程序: python3 lidar_data_recorder.py")
        return
    
    # 使用最新的文件
    latest_file = sorted(npz_files)[-1]
    npz_path = os.path.join(data_dir, latest_file)
    
    print("🎯 激光雷达数据使用示例")
    print("=" * 50)
    
    # 1. 加载数据
    data = load_lidar_data(npz_path)
    
    # 2. 基本处理
    xyz, intensity, distances = basic_point_cloud_processing(data['points'])
    
    # 3. 距离过滤
    print()
    filtered_by_distance = filter_points_by_distance(data['points'], 1.5, 3.0)
    
    # 4. 强度过滤
    print()
    filtered_by_intensity = filter_points_by_intensity(data['points'], 150)
    
    # 5. 组合过滤
    print()
    print("🔧 组合过滤 (距离 + 强度):")
    combined_filtered = filter_points_by_intensity(filtered_by_distance, 150)
    
    # 6. 提取单个扫描
    print()
    if len(data['scan_ids']) > 0:
        first_scan_id = data['scan_ids'][0]
        scan_points = extract_scan_by_id(data, first_scan_id)
    
    # 7. IMU数据示例
    print()
    print("🧭 IMU数据示例:")
    print(f"   IMU数据点数: {len(data['imu_timestamps'])}")
    if len(data['imu_timestamps']) > 0:
        print(f"   第一个四元数: {data['imu_quaternions'][0]}")
        print(f"   第一个角速度: {data['imu_angular_velocities'][0]}")
        print(f"   第一个线性加速度: {data['imu_linear_accelerations'][0]}")
    
    print()
    print("✅ 示例完成!")
    print()
    print("💡 在你的项目中使用:")
    print("   1. 复制 load_lidar_data() 函数")
    print("   2. 使用 data = load_lidar_data('your_file.npz')")
    print("   3. 访问 data['points'] 获取点云数据")
    print("   4. 访问 data['imu_*'] 获取IMU数据")

if __name__ == "__main__":
    main()