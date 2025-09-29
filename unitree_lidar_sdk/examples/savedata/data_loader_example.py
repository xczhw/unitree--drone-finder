#!/usr/bin/env python3
"""
激光雷达数据加载和分析示例
演示如何加载NPZ格式的点云数据并进行基本分析

作者: AI Assistant
日期: 2025年
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import argparse

def load_and_analyze_lidar_data(filepath):
    """
    加载并分析激光雷达数据
    
    Args:
        filepath: NPZ文件路径
    """
    print(f"📂 加载数据文件: {filepath}")
    
    # 检查文件是否存在
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return
    
    # 加载数据
    data = np.load(filepath, allow_pickle=True)
    
    print("\n📊 数据文件内容:")
    for key in data.files:
        print(f"   {key}: {type(data[key])}")
    
    # 提取记录信息
    if 'recording_info' in data:
        info = data['recording_info'].item()
        print(f"\n🕒 记录信息:")
        print(f"   记录时长: {info['duration']:.2f}秒")
        print(f"   扫描帧数: {info['scan_count']}")
        print(f"   IMU数据: {info['imu_count']}")
    
    # 分析点云数据
    if 'points' in data:
        points = data['points']
        print(f"\n☁️  点云数据分析:")
        print(f"   总点数: {len(points):,}")
        print(f"   数据形状: {points.shape}")
        print(f"   字段: [x, y, z, intensity, time, ring]")
        
        # 统计信息
        x, y, z, intensity, time, ring = points.T
        print(f"\n📈 坐标范围:")
        print(f"   X: [{x.min():.3f}, {x.max():.3f}] 米")
        print(f"   Y: [{y.min():.3f}, {y.max():.3f}] 米") 
        print(f"   Z: [{z.min():.3f}, {z.max():.3f}] 米")
        print(f"   强度: [{intensity.min():.0f}, {intensity.max():.0f}]")
        print(f"   时间: [{time.min():.6f}, {time.max():.6f}]")
        print(f"   环数: [{ring.min():.0f}, {ring.max():.0f}]")
        
        # 距离分析
        distances = np.sqrt(x**2 + y**2 + z**2)
        print(f"   距离: [{distances.min():.3f}, {distances.max():.3f}] 米")
        print(f"   平均距离: {distances.mean():.3f} 米")
        
        return points, data
    
    return None, data

def visualize_point_cloud(points, max_points=10000):
    """
    可视化点云数据
    
    Args:
        points: 点云数据 [N, 6]
        max_points: 最大显示点数
    """
    if points is None or len(points) == 0:
        print("❌ 没有点云数据可视化")
        return
    
    # 如果点太多，随机采样
    if len(points) > max_points:
        indices = np.random.choice(len(points), max_points, replace=False)
        points_vis = points[indices]
        print(f"🎯 随机采样 {max_points:,} 个点进行可视化")
    else:
        points_vis = points
    
    x, y, z, intensity, time, ring = points_vis.T
    
    # 创建图形
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 俯视图 (X-Y)
    ax1 = fig.add_subplot(2, 3, 1)
    scatter1 = ax1.scatter(x, y, c=intensity, cmap='viridis', s=1, alpha=0.6)
    ax1.set_xlabel('X (米)')
    ax1.set_ylabel('Y (米)')
    ax1.set_title('俯视图 (X-Y) - 按强度着色')
    ax1.set_aspect('equal')
    plt.colorbar(scatter1, ax=ax1, label='强度')
    
    # 2. 侧视图 (X-Z)
    ax2 = fig.add_subplot(2, 3, 2)
    scatter2 = ax2.scatter(x, z, c=intensity, cmap='viridis', s=1, alpha=0.6)
    ax2.set_xlabel('X (米)')
    ax2.set_ylabel('Z (米)')
    ax2.set_title('侧视图 (X-Z) - 按强度着色')
    plt.colorbar(scatter2, ax=ax2, label='强度')
    
    # 3. 正视图 (Y-Z)
    ax3 = fig.add_subplot(2, 3, 3)
    scatter3 = ax3.scatter(y, z, c=intensity, cmap='viridis', s=1, alpha=0.6)
    ax3.set_xlabel('Y (米)')
    ax3.set_ylabel('Z (米)')
    ax3.set_title('正视图 (Y-Z) - 按强度着色')
    plt.colorbar(scatter3, ax=ax3, label='强度')
    
    # 4. 距离分布
    ax4 = fig.add_subplot(2, 3, 4)
    distances = np.sqrt(x**2 + y**2 + z**2)
    ax4.hist(distances, bins=50, alpha=0.7, edgecolor='black')
    ax4.set_xlabel('距离 (米)')
    ax4.set_ylabel('点数')
    ax4.set_title('距离分布直方图')
    ax4.grid(True, alpha=0.3)
    
    # 5. 强度分布
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.hist(intensity, bins=50, alpha=0.7, edgecolor='black', color='orange')
    ax5.set_xlabel('强度')
    ax5.set_ylabel('点数')
    ax5.set_title('强度分布直方图')
    ax5.grid(True, alpha=0.3)
    
    # 6. 3D散点图
    ax6 = fig.add_subplot(2, 3, 6, projection='3d')
    # 进一步采样以提高3D显示性能
    if len(points_vis) > 5000:
        indices_3d = np.random.choice(len(points_vis), 5000, replace=False)
        x_3d, y_3d, z_3d, intensity_3d = x[indices_3d], y[indices_3d], z[indices_3d], intensity[indices_3d]
    else:
        x_3d, y_3d, z_3d, intensity_3d = x, y, z, intensity
    
    scatter6 = ax6.scatter(x_3d, y_3d, z_3d, c=intensity_3d, cmap='viridis', s=1, alpha=0.6)
    ax6.set_xlabel('X (米)')
    ax6.set_ylabel('Y (米)')
    ax6.set_zlabel('Z (米)')
    ax6.set_title('3D点云视图')
    
    plt.tight_layout()
    plt.show()

def analyze_scan_sequence(data):
    """
    分析扫描序列
    
    Args:
        data: 加载的数据字典
    """
    if 'scan_timestamps' not in data:
        print("❌ 没有扫描时间戳数据")
        return
    
    timestamps = data['scan_timestamps']
    scan_ids = data['scan_ids']
    valid_points = data['scan_valid_points']
    
    print(f"\n🔄 扫描序列分析:")
    print(f"   扫描帧数: {len(timestamps)}")
    print(f"   时间跨度: {timestamps[-1] - timestamps[0]:.3f}秒")
    
    # 计算扫描频率
    if len(timestamps) > 1:
        time_diffs = np.diff(timestamps)
        avg_interval = np.mean(time_diffs)
        frequency = 1.0 / avg_interval if avg_interval > 0 else 0
        print(f"   平均扫描间隔: {avg_interval:.4f}秒")
        print(f"   平均扫描频率: {frequency:.2f} Hz")
    
    print(f"   每帧点数范围: [{valid_points.min()}, {valid_points.max()}]")
    print(f"   平均每帧点数: {valid_points.mean():.1f}")
    
    # 绘制扫描统计图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # 每帧点数变化
    ax1.plot(range(len(valid_points)), valid_points, 'b-', linewidth=1)
    ax1.set_xlabel('扫描帧序号')
    ax1.set_ylabel('有效点数')
    ax1.set_title('每帧点数变化')
    ax1.grid(True, alpha=0.3)
    
    # 扫描间隔变化
    if len(timestamps) > 1:
        ax2.plot(range(len(time_diffs)), time_diffs * 1000, 'r-', linewidth=1)
        ax2.set_xlabel('扫描间隔序号')
        ax2.set_ylabel('时间间隔 (毫秒)')
        ax2.set_title('扫描时间间隔变化')
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='激光雷达数据加载和分析')
    parser.add_argument('filepath', help='NPZ数据文件路径')
    parser.add_argument('--no-plot', action='store_true', help='不显示图形')
    parser.add_argument('--max-points', type=int, default=10000, help='可视化最大点数')
    
    args = parser.parse_args()
    
    # 加载和分析数据
    points, data = load_and_analyze_lidar_data(args.filepath)
    
    if not args.no_plot and points is not None:
        print(f"\n🎨 开始可视化...")
        
        # 可视化点云
        visualize_point_cloud(points, args.max_points)
        
        # 分析扫描序列
        analyze_scan_sequence(data)
    
    print(f"\n✅ 分析完成!")

if __name__ == "__main__":
    main()