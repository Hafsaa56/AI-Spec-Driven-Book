# Quickstart Guide: RAG-Based Chatbot Integration

## Overview
This guide provides a quick introduction to setting up and using the RAG-based chatbot for the Physical AI and Humanoid Robotics book. The system allows readers to ask questions about the book content and get AI-powered answers based on the documentation.

## Prerequisites
- Python 3.9+ installed
- Node.js 16+ installed (for Docusaurus)
- Access to OpenRouter API (with Claude 3.5 Sonnet)
- Qdrant Cloud account
- Neon Postgres account
- Basic understanding of FastAPI and React

## Environment Setup

### 1. Clone and Navigate to Project
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

### 3. Environment Variables
Create or update the `.env` file with your credentials:

```env
# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_api_key

# Qdrant Cloud
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key

# Neon Postgres
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname

# Application settings
SECRET_KEY=your_secret_key
DEBUG=false
```

## Backend Setup

### 1. Install Dependencies
```bash
pip install fastapi uvicorn python-dotenv asyncpg qdrant-client openrouter python-multipart
```

### 2. Initialize the Application
```bash
# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

The backend server will be available at `http://localhost:8000`.

### 3. Run Initial Ingestion
```bash
# Process all documentation files
curl -X POST http://localhost:8000/api/ingest
```

## Frontend Integration

### 1. Docusaurus Setup
```bash
# Navigate to your Docusaurus project
cd frontend

# Install the chatbot plugin
npm install @your-org/rag-chatbot-plugin

# Or if developing locally, link the plugin
npm link /path/to/chatbot/plugin
```

### 2. Configure Docusaurus
Update `docusaurus.config.js`:

```javascript
module.exports = {
  // ... other config
  plugins: [
    [
      '@your-org/rag-chatbot-plugin',
      {
        backendUrl: 'http://localhost:8000',
        // Additional configuration options
      },
    ],
  ],
};
```

### 3. Add Chat Component
In your Docusaurus layout, add the chat component:

```jsx
// In src/theme/Layout/index.js or similar
import ChatWidget from '@your-org/rag-chatbot-plugin';

function Layout(props) {
  return (
    <>
      <OriginalLayout {...props} />
      <ChatWidget />
    </>
  );
}
```

## Core Features

### 1. Basic Chat Functionality
Users can ask questions about the book content through the chat interface:

```javascript
// Example API call
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Explain how ROS 2 handles communication between nodes',
    session_id: 'existing-session-id' // Optional, creates new if not provided
  })
});
```

### 2. Text Selection Feature
The system detects text selection and provides a "Consult AI" button:

```javascript
// Text selection handler (simplified)
document.addEventListener('mouseup', () => {
  const selection = window.getSelection();
  if (selection.toString().length > 0 && selection.toString().split(' ').length <= 500) {
    showConsultAIButton(selection);
  }
});
```

### 3. Session Management
The system maintains conversation context within sessions:

```javascript
// Get chat history for a session
const history = await fetch(`/api/session/${sessionId}`);
```

## API Usage Examples

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123",
    "message": "What is the main advantage of ROS 2 over ROS 1?",
    "selected_text": "ROS 2 uses a DDS-based middleware"
  }'
```

### Ingestion Endpoint
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": ["/docs/modules/module-1-ros/index.md"],
    "force_reprocess": true
  }'
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

## Development Workflow

### 1. Adding New Documentation
1. Add your `.md` file to the `/docs` directory
2. Run the ingestion endpoint to process the new content:
   ```bash
   curl -X POST http://localhost:8000/api/ingest
   ```

### 2. Testing Changes
1. Run backend tests:
   ```bash
   python -m pytest tests/
   ```
2. Test the chat functionality manually through the UI
3. Verify that new content is properly indexed and retrievable

### 3. Performance Monitoring
- Monitor API response times
- Check vector database query performance
- Track LLM API usage and costs

## Troubleshooting

### Common Issues

#### API Connection Errors
- Verify all API keys are correct in `.env`
- Check that external services (OpenRouter, Qdrant, Neon) are accessible
- Confirm network connectivity to external services

#### Slow Response Times
- Check if vector database is properly indexed
- Verify LLM API is responding within expected timeframes
- Monitor database connection pool usage

#### Document Not Found in Responses
- Run ingestion again to ensure documents are processed
- Verify document paths are correct
- Check that documents follow the expected format

### Debugging Tips
1. Enable debug logging by setting `DEBUG=true` in `.env`
2. Check the health endpoint to verify all dependencies are connected
3. Review the ingestion logs to confirm documents were processed
4. Use the session endpoint to verify chat history is being stored correctly

## Next Steps
1. Customize the chat widget UI to match your site's design
2. Add analytics to track usage and effectiveness
3. Implement additional features like favorites or bookmarking
4. Set up monitoring and alerting for production deployments