#!/usr/bin/env python3
"""
无人机检测配置工具
用于调整检测参数和预设模式
"""

import sys
import argparse
from config import DetectionConfig, QuickPresets

def show_current_config():
    """显示当前配置"""
    print("📋 当前检测配置:")
    print(f"  置信度阈值: {DetectionConfig.CONFIDENCE_THRESHOLD}")
    print(f"  无人机尺寸范围: {DetectionConfig.DRONE_SIZE_MIN}-{DetectionConfig.DRONE_SIZE_MAX_XY}m (XY), {DetectionConfig.DRONE_SIZE_MAX_Z}m (Z)")
    print(f"  检测距离范围: {DetectionConfig.DETECTION_DISTANCE_MIN}-{DetectionConfig.DETECTION_DISTANCE_MAX}m")
    print(f"  最小高度: {DetectionConfig.MIN_HEIGHT}m")
    print(f"  聚类距离: {DetectionConfig.CLUSTERING_DISTANCE}m")
    print(f"  最小点数: {DetectionConfig.MIN_POINTS_PER_CLUSTER}")
    print(f"  检测间隔: {DetectionConfig.DETECTION_INTERVAL}s")
    print(f"  安静模式: {'开启' if DetectionConfig.QUIET_MODE else '关闭'}")

def apply_preset(preset_name):
    """应用预设配置"""
    presets = {
        'high': QuickPresets.high_precision,
        'balanced': QuickPresets.balanced,
        'sensitive': QuickPresets.sensitive,
        'debug': QuickPresets.debug
    }
    
    if preset_name in presets:
        presets[preset_name]()
        print(f"✅ 已应用 '{preset_name}' 预设配置")
        return True
    else:
        print(f"❌ 未知预设: {preset_name}")
        print("可用预设: high, balanced, sensitive, debug")
        return False

def set_confidence(value):
    """设置置信度阈值"""
    try:
        confidence = float(value)
        if 0.0 <= confidence <= 1.0:
            DetectionConfig.CONFIDENCE_THRESHOLD = confidence
            print(f"✅ 置信度阈值设置为: {confidence}")
            return True
        else:
            print("❌ 置信度必须在 0.0-1.0 之间")
            return False
    except ValueError:
        print("❌ 无效的置信度值")
        return False

def interactive_config():
    """交互式配置"""
    print("🔧 交互式配置模式")
    print("输入 'q' 退出，'show' 显示当前配置")
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'q' or cmd == 'quit':
                break
            elif cmd == 'show':
                show_current_config()
            elif cmd.startswith('confidence '):
                value = cmd.split()[1]
                set_confidence(value)
            elif cmd.startswith('preset '):
                preset = cmd.split()[1]
                apply_preset(preset)
            elif cmd == 'help':
                print("可用命令:")
                print("  show - 显示当前配置")
                print("  confidence <值> - 设置置信度阈值 (0.0-1.0)")
                print("  preset <名称> - 应用预设 (high/balanced/sensitive/debug)")
                print("  q - 退出")
            else:
                print("未知命令，输入 'help' 查看帮助")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except EOFError:
            break

def main():
    parser = argparse.ArgumentParser(description='无人机检测配置工具')
    parser.add_argument('--show', action='store_true', help='显示当前配置')
    parser.add_argument('--preset', choices=['high', 'balanced', 'sensitive', 'debug'], 
                       help='应用预设配置')
    parser.add_argument('--confidence', type=float, metavar='VALUE',
                       help='设置置信度阈值 (0.0-1.0)')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='进入交互式配置模式')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        # 没有参数时显示当前配置
        show_current_config()
        return
    
    if args.show:
        show_current_config()
    
    if args.preset:
        apply_preset(args.preset)
        show_current_config()
    
    if args.confidence is not None:
        if set_confidence(args.confidence):
            show_current_config()
    
    if args.interactive:
        interactive_config()

if __name__ == "__main__":
    main()