---
sidebar_position: 2
---

# Environment Configuration for Ubuntu 22.04

This guide provides the necessary steps to configure your Ubuntu 22.04 environment for the Physical AI and Humanoid Robotics book.

## Prerequisites

Before starting with the book content, ensure your Ubuntu 22.04 system has the following:

- Python 3.10+ installed
- Node.js 18+ installed
- Git version control system
- Basic development tools

## System Setup

### 1. Update System Packages

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python 3.10+

```bash
sudo apt install python3.10 python3.10-dev python3.10-venv python3-pip -y
```

### 3. Install Node.js 18+

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 4. Install Git

```bash
sudo apt install git -y
```

### 5. Install Additional Development Tools

```bash
sudo apt install build-essential cmake pkg-config libusb-1.0-0-dev libtbb-dev libeigen3-dev -y
```

## ROS 2 Humble Hawksbill Installation

### 1. Setup Locale

```bash
sudo locale-gen en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
```

### 2. Setup Sources

```bash
sudo apt update && sudo apt install curl gnupg lsb-release
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

### 3. Install ROS 2

```bash
sudo apt update
sudo apt install ros-humble-desktop
sudo apt install python3-colcon-common-extensions
sudo apt install ros-humble-rosbridge-suite
```

### 4. Source ROS 2 Environment

```bash
source /opt/ros/humble/setup.bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```

## NVIDIA Isaac Setup (Optional)

### 1. Install NVIDIA Container Toolkit

```bash
sudo apt install nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. Verify GPU Access

```bash
nvidia-smi
```

## Development Environment Verification

To verify your environment is properly configured, run:

```bash
# Check Python version
python3 --version

# Check Node.js version
node --version

# Check ROS 2 installation
source /opt/ros/humble/setup.bash
ros2 --version

# Check Git installation
git --version
```

## Troubleshooting

### Common Issues

1. **Permission denied errors with Docker**:
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in for changes to take effect
   ```

2. **ROS 2 command not found**:
   Ensure you've sourced the ROS 2 environment:
   ```bash
   source /opt/ros/humble/setup.bash
   ```

3. **Node.js version too old**:
   Remove old Node.js and reinstall:
   ```bash
   sudo apt remove nodejs
   # Then follow the installation steps above
   ```

Your Ubuntu 22.04 environment is now properly configured for the Physical AI and Humanoid Robotics book!