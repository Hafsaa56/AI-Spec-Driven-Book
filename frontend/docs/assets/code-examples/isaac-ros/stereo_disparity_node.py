#!/usr/bin/env python3
"""
Isaac ROS Stereo Disparity Node

This script demonstrates a GPU-accelerated stereo disparity processing node using Isaac ROS.
"""

import rclpy
from rclpy.node import Node
from stereo_msgs.msg import DisparityImage
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import numpy as np
import cv2
from message_filters import ApproximateTimeSynchronizer, Subscriber
import torch
import torch.nn as nn


class IsaacROSDisparityNode(Node):
    """
    A GPU-accelerated stereo disparity processing node
    """
    def __init__(self):
        super().__init__('isaac_ros_disparity_node')

        # Create subscribers for left and right camera images
        self.left_sub = Subscriber(self, Image, '/camera/left/image_rect_color')
        self.right_sub = Subscriber(self, Image, '/camera/right/image_rect_color')

        # Create subscriber for camera info
        self.left_info_sub = self.create_subscription(
            CameraInfo, '/camera/left/camera_info', self.left_info_callback, 10
        )
        self.right_info_sub = self.create_subscription(
            CameraInfo, '/camera/right/camera_info', self.right_info_callback, 10
        )

        # Create publisher for disparity image
        self.disparity_pub = self.create_publisher(
            DisparityImage, '/stereo/disparity', 10
        )

        # Initialize CV bridge
        self.cv_bridge = CvBridge()

        # Initialize stereo matcher (using OpenCV's StereoBM as example)
        self.stereo_matcher = cv2.StereoBM_create(numDisparities=64, blockSize=15)

        # Store camera parameters
        self.left_camera_info = None
        self.right_camera_info = None

        # Synchronize left and right images
        self.ts = ApproximateTimeSynchronizer(
            [self.left_sub, self.right_sub], queue_size=10, slop=0.1
        )
        self.ts.registerCallback(self.stereo_callback)

        self.get_logger().info('Isaac ROS Disparity Node initialized')

    def left_info_callback(self, msg):
        """Handle left camera info"""
        self.left_camera_info = msg

    def right_info_callback(self, msg):
        """Handle right camera info"""
        self.right_camera_info = msg

    def stereo_callback(self, left_msg, right_msg):
        """Process synchronized stereo pair"""
        try:
            # Convert ROS images to OpenCV
            left_cv = self.cv_bridge.imgmsg_to_cv2(left_msg, 'bgr8')
            right_cv = self.cv_bridge.imgmsg_to_cv2(right_msg, 'bgr8')

            # Convert to grayscale for stereo processing
            left_gray = cv2.cvtColor(left_cv, cv2.COLOR_BGR2GRAY)
            right_gray = cv2.cvtColor(right_cv, cv2.COLOR_BGR2GRAY)

            # Compute disparity using GPU-accelerated method (simulated here)
            # In a real Isaac ROS implementation, this would use CUDA
            disparity = self.compute_disparity_gpu(left_gray, right_gray)

            # Create disparity message
            disp_msg = DisparityImage()
            disp_msg.image = self.cv_bridge.cv2_to_imgmsg(disparity, '32FC1')
            disp_msg.image.header = left_msg.header
            disp_msg.header = left_msg.header

            # Set disparity parameters based on camera info if available
            if self.left_camera_info and self.right_camera_info:
                # Calculate baseline * focal length
                # This is simplified - in practice, you'd extract from stereo calibration
                disp_msg.T = 0.1  # Baseline (meters) - should come from calibration
                disp_msg.f = self.left_camera_info.k[0]  # Focal length in x
                disp_msg.min_disparity = 0.0
                disp_msg.max_disparity = 64.0
                disp_msg.delta_d = 1.0

            # Publish disparity image
            self.disparity_pub.publish(disp_msg)

            self.get_logger().info(f'Disparity computed and published')

        except Exception as e:
            self.get_logger().error(f'Error in stereo callback: {str(e)}')

    def compute_disparity_gpu(self, left_img, right_img):
        """
        Compute disparity using GPU-accelerated method
        In a real Isaac ROS implementation, this would use CUDA
        """
        # For demonstration, using OpenCV's CPU implementation
        # In Isaac ROS, this would use GPU-accelerated algorithms
        disparity = self.stereo_matcher.compute(left_img, right_img)

        # Convert to float32 and normalize
        disparity = disparity.astype(np.float32) / 16.0  # OpenCV returns 16x disparity

        return disparity


def main(args=None):
    """
    Main function to run the Isaac ROS disparity node
    """
    rclpy.init(args=args)

    node = IsaacROSDisparityNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down Isaac ROS Disparity Node')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()