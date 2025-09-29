#include <iostream>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

// Unitree SDK headers
#include "unitree_lidar_sdk.h"
#include "unitree_lidar_sdk_pcl.h"  // 包含PCL转换功能

using namespace unitree_lidar_sdk;

class UDPToPCLConverter {
private:
    int sockfd;
    struct sockaddr_in server_addr;
    
public:
    UDPToPCLConverter(int port = 12345) {
        // 创建UDP socket
        sockfd = socket(AF_INET, SOCK_DGRAM, 0);
        if (sockfd < 0) {
            std::cerr << "Error creating socket" << std::endl;
            exit(1);
        }
        
        // 设置服务器地址
        memset(&server_addr, 0, sizeof(server_addr));
        server_addr.sin_family = AF_INET;
        server_addr.sin_addr.s_addr = INADDR_ANY;
        server_addr.sin_port = htons(port);
        
        // 绑定socket
        if (bind(sockfd, (const struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
            std::cerr << "Error binding socket" << std::endl;
            exit(1);
        }
        
        std::cout << "UDP server listening on port " << port << std::endl;
    }
    
    ~UDPToPCLConverter() {
        close(sockfd);
    }
    
    void processMessages() {
        char buffer[65536];  // 64KB buffer
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        
        while (true) {
            // 接收UDP数据
            ssize_t recv_len = recvfrom(sockfd, buffer, sizeof(buffer), 0,
                                      (struct sockaddr*)&client_addr, &client_len);
            
            if (recv_len < 0) {
                std::cerr << "Error receiving data" << std::endl;
                continue;
            }
            
            // 解析消息头
            if (recv_len < 8) {  // 至少需要8字节的头部
                std::cerr << "Received data too short" << std::endl;
                continue;
            }
            
            uint32_t msgType = *((uint32_t*)buffer);
            uint32_t dataSize = *((uint32_t*)(buffer + 4));
            
            std::cout << "Received message: Type=" << msgType 
                      << ", DataSize=" << dataSize 
                      << ", RecvLen=" << recv_len << std::endl;
            
            // 处理不同类型的消息
            if (msgType == 101) {  // IMU消息
                processIMUMessage(buffer + 8, dataSize);
            } else if (msgType == 102) {  // 点云消息
                processPointCloudMessage(buffer + 8, dataSize);
            } else {
                std::cout << "Unknown message type: " << msgType << std::endl;
            }
        }
    }
    
private:
    void processIMUMessage(const char* data, uint32_t size) {
        if (size != sizeof(IMUUnitree)) {
            std::cerr << "IMU data size mismatch" << std::endl;
            return;
        }
        
        const IMUUnitree* imu = reinterpret_cast<const IMUUnitree*>(data);
        std::cout << "IMU Data - Stamp: " << imu->stamp 
                  << ", ID: " << imu->id 
                  << ", Quaternion: [" << imu->quaternion[0] 
                  << ", " << imu->quaternion[1] 
                  << ", " << imu->quaternion[2] 
                  << ", " << imu->quaternion[3] << "]" << std::endl;
    }
    
    void processPointCloudMessage(const char* data, uint32_t size) {
        if (size != sizeof(ScanUnitree)) {
            std::cerr << "Scan data size mismatch" << std::endl;
            return;
        }
        
        const ScanUnitree* scan = reinterpret_cast<const ScanUnitree*>(data);
        
        std::cout << "Scan Data - Stamp: " << scan->stamp 
                  << ", ID: " << scan->id 
                  << ", Valid Points: " << scan->validPointsNum << std::endl;
        
        // 转换为PCL格式
        convertToPCL(*scan);
    }
    
    void convertToPCL(const ScanUnitree& scan) {
        // 创建Unitree点云对象
        PointCloudUnitree unitree_cloud;
        unitree_cloud.stamp = scan.stamp;
        unitree_cloud.id = scan.id;
        
        // 复制有效的点云数据 (scan.points是数组，需要逐个复制)
        unitree_cloud.points.clear();
        for (uint32_t i = 0; i < scan.validPointsNum && i < 120; i++) {
            unitree_cloud.points.push_back(scan.points[i]);
        }
        
        // 创建PCL点云对象
        pcl::PointCloud<PointType>::Ptr pcl_cloud(new pcl::PointCloud<PointType>);
        
        // 使用SDK提供的转换函数
        transformUnitreeCloudToPCL(unitree_cloud, pcl_cloud);
        
        std::cout << "✅ 转换为PCL格式成功!" << std::endl;
        std::cout << "PCL点云信息:" << std::endl;
        std::cout << "  - 点数量: " << pcl_cloud->size() << std::endl;
        std::cout << "  - 是否有序: " << (pcl_cloud->isOrganized() ? "是" : "否") << std::endl;
        std::cout << "  - 宽度: " << pcl_cloud->width << std::endl;
        std::cout << "  - 高度: " << pcl_cloud->height << std::endl;
        
        // 显示前5个点的PCL格式数据
        std::cout << "前5个点的PCL格式数据:" << std::endl;
        for (size_t i = 0; i < std::min((size_t)5, pcl_cloud->size()); i++) {
            const PointType& pt = pcl_cloud->points[i];
            std::cout << "  点" << i << ": x=" << pt.x 
                      << ", y=" << pt.y 
                      << ", z=" << pt.z 
                      << ", intensity=" << pt.intensity 
                      << ", ring=" << pt.ring 
                      << ", time=" << pt.time << std::endl;
        }
        
        // 这里你可以进行PCL的各种处理操作
        // 例如：滤波、特征提取、保存为PCD文件等
        
        // 示例：保存为PCD文件
        // std::string filename = "scan_" + std::to_string(scan.id) + ".pcd";
        // pcl::io::savePCDFileASCII(filename, *pcl_cloud);
        // std::cout << "保存PCL文件: " << filename << std::endl;
        
        std::cout << "---" << std::endl;
    }
};

int main() {
    std::cout << "UDP到PCL转换器启动..." << std::endl;
    std::cout << "等待来自unilidar_publisher_udp的数据..." << std::endl;
    
    UDPToPCLConverter converter;
    converter.processMessages();
    
    return 0;
}