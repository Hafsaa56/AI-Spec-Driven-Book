---
sidebar_position: 4
---

# Module 4 Exercises: Vision-Language-Action and Conversational Robots

## Exercise 1: Basic Vision-Language Model Implementation

### Objective
Implement a basic vision-language model that can understand simple commands in a visual context.

### Prerequisites
- Python programming skills
- PyTorch or TensorFlow knowledge
- Basic understanding of neural networks
- ROS 2 Humble installed

### Steps
1. Set up a basic vision-language model architecture
2. Implement image encoding using a pre-trained CNN
3. Implement text encoding using a simple transformer
4. Create a fusion mechanism to combine visual and textual features
5. Test the model with sample image-text pairs

### Expected Outcome
A functional vision-language model that can process simple visual scenes and natural language commands.

### Code Template
```python
import torch
import torch.nn as nn
import torchvision.models as models
from transformers import AutoTokenizer, AutoModel

class BasicVisionLanguageModel(nn.Module):
    def __init__(self):
        super().__init__()

        # Vision encoder (using ResNet as example)
        self.vision_encoder = models.resnet18(pretrained=True)
        # Remove the final classification layer
        self.vision_encoder = nn.Sequential(*list(self.vision_encoder.children())[:-1])

        # Text encoder
        self.text_tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.text_encoder = AutoModel.from_pretrained('bert-base-uncased')

        # Feature fusion layer
        self.fusion_layer = nn.Linear(512 + 768, 512)  # ResNet out + BERT out

        # Output layer for simple classification
        self.output_layer = nn.Linear(512, 10)  # 10 possible actions

    def forward(self, images, text_commands):
        # Process images
        image_features = self.vision_encoder(images)
        image_features = torch.flatten(image_features, 1)

        # Process text commands
        text_tokens = self.text_tokenizer(
            text_commands,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=128
        )
        text_outputs = self.text_encoder(**text_tokens)
        text_features = text_outputs.last_hidden_state[:, 0, :]  # [CLS] token

        # Fuse features
        combined_features = torch.cat([image_features, text_features], dim=1)
        fused_features = self.fusion_layer(combined_features)

        # Generate output
        output = self.output_layer(fused_features)

        return output

# Initialize model
model = BasicVisionLanguageModel()

# Example usage
images = torch.randn(1, 3, 224, 224)  # Batch of 1 RGB image
text_commands = ["pick up the red object"]  # List of commands

output = model(images, text_commands)
print(f"Model output shape: {output.shape}")
```

### Questions
1. How does the fusion layer combine visual and textual features?
2. What are the advantages of using pre-trained models for vision and language encoding?
3. How would you modify this model to handle more complex commands?

## Exercise 2: ROS 2 Integration for Vision-Language-Action

### Objective
Integrate the vision-language model with ROS 2 to create a basic VLA pipeline.

### Prerequisites
- ROS 2 Humble installed
- Basic ROS 2 knowledge (nodes, topics, messages)
- Completed Exercise 1

### Steps
1. Create a ROS 2 node for the VLA system
2. Set up publishers and subscribers for camera images and commands
3. Implement the VLA model within the ROS 2 node
4. Test the system with simulated camera data
5. Verify real-time performance

### Expected Outcome
A ROS 2 node that processes camera images and natural language commands to generate robotic actions.

### Code Template
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from cv_bridge import CvBridge
import torch

class VLAROSNode(Node):
    def __init__(self):
        super().__init__('vla_ros_node')

        # Initialize CV bridge
        self.cv_bridge = CvBridge()

        # Initialize VLA model (from Exercise 1)
        self.vla_model = BasicVisionLanguageModel()
        self.vla_model.eval()  # Set to evaluation mode

        # Create subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.command_sub = self.create_subscription(
            String,
            '/vla/command',
            self.command_callback,
            10
        )

        # Create publishers
        self.action_pub = self.create_publisher(Pose, '/vla/action', 10)
        self.status_pub = self.create_publisher(String, '/vla/status', 10)

        # Store latest image and command
        self.latest_image = None
        self.pending_command = None

        # Timer for processing
        self.process_timer = self.create_timer(0.1, self.process_vla)

    def image_callback(self, msg):
        """Handle incoming camera images"""
        try:
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, 'bgr8')
            # Convert to tensor and preprocess
            self.latest_image = self.preprocess_image(cv_image)
            self.get_logger().info("Received new image")
        except Exception as e:
            self.get_logger().error(f'Error processing image: {str(e)}')

    def command_callback(self, msg):
        """Handle incoming commands"""
        self.pending_command = msg.data
        self.get_logger().info(f'Received command: {msg.data}')

    def preprocess_image(self, cv_image):
        """Preprocess image for VLA model"""
        import cv2
        import numpy as np

        # Resize image to expected input size
        resized = cv2.resize(cv_image, (224, 224))

        # Convert to tensor and normalize
        tensor_image = torch.from_numpy(resized).float()
        tensor_image = tensor_image.permute(2, 0, 1)  # HWC to CHW
        tensor_image = tensor_image.unsqueeze(0)  # Add batch dimension
        tensor_image = tensor_image / 255.0  # Normalize to [0, 1]

        return tensor_image

    def process_vla(self):
        """Process VLA pipeline when both image and command are available"""
        if self.latest_image is not None and self.pending_command is not None:
            try:
                with torch.no_grad():
                    # Generate action using VLA model
                    action_output = self.vla_model(
                        self.latest_image,
                        [self.pending_command]
                    )

                    # Convert model output to action (simplified)
                    action = self.output_to_action(action_output)

                    # Publish action
                    self.action_pub.publish(action)

                    # Publish status
                    status_msg = String()
                    status_msg.data = f'Executed command: {self.pending_command}'
                    self.status_pub.publish(status_msg)

                    # Clear pending command
                    self.pending_command = None

                    self.get_logger().info(f'Action published for command: {self.pending_command}')

            except Exception as e:
                self.get_logger().error(f'Error in VLA processing: {str(e)}')

    def output_to_action(self, model_output):
        """Convert model output to ROS Pose message"""
        import numpy as np

        # Get action probabilities
        action_probs = torch.softmax(model_output, dim=1)
        predicted_action = torch.argmax(action_probs, dim=1)

        # Convert to Pose message (simplified mapping)
        pose = Pose()

        # Example: map action index to position
        action_idx = predicted_action.item()

        # Define some example positions based on action index
        positions = [
            (0.5, 0.0, 0.0),  # Action 0: Move forward
            (-0.5, 0.0, 0.0), # Action 1: Move backward
            (0.0, 0.5, 0.0),  # Action 2: Move right
            (0.0, -0.5, 0.0), # Action 3: Move left
            (0.0, 0.0, 0.5),  # Action 4: Move up
            (0.0, 0.0, -0.5), # Action 5: Move down
        ]

        if action_idx < len(positions):
            x, y, z = positions[action_idx]
        else:
            x, y, z = (0.0, 0.0, 0.0)  # Default position

        pose.position.x = float(x)
        pose.position.y = float(y)
        pose.position.z = float(z)

        # Set orientation to identity (no rotation)
        pose.orientation.w = 1.0

        return pose

def main(args=None):
    rclpy.init(args=args)

    vla_node = VLAROSNode()

    try:
        rclpy.spin(vla_node)
    except KeyboardInterrupt:
        vla_node.get_logger().info('Shutting down VLA ROS node')
    finally:
        vla_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Commands to Test
```bash
# Terminal 1: Build and source workspace
cd ~/vla_ws
colcon build --packages-select vla_package
source install/setup.bash

# Terminal 2: Run the VLA node
ros2 run vla_package vla_ros_node

# Terminal 3: Send a test command
ros2 topic pub /vla/command std_msgs/String "data: 'move forward'"

# Terminal 4: Monitor actions
ros2 topic echo /vla/action
```

### Questions
1. How does the ROS 2 integration handle real-time constraints?
2. What are the challenges in maintaining synchronization between image and command streams?
3. How would you improve the action mapping from model output to robot commands?

## Exercise 3: Conversational Robot with Speech Recognition

### Objective
Build a conversational robot system with speech recognition, natural language understanding, and speech synthesis.

### Prerequisites
- Microphone and speaker setup
- Speech recognition libraries (speech_recognition, pyttsx3)
- Completed previous exercises

### Steps
1. Set up speech recognition using the speech_recognition library
2. Integrate natural language understanding with spaCy
3. Implement text-to-speech with pyttsx3
4. Create a dialogue manager to handle conversation flow
5. Test the system with spoken commands

### Expected Outcome
A functional conversational robot that can understand spoken commands and respond appropriately.

### Code Template
```python
import speech_recognition as sr
import pyttsx3
import spacy
import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool

class ConversationalRobot:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()

        # Configure TTS properties
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)

        # Initialize NLP model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None

        # Initialize ROS node and topics
        rospy.init_node('conversational_robot', anonymous=True)

        # Publishers and subscribers
        self.command_pub = rospy.Publisher('/robot/command', String, queue_size=10)
        self.response_pub = rospy.Publisher('/robot/response', String, queue_size=10)
        self.listening_pub = rospy.Publisher('/robot/listening', Bool, queue_size=10)

        # Subscribe to interrupt commands
        rospy.Subscriber('/robot/interrupt', Bool, self.interrupt_callback)

        # Robot state
        self.is_listening = False
        self.interrupted = False

    def start_conversation(self):
        """Start the main conversation loop"""
        self.say_text("Hello! I'm your conversational robot. How can I help you?")

        while not rospy.is_shutdown():
            try:
                self.listen_and_respond()
            except KeyboardInterrupt:
                rospy.loginfo("Shutting down conversational robot")
                break

    def listen_and_respond(self):
        """Listen for speech and respond appropriately"""
        if self.interrupted:
            self.interrupted = False
            return

        rospy.loginfo("Listening...")
        self.is_listening = True
        self.listening_pub.publish(Bool(data=True))

        try:
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(source, timeout=5.0, phrase_time_limit=5.0)

            self.is_listening = False
            self.listening_pub.publish(Bool(data=False))

            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            rospy.loginfo(f"Recognized: {text}")

            # Process the text and generate response
            response = self.process_command(text)

            # Respond
            self.say_text(response)

        except sr.WaitTimeoutError:
            # No speech detected within timeout
            pass
        except sr.UnknownValueError:
            self.say_text("Sorry, I didn't understand that. Could you repeat?")
        except sr.RequestError as e:
            rospy.logerr(f"Speech recognition error: {e}")
            self.say_text("Sorry, I'm having trouble understanding speech right now.")

    def process_command(self, text):
        """Process the recognized text and generate a response"""
        if not self.nlp:
            return "I'm sorry, I don't have the necessary language processing capabilities."

        # Process with spaCy
        doc = self.nlp(text.lower())

        # Extract intent and entities
        intent = self.extract_intent(doc)

        if intent == 'greeting':
            return self.handle_greeting(text)
        elif intent == 'navigation':
            return self.handle_navigation(text, doc)
        elif intent == 'information':
            return self.handle_information_request(text, doc)
        else:
            return self.handle_unknown_command(text)

    def extract_intent(self, doc):
        """Extract intent from processed text"""
        text = doc.text

        # Simple keyword-based intent extraction
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
        navigation_keywords = ['go to', 'move to', 'navigate', 'walk to', 'go']
        information_keywords = ['what', 'how', 'tell me', 'explain', 'describe']

        if any(keyword in text for keyword in greeting_keywords):
            return 'greeting'
        elif any(keyword in text for keyword in navigation_keywords):
            return 'navigation'
        elif any(keyword in text for keyword in information_keywords):
            return 'information'
        else:
            return 'unknown'

    def handle_greeting(self, text):
        """Handle greeting commands"""
        responses = [
            "Hello! It's nice to meet you.",
            "Hi there! How can I assist you today?",
            "Greetings! What can I do for you?"
        ]

        import random
        return random.choice(responses)

    def handle_navigation(self, text, doc):
        """Handle navigation commands"""
        # Extract destination from entities
        destination = None
        for ent in doc.ents:
            if ent.label_ in ['LOC', 'GPE', 'FAC']:  # Location entities
                destination = ent.text
                break

        if destination:
            # Publish navigation command
            cmd_msg = String()
            cmd_msg.data = f"navigate_to:{destination}"
            self.command_pub.publish(cmd_msg)

            return f"Okay, I'll navigate to {destination}."
        else:
            return "Where would you like me to go?"

    def handle_information_request(self, text, doc):
        """Handle information requests"""
        # This would typically query a knowledge base
        # For now, return a generic response
        return "I can help with navigation and basic tasks. What specific information do you need?"

    def handle_unknown_command(self, text):
        """Handle unknown commands"""
        return "I'm not sure I understand. Could you rephrase that?"

    def say_text(self, text):
        """Speak the given text"""
        rospy.loginfo(f"Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def interrupt_callback(self, msg):
        """Handle interruption commands"""
        if msg.data:
            self.interrupted = True
            self.tts_engine.stop()

def main():
    robot = ConversationalRobot()

    try:
        robot.start_conversation()
    except rospy.ROSInterruptException:
        pass

if __name__ == '__main__':
    main()
```

### Commands to Test
```bash
# Install required packages
pip install speech_recognition pyttsx3 spacy
python -m spacy download en_core_web_sm

# Run the conversational robot
python conversational_robot.py
```

### Questions
1. How does the system handle interruptions during speech synthesis?
2. What are the challenges in speech recognition in noisy environments?
3. How would you improve the natural language understanding component?

## Exercise 4: Vision-Language-Action with Object Detection

### Objective
Enhance the VLA system with real-time object detection to enable more precise action execution.

### Prerequisites
- Completed Exercise 2 (VLA ROS integration)
- Object detection model (e.g., YOLO, SSD)
- Camera with known intrinsic parameters

### Steps
1. Integrate object detection with the VLA pipeline
2. Implement spatial reasoning to connect language commands with detected objects
3. Create action grounding that maps commands to specific objects in the environment
4. Test with commands that reference specific objects (e.g., "pick up the red cup")

### Expected Outcome
A VLA system that can identify objects in the environment and execute commands that reference specific objects.

### Code Template
```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D
from std_msgs.msg import String
from geometry_msgs.msg import Pose
from cv_bridge import CvBridge
import torch
import torchvision.transforms as T
from PIL import Image as PILImage
import numpy as np

class VLAWithObjectDetection(Node):
    def __init__(self):
        super().__init__('vla_object_detection_node')

        # Initialize CV bridge
        self.cv_bridge = CvBridge()

        # Load object detection model (using torchvision's pre-trained model)
        self.detection_model = torch.hub.load(
            'ultralytics/yolov5', 'yolov5s', pretrained=True
        )
        self.detection_model.eval()

        # Create subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )

        self.command_sub = self.create_subscription(
            String, '/vla/command', self.command_callback, 10
        )

        # Create publishers
        self.detection_pub = self.create_publisher(
            Detection2DArray, '/object_detections', 10
        )

        self.action_pub = self.create_publisher(Pose, '/vla/action', 10)

        # Store latest data
        self.latest_image = None
        self.latest_detections = None
        self.pending_command = None

        # Timer for processing
        self.process_timer = self.create_timer(0.1, self.process_pipeline)

    def image_callback(self, msg):
        """Handle incoming images and perform object detection"""
        try:
            # Convert ROS image to OpenCV
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, 'bgr8')

            # Perform object detection
            results = self.detection_model(cv_image)

            # Convert YOLO results to Detection2DArray
            detection_array = self.yolo_to_detection_array(results, msg.header)

            # Publish detections
            self.detection_pub.publish(detection_array)

            # Store for VLA processing
            self.latest_detections = detection_array
            self.latest_image = cv_image

        except Exception as e:
            self.get_logger().error(f'Error in image processing: {str(e)}')

    def yolo_to_detection_array(self, yolo_results, header):
        """Convert YOLO results to Detection2DArray message"""
        detection_array = Detection2DArray()
        detection_array.header = header

        # Get detection results
        detections = yolo_results.xyxy[0].cpu().numpy()  # x1, y1, x2, y2, conf, class

        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection

            if conf > 0.5:  # Confidence threshold
                det_msg = Detection2D()

                # Set bounding box
                det_msg.bbox.center.x = (x1 + x2) / 2
                det_msg.bbox.center.y = (y1 + y2) / 2
                det_msg.bbox.size_x = x2 - x1
                det_msg.bbox.size_y = y2 - y1

                # Set confidence
                from vision_msgs.msg import ObjectHypothesisWithPose
                hypothesis = ObjectHypothesisWithPose()
                hypothesis.id = str(int(cls))
                hypothesis.score = float(conf)

                det_msg.results.append(hypothesis)

                detection_array.detections.append(det_msg)

        return detection_array

    def command_callback(self, msg):
        """Handle incoming commands"""
        self.pending_command = msg.data
        self.get_logger().info(f'Received command: {msg.data}')

    def process_pipeline(self):
        """Process VLA pipeline with object detection"""
        if (self.latest_detections is not None and
            self.pending_command is not None):

            try:
                # Parse command to identify target object
                target_object = self.parse_command_for_object(self.pending_command)

                if target_object:
                    # Find matching object in detections
                    target_detection = self.find_object_in_detections(
                        target_object, self.latest_detections
                    )

                    if target_detection:
                        # Generate action to interact with target object
                        action = self.generate_action_for_object(
                            target_detection, self.pending_command
                        )

                        # Publish action
                        self.action_pub.publish(action)

                        self.get_logger().info(
                            f'Action generated for {target_object} at '
                            f'({target_detection.bbox.center.x}, {target_detection.bbox.center.y})'
                        )
                    else:
                        self.get_logger().warn(f'Could not find {target_object} in scene')
                else:
                    self.get_logger().warn('Could not parse target object from command')

                # Clear pending command
                self.pending_command = None

            except Exception as e:
                self.get_logger().error(f'Error in VLA pipeline: {str(e)}')

    def parse_command_for_object(self, command):
        """Parse command to identify target object"""
        # Simple keyword-based parsing (in practice, use NLP)
        command_lower = command.lower()

        # Common object categories
        object_keywords = [
            'cup', 'bottle', 'book', 'box', 'chair', 'table',
            'person', 'door', 'window', 'phone', 'computer'
        ]

        for keyword in object_keywords:
            if keyword in command_lower:
                return keyword

        # Try to extract color + object
        colors = ['red', 'blue', 'green', 'yellow', 'black', 'white']
        for color in colors:
            if color in command_lower:
                for obj in object_keywords:
                    if obj in command_lower:
                        return f"{color} {obj}"

        return None

    def find_object_in_detections(self, target_object, detections):
        """Find target object in detection results"""
        # This would typically use more sophisticated matching
        # For now, use class ID mapping (COCO dataset indices)

        # COCO dataset class names to indices
        coco_classes = [
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

        # Find the most confident detection of the target object
        best_detection = None
        best_confidence = 0.0

        for detection in detections.detections:
            if detection.results:
                class_id = int(detection.results[0].id)
                confidence = detection.results[0].score

                if (class_id < len(coco_classes) and
                    target_object in coco_classes[class_id].lower() and
                    confidence > best_confidence):
                    best_detection = detection
                    best_confidence = confidence

        return best_detection

    def generate_action_for_object(self, detection, command):
        """Generate action to interact with detected object"""
        pose = Pose()

        # Convert image coordinates to world coordinates (simplified)
        # In practice, you'd use camera calibration and depth information
        pose.position.x = float(detection.bbox.center.x)
        pose.position.y = float(detection.bbox.center.y)
        pose.position.z = 0.0  # Placeholder depth

        # Set orientation
        pose.orientation.w = 1.0

        return pose

def main(args=None):
    rclpy.init(args=args)

    node = VLAWithObjectDetection()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down VLA object detection node')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Commands to Test
```bash
# Terminal 1: Run object detection VLA node
ros2 run vla_package vla_object_detection_node

# Terminal 2: Send a command referencing an object
ros2 topic pub /vla/command std_msgs/String "data: 'pick up the red cup'"

# Terminal 3: Monitor detections
ros2 topic echo /object_detections

# Terminal 4: Monitor actions
ros2 topic echo /vla/action
```

### Questions
1. How does the system determine which detected object matches the command description?
2. What are the challenges in converting 2D image coordinates to 3D world coordinates?
3. How would you improve the object recognition and matching process?

## Exercise 5: Conversational Navigation System

### Objective
Create a system that combines conversational interaction with robot navigation capabilities.

### Prerequisites
- Navigation stack (Nav2) installed and configured
- Completed previous conversational robot exercise
- Robot with navigation capabilities

### Steps
1. Integrate the conversational system with navigation commands
2. Implement spatial understanding for navigation commands
3. Add confirmation and feedback mechanisms
4. Test with various navigation commands in different environments

### Expected Outcome
A conversational robot that can understand navigation commands like "go to the kitchen" and execute them using the navigation system.

### Code Template
```python
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
from nav2_msgs.action import NavigateToPose
import json

class ConversationalNavigation(Node):
    def __init__(self):
        super().__init__('conversational_navigation')

        # Initialize navigation action client
        self.nav_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose'
        )

        # Create subscribers
        self.command_sub = self.create_subscription(
            String, '/nav/command', self.command_callback, 10
        )

        # Create publishers
        self.status_pub = self.create_publisher(String, '/nav/status', 10)

        # Known locations in the environment
        self.known_locations = {
            'kitchen': [2.0, 1.0, 0.0],      # [x, y, theta]
            'living room': [0.0, 0.0, 0.0],
            'bedroom': [-2.0, 1.0, 3.14],
            'office': [1.0, -2.0, 1.57],
            'entrance': [0.0, 2.0, 0.0]
        }

        self.waiting_for_nav_result = False

    def command_callback(self, msg):
        """Process navigation commands"""
        command = msg.data.lower()

        # Parse location from command
        target_location = self.extract_location(command)

        if target_location in self.known_locations:
            # Send navigation goal
            self.navigate_to_location(target_location)
        else:
            # Ask for clarification or provide options
            self.request_location_clarification(command)

    def extract_location(self, command):
        """Extract target location from command"""
        for location in self.known_locations.keys():
            if location in command:
                return location
        return None

    def navigate_to_location(self, location_name):
        """Send navigation goal to the specified location"""
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Navigation action server not available')
            return

        # Get coordinates for the location
        coords = self.known_locations[location_name]

        # Create navigation goal
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = coords[0]
        goal_msg.pose.pose.position.y = coords[1]
        goal_msg.pose.pose.position.z = 0.0

        # Set orientation (simplified - just yaw angle)
        from math import sin, cos
        theta = coords[2]
        goal_msg.pose.pose.orientation.z = sin(theta / 2.0)
        goal_msg.pose.pose.orientation.w = cos(theta / 2.0)

        # Send goal
        self.get_logger().info(f'Navigating to {location_name}')
        self.waiting_for_nav_result = True

        self.nav_client.send_goal_async(
            goal_msg,
            feedback_callback=self.nav_feedback_callback
        ).add_done_callback(self.nav_goal_response_callback)

    def nav_goal_response_callback(self, future):
        """Handle navigation goal response"""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Navigation goal rejected')
            self.waiting_for_nav_result = False
            return

        self.get_logger().info('Navigation goal accepted')
        goal_handle.get_result_async().add_done_callback(
            self.nav_result_callback
        )

    def nav_feedback_callback(self, feedback_msg):
        """Handle navigation feedback"""
        feedback = feedback_msg.feedback
        # Process feedback as needed
        self.get_logger().debug(f'Navigation feedback: {feedback}')

    def nav_result_callback(self, future):
        """Handle navigation result"""
        result = future.result().result
        status = future.result().status

        self.waiting_for_nav_result = False

        if status == 3:  # SUCCEEDED
            self.get_logger().info('Navigation completed successfully')
            status_msg = String()
            status_msg.data = 'navigation_success'
            self.status_pub.publish(status_msg)
        else:
            self.get_logger().info(f'Navigation failed with status: {status}')
            status_msg = String()
            status_msg.data = 'navigation_failed'
            self.status_pub.publish(status_msg)

    def request_location_clarification(self, command):
        """Request clarification for unknown locations"""
        available_locations = ', '.join(self.known_locations.keys())

        status_msg = String()
        status_msg.data = f'unknown_location: Available locations are {available_locations}'
        self.status_pub.publish(status_msg)

def main(args=None):
    rclpy.init(args=args)

    node = ConversationalNavigation()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down conversational navigation')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Commands to Test
```bash
# Terminal 1: Launch navigation system
ros2 launch nav2_bringup navigation_launch.py

# Terminal 2: Run conversational navigation
ros2 run nav_package conversational_navigation

# Terminal 3: Send navigation commands
ros2 topic pub /nav/command std_msgs/String "data: 'go to the kitchen'"

# Terminal 4: Monitor status
ros2 topic echo /nav/status
```

### Questions
1. How does the system handle navigation failures or obstacles?
2. What are the safety considerations when combining navigation with voice commands?
3. How would you extend this system to handle unknown or dynamic locations?

## Exercise 6: Evaluation and Performance Testing

### Objective
Implement evaluation metrics and performance testing for the VLA and conversational systems.

### Prerequisites
- Completed all previous exercises
- Test environment with known scenarios

### Steps
1. Implement metrics for VLA system performance
2. Create test scenarios for different command types
3. Measure real-time performance and latency
4. Evaluate accuracy of command interpretation
5. Test robustness to environmental variations

### Expected Outcome
A comprehensive evaluation framework for VLA and conversational systems with measurable performance metrics.

### Code Template
```python
import time
import statistics
from dataclasses import dataclass
from typing import List, Dict, Tuple
import numpy as np

@dataclass
class VLAEvaluationResult:
    command: str
    expected_action: str
    actual_action: str
    execution_time: float
    success: bool
    accuracy_score: float

class VLAEvaluator:
    def __init__(self):
        self.results = []
        self.test_scenarios = [
            {
                'command': 'go to the kitchen',
                'expected_action': 'navigate_to_kitchen',
                'context': 'indoor_environment'
            },
            {
                'command': 'pick up the red cup',
                'expected_action': 'grasp_red_object',
                'context': 'object_interaction'
            },
            {
                'command': 'what time is it',
                'expected_action': 'provide_time_information',
                'context': 'information_request'
            }
        ]

    def run_evaluation(self, vla_system):
        """Run comprehensive evaluation of VLA system"""
        print("Starting VLA system evaluation...")

        for i, scenario in enumerate(self.test_scenarios):
            print(f"Running scenario {i+1}: {scenario['command']}")

            result = self.run_single_scenario(vla_system, scenario)
            self.results.append(result)

            print(f"  Success: {result.success}")
            print(f"  Execution time: {result.execution_time:.3f}s")
            print(f"  Accuracy: {result.accuracy_score:.3f}")

        # Calculate overall metrics
        self.calculate_metrics()

        return self.results

    def run_single_scenario(self, vla_system, scenario) -> VLAEvaluationResult:
        """Run a single evaluation scenario"""
        start_time = time.time()

        # Execute command through VLA system
        actual_action = vla_system.execute_command(scenario['command'])

        execution_time = time.time() - start_time

        # Determine success and accuracy
        success = self.compare_actions(scenario['expected_action'], actual_action)
        accuracy_score = self.calculate_accuracy_score(
            scenario['expected_action'], actual_action
        )

        return VLAEvaluationResult(
            command=scenario['command'],
            expected_action=scenario['expected_action'],
            actual_action=actual_action,
            execution_time=execution_time,
            success=success,
            accuracy_score=accuracy_score
        )

    def compare_actions(self, expected: str, actual: str) -> bool:
        """Compare expected and actual actions for success"""
        # Simplified comparison (in practice, use more sophisticated methods)
        return expected == actual or expected in actual

    def calculate_accuracy_score(self, expected: str, actual: str) -> float:
        """Calculate numerical accuracy score"""
        if expected == actual:
            return 1.0
        elif expected in actual or actual in expected:
            return 0.8
        elif self.partial_match(expected, actual):
            return 0.5
        else:
            return 0.0

    def partial_match(self, expected: str, actual: str) -> bool:
        """Check for partial semantic match between actions"""
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())

        # Check if there's significant overlap
        intersection = expected_words.intersection(actual_words)
        union = expected_words.union(actual_words)

        if union:
            jaccard_similarity = len(intersection) / len(union)
            return jaccard_similarity > 0.3
        return False

    def calculate_metrics(self):
        """Calculate overall evaluation metrics"""
        if not self.results:
            print("No results to evaluate")
            return

        # Success rate
        success_rate = sum(1 for r in self.results if r.success) / len(self.results)

        # Average execution time
        avg_time = statistics.mean(r.execution_time for r in self.results)

        # Average accuracy
        avg_accuracy = statistics.mean(r.accuracy_score for r in self.results)

        # Time statistics
        time_std = statistics.stdev([r.execution_time for r in self.results]) if len(self.results) > 1 else 0

        print("\n=== VLA System Evaluation Results ===")
        print(f"Success Rate: {success_rate:.2%}")
        print(f"Average Execution Time: {avg_time:.3f}s (±{time_std:.3f}s)")
        print(f"Average Accuracy: {avg_accuracy:.3f}")
        print(f"Total Scenarios: {len(self.results)}")

        # Breakdown by context
        context_results = {}
        for result in self.results:
            # In a real implementation, you'd get context from the scenario
            context = "general"  # Placeholder
            if context not in context_results:
                context_results[context] = []
            context_results[context].append(result)

        for context, results in context_results.items():
            ctx_success_rate = sum(1 for r in results if r.success) / len(results)
            print(f"{context.title()} Success Rate: {ctx_success_rate:.2%}")

# Example usage
def example_vla_system():
    """Mock VLA system for testing"""
    class MockVLASystem:
        def execute_command(self, command: str) -> str:
            # Simulate processing time
            time.sleep(0.1)

            # Simple command-to-action mapping
            if 'kitchen' in command.lower():
                return 'navigate_to_kitchen'
            elif 'red' in command.lower() and ('cup' in command.lower() or 'object' in command.lower()):
                return 'grasp_red_object'
            elif 'time' in command.lower():
                return 'provide_time_information'
            else:
                return 'unknown_action'

    return MockVLASystem()

def main():
    evaluator = VLAEvaluator()
    vla_system = example_vla_system()

    results = evaluator.run_evaluation(vla_system)

    # Additional analysis
    print("\nDetailed Results:")
    for i, result in enumerate(results):
        print(f"  {i+1}. Command: '{result.command}' -> "
              f"Expected: {result.expected_action}, "
              f"Actual: {result.actual_action}, "
              f"Success: {result.success}")

if __name__ == '__main__':
    main()
```

### Commands to Test
```bash
# Run the evaluation
python vla_evaluation.py

# For real system testing, you would run:
# ros2 run evaluation_package vla_evaluator
```

### Questions
1. What are the most important metrics for evaluating VLA systems?
2. How do environmental factors affect VLA system performance?
3. What are the challenges in creating standardized evaluation benchmarks?

## Summary

These exercises provide comprehensive hands-on experience with Vision-Language-Action systems and conversational robotics. Each exercise builds upon the previous ones, creating a complete pipeline from basic vision-language models to fully integrated conversational robotic systems that can understand natural language commands and execute appropriate actions in real-world environments.

The exercises cover key aspects of VLA and conversational systems including model implementation, ROS 2 integration, object detection, navigation, and evaluation. By completing these exercises, you will gain practical experience in developing and deploying advanced multimodal AI systems for robotics applications.