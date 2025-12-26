import React, { useState, useEffect, useRef } from 'react';
import './styles.css';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [showSelectionButton, setShowSelectionButton] = useState(false);
  const [selectionPosition, setSelectionPosition] = useState({ x: 0, y: 0 });
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Check if we're in the browser (not server-side rendering)
  const isBrowser = typeof window !== 'undefined';

  // Handle text selection
  useEffect(() => {
    if (!isBrowser) return;

    const handleSelection = () => {
      if (window.getSelection) {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();

        if (selectedText && selectedText.split(' ').length <= 500) {
          const range = selection.getRangeAt(0);
          const rect = range.getBoundingClientRect();

          setSelectionPosition({
            x: rect.left + window.scrollX,
            y: rect.top + window.scrollY - 40  // Position above the selection
          });

          setSelectedText(selectedText);
          setShowSelectionButton(true);
        } else {
          setShowSelectionButton(false);
        }
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, [isBrowser]);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Toggle chat widget
  const toggleChat = () => {
    setIsOpen(!isOpen);
    if (!isOpen && textareaRef.current) {
      setTimeout(() => textareaRef.current.focus(), 100);
    }
  };

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Call the backend API - using absolute URL (simple API)
      console.log('Sending request to backend:', {
        message: userMessage.text,
        session_id: localStorage.getItem('chat_session_id') || null
      });

      const response = await fetch('http://localhost:8004/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.text,
          session_id: localStorage.getItem('chat_session_id') || null
        })
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Received response:', data);

      // Store session ID for future messages
      if (data.session_id) {
        localStorage.setItem('chat_session_id', data.session_id);
      }

      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        sources: data.sources || [],
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      console.error('Error details:', error.message);

      const errorMessage = {
        id: Date.now() + 1,
        text: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        sender: 'bot',
        error: true,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setSelectedText(''); // Clear selected text after sending
    }
  };

  // Handle key press (Enter to send, Shift+Enter for new line)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Handle "Explain this" button click
  const handleExplainThis = () => {
    if (selectedText) {
      setInputValue(`Explain this: ${selectedText}`);
      setShowSelectionButton(false);
      if (!isOpen) {
        setIsOpen(true);
      }
      setTimeout(() => textareaRef.current?.focus(), 100);
    }
  };

  return (
    <>
      {/* Floating "Explain this" button for selected text */}
      {showSelectionButton && (
        <button
          className="explain-this-button"
          style={{
            position: 'fixed',
            left: `${selectionPosition.x}px`,
            top: `${selectionPosition.y}px`,
            zIndex: 10000,
            backgroundColor: '#00ffff', // Electric blue
            color: '#000',
            border: '1px solid #00ffff',
            borderRadius: '4px',
            padding: '4px 8px',
            fontSize: '12px',
            cursor: 'pointer',
            boxShadow: '0 0 10px rgba(0, 255, 255, 0.5)'
          }}
          onClick={handleExplainThis}
        >
          Explain this
        </button>
      )}

      {/* Chat widget */}
      <div className={`chat-widget ${isOpen ? 'open' : 'closed'}`}>
        <div className="chat-header" onClick={toggleChat}>
          <div className="chat-title">AI Assistant</div>
          <div className="chat-toggle">{isOpen ? '−' : '+'}</div>
        </div>

        {isOpen && (
          <div className="chat-content">
            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="chat-welcome">
                  <p>Hello! I'm your AI assistant for the Physical AI and Humanoid Robotics book.</p>
                  <p>You can ask me questions about the content, or select text and click "Explain this" to get more information.</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`chat-message ${message.sender}`}
                  >
                    <div className="message-content">
                      {message.text}
                      {message.sources && message.sources.length > 0 && (
                        <div className="message-sources">
                          <details>
                            <summary>Sources</summary>
                            <ul>
                              {message.sources.map((source, idx) => (
                                <li key={idx}>
                                  {source.metadata?.source_file || 'Documentation'}
                                </li>
                              ))}
                            </ul>
                          </details>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              {isLoading && (
                <div className="chat-message bot">
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="chat-input-area">
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about the content..."
                className="chat-input"
                rows="1"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="chat-send-button"
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default ChatWidget;