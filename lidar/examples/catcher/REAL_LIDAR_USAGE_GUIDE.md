# Unitree 雷达真实数据使用指南

## 概述

本指南介绍如何使用连接到 `/dev/ttyUSB0` 的真实 Unitree 雷达进行数据采集和目标检测。

## 系统架构

```
真实雷达硬件 (/dev/ttyUSB0)
    ↓
unilidar_publisher_udp (C++)  ← 读取串口数据，通过UDP广播
    ↓ (UDP: 127.0.0.1:12345)
接收器程序:
├── lidar_udp_receiver.py     ← Python UDP接收器
├── simple_drone_detector.py  ← 简化版目标检测器
└── drone_detector.py         ← 完整版检测器(需要open3d)
```

## 快速开始

### 🚀 方法一：一键启动（推荐）

```bash
cd /home/xczhw/Documents/sdk/unitree_lidar_sdk/examples/catcher
python3 main.py
```

或者使用启动脚本：
```bash
cd /home/xczhw/Documents/sdk/unitree_lidar_sdk/examples/catcher
./start_lidar.sh
```

这将自动：
- 检查系统前提条件
- 启动数据发布器
- 启动目标检测器
- 显示实时检测结果

### 📋 方法二：手动分步启动

#### 1. 启动数据发布器

在终端1中运行：
```bash
cd /home/xczhw/Documents/sdk/unitree_lidar_sdk
./bin/unilidar_publisher_udp /dev/ttyUSB0
```

预期输出：
```
Unitree Lidar SDK v1.0.10
Lidar firmware version: 1.0.3
Lidar working mode: NORMAL
Sending scan message, type: 102
Sending IMU message, type: 101
```

#### 2. 运行目标检测器

在终端2中运行：
```bash
cd /home/xczhw/Documents/sdk/unitree_lidar_sdk/examples/catcher
python3 simple_drone_detector.py
```

## 可用程序说明

### 1. unilidar_publisher_udp (C++)
- **功能**: 从串口读取雷达数据，通过UDP广播
- **用法**: `./bin/unilidar_publisher_udp <串口设备> [IP] [端口]`
- **默认**: IP=127.0.0.1, 端口=12345

### 2. lidar_udp_receiver.py
- **功能**: Python UDP接收器，解析雷达数据
- **特点**: 
  - 自动解析点云和IMU数据
  - 线程安全的数据访问
  - 兼容 drone_detector.py 接口

### 3. simple_drone_detector.py
- **功能**: 简化版目标检测器
- **特点**:
  - 不依赖open3d库
  - 实时目标检测和分类
  - 输出目标位置、尺寸、距离等信息

### 4. drone_detector.py
- **功能**: 完整版目标检测器
- **依赖**: open3d, numpy
- **特点**: 更高级的点云处理和可视化

### 5. main.py
- **功能**: 一键启动程序
- **特点**:
  - 自动检查系统前提条件
  - 同时启动发布器和检测器
  - 统一的进程管理和监控
  - 优雅的退出处理

### 6. start_lidar.sh
- **功能**: 简化启动脚本
- **用法**: `./start_lidar.sh [参数]`

## 检测结果示例

```
时间: 1760322650.107
检测到 1 个目标:
  目标 1: 可能是无人机
    位置: (0.67, -1.31, 0.67)
    尺寸: 0.10×0.17×0.27m
    距离: 1.47m
    置信度: 0.37
    点数: 5
```

## 检测参数调整

在 `simple_drone_detector.py` 中可以调整以下参数：

```python
class SimpleDroneDetector:
    def __init__(self):
        self.min_cluster_size = 5      # 最小聚类点数
        self.max_cluster_size = 100    # 最大聚类点数
        self.cluster_distance = 0.5    # 聚类距离阈值(米)
        self.min_height = 0.5          # 最小检测高度(米)
        self.max_height = 10.0         # 最大检测高度(米)
```

## 无人机判断逻辑

目标被判断为"可能是无人机"需要满足：
- 尺寸: 0.1-2.0m × 0.1-2.0m × 0.1-1.0m
- 距离: 1.0-50.0m
- 高度: ≥0.5m
- 点数: 5-100个点

## 故障排除

### 1. 串口权限问题
```bash
# 检查设备存在
ls -la /dev/ttyUSB0

# 检查用户组权限
groups $USER

# 如果不在dialout组，添加权限
sudo usermod -a -G dialout $USER
```

### 2. 编译问题
```bash
cd /home/xczhw/Documents/sdk/unitree_lidar_sdk
mkdir -p build && cd build
cmake ..
make -j4
```

### 3. Python依赖
```bash
pip install numpy
# 如果需要完整版检测器
pip install open3d
```

### 4. UDP端口占用
```bash
# 检查端口使用情况
netstat -un | grep 12345

# 如果需要，可以修改端口
./bin/unilidar_publisher_udp /dev/ttyUSB0 127.0.0.1 12346
```

## 集成到其他项目

### 使用接收器类
```python
from lidar_udp_receiver import LidarUDPReceiver

# 创建接收器
receiver = LidarUDPReceiver()
receiver.connect()
receiver.start_streaming()

# 获取数据
point_cloud = receiver.get_latest_raw_data()
if point_cloud and point_cloud.points is not None:
    print(f"接收到 {len(point_cloud.points)} 个点")
    # 处理点云数据...

receiver.stop_streaming()
```

### 自定义检测逻辑
```python
from simple_drone_detector import SimpleDroneDetector

detector = SimpleDroneDetector()
# 修改检测参数
detector.min_cluster_size = 3
detector.cluster_distance = 0.3

# 检测目标
objects = detector.detect_objects(points)
for obj in objects:
    if obj['is_drone_like']:
        print(f"发现无人机: {obj['center']}")
```

## 性能优化

1. **检测频率**: 调整 `time.sleep()` 间隔
2. **聚类参数**: 根据环境调整距离阈值
3. **过滤条件**: 调整尺寸和高度范围
4. **数据缓存**: 使用多线程处理

## 注意事项

1. 确保雷达硬件正确连接到 `/dev/ttyUSB0`
2. 发布器必须先启动，接收器才能获取数据
3. 检测精度受环境和雷达质量影响
4. 建议在开阔环境中测试以获得最佳效果

## 支持

如有问题，请检查：
1. 硬件连接状态
2. 串口权限设置
3. UDP网络连接
4. Python依赖安装

---
*最后更新: 2024年*