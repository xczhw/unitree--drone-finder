cmake_minimum_required(VERSION 3.0)
project(unitree_lidar_sdk)

set(CMAKE_BUILD_TYPE "Release")
set(CMAKE_CXX_FLAGS "-std=c++14")
set(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -Wall -g2 -ggdb")
set(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3 -Wall -DNDEBUG") 

# 查找PCL库
find_package(PCL QUIET)
if(PCL_FOUND)
    message(STATUS "PCL found: ${PCL_VERSION}")
    include_directories(${PCL_INCLUDE_DIRS})
    link_directories(${PCL_LIBRARY_DIRS})
    add_definitions(${PCL_DEFINITIONS})
else()
    message(WARNING "PCL not found. PCL-related examples will not be built.")
endif()

include_directories(include)

link_directories(lib/${CMAKE_SYSTEM_PROCESSOR})

SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib/${CMAKE_SYSTEM_PROCESSOR})

add_executable(example_lidar
  examples/example_lidar.cpp
)
target_link_libraries(example_lidar  libunitree_lidar_sdk.a )

add_executable(unilidar_publisher_udp
  examples/unilidar_publisher_udp.cpp
)
target_link_libraries(unilidar_publisher_udp  libunitree_lidar_sdk.a )

add_executable(unilidar_subscriber_udp
  examples/unilidar_subscriber_udp.cpp
)
target_link_libraries(unilidar_subscriber_udp  libunitree_lidar_sdk.a )

# PCL转换器 (仅在找到PCL时编译)
if(PCL_FOUND)
    add_executable(udp_to_pcl_example
      examples/udp_to_pcl_example.cpp
    )
    target_link_libraries(udp_to_pcl_example libunitree_lidar_sdk.a ${PCL_LIBRARIES})
    
    add_executable(simple_pcl_test
      examples/simple_pcl_test.cpp
    )
    target_link_libraries(simple_pcl_test libunitree_lidar_sdk.a ${PCL_LIBRARIES})
endif()