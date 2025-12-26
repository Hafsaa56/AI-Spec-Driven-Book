# Basic Publisher-Subscriber Exercise

## Objective

Implement a simple publisher-subscriber pair in ROS 2 to understand the fundamental communication pattern.

## Prerequisites

- ROS 2 Humble Hawksbill installed
- Basic Python knowledge
- Terminal/command line proficiency

## Exercise Steps

### 1. Create a New Package

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python basic_pubsub --dependencies rclpy std_msgs
cd basic_pubsub
```

### 2. Create the Publisher Node

Create `basic_pubsub/basic_pubsub/talker.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.publisher = self.create_publisher(String, 'chatter', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)
    talker = Talker()

    try:
        rclpy.spin(talker)
    except KeyboardInterrupt:
        pass
    finally:
        talker.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 3. Create the Subscriber Node

Create `basic_pubsub/basic_pubsub/listener.py`:

```python
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.subscription = self.create_subscription(
            String,
            'chatter',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    listener = Listener()

    try:
        rclpy.spin(listener)
    except KeyboardInterrupt:
        pass
    finally:
        listener.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### 4. Update setup.py

Modify `basic_pubsub/setup.py` to include the executables:

```python
import os
from glob import glob
from setuptools import setup
from setuptools import find_packages

package_name = 'basic_pubsub'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Basic publisher subscriber example',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = basic_pubsub.talker:main',
            'listener = basic_pubsub.listener:main',
        ],
    },
)
```

### 5. Build and Run

```bash
cd ~/ros2_ws
colcon build --packages-select basic_pubsub
source install/setup.bash

# In separate terminals:
ros2 run basic_pubsub talker
ros2 run basic_pubsub listener
```

## Expected Output

The talker node should publish messages every 0.5 seconds, and the listener node should receive and display them:

```
[INFO] [1620000000.000000000] [talker]: Publishing: "Hello World: 0"
[INFO] [1620000000.000000000] [listener]: I heard: "Hello World: 0"
[INFO] [1620000000.500000000] [talker]: Publishing: "Hello World: 1"
[INFO] [1620000000.500000000] [listener]: I heard: "Hello World: 1"
```

## Troubleshooting

1. **Package not found**: Ensure you sourced the setup file after building
2. **Permission denied**: Make sure your Python files have execute permissions
3. **No communication**: Check that both nodes are using the same topic name

## Extensions

1. Modify the message content to include timestamps
2. Add a parameter to control the publishing rate
3. Create multiple publishers with different message content
4. Add QoS settings to the publisher and subscriber

## Learning Outcomes

After completing this exercise, you should understand:
- How to create a basic ROS 2 package
- The publisher-subscriber communication pattern
- How to create and run ROS 2 nodes
- Basic ROS 2 project structure and build process