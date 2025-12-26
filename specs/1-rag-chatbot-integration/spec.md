# Feature Specification: RAG-Based Chatbot Integration

## Overview

Integrate a RAG (Retrieval-Augmented Generation) based chatbot into the Docusaurus book to provide an interactive Q&A experience for readers. The chatbot will allow users to ask questions about the book content and get contextually relevant answers based on the documentation.

## Business Context

The Physical AI and Humanoid Robotics book needs an interactive way for readers to ask questions and get answers from the content. This will improve user engagement and comprehension by providing immediate assistance when readers have questions about the material.

## User Scenarios & Testing

### Primary User Scenario
As a reader of the Physical AI and Humanoid Robotics book, I want to ask questions about the content so that I can get immediate, accurate answers based on the book's documentation.

### Secondary User Scenario
As a reader, I want to highlight/select text from the book and click a "Consult AI" button so that I can get an explanation of the selected content based on the book's documentation.

### Testing Approach
- Test that questions about book content return answers based only on the book's documentation
- Test that the selection-based QA feature works properly with the "Consult AI" button
- Test that the "Consult AI" button appears when text is selected
- Test that chat history is preserved across sessions
- Test that the chatbot handles various question formats appropriately
- Test that the system properly parses all .md files in the /docs folder as the knowledge base

## Functional Requirements

### FR-1: Content-Based Q&A
The system SHALL allow users to ask questions about the book content and provide answers based ONLY on the book's documentation.

**Acceptance Criteria:**
- Given a question about the book content, when the user submits it, then the system returns a relevant answer based ONLY on the book's documentation.
- The system SHALL use RAG to retrieve relevant context from the book documentation before generating responses.
- The system SHALL NOT provide answers based on external knowledge or general AI knowledge that is not present in the book content.

### FR-2: Selection-Based QA
The system SHALL allow users to select/highlight text in the book and provide a "Consult AI" button to explain the selected snippet.

**Acceptance Criteria:**
- Given text selected/highlighted in the book (up to 500 words), when the user clicks the "Consult AI" button, then the system returns an explanation focused on the selected text.
- The system SHALL display the "Consult AI" button near the selected text for easy access.
- The system SHALL ensure the explanation is based strictly on the book's content and related context.
- The system SHALL provide feedback if the user attempts to select more than 500 words.

### FR-3: Chat History
The system SHALL store conversation history for users.

**Acceptance Criteria:**
- Given a user session, when the user returns to the chat, then their previous conversation history is available.
- The system SHALL store chat history in a persistent database.

### FR-4: Integration with Docusaurus
The system SHALL be seamlessly integrated into the existing Docusaurus book interface.

**Acceptance Criteria:**
- The chatbot SHALL be accessible from all pages of the book.
- The chat interface SHALL match the visual design of the existing Docusaurus theme.

### FR-5: LLM Integration
The system SHALL use OpenRouter with Claude 3.5 Sonnet for generating responses.

**Acceptance Criteria:**
- The system SHALL connect to OpenRouter API.
- The system SHALL properly format prompts for the LLM.
- The system SHALL handle API errors gracefully by showing a user-friendly error message and offering to retry the request.

### FR-6: Knowledge Base Processing
The system SHALL automatically parse .md files in the /docs folder as the knowledge base, excluding certain system directories and files.

**Acceptance Criteria:**
- The system SHALL scan and process .md files in the /docs directory to create the knowledge base.
- The system SHALL exclude files in /assets, /node_modules, and files starting with _ or . (hidden files) from processing.
- The system SHALL update the knowledge base on a scheduled basis every 24 hours.
- The system SHALL ensure all book content is included in the knowledge base without manual intervention.

### FR-7: Embedding Generation
The system SHALL use Qwen embeddings to create vector representations of the documentation.

**Acceptance Criteria:**
- The system SHALL generate embeddings for all book content from the processed .md files.
- The system SHALL update embeddings when content changes.

## Non-Functional Requirements

### NFR-1: Performance
The system SHALL respond to user queries within 5 seconds under normal load conditions.

### NFR-2: Availability
The system SHALL be available 99% of the time during business hours.

### NFR-3: Scalability
The system SHALL support up to 100 concurrent users without performance degradation.

## Success Criteria

- Users can ask questions about book content and receive relevant answers within 5 seconds
- At least 85% of user questions receive contextually appropriate responses
- Selection-based QA feature is used by at least 60% of active users
- User engagement time with the book increases by at least 25% after chatbot integration
- User satisfaction score for book accessibility and helpfulness increases by at least 30%

## Key Entities

### Chat Session
- session_id: Unique identifier for the conversation
- created_at: Timestamp when session started
- updated_at: Timestamp of last activity

### Chat Message
- message_id: Unique identifier for the message
- session_id: Reference to the chat session
- role: 'user' or 'assistant'
- content: The text content of the message
- timestamp: When the message was created

### Document Chunk
- chunk_id: Unique identifier for the document chunk
- document_id: Reference to the source document
- content: The text content of the chunk
- embedding: Vector representation of the content
- metadata: Additional information about the chunk

## Assumptions

- The book content is structured in a way that can be processed for RAG
- OpenRouter API access is available and stable
- Qwen embedding model is accessible for vector generation
- Qdrant Cloud provides sufficient storage and query performance
- Neon Serverless Postgres can handle the expected load for chat history

## Dependencies

- Docusaurus documentation site
- OpenRouter API access
- Qdrant Cloud account
- Neon Serverless Postgres account
- Qwen embedding model access

## Scope

### In Scope
- RAG-based question answering system
- Selection-based QA feature
- Chat history storage and retrieval
- Docusaurus integration
- LLM integration with OpenRouter
- Vector database with Qdrant Cloud
- Chat history database with Neon Postgres

### Out of Scope
- User authentication system (beyond session management)
- Advanced analytics dashboard
- Multi-language support
- Offline functionality
- Integration with other external documentation sources

## Clarifications

### Session 2025-12-22

- Q: Should the system track chat history by identifiable users or use anonymous sessions? → A: Anonymous sessions only
- Q: How frequently should the system check for and process changes to the documentation? → A: Scheduled updates every 24 hours
- Q: Should there be a limit on how much text users can select for the "Consult AI" feature? → A: 500 words limit
- Q: What should the system do when the LLM API is unavailable or returns an error? → A: Show a user-friendly message and offer to retry
- Q: Should all .md files be processed, or should certain files/directories be excluded from the knowledge base? → A: Exclude files in /assets, /node_modules, and files starting with _ or . (hidden files)

## Constraints

- Must work within the free tier limitations of Qdrant Cloud and Neon Postgres
- Must integrate with the existing Docusaurus theme without major UI changes
- Must handle the technical complexity of RAG without exposing it to users
- Must comply with any API rate limits from OpenRouter