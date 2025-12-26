#!/usr/bin/env python3
"""
Conversational Vision-Language-Action System

This script demonstrates a conversational interface for VLA systems.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose
from cv_bridge import CvBridge
import speech_recognition as sr
import pyttsx3
import torch
import numpy as np
import threading
import queue


class ConversationalVLANode(Node):
    """
    A conversational VLA node that integrates speech recognition and synthesis
    """
    def __init__(self):
        super().__init__('conversational_vla_node')

        # Initialize CV bridge
        self.cv_bridge = CvBridge()

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

        # Load VLA model
        self.vla_model = self.load_vla_model()
        self.vla_model.eval()

        # Create subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )

        # Create publishers
        self.action_pub = self.create_publisher(Pose, '/vla/action', 10)
        self.response_pub = self.create_publisher(String, '/vla/response', 10)

        # Initialize internal state
        self.latest_image = None
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()

        # Start speech recognition thread
        self.speech_thread = threading.Thread(target=self.speech_recognition_loop, daemon=True)
        self.speech_thread.start()

        # Timer for processing commands
        self.command_timer = self.create_timer(0.1, self.process_commands)

        self.get_logger().info('Conversational VLA Node initialized')

    def load_vla_model(self):
        """
        Load the VLA model for processing commands
        """
        try:
            # Import and use the VLA model
            from basic_vla_model import VisionLanguageActionModel
            model = VisionLanguageActionModel()

            # Move to GPU if available
            if torch.cuda.is_available():
                model = model.cuda()

            self.get_logger().info('VLA model loaded successfully')
            return model
        except ImportError:
            self.get_logger().warn('Basic VLA model not found, using mock model')
            return MockVLAModel()

    def image_callback(self, msg):
        """
        Handle incoming camera images
        """
        try:
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, 'bgr8')
            self.latest_image = self.preprocess_image(cv_image)
            self.get_logger().debug('Image updated')
        except Exception as e:
            self.get_logger().error(f'Error processing image: {str(e)}')

    def preprocess_image(self, cv_image):
        """
        Preprocess image for VLA model
        """
        import cv2

        # Resize image to expected input size
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

    def speech_recognition_loop(self):
        """
        Continuous speech recognition loop running in a separate thread
        """
        self.get_logger().info('Starting speech recognition loop')

        with self.microphone as source:
            while rclpy.ok():
                try:
                    self.get_logger().debug('Listening for speech...')

                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1.0, phrase_time_limit=5.0)

                    # Recognize speech
                    text = self.recognizer.recognize_google(audio)
                    self.get_logger().info(f'Recognized: {text}')

                    # Add to command queue
                    self.command_queue.put(text)

                except sr.WaitTimeoutError:
                    # No speech detected, continue listening
                    continue
                except sr.UnknownValueError:
                    self.speak_text("Sorry, I didn't understand that. Could you repeat?")
                except sr.RequestError as e:
                    self.get_logger().error(f'Speech recognition error: {e}')
                    self.speak_text("Sorry, I'm having trouble understanding speech right now.")

    def process_commands(self):
        """
        Process commands from the speech recognition queue
        """
        try:
            # Get command from queue without blocking
            while True:
                command = self.command_queue.get_nowait()
                self.handle_command(command)
        except queue.Empty:
            # No commands to process
            pass

    def handle_command(self, command):
        """
        Handle a recognized command
        """
        self.get_logger().info(f'Processing command: {command}')

        # Generate response based on command
        response = self.process_command(command)

        # Publish response
        response_msg = String()
        response_msg.data = response
        self.response_pub.publish(response_msg)

        # Speak the response
        self.speak_text(response)

    def process_command(self, command):
        """
        Process a natural language command and generate response
        """
        command_lower = command.lower()

        # Simple command classification
        if any(greeting in command_lower for greeting in ['hello', 'hi', 'hey']):
            return "Hello! I'm your robotic assistant. How can I help you?"
        elif any(action in command_lower for action in ['move', 'go', 'navigate']):
            return self.handle_navigation_command(command)
        elif any(action in command_lower for action in ['pick', 'grasp', 'take']):
            return self.handle_manipulation_command(command)
        elif any(action in command_lower for action in ['what', 'describe', 'tell me']):
            return self.handle_query_command(command)
        else:
            # Use VLA model for complex commands
            return self.handle_complex_command(command)

    def handle_navigation_command(self, command):
        """
        Handle navigation-related commands
        """
        # Extract destination from command (simplified)
        destinations = ['kitchen', 'living room', 'bedroom', 'office']
        for dest in destinations:
            if dest in command.lower():
                return f"Okay, I'll navigate to the {dest}."

        return "Where would you like me to go?"

    def handle_manipulation_command(self, command):
        """
        Handle manipulation-related commands
        """
        if self.latest_image is not None:
            # Process with VLA model
            try:
                with torch.no_grad():
                    action = self.vla_model(self.latest_image, [command])

                    # Convert to action message
                    action_msg = self.action_to_pose(action)
                    self.action_pub.publish(action_msg)

                    return f"Okay, I'll {command}."
            except Exception as e:
                self.get_logger().error(f'Error processing manipulation command: {str(e)}')
                return "I'm having trouble processing that command right now."
        else:
            return "I need to see the environment to perform that action. Can you move me to a better position?"

    def handle_query_command(self, command):
        """
        Handle information query commands
        """
        return "I can help you with navigation, object manipulation, and basic tasks. What would you like me to do?"

    def handle_complex_command(self, command):
        """
        Handle complex commands with VLA model
        """
        if self.latest_image is not None:
            try:
                with torch.no_grad():
                    action = self.vla_model(self.latest_image, [command])

                    # Convert to action message
                    action_msg = self.action_to_pose(action)
                    self.action_pub.publish(action_msg)

                    return f"Okay, I'll {command}."
            except Exception as e:
                self.get_logger().error(f'Error processing complex command: {str(e)}')
                return "I'm not sure how to perform that action. Could you rephrase?"
        else:
            return "I need to see the environment to understand that command. Please position me where I can see what you're referring to."

    def action_to_pose(self, action_tensor):
        """
        Convert VLA action output to ROS Pose message
        """
        # Move to CPU for processing
        action_cpu = action_tensor.cpu()
        action_values = action_cpu[0].tolist()

        pose = Pose()

        # Map action values to pose components
        if len(action_values) >= 6:
            pose.position.x = float(action_values[0])
            pose.position.y = float(action_values[1])
            pose.position.z = float(action_values[2])
            pose.orientation.x = float(action_values[3])
            pose.orientation.y = float(action_values[4])
            pose.orientation.z = float(action_values[5])
            pose.orientation.w = 1.0
        else:
            # Default pose
            pose.position.x = 0.0
            pose.position.y = 0.0
            pose.position.z = 0.0
            pose.orientation.w = 1.0

        return pose

    def speak_text(self, text):
        """
        Speak text using TTS engine
        """
        self.get_logger().debug(f'Speaking: {text}')

        # Use a separate thread for TTS to avoid blocking
        def speak():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

        speak_thread = threading.Thread(target=speak)
        speak_thread.start()


class MockVLAModel(torch.nn.Module):
    """
    Mock VLA model for demonstration
    """
    def __init__(self):
        super().__init__()

    def forward(self, images, text_commands):
        """
        Generate mock actions
        """
        batch_size = images.shape[0]

        # Generate mock actions based on commands
        actions = []
        for cmd in text_commands:
            if 'pick' in cmd.lower():
                action = torch.tensor([0.1, 0.0, -0.1, 0.0, 0.0, 0.0])
            elif 'move' in cmd.lower():
                action = torch.tensor([0.2, 0.0, 0.0, 0.0, 0.0, 0.0])
            elif 'lift' in cmd.lower():
                action = torch.tensor([0.0, 0.0, 0.1, 0.0, 0.0, 0.0])
            else:
                action = torch.tensor([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

            actions.append(action)

        actions_tensor = torch.stack(actions)
        if batch_size > 1:
            actions_tensor = actions_tensor.expand(batch_size, -1)

        return actions_tensor


def main(args=None):
    """
    Main function to run the conversational VLA node
    """
    rclpy.init(args=args)

    node = ConversationalVLANode()

    # Greet the user
    node.speak_text("Hello! I'm your robotic assistant. How can I help you?")

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down Conversational VLA Node')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()