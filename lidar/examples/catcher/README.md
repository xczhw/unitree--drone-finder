# Unitree 雷达目标检测系统

## 🚀 一键启动

```bash
cd /home/xczhw/Documents/sdk/unitree_lidar_sdk/examples/catcher
python3 main.py
```

或者：
```bash
./start_lidar.sh
```

## 📋 系统要求

1. ✅ 雷达连接到 `/dev/ttyUSB0`
2. ✅ 用户在 `dialout` 组中
3. ✅ 已编译 C++ 程序
4. ✅ 已安装 Python 依赖

## 🎯 功能特点

- **智能过滤**: 只显示置信度≥0.3的无人机目标
- **无人机专检**: 专门优化的无人机检测算法
- **实时显示**: 显示目标位置、尺寸、距离等信息
- **一键启动**: 自动管理所有进程
- **安静模式**: 未检测到目标时保持安静

## 📊 检测输出示例

```
时间: 1760322650.107
检测到 1 个无人机目标:
  无人机 1:
    位置: (0.67, -1.31, 0.67)
    尺寸: 0.10×0.17×0.27m
    距离: 1.47m
    置信度: 0.37
    点数: 5
```

**注意**: 只显示置信度≥0.3的无人机目标，其他目标和低置信度目标不会显示。

## ⚙️ 高级选项

### 启动参数
```bash
python3 main.py --help                    # 查看所有选项
python3 main.py --device /dev/ttyUSB1     # 使用不同串口
python3 main.py --port 12346              # 使用不同端口
```

### 检测配置
```bash
python3 configure.py --show               # 显示当前配置
python3 configure.py --confidence 0.5     # 设置置信度阈值
python3 configure.py --preset high        # 应用高精度预设
python3 configure.py -i                   # 交互式配置
```

### 预设模式
- **high**: 高精度模式 (置信度≥0.5)
- **balanced**: 平衡模式 (置信度≥0.3) - 默认
- **sensitive**: 敏感模式 (置信度≥0.2)
- **debug**: 调试模式 (显示所有目标)

## 📁 文件说明

- `main.py` - 一键启动程序
- `start_lidar.sh` - 启动脚本
- `simple_drone_detector.py` - 简化版检测器
- `lidar_udp_receiver.py` - 数据接收器
- `config.py` - 检测配置文件
- `configure.py` - 配置工具
- `REAL_LIDAR_USAGE_GUIDE.md` - 详细使用指南

## 🆘 故障排除

### 权限问题
```bash
sudo usermod -a -G dialout $USER
# 然后重新登录
```

### 编译问题
```bash
cd /home/xczhw/Documents/sdk/unitree_lidar_sdk
mkdir -p build && cd build
cmake .. && make -j4
```

### 依赖安装
```bash
pip install numpy
```

---
按 `Ctrl+C` 停止系统