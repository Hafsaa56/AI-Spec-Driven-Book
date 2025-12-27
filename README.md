# Physical AI and Humanoid Robotics Book with RAG-Based Chatbot

A comprehensive AI-Spec Driven book teaching Physical AI and Humanoid Robotics, featuring an integrated RAG-based chatbot for interactive learning. The project covers the complete journey from ROS 2 fundamentals to advanced Vision-Language-Action pipelines and conversational humanoid robots.

## Overview

This complete educational platform provides a comprehensive resource for understanding and implementing Physical AI systems and humanoid robotics. It follows a sim-to-real approach, bridging the gap between simulation and real-world robotics applications. The platform includes an advanced RAG-based chatbot that allows users to ask questions about the book content and receive contextually relevant answers based on the entire book documentation.

### Key Features

- **Interactive RAG-Based Chatbot**: Ask questions about the book content and get AI-powered responses with source citations
- **Text Selection "Explain This" Feature**: Highlight text on any page and get detailed explanations
- **Cyberpunk-Themed Interface**: Modern, attractive design with electric blue accents matching the robotics theme
- **Complete Documentation**: 4 comprehensive modules with 26 chapters covering all aspects of Physical AI
- **Responsive Design**: Works seamlessly across all devices and screen sizes

### Book Structure

The book is organized into 4 comprehensive modules with 26 chapters covering:

#### Module 1: ROS 2 - The Nervous System of Robots
- Understanding ROS 2 communication patterns
- Topics, services, and actions with Quality of Service settings
- Real-time operation and distributed computing
- Publisher-subscriber architecture and practical exercises

#### Module 2: Digital Twins - Simulation and Reality
- Gazebo physics-based simulation
- Unity integration for high-fidelity graphics
- Digital twin concepts and sim-to-real paradigm
- Physics engines, sensor simulation, and robot models

#### Module 3: NVIDIA Isaac Platform
- Isaac Sim for photorealistic simulation
- Domain randomization and synthetic data generation
- Isaac ROS for GPU-accelerated perception
- Stereo disparity, visual SLAM, and object detection

#### Module 4: Vision-Language-Action Pipelines
- Multimodal AI systems combining vision, language, and action
- Conversational robotics with natural language processing
- Real-time performance optimization
- Integration with ROS 2 and control systems

### Capstone Project
- Complete autonomous humanoid robot implementation
- System architecture and integration guide
- Hardware setup and safety considerations
- Full-stack development from perception to action

### Infrastructure Guidance
- Hardware requirements for development and production
- On-premise vs cloud infrastructure decisions
- Cost-performance trade-offs and optimization strategies

## Chapters Included

1. Quarter Overview - 6-week learning path
2. Physical AI Concepts - Foundation principles
3. ROS 2 Fundamentals - Communication and architecture
4. ROS 2 Nervous System - Advanced patterns and QoS
5. ROS 2 Exercises - Practical publisher-subscriber implementation
6. Digital Twins Introduction - Simulation concepts
7. Gazebo Simulations - Physics and sensor simulation
8. Unity Integration - High-fidelity graphics and Isaac connection
9. Isaac Platform Overview - Ecosystem and components
10. Isaac Sim - Photorealistic simulation and domain randomization
11. Isaac ROS - GPU-accelerated perception pipelines
12. Isaac Exercises - Practical applications
13. Vision-Language-Action Introduction - Multimodal AI
14. VLA Systems - Architecture and implementation
15. Conversational Robots - NLP and dialogue systems
16. VLA Exercises - Practical applications
17. Capstone Project Overview - System definition
18. Capstone Architecture - Component design
19. Capstone Implementation - Full system code
20. Capstone Hardware Setup - Physical configuration
21. Environment Configuration - Ubuntu 22.04 setup
22. Hardware Requirements - Development and production platforms
23. On-Premise vs Cloud - Infrastructure decisions
24. Cost Performance Analysis - Trade-offs and optimization
25. Integration Guide - Complete system integration
26. Advanced Topics - Future considerations and emerging technologies

## Architecture

### Frontend (Docusaurus)
- Built with Docusaurus for documentation
- Custom cyberpunk-themed styling with animations
- Integrated chatbot widget with floating design
- Text selection API for "Explain this" functionality
- Responsive design for all devices

### Backend (FastAPI)
- FastAPI backend with async support
- RAG (Retrieval-Augmented Generation) system
- OpenRouter API for LLM responses (Claude 3.5 Sonnet)
- Qwen embeddings for vector representations
- Qdrant Cloud for vector database storage
- Neon Postgres for chat history storage

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- npm package manager
- Git for version control

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Install frontend dependencies:
   ```bash
   npm install
   ```

4. Navigate to the backend directory:
   ```bash
   cd ../backend
   ```

5. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Create a `.env` file in the backend directory with your API keys:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key
   DATABASE_URL=your_neon_postgres_connection_string
   ```

### Running Locally

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. In a new terminal, start the frontend:
   ```bash
   cd frontend
   npm start
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

The book will be available at this URL with full navigation, search capabilities, and the interactive chatbot.

## Using the Chatbot

The integrated RAG-based chatbot allows you to:
- Ask questions about any topic covered in the book
- Get contextually relevant answers based on the documentation
- See source citations for the information provided
- Use the "Explain this" feature by selecting text on any page

## About This Project

This is an AI-Spec Driven project, meaning it was developed using specification-driven development principles with AI assistance. The content has been carefully structured to provide a comprehensive learning path from fundamental concepts to advanced implementations in Physical AI and Humanoid Robotics.

The project emphasizes the sim-to-real paradigm, preparing users for both simulation-based development and real-world robotics applications. All examples follow industry best practices and are designed to work with current technologies and platforms.

The RAG-based chatbot system provides an interactive learning experience, allowing users to ask questions and get AI-powered responses based on the entire book content, making it an effective educational tool for mastering Physical AI and Humanoid Robotics concepts.

## Target Audience

- Computer Science and Engineering students
- Robotics researchers and practitioners
- AI/ML engineers interested in embodied intelligence
- Developers working with ROS 2 and robotics systems
- Anyone interested in Physical AI and humanoid robotics

## Technologies Covered

- ROS 2 (Humble Hawksbill)
- Gazebo simulation environment
- Unity 3D for high-fidelity graphics
- NVIDIA Isaac Sim and Isaac ROS
- Python, C++, and Bash scripting
- Docusaurus for documentation
- FastAPI for backend
- OpenRouter API for LLM
- Qdrant for vector storage
- Neon Postgres for chat history
- React for frontend components
- Ubuntu 22.04 LTS

## Contributing

This book and platform are designed to be living resources. Contributions, corrections, and improvements are welcome through pull requests or by reporting issues.

## License

[Specify license type here]