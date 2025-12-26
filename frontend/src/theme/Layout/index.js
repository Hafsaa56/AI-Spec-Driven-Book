import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import ChatWidget from '@theme/ChatWidget';

export default function Layout(props) {
  return (
    <>
      <OriginalLayout {...props}>
        {props.children}
        <ChatWidget />
      </OriginalLayout>
    </>
  );
}