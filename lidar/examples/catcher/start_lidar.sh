#!/bin/bash
# Unitree 雷达一键启动脚本

echo "🚁 启动 Unitree 雷达目标检测系统..."
echo "按 Ctrl+C 停止系统"
echo ""

cd "$(dirname "$0")"
python3 main.py "$@"