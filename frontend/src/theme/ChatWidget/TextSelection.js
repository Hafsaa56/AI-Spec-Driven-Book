import { useEffect, useState } from 'react';

// Text selection hook/component
const TextSelection = ({ onSelection }) => {
  const [selectedText, setSelectedText] = useState('');
  const [showButton, setShowButton] = useState(false);
  const [buttonPosition, setButtonPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection.toString().trim();
      
      if (text && text.length > 0 && text.split(' ').length <= 500) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        setButtonPosition({
          x: rect.left + window.scrollX,
          y: rect.top + window.scrollY - 40  // Position above the selection
        });
        
        setSelectedText(text);
        setShowButton(true);
      } else {
        setShowButton(false);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, []);

  const handleExplainThis = () => {
    if (selectedText && onSelection) {
      onSelection(selectedText);
    }
    setShowButton(false);
  };

  if (!showButton) {
    return null;
  }

  return (
    <button
      className="explain-this-button"
      style={{
        position: 'fixed',
        left: `${buttonPosition.x}px`,
        top: `${buttonPosition.y}px`,
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
  );
};

export default TextSelection;

// Standalone hook version
export const useTextSelection = () => {
  const [selectedText, setSelectedText] = useState('');

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection.toString().trim();
      
      if (text && text.length > 0 && text.split(' ').length <= 500) {
        setSelectedText(text);
      } else {
        setSelectedText('');
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, []);

  return selectedText;
};
