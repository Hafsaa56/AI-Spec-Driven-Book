---
sidebar_position: 2
---

# ROS 2: The Nervous System of Robotics

## Introduction

The Robot Operating System 2 (ROS 2) serves as the nervous system of modern robotics, providing a communication framework that enables different software components to interact seamlessly. Just as the biological nervous system coordinates sensing, processing, and actuation in living organisms, ROS 2 coordinates these functions in robotic systems.

## Architecture Overview

ROS 2 is built on Data Distribution Service (DDS), a middleware standard for real-time systems. This architecture provides:

- **Decentralized Communication**: No single point of failure
- **Real-time Performance**: Deterministic behavior for time-critical applications
- **Language Independence**: Support for multiple programming languages
- **Platform Portability**: Runs on various operating systems and hardware

### Core Components

1. **Nodes**: Independent processes that perform computation
2. **Topics**: Unidirectional data streams between nodes
3. **Services**: Bidirectional request-response communication
4. **Actions**: Goal-oriented communication with feedback
5. **Parameters**: Configuration values accessible to nodes
6. **Launch Files**: Configuration for starting multiple nodes

## Communication Patterns

### Topics (Publish/Subscribe)

Topics enable asynchronous, one-to-many communication:

```python
# Publisher example
import rclpy
from std_msgs.msg import String

class Talker(rclpy.node.Node):
    def __init__(self):
        super().__init__('talker')
        self.publisher = self.create_publisher(String, 'chatter', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.get_clock().now().nanoseconds
        self.publisher.publish(msg)
```

```python
# Subscriber example
import rclpy
from std_msgs.msg import String

class Listener(rclpy.node.Node):
    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info('I heard: "%s"' % msg.data)
```

### Services (Request/Response)

Services provide synchronous, two-way communication:

```python
# Service server
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(AddTwoInts, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))
        return response
```

```python
# Service client
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class MinimalClient(Node):
    def __init__(self):
        super().__init__('minimal_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')

    def send_request(self, a, b):
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')

        request = AddTwoInts.Request()
        request.a = a
        request.b = b
        self.future = self.cli.call_async(request)
```

### Actions (Goal-Oriented Communication)

Actions handle long-running tasks with feedback:

```python
# Action server
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci

class FibonacciActionServer(Node):
    def __init__(self):
        super().__init__('fibonacci_action_server')
        self._action_server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        feedback_msg = Fibonacci.Feedback()
        feedback_msg.sequence = [0, 1]

        for i in range(1, goal_handle.request.order):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal canceled')
                return Fibonacci.Result()

            feedback_msg.sequence.append(
                feedback_msg.sequence[i] + feedback_msg.sequence[i-1])

            goal_handle.publish_feedback(feedback_msg)

        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = feedback_msg.sequence
        return result
```

## Quality of Service (QoS) Settings

ROS 2 provides Quality of Service settings to handle different communication requirements:

```python
from rclpy.qos import QoSProfile, QoSDurabilityPolicy, QoSHistoryPolicy, QoSReliabilityPolicy

# For real-time critical data
qos_profile = QoSProfile(
    depth=10,
    durability=QoSDurabilityPolicy.VOLATILE,
    history=QoSHistoryPolicy.KEEP_LAST,
    reliability=QoSReliabilityPolicy.RELIABLE
)

publisher = node.create_publisher(String, 'topic', qos_profile)
```

## Launch Systems

Launch files coordinate multiple nodes:

```python
# launch/example.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='demo_nodes_cpp',
            executable='talker',
            name='talker',
        ),
        Node(
            package='demo_nodes_cpp',
            executable='listener',
            name='listener',
        ),
    ])
```

## Parameter Management

Parameters allow runtime configuration:

```python
# Parameter declaration and usage
class ParameterNode(Node):
    def __init__(self):
        super().__init__('parameter_node')

        # Declare parameters with defaults
        self.declare_parameter('frame_id', 'base_link')
        self.declare_parameter('publish_rate', 10)

        # Access parameters
        self.frame_id = self.get_parameter('frame_id').value
        self.rate = self.get_parameter('publish_rate').value
```

## Real-time Considerations

ROS 2 supports real-time applications with:

- **Real-time scheduling**: Use SCHED_FIFO for time-critical nodes
- **Memory pre-allocation**: Avoid dynamic allocation during real-time operation
- **Deterministic communication**: Configure QoS for predictable behavior

```bash
# Running with real-time priority
chrt -f 95 ros2 run package executable
```

## Best Practices

1. **Node Design**: Keep nodes focused on single responsibilities
2. **Topic Naming**: Use descriptive, consistent naming conventions
3. **Error Handling**: Implement robust error handling and recovery
4. **Resource Management**: Properly manage memory and system resources
5. **Testing**: Write comprehensive tests for all components

## Debugging and Profiling

ROS 2 provides tools for debugging and profiling:

```bash
# Monitor topics
ros2 topic echo /topic_name

# Monitor services
ros2 service list

# Visualize the node graph
rqt_graph

# Monitor parameters
ros2 param list
```

## Integration with Physical AI

ROS 2's architecture aligns perfectly with Physical AI principles:

- **Embodiment**: ROS 2 nodes can represent physical components
- **Real-time Operation**: Built-in support for time-critical applications
- **Distributed Intelligence**: Nodes can run on different hardware
- **Sensorimotor Coupling**: Topics enable sensor-actuator loops

The next section will explore practical exercises to reinforce these concepts.