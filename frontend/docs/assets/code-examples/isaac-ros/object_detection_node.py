#!/usr/bin/env python3
"""
Isaac ROS Object Detection Node

This script demonstrates GPU-accelerated object detection using Isaac ROS.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from cv_bridge import CvBridge
import numpy as np
import cv2
import torch
import torchvision.transforms as T
from std_msgs.msg import Header


class IsaacROSObjectDetectionNode(Node):
    """
    A GPU-accelerated object detection node using Isaac ROS principles
    """
    def __init__(self):
        super().__init__('isaac_ros_object_detection_node')

        # Create subscriber for camera image
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )

        # Create publisher for detections
        self.detections_pub = self.create_publisher(
            Detection2DArray, '/isaac_ros/detections', 10
        )

        # Initialize CV bridge
        self.cv_bridge = CvBridge()

        # Load a pre-trained model (using torchvision's model as example)
        # In a real Isaac ROS implementation, this would use TensorRT-optimized models
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        self.model.eval()

        # Move model to GPU if available
        if torch.cuda.is_available():
            self.model = self.model.cuda()
            self.get_logger().info('Using GPU for object detection')
        else:
            self.get_logger().info('Using CPU for object detection')

        # COCO dataset class names
        self.coco_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
            'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',
            'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella',
            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',
            'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard',
            'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork',
            'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',
            'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv',
            'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
            'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
            'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]

        self.get_logger().info('Isaac ROS Object Detection Node initialized')

    def image_callback(self, msg):
        """
        Process incoming image and detect objects
        """
        try:
            # Convert ROS image to OpenCV
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, 'bgr8')

            # Perform object detection
            results = self.perform_detection(cv_image)

            # Convert results to vision_msgs format
            detection_array = self.results_to_vision_msgs(results, msg.header)

            # Publish detections
            self.detections_pub.publish(detection_array)

            self.get_logger().info(f'Detected {len(detection_array.detections)} objects')

        except Exception as e:
            self.get_logger().error(f'Error in object detection: {str(e)}')

    def perform_detection(self, image):
        """
        Perform object detection on the input image
        """
        # Convert image to tensor format expected by the model
        input_tensor = self.preprocess_image(image)

        # Move tensor to GPU if available
        if torch.cuda.is_available():
            input_tensor = input_tensor.cuda()

        # Perform inference
        with torch.no_grad():
            results = self.model(input_tensor)

        return results

    def preprocess_image(self, image):
        """
        Preprocess image for the model
        """
        # Convert image to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = image

        # Convert to tensor and normalize
        transform = T.Compose([
            T.ToPILImage(),
            T.Resize((640, 640)),  # YOLOv5 typically expects 640x640 input
            T.ToTensor(),
        ])

        # Apply transform
        image_pil = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)  # Convert back for PIL
        input_tensor = transform(image_pil).unsqueeze(0)  # Add batch dimension

        return input_tensor

    def results_to_vision_msgs(self, results, header):
        """
        Convert detection results to vision_msgs format
        """
        detection_array = Detection2DArray()
        detection_array.header = header

        # Get detections from YOLO results
        # results.pred[0] contains the detections for the first (and only) image in the batch
        detections = results.xyxy[0].cpu().numpy()  # x1, y1, x2, y2, conf, class

        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection

            # Apply confidence threshold
            if conf > 0.5:
                det_msg = Detection2D()
                det_msg.header = header

                # Set bounding box
                det_msg.bbox.center.x = float((x1 + x2) / 2)
                det_msg.bbox.center.y = float((y1 + y2) / 2)
                det_msg.bbox.size_x = float(x2 - x1)
                det_msg.bbox.size_y = float(y2 - y1)

                # Set detection results (confidence and class)
                hypothesis = ObjectHypothesisWithPose()
                class_id = int(cls)
                if class_id < len(self.coco_names):
                    hypothesis.id = self.coco_names[class_id]
                else:
                    hypothesis.id = str(class_id)
                hypothesis.score = float(conf)

                det_msg.results.append(hypothesis)
                detection_array.detections.append(det_msg)

        return detection_array


def main(args=None):
    """
    Main function to run the Isaac ROS object detection node
    """
    rclpy.init(args=args)

    node = IsaacROSObjectDetectionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down Isaac ROS Object Detection Node')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()