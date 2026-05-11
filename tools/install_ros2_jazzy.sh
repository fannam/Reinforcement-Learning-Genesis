#!/bin/bash

# 1. Thiết lập Locale
sudo apt update && sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

# 2. Thêm ROS 2 GPG key và Repository
sudo apt install software-properties-common -y
sudo add-apt-repository universe -y
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 3. Cài đặt ROS 2 Desktop (bao gồm Gazebo và các công cụ GUI)
sudo apt update
sudo apt upgrade -y
sudo apt install ros-jazzy-desktop -y

# 4. Cài đặt công cụ build và phát triển (colcon, python)
sudo apt install python3-colcon-common-extensions python3-rosdep python3-argcomplete -y

# 5. Cấu hình tự động nạp môi trường mỗi khi mở terminal
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc

echo "Cài đặt ROS 2 Jazzy thành công!"