# 激光雷达数据记录和处理

本目录包含用于记录、保存和分析Unitree激光雷达数据的Python程序。

## 文件说明

### 核心程序
- `lidar_data_recorder.py` - 主要的数据记录程序
- `data_loader_example.py` - 数据分析和可视化程序
- `simple_usage_example.py` - 简单的使用示例

### 辅助程序
- `mock_udp_publisher.py` - 模拟UDP数据发送器（用于测试）

## 快速开始

### 1. 记录真实激光雷达数据

首先启动激光雷达UDP发布器：
```bash
cd ../bin
sudo ./unilidar_publisher_udp
```

然后在另一个终端记录数据：
```bash
cd examples
python3 lidar_data_recorder.py --max-scans 100 --max-duration 60
```

### 2. 使用模拟数据测试

如果没有真实硬件，可以使用模拟数据：

启动模拟发送器：
```bash
python3 mock_udp_publisher.py --duration 30 --scan-rate 10
```

在另一个终端记录数据：
```bash
python3 lidar_data_recorder.py --max-scans 50 --max-duration 30
```

### 3. 分析保存的数据

查看数据信息：
```bash
python3 lidar_data_recorder.py --load ../data/your_file.npz
```

详细分析和可视化：
```bash
python3 data_loader_example.py ../data/your_file.npz
```

简单使用示例：
```bash
python3 simple_usage_example.py
```

## 数据格式

数据保存为NPZ格式（NumPy压缩数组），包含以下字段：

### 点云数据
- `points`: [N, 6] 数组，包含 x, y, z, intensity, time, ring
- `scan_timestamps`: 每帧扫描的时间戳
- `scan_ids`: 每帧扫描的ID

### IMU数据
- `imu_timestamps`: IMU数据时间戳
- `imu_quaternions`: 四元数 [w, x, y, z]
- `imu_angular_velocities`: 角速度 [x, y, z]
- `imu_linear_accelerations`: 线性加速度 [x, y, z]

### 元数据
- `recording_info`: 记录信息（开始时间、持续时间等）

## 在你的项目中使用

### 基本加载
```python
import numpy as np

# 加载数据
data = np.load('your_file.npz', allow_pickle=True)

# 获取点云数据 [N, 6] - x, y, z, intensity, time, ring
points = data['points']

# 获取坐标
xyz = points[:, :3]  # x, y, z
intensity = points[:, 3]  # 强度
time = points[:, 4]  # 时间
ring = points[:, 5]  # 环数

# 获取IMU数据
imu_quaternions = data['imu_quaternions']
imu_angular_velocities = data['imu_angular_velocities']
imu_linear_accelerations = data['imu_linear_accelerations']
```

### 使用提供的函数
```python
# 复制 simple_usage_example.py 中的 load_lidar_data 函数
from simple_usage_example import load_lidar_data

# 加载数据
data = load_lidar_data('your_file.npz')

# 使用数据
points = data['points']
# ... 其他处理
```

## 命令行参数

### lidar_data_recorder.py
- `--output-dir`: 输出目录（默认：../data）
- `--max-scans`: 最大扫描帧数（默认：1000）
- `--max-duration`: 最大记录时间（秒，默认：300）
- `--load`: 加载并显示NPZ文件信息

### data_loader_example.py
- `npz_file`: NPZ文件路径
- `--no-plot`: 禁用图形显示
- `--max-points`: 可视化的最大点数（默认：10000）

### mock_udp_publisher.py
- `--duration`: 发送持续时间（秒，默认：60）
- `--scan-rate`: 扫描频率（Hz，默认：10）
- `--imu-rate`: IMU频率（Hz，默认：100）

## 数据处理示例

### 距离过滤
```python
xyz = points[:, :3]
distances = np.sqrt(np.sum(xyz**2, axis=1))
mask = (distances >= 1.0) & (distances <= 10.0)
filtered_points = points[mask]
```

### 强度过滤
```python
intensity = points[:, 3]
mask = intensity >= 100
filtered_points = points[mask]
```

### 按环数分组
```python
ring = points[:, 5].astype(int)
for ring_id in np.unique(ring):
    ring_points = points[ring == ring_id]
    print(f"环 {ring_id}: {len(ring_points)} 个点")
```

## 注意事项

1. **文件大小**: NPZ文件会根据记录时间和点云密度变化，通常几MB到几百MB
2. **内存使用**: 加载大文件时注意内存使用，可以考虑分批处理
3. **坐标系**: 点云坐标为激光雷达本地坐标系
4. **时间戳**: 时间戳为相对于记录开始的时间（秒）
5. **数据质量**: 模拟数据仅用于测试，真实数据质量取决于硬件和环境

## 故障排除

### 常见问题
1. **权限错误**: 运行真实硬件程序需要sudo权限
2. **端口占用**: 确保UDP端口12345未被占用
3. **依赖缺失**: 确保安装了numpy, matplotlib等依赖
4. **文件路径**: 注意相对路径，确保在正确目录运行

### 调试技巧
1. 使用 `--load` 参数检查保存的数据
2. 使用模拟数据测试程序功能
3. 检查终端输出的错误信息
4. 使用 `simple_usage_example.py` 验证数据格式