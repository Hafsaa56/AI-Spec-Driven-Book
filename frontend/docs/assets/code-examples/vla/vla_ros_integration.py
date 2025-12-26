#!/usr/bin/env python3
"""
Vision-Language-Action ROS 2 Integration

This script demonstrates how to integrate a VLA model with ROS 2.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from vision_msgs.msg import Detection2DArray
from cv_bridge import CvBridge
import torch
import numpy as np


class VLAROSNode(Node):
    """
    ROS 2 node for Vision-Language-Action system
    """
    def __init__(self):
        super().__init__('vla_ros_node')

        # Initialize CV bridge
        self.cv_bridge = CvBridge()

        # Load pre-trained VLA model
        self.vla_model = self.load_vla_model()
        self.vla_model.eval()  # Set to evaluation mode

        # Create subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )

        self.command_sub = self.create_subscription(
            String, '/vla/command', self.command_callback, 10
        )

        self.detection_sub = self.create_subscription(
            Detection2DArray, '/object_detections', self.detection_callback, 10
        )

        # Create publishers
        self.action_pub = self.create_publisher(Pose, '/vla/action', 10)
        self.status_pub = self.create_publisher(String, '/vla/status', 10)

        # Store latest data
        self.latest_image = None
        self.latest_detections = None
        self.pending_command = None

        # Timer for processing pipeline
        self.process_timer = self.create_timer(0.1, self.process_vla_pipeline)

        self.get_logger().info('VLA ROS Node initialized')

    def load_vla_model(self):
        """
        Load pre-trained VLA model
        In practice, this would load a saved model
        """
        # For demonstration, we'll create a simple model
        # In real implementation, load from checkpoint
        try:
            # Import the VLA model from our basic implementation
            from basic_vla_model import VisionLanguageActionModel
            model = VisionLanguageActionModel()

            # Check if we have a saved model
            try:
                # This would load a pre-trained model in practice
                # model.load_state_dict(torch.load('vla_model.pth'))
                self.get_logger().info('Pre-trained VLA model loaded')
            except:
                self.get_logger().info('Using randomly initialized VLA model')

            # Move model to GPU if available
            if torch.cuda.is_available():
                model = model.cuda()
                self.get_logger().info('VLA model moved to GPU')

            return model
        except ImportError:
            self.get_logger().warn('Basic VLA model not found, using mock model')
            return MockVLAModel()

    def image_callback(self, msg):
        """
        Handle incoming camera images
        """
        try:
            # Convert ROS image to OpenCV
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, 'bgr8')

            # Preprocess image for VLA model
            self.latest_image = self.preprocess_image(cv_image)

            self.get_logger().info('Received and processed new image')

        except Exception as e:
            self.get_logger().error(f'Error processing image: {str(e)}')

    def command_callback(self, msg):
        """
        Handle incoming natural language commands
        """
        self.pending_command = msg.data
        self.get_logger().info(f'Received command: {msg.data}')

    def detection_callback(self, msg):
        """
        Handle incoming object detections
        """
        self.latest_detections = msg
        self.get_logger().info(f'Received {len(msg.detections)} detections')

    def preprocess_image(self, cv_image):
        """
        Preprocess image for VLA model
        """
        import cv2

        # Resize image to expected input size (224x224 for our model)
        resized = cv2.resize(cv_image, (224, 224))

        # Convert to tensor and normalize
        tensor_image = torch.from_numpy(resized).float()
        tensor_image = tensor_image.permute(2, 0, 1)  # HWC to CHW
        tensor_image = tensor_image.unsqueeze(0)  # Add batch dimension
        tensor_image = tensor_image / 255.0  # Normalize to [0, 1]

        # Move to GPU if available
        if torch.cuda.is_available():
            tensor_image = tensor_image.cuda()

        return tensor_image

    def process_vla_pipeline(self):
        """
        Process VLA pipeline when both image and command are available
        """
        if (self.latest_image is not None and
            self.pending_command is not None):

            try:
                # Generate action using VLA model
                action = self.generate_action()

                if action is not None:
                    # Convert action to ROS Pose message
                    pose_msg = self.action_to_pose(action)

                    # Publish action
                    self.action_pub.publish(pose_msg)

                    # Publish status
                    status_msg = String()
                    status_msg.data = f'Executed command: {self.pending_command}'
                    self.status_pub.publish(status_msg)

                    self.get_logger().info(f'Action published for command: {self.pending_command}')

                    # Clear pending command
                    self.pending_command = None

            except Exception as e:
                self.get_logger().error(f'Error in VLA pipeline: {str(e)}')

    def generate_action(self):
        """
        Generate action using the VLA model
        """
        if torch.cuda.is_available():
            # Move command to GPU context if needed
            command_input = [self.pending_command]
        else:
            command_input = [self.pending_command]

        try:
            with torch.no_grad():
                # Generate action
                action_output = self.vla_model(self.latest_image, command_input)

                # Convert to CPU for ROS message creation
                action_cpu = action_output.cpu()

                return action_cpu

        except Exception as e:
            self.get_logger().error(f'Error generating action: {str(e)}')
            return None

    def action_to_pose(self, action_tensor):
        """
        Convert VLA action output to ROS Pose message
        """
        # Extract action values (assuming 6-dof action: x, y, z, rx, ry, rz)
        action_values = action_tensor[0].tolist()  # Remove batch dimension

        pose = Pose()

        # Map action values to pose components
        # This is a simplified mapping - in practice, this would be more complex
        if len(action_values) >= 6:
            pose.position.x = float(action_values[0])
            pose.position.y = float(action_values[1])
            pose.position.z = float(action_values[2])

            # For orientation, we'll use a simplified approach
            # In practice, you might use quaternions or convert Euler angles
            pose.orientation.x = float(action_values[3])
            pose.orientation.y = float(action_values[4])
            pose.orientation.z = float(action_values[5])
            pose.orientation.w = 1.0  # Default quaternion scalar
        else:
            # Default pose if action vector is too short
            pose.position.x = 0.0
            pose.position.y = 0.0
            pose.position.z = 0.0
            pose.orientation.w = 1.0

        return pose


class MockVLAModel(torch.nn.Module):
    """
    Mock VLA model for demonstration when the real model is not available
    """
    def __init__(self):
        super().__init__()

    def forward(self, images, text_commands):
        """
        Generate mock action based on command
        """
        batch_size = images.shape[0]

        # Generate mock actions based on text commands
        actions = []
        for command in text_commands:
            if 'pick' in command.lower() or 'grasp' in command.lower():
                # Action for picking/grasping
                action = torch.tensor([0.1, 0.0, -0.1, 0.0, 0.0, 0.0])  # Move down
            elif 'move' in command.lower() or 'go' in command.lower():
                # Action for moving
                action = torch.tensor([0.2, 0.0, 0.0, 0.0, 0.0, 0.0])   # Move forward
            elif 'lift' in command.lower():
                # Action for lifting
                action = torch.tensor([0.0, 0.0, 0.1, 0.0, 0.0, 0.0])   # Move up
            else:
                # Default action
                action = torch.tensor([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])   # No movement

            actions.append(action)

        # Stack actions and expand batch size
        actions_tensor = torch.stack(actions)
        if batch_size > 1:
            actions_tensor = actions_tensor.expand(batch_size, -1)

        return actions_tensor

    def predict_action(self, image, command):
        """
        Convenience method for single prediction
        """
        return self.forward(image.unsqueeze(0), [command])[0]


def main(args=None):
    """
    Main function to run the VLA ROS node
    """
    rclpy.init(args=args)

    node = VLAROSNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down VLA ROS Node')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()