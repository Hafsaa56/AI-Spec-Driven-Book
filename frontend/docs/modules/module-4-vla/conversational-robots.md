---
sidebar_position: 3
---

# Conversational Robots: Natural Language Interfaces for Robotics

## Overview

Conversational robots represent the next frontier in human-robot interaction, enabling natural communication between humans and robotic systems through spoken or written language. This chapter explores the design, implementation, and deployment of conversational interfaces for robotics applications, covering everything from speech recognition to dialogue management and natural language understanding.

Conversational robots go beyond simple command-response systems to create interactive experiences where robots can understand context, maintain dialogue state, and engage in meaningful conversations. This capability is essential for applications in customer service, healthcare assistance, education, and home robotics.

## Key Components of Conversational Systems

### Speech Recognition (ASR)

Automatic Speech Recognition (ASR) converts spoken language into text that can be processed by the conversational system:

```python
# Example: Speech recognition with streaming audio
import speech_recognition as sr
import rospy
from std_msgs.msg import String

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # Initialize ROS publisher for recognized text
        self.text_pub = rospy.Publisher('/speech/text', String, queue_size=10)

    def listen_continuously(self):
        """Continuously listen for speech and publish recognized text"""
        with self.microphone as source:
            while not rospy.is_shutdown():
                try:
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=1.0)

                    # Recognize speech
                    text = self.recognizer.recognize_google(audio)

                    # Publish recognized text
                    text_msg = String()
                    text_msg.data = text
                    self.text_pub.publish(text_msg)

                    rospy.loginfo(f"Recognized: {text}")

                except sr.WaitTimeoutError:
                    # No speech detected, continue listening
                    continue
                except sr.UnknownValueError:
                    rospy.logwarn("Could not understand audio")
                except sr.RequestError as e:
                    rospy.logerr(f"Speech recognition error: {e}")
```

### Natural Language Understanding (NLU)

Natural Language Understanding parses the recognized text to extract intent and entities:

```python
# Example: Natural Language Understanding with spaCy
import spacy
import rospy
from std_msgs.msg import String
from your_package.msg import NLUResult

class NaturalLanguageUnderstanding:
    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")

        # Define intent patterns
        self.intent_patterns = {
            'navigation': ['go to', 'move to', 'navigate to', 'walk to'],
            'object_interaction': ['pick up', 'grasp', 'take', 'get', 'bring'],
            'information_request': ['what is', 'tell me about', 'describe', 'explain'],
            'status_request': ['what can you', 'what are you', 'what do you']
        }

        # Subscribe to recognized text
        self.text_sub = rospy.Subscriber('/speech/text', String, self.process_text)

        # Publish NLU results
        self.nlu_pub = rospy.Publisher('/nlu/result', NLUResult, queue_size=10)

    def process_text(self, msg):
        """Process text and extract intent and entities"""
        text = msg.data.lower()
        doc = self.nlp(text)

        # Extract intent
        intent = self.extract_intent(text)

        # Extract entities
        entities = self.extract_entities(doc)

        # Create and publish NLU result
        nlu_result = NLUResult()
        nlu_result.intent = intent
        nlu_result.entities = entities
        nlu_result.original_text = text

        self.nlu_pub.publish(nlu_result)

        rospy.loginfo(f"NLU - Intent: {intent}, Entities: {entities}")

    def extract_intent(self, text):
        """Extract intent from text using pattern matching"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return intent
        return 'unknown'

    def extract_entities(self, doc):
        """Extract named entities from text"""
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })

        # Extract additional entities like numbers, locations
        for token in doc:
            if token.pos_ == 'NUM':
                entities.append({
                    'text': token.text,
                    'label': 'NUMBER',
                    'start': token.idx,
                    'end': token.idx + len(token.text)
                })

        return entities
```

### Dialogue Management

Dialogue management maintains conversation context and manages the flow of interaction:

```python
# Example: Dialogue manager for conversational robotics
import rospy
from std_msgs.msg import String
from your_package.msg import NLUResult, DialogueAction
from collections import deque

class DialogueManager:
    def __init__(self):
        # Subscribe to NLU results
        self.nlu_sub = rospy.Subscriber('/nlu/result', NLUResult, self.process_nlu_result)

        # Subscribe to robot status updates
        self.status_sub = rospy.Subscriber('/robot/status', String, self.update_status)

        # Publish dialogue actions
        self.action_pub = rospy.Publisher('/dialogue/action', DialogueAction, queue_size=10)

        # Maintain conversation context
        self.conversation_history = deque(maxlen=10)
        self.current_context = {}
        self.pending_requests = {}

        # Initialize dialogue state
        self.dialogue_state = {
            'current_topic': 'greeting',
            'user_profile': {},
            'task_in_progress': None
        }

    def process_nlu_result(self, msg):
        """Process NLU result and generate appropriate response"""
        # Add to conversation history
        self.conversation_history.append({
            'text': msg.original_text,
            'intent': msg.intent,
            'entities': msg.entities,
            'timestamp': rospy.Time.now()
        })

        # Determine appropriate response based on intent and context
        response = self.generate_response(msg)

        # Publish dialogue action
        action_msg = DialogueAction()
        action_msg.action_type = response['action_type']
        action_msg.content = response['content']
        action_msg.context = self.dialogue_state

        self.action_pub.publish(action_msg)

    def generate_response(self, nlu_result):
        """Generate response based on NLU result and current context"""
        intent = nlu_result.intent

        if intent == 'greeting':
            return self.handle_greeting()
        elif intent == 'navigation':
            return self.handle_navigation(nlu_result)
        elif intent == 'object_interaction':
            return self.handle_object_interaction(nlu_result)
        elif intent == 'information_request':
            return self.handle_information_request(nlu_result)
        else:
            return self.handle_unknown_intent(nlu_result)

    def handle_greeting(self):
        """Handle greeting interactions"""
        responses = [
            "Hello! How can I assist you today?",
            "Hi there! What would you like me to do?",
            "Greetings! I'm ready to help. What do you need?"
        ]

        import random
        return {
            'action_type': 'speak',
            'content': random.choice(responses)
        }

    def handle_navigation(self, nlu_result):
        """Handle navigation requests"""
        # Extract destination from entities
        destination = None
        for entity in nlu_result.entities:
            if entity.label in ['LOC', 'GPE', 'FAC']:  # Location entities
                destination = entity.text
                break

        if destination:
            # Set task in progress
            self.dialogue_state['task_in_progress'] = 'navigation'

            return {
                'action_type': 'navigate',
                'content': destination
            }
        else:
            return {
                'action_type': 'ask_for_clarification',
                'content': "Where would you like me to go?"
            }

    def handle_object_interaction(self, nlu_result):
        """Handle object interaction requests"""
        # Extract object from entities
        target_object = None
        for entity in nlu_result.entities:
            if entity.label in ['OBJECT', 'PRODUCT']:  # Assuming custom object labels
                target_object = entity.text
                break

        if target_object:
            self.dialogue_state['task_in_progress'] = 'manipulation'

            return {
                'action_type': 'manipulate',
                'content': f"pick up {target_object}"
            }
        else:
            return {
                'action_type': 'ask_for_clarification',
                'content': "What object would you like me to interact with?"
            }

    def handle_information_request(self, nlu_result):
        """Handle information requests"""
        # This would typically query a knowledge base
        # For now, return a generic response
        return {
            'action_type': 'speak',
            'content': "I can help you with navigation, object manipulation, and general information. What would you like to know?"
        }

    def handle_unknown_intent(self, nlu_result):
        """Handle unknown or unclear intents"""
        return {
            'action_type': 'ask_for_clarification',
            'content': f"I'm not sure I understand. Could you rephrase that?"
        }

    def update_status(self, msg):
        """Update dialogue state based on robot status"""
        status = msg.data
        if status == 'navigation_complete':
            self.dialogue_state['task_in_progress'] = None
            # Acknowledge completion
            ack_msg = DialogueAction()
            ack_msg.action_type = 'speak'
            ack_msg.content = "I've reached the destination."
            self.action_pub.publish(ack_msg)
```

### Speech Synthesis (TTS)

Text-to-Speech converts the robot's responses back to spoken language:

```python
# Example: Text-to-Speech with ROS integration
import rospy
import pyttsx3
from std_msgs.msg import String
from your_package.msg import DialogueAction

class TextToSpeech:
    def __init__(self):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

        # Configure voice properties
        self.configure_voice()

        # Subscribe to dialogue actions
        self.action_sub = rospy.Subscriber('/dialogue/action', DialogueAction, self.handle_dialogue_action)

        # Subscribe to speech interruption commands
        self.interrupt_sub = rospy.Subscriber('/tts/interrupt', String, self.interrupt_speech)

    def configure_voice(self):
        """Configure TTS voice properties"""
        # Get available voices
        voices = self.engine.getProperty('voices')

        # Set voice (preferably a natural-sounding one)
        if len(voices) > 0:
            self.engine.setProperty('voice', voices[0].id)

        # Set speech rate
        self.engine.setProperty('rate', 150)  # Words per minute

        # Set volume
        self.engine.setProperty('volume', 0.9)

    def handle_dialogue_action(self, msg):
        """Handle dialogue actions that require speech output"""
        if msg.action_type == 'speak':
            self.speak_text(msg.content)
        elif msg.action_type == 'speak_with_emotion':
            self.speak_with_emotion(msg.content, msg.emotion)

    def speak_text(self, text):
        """Speak the given text"""
        if self.engine.isBusy():
            self.engine.stop()  # Stop current speech

        rospy.loginfo(f"Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def speak_with_emotion(self, text, emotion):
        """Speak text with emotion-appropriate voice modulation"""
        # Adjust voice properties based on emotion
        if emotion == 'happy':
            rate = 160
            volume = 1.0
        elif emotion == 'sad':
            rate = 120
            volume = 0.7
        elif emotion == 'excited':
            rate = 180
            volume = 1.0
        else:
            rate = 150
            volume = 0.9

        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)

        self.speak_text(text)

        # Reset to default after speaking
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)

    def interrupt_speech(self, msg):
        """Interrupt current speech"""
        if self.engine.isBusy():
            self.engine.stop()
            rospy.loginfo("Speech interrupted")
```

## Integration with ROS 2

### Conversational Robot Node

```python
# Example: Complete conversational robot node
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose
from your_package.msg import NLUResult, DialogueAction
from cv_bridge import CvBridge
import threading
import time

class ConversationalRobot(Node):
    def __init__(self):
        super().__init__('conversational_robot')

        # Initialize components
        self.speech_recognizer = SpeechRecognizer(self)
        self.nlu_processor = NaturalLanguageUnderstanding(self)
        self.dialogue_manager = DialogueManager(self)
        self.text_to_speech = TextToSpeech(self)

        # Initialize CV bridge for visual context
        self.cv_bridge = CvBridge()

        # Robot state
        self.robot_pose = None
        self.robot_status = "idle"

        # Publishers and subscribers
        self.status_pub = self.create_publisher(String, '/robot/status', 10)
        self.pose_sub = self.create_subscription(Pose, '/robot/pose', self.update_pose, 10)

        # Timer for periodic status updates
        self.status_timer = self.create_timer(1.0, self.publish_status)

    def update_pose(self, msg):
        """Update robot pose from navigation system"""
        self.robot_pose = msg

    def publish_status(self):
        """Publish robot status periodically"""
        status_msg = String()
        status_msg.data = self.robot_status
        self.status_pub.publish(status_msg)

    def start_listening(self):
        """Start the speech recognition system"""
        self.speech_recognizer.start_listening()

class SpeechRecognizer:
    def __init__(self, node):
        self.node = node
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

        # ROS publisher for recognized text
        self.text_pub = node.create_publisher(String, '/speech/text', 10)

    def start_listening(self):
        """Start continuous listening in a separate thread"""
        def listen_thread():
            with self.microphone as source:
                while rclpy.ok():
                    try:
                        # Listen for audio
                        audio = self.recognizer.listen(source, timeout=1.0)

                        # Recognize speech
                        text = self.recognizer.recognize_google(audio)

                        # Publish recognized text
                        text_msg = String()
                        text_msg.data = text
                        self.text_pub.publish(text_msg)

                        self.node.get_logger().info(f"Recognized: {text}")

                    except sr.WaitTimeoutError:
                        # No speech detected, continue listening
                        continue
                    except sr.UnknownValueError:
                        self.node.get_logger().warn("Could not understand audio")
                    except sr.RequestError as e:
                        self.node.get_logger().error(f"Speech recognition error: {e}")

        # Start listening in background thread
        listener_thread = threading.Thread(target=listen_thread, daemon=True)
        listener_thread.start()

class NaturalLanguageUnderstanding:
    def __init__(self, node):
        self.node = node

        # Load spaCy model (assuming it's installed)
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.node.get_logger().error("Could not load spaCy model")
            self.nlp = None

        # Define intent patterns
        self.intent_patterns = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
            'navigation': ['go to', 'move to', 'navigate to', 'walk to', 'go', 'move'],
            'object_interaction': ['pick up', 'grasp', 'take', 'get', 'bring', 'hold'],
            'information_request': ['what is', 'tell me about', 'describe', 'explain', 'what'],
            'status_request': ['what can you', 'what are you', 'what do you', 'what are you able']
        }

        # Subscribe to recognized text
        self.text_sub = self.node.create_subscription(
            String, '/speech/text', self.process_text, 10
        )

        # Publisher for NLU results
        self.nlu_pub = self.node.create_publisher(NLUResult, '/nlu/result', 10)

    def process_text(self, msg):
        """Process text and extract intent and entities"""
        if not self.nlp:
            return

        text = msg.data.lower()
        doc = self.nlp(text)

        # Extract intent
        intent = self.extract_intent(text)

        # Extract entities
        entities = self.extract_entities(doc)

        # Create and publish NLU result
        nlu_result = NLUResult()
        nlu_result.intent = intent
        nlu_result.entities = str(entities)  # Convert to string for simplicity
        nlu_result.original_text = text

        self.nlu_pub.publish(nlu_result)

        self.node.get_logger().info(f"NLU - Intent: {intent}, Entities: {entities}")

    def extract_intent(self, text):
        """Extract intent from text using pattern matching"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    return intent
        return 'unknown'

    def extract_entities(self, doc):
        """Extract named entities from text"""
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_
            })
        return entities

class DialogueManager:
    def __init__(self, node):
        self.node = node

        # Subscribe to NLU results
        self.nlu_sub = self.node.create_subscription(
            NLUResult, '/nlu/result', self.process_nlu_result, 10
        )

        # Publisher for dialogue actions
        self.action_pub = self.node.create_publisher(DialogueAction, '/dialogue/action', 10)

        # Maintain conversation context
        self.conversation_history = []

    def process_nlu_result(self, msg):
        """Process NLU result and generate appropriate response"""
        # Add to conversation history
        self.conversation_history.append({
            'text': msg.original_text,
            'intent': msg.intent,
            'timestamp': self.node.get_clock().now()
        })

        # Determine appropriate response based on intent
        response = self.generate_response(msg)

        # Publish dialogue action
        action_msg = DialogueAction()
        action_msg.action_type = response['action_type']
        action_msg.content = response['content']

        self.action_pub.publish(action_msg)

    def generate_response(self, nlu_result):
        """Generate response based on NLU result"""
        intent = nlu_result.intent

        if intent == 'greeting':
            return {
                'action_type': 'speak',
                'content': "Hello! How can I assist you today?"
            }
        elif intent == 'navigation':
            return {
                'action_type': 'ask_for_destination',
                'content': "Where would you like me to go?"
            }
        elif intent == 'object_interaction':
            return {
                'action_type': 'ask_for_object',
                'content': "Which object would you like me to interact with?"
            }
        elif intent == 'information_request':
            return {
                'action_type': 'speak',
                'content': "I can help you with navigation and basic tasks. What would you like to know?"
            }
        else:
            return {
                'action_type': 'speak',
                'content': "I'm not sure I understand. Could you rephrase that?"
            }

class TextToSpeech:
    def __init__(self, node):
        self.node = node

        # Subscribe to dialogue actions
        self.action_sub = self.node.create_subscription(
            DialogueAction, '/dialogue/action', self.handle_dialogue_action, 10
        )

        # Initialize text-to-speech (using espeak as example)
        import subprocess
        self.tts_process = None

    def handle_dialogue_action(self, msg):
        """Handle dialogue actions that require speech output"""
        if msg.action_type == 'speak':
            self.speak_text(msg.content)

    def speak_text(self, text):
        """Speak the given text using espeak"""
        import subprocess
        try:
            subprocess.run(['espeak', '-v', 'en', text], check=True)
            self.node.get_logger().info(f"Spoke: {text}")
        except subprocess.CalledProcessError:
            self.node.get_logger().error(f"Failed to speak: {text}")
        except FileNotFoundError:
            self.node.get_logger().error("espeak not found. Please install espeak.")

def main(args=None):
    rclpy.init(args=args)

    conversational_robot = ConversationalRobot()

    try:
        conversational_robot.start_listening()
        rclpy.spin(conversational_robot)
    except KeyboardInterrupt:
        conversational_robot.get_logger().info("Shutting down conversational robot")
    finally:
        conversational_robot.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Launch File for Conversational System

```xml
<!-- Example: Launch file for conversational robot system -->
<launch>
  <!-- Arguments -->
  <arg name="use_sim_time" default="false"/>
  <arg name="robot_name" default="conversational_robot"/>

  <!-- Conversational robot node -->
  <node pkg="your_robot_package"
        exec="conversational_robot_node"
        name="conversational_robot"
        output="screen">
    <param name="use_sim_time" value="$(var use_sim_time)"/>
    <param name="robot_name" value="$(var robot_name)"/>
  </node>

  <!-- Speech recognition node -->
  <node pkg="your_robot_package"
        exec="speech_recognition_node"
        name="speech_recognizer"
        output="screen">
    <param name="use_sim_time" value="$(var use_sim_time)"/>
  </node>

  <!-- Natural language understanding node -->
  <node pkg="your_robot_package"
        exec="nlu_node"
        name="nlu_processor"
        output="screen">
    <param name="use_sim_time" value="$(var use_sim_time)"/>
  </node>

  <!-- Text-to-speech node -->
  <node pkg="your_robot_package"
        exec="tts_node"
        name="text_to_speech"
        output="screen">
    <param name="use_sim_time" value="$(var use_sim_time)"/>
  </node>

  <!-- Dialogue manager node -->
  <node pkg="your_robot_package"
        exec="dialogue_manager_node"
        name="dialogue_manager"
        output="screen">
    <param name="use_sim_time" value="$(var use_sim_time)"/>
  </node>
</launch>
```

## Advanced Conversational Features

### Context Awareness

```python
# Example: Context-aware conversation management
class ContextAwareDialogueManager(DialogueManager):
    def __init__(self, node):
        super().__init__(node)

        # Subscribe to additional context sources
        self.environment_sub = self.node.create_subscription(
            String, '/environment/context', self.update_environment_context, 10
        )

        self.user_tracking_sub = self.node.create_subscription(
            String, '/user/tracking', self.update_user_context, 10
        )

        # Context variables
        self.current_environment = {}
        self.current_user = {}
        self.task_context = {}

    def update_environment_context(self, msg):
        """Update environment context from perception system"""
        import json
        try:
            env_data = json.loads(msg.data)
            self.current_environment.update(env_data)
        except json.JSONDecodeError:
            self.node.get_logger().error("Failed to parse environment context")

    def update_user_context(self, msg):
        """Update user context from tracking system"""
        import json
        try:
            user_data = json.loads(msg.data)
            self.current_user.update(user_data)
        except json.JSONDecodeError:
            self.node.get_logger().error("Failed to parse user context")

    def generate_contextual_response(self, nlu_result):
        """Generate response considering current context"""
        intent = nlu_result.intent

        # Enhance response with contextual information
        if intent == 'navigation' and self.current_environment:
            # Provide navigation options based on current environment
            available_locations = self.current_environment.get('locations', [])
            if available_locations:
                response = f"I can go to: {', '.join(available_locations)}. Where would you like me to go?"
            else:
                response = "Where would you like me to go?"
        elif intent == 'information_request' and self.current_user:
            # Personalize response based on user
            user_name = self.current_user.get('name', 'there')
            response = f"Hello {user_name}! I can help you with navigation and basic tasks. What would you like to know?"
        else:
            response = super().generate_response(nlu_result)['content']

        return {
            'action_type': 'speak',
            'content': response
        }
```

### Multi-turn Dialogue Management

```python
# Example: Multi-turn dialogue with task completion
class MultiTurnDialogueManager(DialogueManager):
    def __init__(self, node):
        super().__init__(node)

        # Task-specific dialogue states
        self.active_tasks = {}
        self.task_requirements = {
            'navigation': ['destination'],
            'object_interaction': ['object_type', 'location'],
            'information_request': ['topic']
        }

    def process_nlu_result(self, msg):
        """Process NLU result with multi-turn dialogue support"""
        intent = msg.intent

        # Check if we're in the middle of a task
        current_task = self.get_active_task()

        if current_task:
            # Continue the current task
            response = self.continue_task(current_task, msg)
        else:
            # Start a new task based on intent
            response = self.start_new_task(intent, msg)

        # Publish response
        action_msg = DialogueAction()
        action_msg.action_type = response['action_type']
        action_msg.content = response['content']

        self.action_pub.publish(action_msg)

    def start_new_task(self, intent, nlu_result):
        """Start a new task based on intent"""
        if intent in self.task_requirements:
            required_params = self.task_requirements[intent]
            provided_params = self.extract_entities(nlu_result)

            # Check which parameters are missing
            missing_params = []
            for param in required_params:
                if param not in provided_params:
                    missing_params.append(param)

            if missing_params:
                # Need more information
                self.active_tasks[intent] = {
                    'intent': intent,
                    'provided_params': provided_params,
                    'missing_params': missing_params
                }

                return {
                    'action_type': 'ask_for_information',
                    'content': f"What {missing_params[0]} would you like me to use?"
                }
            else:
                # All required parameters provided
                self.complete_task(intent, provided_params)
                return {
                    'action_type': 'confirm_task',
                    'content': f"Okay, I'll {intent} now."
                }
        else:
            # Handle as single-turn interaction
            return self.generate_response(nlu_result)

    def continue_task(self, task, nlu_result):
        """Continue an active task with additional information"""
        provided_params = self.extract_entities(nlu_result)

        # Update task with new information
        for param, value in provided_params.items():
            if param in task['missing_params']:
                task['provided_params'][param] = value
                task['missing_params'].remove(param)

        if not task['missing_params']:
            # Task is complete
            self.complete_task(task['intent'], task['provided_params'])
            del self.active_tasks[task['intent']]

            return {
                'action_type': 'confirm_task',
                'content': f"Okay, I'll {task['intent']} now."
            }
        else:
            # Still need more information
            return {
                'action_type': 'ask_for_information',
                'content': f"What {task['missing_params'][0]} would you like me to use?"
            }

    def complete_task(self, intent, params):
        """Complete a task and trigger appropriate action"""
        # Publish task completion message
        task_msg = String()
        task_msg.data = f"{intent}:{str(params)}"
        # Publish to appropriate topic based on task type
```

## Performance and Quality Considerations

### Speech Recognition Quality

```python
# Example: Adaptive speech recognition with quality assessment
class AdaptiveSpeechRecognizer(SpeechRecognizer):
    def __init__(self, node):
        super().__init__(node)

        # Quality metrics
        self.recognition_quality = 0.0
        self.error_count = 0
        self.total_attempts = 0

        # Adaptive parameters
        self.energy_threshold = self.recognizer.energy_threshold
        self.dynamic_energy_threshold = True

    def assess_recognition_quality(self, audio):
        """Assess the quality of audio input"""
        # Calculate audio energy
        energy = audio.get_energy()

        # Check for background noise
        noise_level = self.estimate_noise_level(audio)

        # Calculate quality score
        quality_score = self.calculate_quality_score(energy, noise_level)

        return quality_score

    def calculate_quality_score(self, energy, noise_level):
        """Calculate quality score based on energy and noise"""
        # Normalize energy (assuming typical range)
        normalized_energy = min(energy / 1000.0, 1.0)  # Adjust normalization as needed

        # Penalize high noise
        noise_penalty = min(noise_level / 100.0, 0.5)  # Adjust as needed

        quality_score = max(normalized_energy - noise_penalty, 0.0)

        return quality_score

    def estimate_noise_level(self, audio):
        """Estimate noise level in audio"""
        # Simple noise estimation based on low-energy portions
        # In practice, this would use more sophisticated methods
        return 10.0  # Placeholder

    def adapt_for_environment(self, quality_score):
        """Adapt recognition parameters based on environment quality"""
        if quality_score < 0.3:
            # Poor quality - increase energy threshold to reduce false positives
            self.recognizer.energy_threshold = min(self.energy_threshold * 1.5, 4000)
        elif quality_score > 0.7:
            # Good quality - decrease energy threshold for better sensitivity
            self.recognizer.energy_threshold = max(self.energy_threshold * 0.8, 50)
```

### Dialogue Flow Management

```python
# Example: State machine for dialogue management
from enum import Enum

class DialogueState(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    WAITING_FOR_INPUT = "waiting_for_input"
    TASK_IN_PROGRESS = "task_in_progress"

class StatefulDialogueManager(DialogueManager):
    def __init__(self, node):
        super().__init__(node)

        self.current_state = DialogueState.IDLE
        self.state_transitions = {}

        # Initialize state-specific timers
        self.response_timer = None
        self.timeout_duration = 10.0  # seconds

    def transition_to_state(self, new_state):
        """Transition to a new dialogue state"""
        old_state = self.current_state
        self.current_state = new_state

        # Perform state-specific actions
        if new_state == DialogueState.LISTENING:
            self.start_listening_sequence()
        elif new_state == DialogueState.PROCESSING:
            self.start_processing_sequence()
        elif new_state == DialogueState.WAITING_FOR_INPUT:
            self.start_timeout_timer()

        self.node.get_logger().info(f"Dialogue state: {old_state.value} -> {new_state.value}")

    def start_listening_sequence(self):
        """Start the listening sequence"""
        # Publish request for user attention
        attention_msg = String()
        attention_msg.data = "ready_to_listen"
        # Publish to attention topic

    def start_processing_sequence(self):
        """Start the processing sequence"""
        # Show processing indicator
        status_msg = String()
        status_msg.data = "processing"
        self.node.get_logger().info("Processing user input...")

    def start_timeout_timer(self):
        """Start timeout timer for waiting states"""
        if self.response_timer:
            self.response_timer.cancel()

        self.response_timer = self.node.create_timer(
            self.timeout_duration,
            self.handle_timeout
        )

    def handle_timeout(self):
        """Handle timeout in waiting states"""
        if self.current_state == DialogueState.WAITING_FOR_INPUT:
            # Return to idle state
            self.transition_to_state(DialogueState.IDLE)

            # Apologize for timeout
            timeout_msg = DialogueAction()
            timeout_msg.action_type = 'speak'
            timeout_msg.content = "I didn't receive a response. Let me know if you need help."

            self.action_pub.publish(timeout_msg)
```

## Safety and Privacy Considerations

### Privacy Protection

```python
# Example: Privacy-aware conversational system
import hashlib
import re
from datetime import datetime, timedelta

class PrivacyAwareConversationalRobot(ConversationalRobot):
    def __init__(self, node):
        super().__init__(node)

        # Privacy settings
        self.conversation_log = []
        self.max_log_age = timedelta(hours=24)  # Maximum log retention
        self.personal_data_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone number
        ]

    def process_conversation_turn(self, user_input, robot_response):
        """Process a conversation turn with privacy protection"""
        # Anonymize personal data in user input
        anonymized_input = self.anonymize_personal_data(user_input)

        # Log conversation turn (anonymized)
        log_entry = {
            'timestamp': datetime.now(),
            'user_input': anonymized_input,
            'robot_response': robot_response,
            'session_id': self.get_session_id()
        }

        self.conversation_log.append(log_entry)

        # Clean old logs
        self.cleanup_old_logs()

    def anonymize_personal_data(self, text):
        """Anonymize personal data in text"""
        anonymized_text = text

        for pattern in self.personal_data_patterns:
            # Replace with generic placeholder
            anonymized_text = re.sub(pattern, '[PERSONAL_DATA]', anonymized_text)

        return anonymized_text

    def get_session_id(self):
        """Generate anonymized session ID"""
        # Create session ID based on current time (not user-specific)
        session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        return hashlib.md5(session_time.encode()).hexdigest()[:8]

    def cleanup_old_logs(self):
        """Remove logs older than maximum retention period"""
        current_time = datetime.now()
        self.conversation_log = [
            entry for entry in self.conversation_log
            if current_time - entry['timestamp'] <= self.max_log_age
        ]
```

## Evaluation and Testing

### Conversational System Testing

```python
# Example: Testing framework for conversational systems
import unittest
from unittest.mock import Mock, patch

class TestConversationalRobot(unittest.TestCase):
    def setUp(self):
        # Mock ROS node
        self.mock_node = Mock()

        # Initialize components with mock node
        self.speech_recognizer = SpeechRecognizer(self.mock_node)
        self.nlu_processor = NaturalLanguageUnderstanding(self.mock_node)
        self.dialogue_manager = DialogueManager(self.mock_node)

    def test_greeting_recognition(self):
        """Test recognition of greeting intents"""
        test_text = "Hello robot"

        # Mock the NLP processing
        with patch.object(self.nlu_processor, 'extract_intent', return_value='greeting'):
            intent = self.nlu_processor.extract_intent(test_text.lower())

        self.assertEqual(intent, 'greeting')

    def test_navigation_intent_extraction(self):
        """Test extraction of navigation intents"""
        test_cases = [
            ("Go to the kitchen", 'navigation'),
            ("Move to the table", 'navigation'),
            ("Navigate to the door", 'navigation')
        ]

        for text, expected_intent in test_cases:
            with self.subTest(text=text):
                intent = self.nlu_processor.extract_intent(text.lower())
                self.assertEqual(intent, expected_intent)

    def test_dialogue_response_generation(self):
        """Test dialogue response generation"""
        # Create mock NLU result
        mock_nlu_result = Mock()
        mock_nlu_result.intent = 'greeting'
        mock_nlu_result.original_text = 'hello'

        response = self.dialogue_manager.generate_response(mock_nlu_result)

        self.assertEqual(response['action_type'], 'speak')
        self.assertIn('Hello', response['content'])

if __name__ == '__main__':
    unittest.main()
```

## Summary

Conversational robots represent a significant advancement in human-robot interaction, enabling more natural and intuitive communication. By combining speech recognition, natural language understanding, dialogue management, and speech synthesis, these systems can engage in meaningful conversations and perform complex tasks based on natural language commands.

The implementation of conversational robots requires careful attention to real-time performance, context awareness, multi-turn dialogue management, and privacy considerations. As these systems continue to evolve, they will play an increasingly important role in making robotics accessible to non-technical users and enabling new applications in customer service, healthcare, education, and domestic assistance.

The integration with ROS 2 provides a robust framework for building conversational robotic systems that can leverage the full capabilities of modern robotics platforms while maintaining the flexibility to adapt to various applications and environments.