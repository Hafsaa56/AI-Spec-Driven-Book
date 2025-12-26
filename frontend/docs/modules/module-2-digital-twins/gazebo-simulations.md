---
sidebar_position: 2
---

# Gazebo Simulations: Physics-Based Digital Twins

## Introduction

Gazebo is a physics-based simulation environment that provides realistic sensor simulation and dynamics for robotics applications. As a key component of the sim-to-real paradigm, Gazebo enables safe testing of complex behaviors before deployment on physical robots.

## Core Concepts

### Physics Engine
Gazebo uses Open Dynamics Engine (ODE), Bullet, or DART for physics simulation, providing:
- Accurate rigid body dynamics
- Collision detection and response
- Joint constraints and motor simulation
- Realistic friction and contact models

### Sensor Simulation
Gazebo includes realistic sensor models:
- **Cameras**: RGB, depth, and stereo vision
- **LIDAR**: 2D and 3D laser range finders
- **IMU**: Inertial measurement units
- **Force/Torque**: Joint and contact force sensors
- **GPS**: Global positioning simulation

### Robot Models (URDF/SDF)
Robots are defined using:
- **URDF (Unified Robot Description Format)**: For ROS integration
- **SDF (Simulation Description Format)**: Gazebo native format

## Installation and Setup

### Installing Gazebo
```bash
# For ROS 2 Humble with Gazebo Garden
sudo apt install ros-humble-gazebo-ros-pkgs
sudo apt install gazebo
```

### Basic Gazebo Launch
```bash
# Launch Gazebo standalone
gazebo

# Launch with ROS 2 integration
ros2 launch gazebo_ros gazebo.launch.py
```

## Creating Robot Models

### Basic URDF Example
```xml
<?xml version="1.0"?>
<robot name="simple_robot">
  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 0.8"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.5 0.5 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

  <!-- Camera Sensor -->
  <link name="camera_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
    </visual>
  </link>

  <joint name="camera_joint" type="fixed">
    <parent link="base_link"/>
    <child link="camera_link"/>
    <origin xyz="0.2 0 0.1" rpy="0 0 0"/>
  </joint>

  <!-- Gazebo plugin for camera -->
  <gazebo reference="camera_link">
    <sensor type="camera" name="camera1">
      <update_rate>30.0</update_rate>
      <camera name="head">
        <horizontal_fov>1.3962634</horizontal_fov>
        <image>
          <width>800</width>
          <height>600</height>
          <format>R8G8B8</format>
        </image>
        <clip>
          <near>0.02</near>
          <far>300</far>
        </clip>
      </camera>
      <plugin name="camera_controller" filename="libgazebo_ros_camera.so">
        <frame_name>camera_link</frame_name>
      </plugin>
    </sensor>
  </gazebo>
</robot>
```

## Launching Simulations with ROS 2

### World Files
Create a world file (`my_world.sdf`):
```xml
<sdf version="1.7">
  <world name="default">
    <light name="sun" type="directional">
      <cast_shadows>1</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <attenuation>
        <range>1000</range>
        <constant>0.9</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
      <direction>-0.6 0.4 -0.8</direction>
    </light>

    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
            </plane>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>100 100</size>
            </plane>
          </geometry>
          <material>
            <ambient>0.3 0.3 0.3 1</ambient>
            <diffuse>0.5 0.5 0.5 1</diffuse>
            <specular>0 0 0 1</specular>
          </material>
        </visual>
      </link>
    </model>

    <!-- Include your robot -->
    <include>
      <uri>model://simple_robot</uri>
      <pose>0 0 0.5 0 0 0</pose>
    </include>
  </world>
</sdf>
```

### ROS 2 Launch File
Create `launch/gazebo_sim.launch.py`:
```python
import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    world = LaunchConfiguration('world')

    # Launch Gazebo with world file
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch'), '/gazebo.launch.py']),
        launch_arguments={'world': world}.items()
    )

    # Spawn robot in Gazebo
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'simple_robot'],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_entity,
    ])
```

## Sensor Integration

### Camera Integration
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
        self.subscription = self.create_subscription(
            Image,
            '/camera1/image_raw',
            self.image_callback,
            10)
        self.bridge = CvBridge()

    def image_callback(self, msg):
        # Convert ROS Image message to OpenCV image
        cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

        # Process image (example: edge detection)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        # Display image
        cv2.imshow("Camera View", cv_image)
        cv2.imshow("Edges", edges)
        cv2.waitKey(1)
```

### LIDAR Integration
```python
from sensor_msgs.msg import LaserScan
import numpy as np

class LIDARProcessor(Node):
    def __init__(self):
        super().__init__('lidar_processor')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

    def scan_callback(self, msg):
        # Process LIDAR data
        ranges = np.array(msg.ranges)

        # Remove invalid ranges
        valid_ranges = ranges[np.isfinite(ranges)]

        # Calculate minimum distance
        if len(valid_ranges) > 0:
            min_distance = np.min(valid_ranges)
            self.get_logger().info(f'Minimum distance: {min_distance:.2f}m')
```

## Control Integration

### Joint State Publisher
```python
from sensor_msgs.msg import JointState
from std_msgs.msg import Header

class JointStatePublisher(Node):
    def __init__(self):
        super().__init__('joint_state_publisher')
        self.publisher = self.create_publisher(JointState, 'joint_states', 10)
        self.timer = self.create_timer(0.1, self.publish_joint_states)

    def publish_joint_states(self):
        msg = JointState()
        msg.name = ['joint1', 'joint2']
        msg.position = [0.0, 0.0]  # Current joint positions
        msg.velocity = [0.0, 0.0]
        msg.effort = [0.0, 0.0]

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        self.publisher.publish(msg)
```

## Simulation Scenarios

### Navigation Simulation
```python
# Example: Simple navigation in Gazebo
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

class SimpleNavigator(Node):
    def __init__(self):
        super().__init__('simple_navigator')
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        self.target_x = 5.0
        self.target_y = 5.0
        self.current_x = 0.0
        self.current_y = 0.0

        self.timer = self.create_timer(0.1, self.navigate)

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

    def navigate(self):
        msg = Twist()

        # Simple proportional controller
        dx = self.target_x - self.current_x
        dy = self.target_y - self.current_y

        msg.linear.x = min(0.5, max(-0.5, 0.5 * dx))
        msg.angular.z = min(1.0, max(-1.0, 1.0 * dy))

        self.cmd_vel_pub.publish(msg)
```

## Reality Gap Mitigation

### Domain Randomization
- Randomize physical parameters (friction, mass, damping)
- Add noise to sensor readings
- Vary environmental conditions

### System Identification
- Compare simulation and real-world robot responses
- Adjust simulation parameters to match reality
- Validate models with physical experiments

### Transfer Learning
- Train policies in multiple simulated environments
- Fine-tune on real robot with minimal data
- Use simulators as pre-training environments

## Best Practices

1. **Model Validation**: Regularly validate simulation against real hardware
2. **Computational Efficiency**: Balance accuracy with simulation speed
3. **Sensor Fidelity**: Match simulated sensors to real hardware specifications
4. **Physics Parameters**: Calibrate friction, damping, and contact models
5. **Scalability**: Design simulations that can handle complex scenarios

## Debugging Tips

- Use Gazebo's built-in visualization tools
- Monitor ROS 2 topics during simulation
- Validate URDF/SDF models with checkers
- Test individual components before integration

The next section will explore Unity integration for high-fidelity graphics and visualization.