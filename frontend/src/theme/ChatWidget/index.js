import React from 'react';
import ChatWidget from './ChatWidget';

// This is a wrapper component that renders the ChatWidget
const ChatWidgetWrapper = (props) => {
  return <ChatWidget {...props} />;
};

export default ChatWidgetWrapper;