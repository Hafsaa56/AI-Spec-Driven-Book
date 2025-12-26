---
sidebar_position: 4
---

# Hardware Setup: Physical Robot Configuration

## Overview

This chapter provides comprehensive guidance for setting up the physical humanoid robot hardware. The setup process involves mechanical assembly, electrical connections, software installation, and system calibration to ensure safe and effective operation.

## Safety First

### Pre-Assembly Safety
- **Work Area**: Clear, well-lit, and stable workspace
- **Tools**: Properly maintained and appropriate for tasks
- **Personal Protection**: Safety glasses when working with tools
- **Electrical Safety**: Unplug power sources before making connections
- **Lifting**: Use proper lifting techniques for heavy components

### Operational Safety
- **Emergency Stop**: Easily accessible emergency stop procedures
- **Power Management**: Proper grounding and power distribution
- **Physical Barriers**: Safety perimeters during testing
- **Supervision**: Never leave robot unattended during initial testing
- **Maintenance**: Regular inspection of mechanical and electrical components

## Mechanical Assembly

### Frame Assembly
1. **Base Platform**: Start with the main torso/chassis assembly
   - Align and secure main structural components
   - Torque bolts to manufacturer specifications
   - Verify structural integrity before proceeding

2. **Limb Attachment**: Attach arms and legs in sequence
   - Install joint actuators with proper alignment
   - Connect mechanical linkages with appropriate fasteners
   - Verify range of motion for each joint

3. **Head Assembly**: Install head and sensor components
   - Mount head with proper neck joint alignment
   - Install camera and other sensors
   - Route cables through neck passage

### Joint Installation
- **Actuator Mounting**: Secure servo motors/actuators to joint brackets
- **Coupling**: Connect motor shafts to joint mechanisms
- **Limit Switches**: Install and calibrate joint limit switches
- **Cable Management**: Route and secure cables to prevent interference

## Electrical System

### Power Distribution
1. **Main Power Supply**
   - Install main battery pack or power connection
   - Verify voltage and current ratings
   - Install main power switch and fuses

2. **Power Regulation**
   - Install voltage regulators for different subsystems
   - 12V for actuators, 5V for sensors, 3.3V for logic
   - Add filtering capacitors for clean power

3. **Wiring Harness**
   - Create organized wiring harness for each limb
   - Use appropriate gauge wire for current requirements
   - Install connectors with proper pin assignments
   - Label all connections for troubleshooting

### Control System Hardware

#### Main Computing Platform
- **Single Board Computer**: NVIDIA Jetson AGX Xavier or equivalent
  - Mount securely with vibration isolation
  - Ensure adequate cooling with fans/heat sinks
  - Connect to power and communication buses

- **Real-time Controller**: For time-critical control tasks
  - Install microcontroller for joint control
  - Connect to actuator interfaces
  - Program with safety-critical control loops

#### Communication Infrastructure
- **CAN Bus**: For high-reliability actuator communication
  - Install CAN transceivers for each node
  - Terminate bus properly at both ends
  - Verify communication before power-on

- **Ethernet**: For high-bandwidth sensor data
  - Install gigabit switch for sensor networking
  - Connect cameras, LIDAR, and other high-bandwidth sensors
  - Verify network connectivity and bandwidth

## Sensor Installation

### Vision System
1. **RGB-D Camera**
   - Mount in head assembly with proper alignment
   - Connect USB/Ethernet and power cables
   - Calibrate intrinsic and extrinsic parameters

2. **Additional Cameras** (if applicable)
   - Mount in appropriate locations (chest, hands, etc.)
   - Ensure wide field of view without self-occlusion
   - Secure cables to prevent movement during operation

### Audition System
1. **Microphone Array**
   - Install in head with proper spacing for sound localization
   - Connect to audio processing board
   - Calibrate for acoustic environment

2. **Speaker System**
   - Install for speech output
   - Connect to audio amplifier
   - Test audio quality and volume levels

### Proprioceptive Sensors
1. **IMU Installation**
   - Mount in torso for body orientation
   - Secure to prevent vibration-induced errors
   - Calibrate for local magnetic field

2. **Joint Encoders**
   - Install on each actuator shaft
   - Connect to joint controller boards
   - Calibrate zero positions

3. **Force/Torque Sensors**
   - Install at appropriate locations (feet, hands)
   - Connect to analog/digital conversion boards
   - Calibrate for known weights

## Software Installation

### Operating System Setup
1. **Ubuntu 22.04 Installation**
   ```bash
   # Download Ubuntu 22.04 image for target hardware
   # Flash to main storage device
   # Boot and complete initial setup
   ```

2. **ROS 2 Humble Installation**
   ```bash
   # Add ROS 2 repository
   sudo apt update && sudo apt install curl gnupg lsb-release
   curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

   # Install ROS 2 packages
   sudo apt update
   sudo apt install ros-humble-desktop ros-humble-ros-base
   sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
   ```

### Real-time Kernel Configuration
```bash
# Install real-time kernel
sudo apt install linux-image-rt-generic

# Configure GRUB for real-time scheduling
sudo nano /etc/default/grub
# Add to GRUB_CMDLINE_LINUX_DEFAULT: "quiet splash isolcpus=1,2,3"
sudo update-grub
```

### Hardware Drivers
1. **Actuator Drivers**
   ```bash
   # Install Dynamixel SDK or equivalent
   git clone https://github.com/ROBOTIS-GIT/DynamixelSDK.git
   cd DynamixelSDK
   cd python
   python3 setup.py install
   ```

2. **Sensor Drivers**
   - Install camera drivers (V4L2, libuvc, etc.)
   - Install LIDAR drivers if applicable
   - Install IMU drivers and calibration tools

## System Calibration

### Mechanical Calibration
1. **Joint Zero Positioning**
   - Manually position each joint to mechanical zero
   - Set encoder values to zero at this position
   - Document any offsets for software compensation

2. **Kinematic Calibration**
   - Use calibration patterns for camera systems
   - Measure actual link lengths and offsets
   - Update URDF with calibrated values

### Electrical Calibration
1. **Power System**
   - Verify voltage levels at each subsystem
   - Test current draw under various loads
   - Calibrate power monitoring systems

2. **Sensor Calibration**
   - Camera intrinsic calibration using checkerboard
   - IMU bias calibration in multiple orientations
   - Force/torque sensor zero calibration

## Initial Testing

### Pre-Power-On Checks
- **Visual Inspection**: All connections secure, no loose wires
- **Continuity Testing**: Verify power and ground isolation
- **Resistance Testing**: Check for short circuits in critical paths
- **Software Verification**: Confirm all necessary software is installed

### Power-On Sequence
1. **Initial Power-Up**
   - Apply main power with current monitoring
   - Verify all voltage rails are correct
   - Check for unusual heat or sounds

2. **Communication Testing**
   - Verify ROS 2 master is running
   - Test communication with all subsystems
   - Confirm sensor data publication

3. **Safety System Verification**
   - Test emergency stop functionality
   - Verify safety limits are enforced
   - Confirm fault detection systems are active

## Integration Testing

### Individual Subsystem Tests
1. **Locomotion Testing**
   - Test individual joint movements
   - Verify range of motion is within mechanical limits
   - Test joint control stability

2. **Perception Testing**
   - Verify camera feeds are available
   - Test object detection capabilities
   - Confirm sensor fusion is working

3. **Control Testing**
   - Test basic movement commands
   - Verify safety limits are enforced
   - Test recovery behaviors

### System Integration Tests
1. **Basic Navigation**
   - Test simple movement commands
   - Verify obstacle detection and avoidance
   - Test localization in known environment

2. **Interaction Testing**
   - Test speech recognition and synthesis
   - Verify gesture recognition
   - Test basic dialogue capabilities

## Documentation and Maintenance

### Setup Documentation
- **Wiring Diagrams**: Complete electrical connection diagrams
- **Calibration Records**: All calibration parameters and procedures
- **Software Configuration**: Complete software setup procedures
- **Maintenance Schedule**: Regular inspection and maintenance tasks

### Troubleshooting Guide
- **Common Issues**: Typical problems and solutions
- **Diagnostic Procedures**: Systematic troubleshooting approaches
- **Replacement Procedures**: How to replace common components
- **Backup Procedures**: System backup and recovery processes

## Quality Assurance

### Performance Verification
- **Timing Tests**: Verify real-time performance requirements
- **Accuracy Tests**: Confirm sensor and actuator accuracy
- **Reliability Tests**: Long-term operation stability
- **Safety Tests**: Emergency stop and fault handling

### Validation Checklist
- [ ] All joints move freely within specified ranges
- [ ] All sensors provide expected data
- [ ] Communication systems are reliable
- [ ] Safety systems function correctly
- [ ] Basic behaviors execute as expected
- [ ] Power consumption is within specifications

This hardware setup provides the foundation for the complete autonomous humanoid robot system. Proper setup and calibration are essential for safe and effective operation of the physical system.