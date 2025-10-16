# 无人机检测配置文件

class DetectionConfig:
    """检测配置类"""
    
    # 置信度阈值 (0.0-1.0)
    # 只有置信度大于等于此值的无人机目标才会被显示
    CONFIDENCE_THRESHOLD = 0.0
    
    # 无人机尺寸范围 (米)
    DRONE_SIZE_MIN = 0.1    # 最小尺寸
    DRONE_SIZE_MAX_XY = 2.0 # XY方向最大尺寸
    DRONE_SIZE_MAX_Z = 1.0  # Z方向最大尺寸
    
    # 检测距离范围 (米)
    DETECTION_DISTANCE_MIN = 1.0   # 最小检测距离
    DETECTION_DISTANCE_MAX = 50.0  # 最大检测距离
    
    # 高度阈值 (米)
    MIN_HEIGHT = 0.5  # 最小高度，低于此高度的目标不被认为是无人机
    
    # 聚类参数
    CLUSTERING_DISTANCE = 0.5  # 聚类距离阈值
    MIN_POINTS_PER_CLUSTER = 3 # 每个聚类的最小点数
    
    # 检测间隔 (秒)
    DETECTION_INTERVAL = 0.5
    
    # 显示设置
    SHOW_NON_DRONE_TARGETS = True   # 是否显示非无人机目标
    SHOW_LOW_CONFIDENCE = True      # 是否显示低置信度目标
    QUIET_MODE = False              # 安静模式：未检测到目标时不显示信息

# 快速配置预设
class QuickPresets:
    """快速配置预设"""
    
    @staticmethod
    def high_precision():
        """高精度模式：只显示高置信度目标"""
        DetectionConfig.CONFIDENCE_THRESHOLD = 0.5
        DetectionConfig.QUIET_MODE = True
        DetectionConfig.SHOW_NON_DRONE_TARGETS = False
        
    @staticmethod
    def balanced():
        """平衡模式：中等置信度"""
        DetectionConfig.CONFIDENCE_THRESHOLD = 0.3
        DetectionConfig.QUIET_MODE = True
        DetectionConfig.SHOW_NON_DRONE_TARGETS = False
        
    @staticmethod
    def sensitive():
        """敏感模式：显示更多目标"""
        DetectionConfig.CONFIDENCE_THRESHOLD = 0.2
        DetectionConfig.QUIET_MODE = False
        DetectionConfig.SHOW_NON_DRONE_TARGETS = True
        
    @staticmethod
    def debug():
        """调试模式：显示所有目标"""
        DetectionConfig.CONFIDENCE_THRESHOLD = 0.0
        DetectionConfig.QUIET_MODE = False
        DetectionConfig.SHOW_NON_DRONE_TARGETS = True
        DetectionConfig.SHOW_LOW_CONFIDENCE = True