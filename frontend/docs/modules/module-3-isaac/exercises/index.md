---
sidebar_position: 4
---

# Module 3 Exercises: NVIDIA Isaac Platform

## Exercise 1: Setting Up Isaac Sim Environment

### Objective
Learn to create and configure a basic simulation environment in Isaac Sim.

### Prerequisites
- NVIDIA GPU with RTX technology
- Isaac Sim installed
- Understanding of USD (Universal Scene Description)

### Steps
1. Launch Isaac Sim
2. Create a new stage
3. Add a simple environment (e.g., simple room)
4. Add a sample robot (e.g., UR5e manipulator)
5. Configure the robot's initial position
6. Run the simulation and verify the robot appears correctly

### Expected Outcome
A basic simulation environment with a robot that can be controlled and observed.

### Code Template
```python
# Import required modules
from omni.isaac.core import World
from omni.isaac.core.utils.stage import add_reference_to_stage
from omni.isaac.core.utils.nucleus import get_assets_root_path
import numpy as np

# Initialize the world
world = World(stage_units_in_meters=1.0)

# Get assets root path
assets_root_path = get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets. Ensure Isaac Sim is properly installed.")

# Add environment and robot to the stage
# [Your code here to add environment and robot]

# Reset the world to apply changes
world.reset()

# Run the simulation
for i in range(1000):
    world.step(render=True)

# Cleanup
world.clear()
```

### Questions
1. What is the purpose of the `stage_units_in_meters` parameter?
2. How does Isaac Sim handle different coordinate systems?
3. What are the advantages of using USD for robotics simulation?

## Exercise 2: Domain Randomization Implementation

### Objective
Implement domain randomization techniques to improve sim-to-real transfer.

### Prerequisites
- Basic understanding of Isaac Sim scene setup
- Knowledge of Python and numpy

### Steps
1. Create a scene with multiple objects
2. Implement visual domain randomization (colors, textures, lighting)
3. Implement physical domain randomization (friction, mass)
4. Collect data from the randomized environment
5. Compare performance with and without domain randomization

### Expected Outcome
A simulation environment that systematically randomizes visual and physical properties to improve model robustness.

### Code Template
```python
import numpy as np
from omni.isaac.core.objects import VisualCuboid
from omni.isaac.core.materials import PhysicsMaterial

class DomainRandomizer:
    def __init__(self, world):
        self.world = world
        self.objects = []

    def add_random_objects(self, count=10):
        """Add objects with randomized properties"""
        for i in range(count):
            # Random color
            color = np.random.rand(3)

            # Random size
            size = np.random.uniform(0.05, 0.2, 3)

            # Random position
            position = np.random.uniform(-1.0, 1.0, 3)
            position[2] = 0.5  # Set z to appropriate height

            # Create object
            obj = VisualCuboid(
                prim_path=f"/World/Cube_{i}",
                name=f"cube_{i}",
                position=position,
                size=size,
                color=color
            )
            self.objects.append(obj)

    def randomize_physics_properties(self):
        """Randomize physics properties of objects"""
        for i, obj in enumerate(self.objects):
            # Create physics material with randomized friction
            material_path = f"/World/Materials/Material_{i}"
            physics_material = PhysicsMaterial(
                prim_path=material_path,
                static_friction=np.random.uniform(0.1, 1.0),
                dynamic_friction=np.random.uniform(0.1, 1.0),
                restitution=np.random.uniform(0.0, 0.5)
            )

# Initialize randomizer and add objects
randomizer = DomainRandomizer(world)
randomizer.add_random_objects(5)
randomizer.randomize_physics_properties()
```

### Questions
1. How does domain randomization help with sim-to-real transfer?
2. What are the potential downsides of excessive domain randomization?
3. How would you measure the effectiveness of domain randomization?

## Exercise 3: Isaac ROS Perception Pipeline

### Objective
Build and test a GPU-accelerated perception pipeline using Isaac ROS packages.

### Prerequisites
- ROS 2 Humble installed
- Isaac ROS packages installed
- Basic ROS 2 knowledge (topics, nodes, launch files)

### Steps
1. Create a ROS 2 workspace for Isaac ROS
2. Set up a stereo camera simulation in Isaac Sim
3. Configure Isaac ROS stereo disparity node
4. Launch the perception pipeline
5. Visualize the output using RViz
6. Verify GPU acceleration is working

### Expected Outcome
A functional perception pipeline that processes stereo images and generates disparity maps using GPU acceleration.

### Launch File Template
```xml
<launch>
  <!-- Arguments -->
  <arg name="use_sim_time" default="false"/>
  <arg name="camera_namespace" default="/camera"/>

  <!-- Stereo camera parameters -->
  <arg name="left_topic" default="$(var camera_namespace)/left/image_rect_color"/>
  <arg name="right_topic" default="$(var camera_namespace)/right/image_rect_color"/>
  <arg name="left_camera_info_topic" default="$(var camera_namespace)/left/camera_info"/>
  <arg name="right_camera_info_topic" default="$(var camera_namespace)/right/camera_info"/>

  <!-- Stereo disparity node -->
  <node pkg="isaac_ros_stereo_image_proc"
        exec="isaac_ros_stereo_disparity_node"
        name="stereo_disparity"
        output="screen">
    <param name="use_sim_time" value="$(var use_sim_time)"/>
    <param name="approximate_sync" value="true"/>
    <param name="disparity_range" value="64"/>
  </node>

  <!-- Point cloud from disparity -->
  <node pkg="isaac_ros_stereo_image_proc"
        exec="isaac_ros_point_cloud_node"
        name="point_cloud"
        output="screen">
    <param name="use_sim_time" value="$(var use_sim_time)"/>
  </node>
</launch>
```

### Commands to Test
```bash
# Build the workspace
cd ~/isaac_ros_ws
colcon build --packages-select isaac_ros_stereo_image_proc

# Source the workspace
source install/setup.bash

# Launch the perception pipeline
ros2 launch your_package stereo_perception.launch.py

# Check topics
ros2 topic list | grep -E "(disparity|points)"

# Monitor GPU usage
nvidia-smi -l 1
```

### Questions
1. What is the difference between stereo disparity and depth images?
2. How does GPU acceleration improve perception pipeline performance?
3. What are the Quality of Service (QoS) considerations for perception topics?

## Exercise 4: Isaac ROS Object Detection

### Objective
Implement GPU-accelerated object detection using Isaac ROS detectnet package.

### Prerequisites
- Isaac ROS detectnet package installed
- Pre-trained model (e.g., SSD MobileNet or YOLO)
- Understanding of ROS 2 message types (sensor_msgs, vision_msgs)

### Steps
1. Download a pre-trained model compatible with TensorRT
2. Configure the detectnet node with the model
3. Connect to a camera source (simulated or real)
4. Visualize detections in RViz
5. Benchmark performance with and without GPU acceleration

### Expected Outcome
A real-time object detection system running on GPU with improved performance compared to CPU-only processing.

### Code Template
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray
from cv_bridge import CvBridge

class ObjectDetectionMonitor(Node):
    def __init__(self):
        super().__init__('object_detection_monitor')

        # Create subscriber for detections
        self.detection_sub = self.create_subscription(
            Detection2DArray,
            '/detectnet/detections',
            self.detection_callback,
            10
        )

        # Create publisher for annotated images (optional)
        self.annotated_pub = self.create_publisher(
            Image,
            '/detectnet/annotated_image',
            10
        )

        self.cv_bridge = CvBridge()
        self.detection_count = 0

    def detection_callback(self, msg):
        """Process incoming detections"""
        self.detection_count += len(msg.detections)
        self.get_logger().info(f'Detected {len(msg.detections)} objects')

        # Print detection details
        for i, detection in enumerate(msg.detections):
            bbox = detection.bbox
            self.get_logger().info(
                f'  Object {i+1}: '
                f'Class: {detection.results[0].id}, '
                f'Confidence: {detection.results[0].score:.2f}, '
                f'BBox: ({bbox.center.x}, {bbox.center.y}) '
                f'Size: ({bbox.size_x}, {bbox.size_y})'
            )

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetectionMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down object detection monitor')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Commands to Test Performance
```bash
# Monitor GPU utilization
nvidia-smi dmon -s u -d 1

# Monitor ROS 2 topics
ros2 topic hz /detectnet/detections

# Check for dropped messages
ros2 topic echo /detectnet/detections --field header.stamp | ts
```

### Questions
1. How does TensorRT optimize neural networks for inference?
2. What are the trade-offs between different object detection models?
3. How can you optimize the inference pipeline for real-time performance?

## Exercise 5: Isaac ROS Manipulation Pipeline

### Objective
Create a GPU-accelerated grasp planning pipeline using Isaac ROS manipulation packages.

### Prerequisites
- Isaac ROS manipulation packages installed
- Point cloud source (simulated or real)
- Understanding of ROS 2 actions and services

### Steps
1. Set up a point cloud processing pipeline
2. Configure Isaac ROS manipulation nodes
3. Implement grasp candidate generation
4. Test with simulated objects
5. Evaluate grasp success rate

### Expected Outcome
A functional grasp planning system that can identify potential grasp points on objects using GPU acceleration.

### Code Template
```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
import numpy as np

class GraspPlannerTester(Node):
    def __init__(self):
        super().__init__('grasp_planner_tester')

        # Create subscriber for grasp candidates
        self.grasps_sub = self.create_subscription(
            PoseArray,
            '/grasp_planner/grasp_candidates',
            self.grasps_callback,
            10
        )

        # Create publisher for test point cloud (if needed)
        self.pc_pub = self.create_publisher(
            PointCloud2,
            '/test_point_cloud',
            10
        )

        self.grasp_count = 0

    def grasps_callback(self, msg):
        """Process incoming grasp candidates"""
        self.grasp_count += len(msg.poses)
        self.get_logger().info(f'Received {len(msg.poses)} grasp candidates')

        # Print grasp details
        for i, pose in enumerate(msg.poses):
            self.get_logger().info(
                f'  Grasp {i+1}: '
                f'Position: ({pose.position.x:.2f}, {pose.position.y:.2f}, {pose.position.z:.2f})'
            )

def main(args=None):
    rclpy.init(args=args)
    node = GraspPlannerTester()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down grasp planner tester')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Commands to Test
```bash
# Launch manipulation pipeline
ros2 launch isaac_ros_manipulation_bringup manipulation.launch.py

# Visualize grasps in RViz
ros2 run rviz2 rviz2

# Test with example objects
ros2 run isaac_ros_test_objects spawn_test_objects
```

### Questions
1. What are the key components of a grasp planning pipeline?
2. How does GPU acceleration benefit manipulation algorithms?
3. What are the challenges in real-world grasp execution?

## Exercise 6: Isaac Sim to Isaac ROS Integration

### Objective
Connect Isaac Sim with Isaac ROS to create a complete simulation-to-perception pipeline.

### Prerequisites
- Both Isaac Sim and Isaac ROS installed
- Understanding of ROS 2 bridges
- Experience with both simulation and perception

### Steps
1. Launch Isaac Sim with ROS bridge enabled
2. Configure camera parameters in simulation
3. Set up Isaac ROS perception nodes
4. Verify data flow from simulation to ROS
5. Test end-to-end perception pipeline

### Expected Outcome
A complete pipeline from simulated sensors through Isaac ROS perception nodes with validated data flow.

### Commands to Test Integration
```bash
# Terminal 1: Launch Isaac Sim with ROS bridge
isaac-sim --enable-ros2-bridge

# Terminal 2: Launch perception pipeline
cd ~/isaac_ros_ws
source install/setup.bash
ros2 launch your_package simulation_perception.launch.py

# Terminal 3: Monitor topics
source /opt/ros/humble/setup.bash
ros2 topic list | grep -E "(camera|image|detection)"

# Terminal 4: Visualize in RViz
source /opt/ros/humble/setup.bash
source install/setup.bash
rviz2
```

### Questions
1. What are the challenges in connecting simulation to ROS?
2. How do you ensure timing consistency between simulation and ROS?
3. What validation techniques can be used to verify the integration?

## Summary

These exercises provide hands-on experience with the NVIDIA Isaac platform, covering simulation, perception, and manipulation aspects. Each exercise builds on the previous ones, creating a comprehensive understanding of how to develop and deploy GPU-accelerated robotics applications using Isaac Sim and Isaac ROS.