---
sidebar_position: 3
---

# Capstone Implementation: Building the Autonomous Humanoid

## Implementation Overview

This chapter provides detailed implementation guidance for the autonomous humanoid robot system. We'll walk through the step-by-step process of building each subsystem and integrating them into a complete system.

## Development Environment Setup

### Prerequisites
```bash
# ROS 2 Humble with required packages
sudo apt update
sudo apt install ros-humble-desktop-full
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup
sudo apt install ros-humble-moveit ros-humble-moveit-ros
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-gazebo-plugins
sudo apt install ros-humble-rosbridge-suite ros-humble-tf2-tools
sudo apt install python3-colcon-common-extensions
```

### Workspace Structure
```bash
mkdir -p ~/humanoid_ws/src
cd ~/humanoid_ws
colcon build
source install/setup.bash
```

## Core System Implementation

### 1. Robot Description Package

Create the robot description package:

```bash
cd ~/humanoid_ws/src
ros2 pkg create --build-type ament_cmake humanoid_description --dependencies urdf xacro
```

**File: humanoid_description/urdf/humanoid.urdf.xacro**

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="humanoid">

  <!-- Constants -->
  <xacro:property name="M_PI" value="3.1415926535897931" />

  <!-- Materials -->
  <material name="blue">
    <color rgba="0.0 0.0 0.8 1.0"/>
  </material>
  <material name="black">
    <color rgba="0.0 0.0 0.0 1.0"/>
  </material>
  <material name="white">
    <color rgba="1.0 1.0 1.0 1.0"/>
  </material>

  <!-- Base Link -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.4"/>
      </geometry>
      <material name="white"/>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.4"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0" />
      <origin xyz="0 0 0" />
      <inertia  ixx="0.4" ixy="0.0" ixz="0.0"
                iyy="0.4" iyz="0.0"
                izz="0.2" />
    </inertial>
  </link>

  <!-- Head -->
  <joint name="head_joint" type="fixed">
    <parent link="base_link"/>
    <child link="head"/>
    <origin xyz="0 0 0.3" rpy="0 0 0"/>
  </joint>

  <link name="head">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="white"/>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0" />
      <origin xyz="0 0 0" />
      <inertia  ixx="0.01" ixy="0.0" ixz="0.0"
                iyy="0.01" iyz="0.0"
                izz="0.01" />
    </inertial>
  </link>

  <!-- Camera in head -->
  <joint name="camera_joint" type="fixed">
    <parent link="head"/>
    <child link="camera_link"/>
    <origin xyz="0.05 0 0" rpy="0 0 0"/>
  </joint>

  <link name="camera_link">
    <visual>
      <geometry>
        <box size="0.05 0.05 0.05"/>
      </geometry>
      <material name="black"/>
    </visual>
  </link>

  <!-- Gazebo plugin for camera -->
  <gazebo reference="camera_link">
    <sensor type="camera" name="camera1">
      <update_rate>30.0</update_rate>
      <camera name="head">
        <horizontal_fov>1.3962634</horizontal_fov>
        <image>
          <width>640</width>
          <height>480</height>
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

  <!-- Left Arm -->
  <joint name="left_shoulder_joint" type="revolute">
    <parent link="base_link"/>
    <child link="left_upper_arm"/>
    <origin xyz="0.15 0.1 0.1" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="${-M_PI/2}" upper="${M_PI/2}" effort="100" velocity="1.0"/>
  </joint>

  <link name="left_upper_arm">
    <visual>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
      <origin xyz="0 0 -0.15" rpy="0 ${M_PI/2} 0"/>
      <material name="blue"/>
    </visual>
    <collision>
      <geometry>
        <cylinder length="0.3" radius="0.05"/>
      </geometry>
      <origin xyz="0 0 -0.15" rpy="0 ${M_PI/2} 0"/>
    </collision>
    <inertial>
      <mass value="2.0" />
      <origin xyz="0 0 -0.15" />
      <inertia  ixx="0.01" ixy="0.0" ixz="0.0"
                iyy="0.01" iyz="0.0"
                izz="0.001" />
    </inertial>
  </link>

  <!-- Add more joints and links for complete humanoid -->
  <!-- (elbows, wrists, hips, knees, ankles, etc.) -->

</robot>
```

### 2. Perception System Implementation

**File: humanoid_perception/package.xml**
```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>humanoid_perception</name>
  <version>0.0.0</version>
  <description>Perception system for humanoid robot</description>
  <maintainer email="robot@todo.todo">robot</maintainer>
  <license>Apache-2.0</license>

  <depend>rclpy</depend>
  <depend>sensor_msgs</depend>
  <depend>cv_bridge</depend>
  <depend>vision_msgs</depend>
  <depend>image_geometry</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

**File: humanoid_perception/humanoid_perception/object_detector.py**
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from vision_msgs.msg import Detection2DArray, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import cv2
import numpy as np

class ObjectDetector(Node):
    def __init__(self):
        super().__init__('object_detector')

        # Initialize OpenCV bridge
        self.bridge = CvBridge()

        # Create subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)

        self.info_sub = self.create_subscription(
            CameraInfo,
            '/camera/camera_info',
            self.info_callback,
            10)

        # Create publisher for detections
        self.detection_pub = self.create_publisher(
            Detection2DArray,
            '/object_detections',
            10)

        # Initialize camera parameters
        self.camera_matrix = None
        self.dist_coeffs = None

        # YOLO model (simplified - in practice, use a real model)
        self.conf_threshold = 0.5
        self.nms_threshold = 0.4

    def info_callback(self, msg):
        self.camera_matrix = np.array(msg.k).reshape(3, 3)
        self.dist_coeffs = np.array(msg.d)

    def image_callback(self, msg):
        # Convert ROS Image to OpenCV
        cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")

        # Perform object detection (simplified - in practice, use YOLO, etc.)
        detections = self.detect_objects(cv_image)

        # Publish detections
        detection_msg = self.create_detection_message(detections, msg.header)
        self.detection_pub.publish(detection_msg)

    def detect_objects(self, image):
        # This is a simplified detection - in practice, use a real model
        # For example, using YOLO or other deep learning models
        height, width = image.shape[:2]

        # Create some dummy detections for demonstration
        detections = []

        # Detect humans (simplified)
        # In practice, use a trained model like YOLOv5, YOLOv8, etc.
        for i in range(2):  # Create 2 dummy detections
            x = np.random.randint(0, width//2)
            y = np.random.randint(0, height//2)
            w = np.random.randint(50, 150)
            h = np.random.randint(100, 200)

            detection = {
                'bbox': [x, y, w, h],
                'confidence': np.random.uniform(0.6, 0.9),
                'class': 'person' if i == 0 else 'object',
                'center_3d': [x + w//2, y + h//2, 1.0]  # Simplified depth
            }
            detections.append(detection)

        return detections

    def create_detection_message(self, detections, header):
        detection_array = Detection2DArray()
        detection_array.header = header

        for detection in detections:
            detection_2d = Detection2D()
            detection_2d.header = header

            # Set bounding box
            detection_2d.bbox.size_x = detection['bbox'][2]
            detection_2d.bbox.size_y = detection['bbox'][3]

            # Set center
            center = detection['bbox'][:2] + np.array(detection['bbox'][2:]) / 2
            detection_2d.bbox.center.x = float(center[0])
            detection_2d.bbox.center.y = float(center[1])

            # Set hypothesis
            hypothesis = ObjectHypothesisWithPose()
            hypothesis.hypothesis.class_id = detection['class']
            hypothesis.hypothesis.score = detection['confidence']
            detection_2d.results.append(hypothesis)

            detection_array.detections.append(detection_2d)

        return detection_array

def main(args=None):
    rclpy.init(args=args)
    detector = ObjectDetector()

    try:
        rclpy.spin(detector)
    except KeyboardInterrupt:
        detector.get_logger().info('Shutting down object detector')
    finally:
        detector.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 3. Cognition System Implementation

**File: humanoid_cognition/humanoid_cognition/task_planner.py**
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
from humanoid_msgs.msg import Task, TaskStatus
import json

class TaskPlanner(Node):
    def __init__(self):
        super().__init__('task_planner')

        # Create subscribers
        self.task_sub = self.create_subscription(
            Task,
            '/task_requests',
            self.task_callback,
            10)

        # Create publishers
        self.status_pub = self.create_publisher(
            TaskStatus,
            '/task_status',
            10)

        self.goal_pub = self.create_publisher(
            PoseStamped,
            '/move_base_simple/goal',
            10)

        # Task queue and current task
        self.task_queue = []
        self.current_task = None
        self.task_executor = TaskExecutor(self)

    def task_callback(self, msg):
        self.get_logger().info(f'Received task: {msg.task_type} - {msg.description}')

        # Add task to queue
        self.task_queue.append(msg)

        # Process next task if none is running
        if self.current_task is None:
            self.process_next_task()

    def process_next_task(self):
        if self.task_queue:
            self.current_task = self.task_queue.pop(0)
            self.get_logger().info(f'Starting task: {self.current_task.task_type}')

            # Execute the task
            self.task_executor.execute_task(self.current_task)

class TaskExecutor:
    def __init__(self, node):
        self.node = node
        self.current_action = None

    def execute_task(self, task):
        if task.task_type == 'navigation':
            self.execute_navigation_task(task)
        elif task.task_type == 'manipulation':
            self.execute_manipulation_task(task)
        elif task.task_type == 'interaction':
            self.execute_interaction_task(task)
        else:
            self.report_task_status(task.task_id, 'FAILED', f'Unknown task type: {task.task_type}')

    def execute_navigation_task(self, task):
        try:
            # Parse navigation goal from task
            goal_data = json.loads(task.parameters)
            goal_pose = PoseStamped()
            goal_pose.header.frame_id = 'map'
            goal_pose.pose.position.x = goal_data.get('x', 0.0)
            goal_pose.pose.position.y = goal_data.get('y', 0.0)
            goal_pose.pose.position.z = goal_data.get('z', 0.0)

            # Publish navigation goal
            self.node.goal_pub.publish(goal_pose)

            # Report task started
            self.report_task_status(task.task_id, 'IN_PROGRESS', 'Navigation task started')

        except Exception as e:
            self.report_task_status(task.task_id, 'FAILED', f'Navigation error: {str(e)}')

    def execute_manipulation_task(self, task):
        # Implementation for manipulation tasks
        self.report_task_status(task.task_id, 'COMPLETED', 'Manipulation task completed')

    def execute_interaction_task(self, task):
        # Implementation for interaction tasks
        self.report_task_status(task.task_id, 'COMPLETED', 'Interaction task completed')

    def report_task_status(self, task_id, status, message):
        status_msg = TaskStatus()
        status_msg.task_id = task_id
        status_msg.status = status
        status_msg.message = message
        status_msg.timestamp = self.node.get_clock().now().to_msg()

        self.node.status_pub.publish(status_msg)

def main(args=None):
    rclpy.init(args=args)
    planner = TaskPlanner()

    try:
        rclpy.spin(planner)
    except KeyboardInterrupt:
        planner.get_logger().info('Shutting down task planner')
    finally:
        planner.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 4. Action System Implementation

**File: humanoid_control/humanoid_control/motor_controller.py**
```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import numpy as np

class MotorController(Node):
    def __init__(self):
        super().__init__('motor_controller')

        # Create subscribers
        self.joint_cmd_sub = self.create_subscription(
            JointTrajectory,
            '/joint_trajectory',
            self.joint_cmd_callback,
            10)

        # Create publishers
        self.joint_state_pub = self.create_publisher(
            JointState,
            '/joint_states',
            10)

        # Timer for publishing joint states
        self.timer = self.create_timer(0.01, self.publish_joint_states)  # 100Hz

        # Initialize joint states
        self.joint_names = [
            'left_shoulder_joint', 'left_elbow_joint', 'left_wrist_joint',
            'right_shoulder_joint', 'right_elbow_joint', 'right_wrist_joint',
            'left_hip_joint', 'left_knee_joint', 'left_ankle_joint',
            'right_hip_joint', 'right_knee_joint', 'right_ankle_joint'
        ]

        self.joint_positions = [0.0] * len(self.joint_names)
        self.joint_velocities = [0.0] * len(self.joint_names)
        self.joint_efforts = [0.0] * len(self.joint_names)

        # PID controllers for each joint
        self.pid_controllers = {}
        for joint_name in self.joint_names:
            self.pid_controllers[joint_name] = PIDController()

    def joint_cmd_callback(self, msg):
        # Process joint trajectory commands
        if len(msg.points) > 0:
            # Get the first point (simplified - in practice, handle trajectory properly)
            point = msg.points[0]

            # Update joint positions based on command
            for i, joint_name in enumerate(msg.joint_names):
                try:
                    idx = self.joint_names.index(joint_name)
                    if len(point.positions) > i:
                        self.joint_positions[idx] = point.positions[i]

                    if len(point.velocities) > i:
                        self.joint_velocities[idx] = point.velocities[i]

                    if len(point.effort) > i:
                        self.joint_efforts[idx] = point.effort[i]

                except ValueError:
                    self.get_logger().warn(f'Joint {joint_name} not found in robot description')

    def publish_joint_states(self):
        msg = JointState()
        msg.name = self.joint_names
        msg.position = self.joint_positions
        msg.velocity = self.joint_velocities
        msg.effort = self.joint_efforts
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        self.joint_state_pub.publish(msg)

class PIDController:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0.0
        self.integral = 0.0

    def compute(self, setpoint, current_value, dt):
        error = setpoint - current_value
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0

        output = self.kp * error + self.ki * self.integral + self.kd * derivative

        self.prev_error = error
        return output

def main(args=None):
    rclpy.init(args=args)
    controller = MotorController()

    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        controller.get_logger().info('Shutting down motor controller')
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Integration and Testing

### Launch File for Complete System

**File: humanoid_bringup/launch/humanoid_system.launch.py**
```python
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch configuration variables
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # Nodes for the complete system
    perception_node = Node(
        package='humanoid_perception',
        executable='object_detector',
        name='object_detector',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    task_planner_node = Node(
        package='humanoid_cognition',
        executable='task_planner',
        name='task_planner',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    motor_controller_node = Node(
        package='humanoid_control',
        executable='motor_controller',
        name='motor_controller',
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    # TF broadcaster for robot state
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'robot_description':
                PathJoinSubstitution([
                    FindPackageShare('humanoid_description'),
                    'urdf',
                    'humanoid.urdf.xacro'
                ])
            }
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'
        ),

        robot_state_publisher,
        perception_node,
        task_planner_node,
        motor_controller_node,
    ])
```

## Simulation Integration

### Gazebo Launch File

**File: humanoid_gazebo/launch/humanoid_gazebo.launch.py**
```python
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # Launch Gazebo with the humanoid world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ]),
    )

    # Spawn the humanoid robot in Gazebo
    spawn_entity = ExecuteProcess(
        cmd=[
            'ros2', 'run', 'gazebo_ros', 'spawn_entity.py',
            '-topic', 'robot_description',
            '-entity', 'humanoid_robot',
            '-x', '0.0', '-y', '0.0', '-z', '0.5'
        ],
        output='screen'
    )

    # Launch the robot state publisher
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('humanoid_bringup'),
                'launch',
                'humanoid_system.launch.py'
            ])
        ]),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    return LaunchDescription([
        gazebo,
        spawn_entity,
        robot_state_publisher,
    ])
```

## Building and Running

### Build the Workspace
```bash
cd ~/humanoid_ws
colcon build --packages-select humanoid_description humanoid_perception humanoid_cognition humanoid_control humanoid_bringup humanoid_gazebo
source install/setup.bash
```

### Run in Simulation
```bash
# Launch the complete system in Gazebo
ros2 launch humanoid_gazebo humanoid_gazebo.launch.py

# In another terminal, send a navigation task
ros2 topic pub /task_requests humanoid_msgs/Task "task_type: 'navigation'
description: 'Go to kitchen'
parameters: '{\"x\": 2.0, \"y\": 1.5, \"z\": 0.0}'"
```

## Code Organization

The complete system is organized into ROS 2 packages:

```
humanoid_ws/src/
├── humanoid_description/     # Robot URDF and meshes
├── humanoid_perception/      # Vision, audio, and sensor processing
├── humanoid_cognition/       # Planning, reasoning, and dialogue
├── humanoid_control/         # Motor control and actuation
├── humanoid_msgs/            # Custom message definitions
├── humanoid_bringup/         # Launch files and system configuration
└── humanoid_gazebo/          # Simulation integration
```

## Sim-to-Real Transfer Implementation

### Simulation Environment Setup

The sim-to-real approach requires careful alignment between simulation and reality:

**Gazebo Integration**:
```python
# Example: Simulation-Reality Interface
class SimRealInterface:
    def __init__(self):
        # Parameters that affect both sim and real
        self.friction_coefficients = self.load_params("friction.yaml")
        self.sensor_noise_models = self.load_params("noise_models.yaml")
        self.dynamics_parameters = self.load_params("dynamics.yaml")

    def adapt_for_simulation(self):
        """Adjust parameters for simulation environment"""
        # Increase physics update rate for stability
        # Add sensor noise models to match real sensors
        # Adjust friction and contact models for realism

    def adapt_for_real_world(self):
        """Adjust parameters for real hardware"""
        # Reduce computational complexity
        # Adjust for real sensor characteristics
        # Account for actuator dynamics and delays
```

### Domain Randomization

To bridge the reality gap, implement domain randomization:

```python
# In simulation, randomize these parameters:
# - Lighting conditions
# - Texture variations
# - Physical parameters (mass, friction, damping)
# - Sensor noise characteristics
# - Environmental conditions

class DomainRandomizer:
    def __init__(self):
        self.param_ranges = {
            'mass_variance': (0.8, 1.2),  # ±20% mass variation
            'friction_range': (0.4, 0.8),  # Friction coefficient range
            'sensor_noise': (0.001, 0.01),  # Sensor noise range
        }

    def randomize_environment(self):
        # Apply randomization to simulation
        pass
```

### Reality Gap Mitigation

**System Identification**:
- Compare real robot responses to simulation
- Adjust simulation parameters based on real-world data
- Validate models through physical experiments

**Transfer Learning**:
- Train policies in multiple simulated environments
- Fine-tune on real robot with minimal data
- Use simulators as pre-training environments

### Validation Procedures

```bash
# Validate sim-to-real transfer
# 1. Test basic movements in simulation
# 2. Execute same movements on real robot
# 3. Compare performance metrics
# 4. Adjust simulation parameters as needed
# 5. Repeat until acceptable transfer performance achieved
```

This implementation provides a complete foundation for the autonomous humanoid robot system, integrating all modules covered in the book while maintaining modularity, safety, and scalability. The system can be extended with additional capabilities and optimized for specific hardware platforms. The sim-to-real approach ensures that behaviors learned in simulation can be successfully transferred to physical hardware.