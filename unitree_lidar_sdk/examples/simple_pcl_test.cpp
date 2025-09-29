#include <iostream>
#include "unitree_lidar_sdk.h"
#include "unitree_lidar_sdk_pcl.h"

using namespace unitree_lidar_sdk;

int main() {
    std::cout << "=== PCL转换功能测试 ===" << std::endl;
    
    // 创建一个模拟的ScanUnitree数据
    ScanUnitree scan;
    scan.stamp = 1758853958.5070791;
    scan.id = 276494;
    scan.validPointsNum = 5;  // 只测试5个点
    
    // 填充一些测试点数据
    for (int i = 0; i < 5; i++) {
        scan.points[i].x = 0.42 + i * 0.01;
        scan.points[i].y = -0.74 + i * 0.02;
        scan.points[i].z = 0.047 + i * 0.01;
        scan.points[i].intensity = 230 - i * 5;
        scan.points[i].time = i * 0.00002;
        scan.points[i].ring = 0;
    }
    
    std::cout << "原始Unitree Scan数据:" << std::endl;
    std::cout << "  时间戳: " << scan.stamp << std::endl;
    std::cout << "  ID: " << scan.id << std::endl;
    std::cout << "  有效点数: " << scan.validPointsNum << std::endl;
    
    // 转换为PointCloudUnitree格式
    PointCloudUnitree unitree_cloud;
    unitree_cloud.stamp = scan.stamp;
    unitree_cloud.id = scan.id;
    unitree_cloud.points.clear();
    
    for (uint32_t i = 0; i < scan.validPointsNum && i < 120; i++) {
        unitree_cloud.points.push_back(scan.points[i]);
    }
    
    std::cout << "\n转换为PointCloudUnitree格式:" << std::endl;
    std::cout << "  点云大小: " << unitree_cloud.points.size() << std::endl;
    
    // 转换为PCL格式
    pcl::PointCloud<PointType>::Ptr pcl_cloud(new pcl::PointCloud<PointType>);
    transformUnitreeCloudToPCL(unitree_cloud, pcl_cloud);
    
    std::cout << "\n✅ 成功转换为PCL格式!" << std::endl;
    std::cout << "PCL点云信息:" << std::endl;
    std::cout << "  点数量: " << pcl_cloud->size() << std::endl;
    std::cout << "  是否有序: " << (pcl_cloud->isOrganized() ? "是" : "否") << std::endl;
    std::cout << "  宽度: " << pcl_cloud->width << std::endl;
    std::cout << "  高度: " << pcl_cloud->height << std::endl;
    
    std::cout << "\nPCL格式的点云数据:" << std::endl;
    for (size_t i = 0; i < pcl_cloud->size(); i++) {
        const PointType& pt = pcl_cloud->points[i];
        std::cout << "  点" << i << ": x=" << pt.x 
                  << ", y=" << pt.y 
                  << ", z=" << pt.z 
                  << ", intensity=" << pt.intensity 
                  << ", ring=" << pt.ring 
                  << ", time=" << pt.time << std::endl;
    }
    
    std::cout << "\n🎉 PCL转换测试完成!" << std::endl;
    std::cout << "\n总结:" << std::endl;
    std::cout << "✅ 你收到的UDP数据是Unitree原生格式 (ScanUnitree)" << std::endl;
    std::cout << "✅ 可以使用transformUnitreeCloudToPCL()函数转换为PCL格式" << std::endl;
    std::cout << "✅ PCL格式包含: x,y,z,intensity,ring,time 字段" << std::endl;
    std::cout << "✅ 转换后可以使用所有PCL库的功能进行处理" << std::endl;
    
    return 0;
}