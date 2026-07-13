import React, { useState, useRef, useEffect } from 'react';

export default function CoachChat({ onSendChatMessage, isCoachLoading, chatHistory, setChatHistory }) {
  const [input, setInput] = useState('');
  const chatEndRef = useRef(null);

  // Auto-scroll to the bottom of the chat log
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isCoachLoading]);

  const handleSend = (e) => {
    e?.preventDefault();
    if (!input.trim() || isCoachLoading) return;
    
    const userMsg = { sender: 'user', text: input.trim() };
    const updatedHistory = [...chatHistory, userMsg];
    setChatHistory(updatedHistory);
    setInput('');
    
    // Call the parent handler
    onSendChatMessage(input.trim(), updatedHistory);
  };

  const handleQuickQuestion = (qText) => {
    if (isCoachLoading) return;
    const userMsg = { sender: 'user', text: qText };
    const updatedHistory = [...chatHistory, userMsg];
    setChatHistory(updatedHistory);
    onSendChatMessage(qText, updatedHistory);
  };

  const quickQuestions = [
    "How can I increase protein in a vegetarian diet?",
    "What is a good pre-workout meal for an explosive sprint?",
    "Should I eat high carbs or high protein on a recovery day?",
    "What is the calorie density of Cooked White Rice vs Roti?"
  ];

  return (
    <div className="animate-fade-in card" style={{ height: '78vh', display: 'flex', flexDirection: 'column', padding: '0px', overflow: 'hidden' }}>
      
      {/* 1. CHAT HEADER */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '20px 24px', borderBottom: '1px solid var(--border-color)', background: 'rgba(255,255,255,0.01)' }}>
        <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'var(--grad-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px' }}>🤖</div>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: '700', color: '#fff' }}>NutriVision AI Coach</h2>
          <span style={{ fontSize: '12px', color: 'var(--color-emerald)', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--color-emerald)', display: 'inline-block' }} />
            Active Nutrition Expert
          </span>
        </div>
      </div>

      {/* 2. CHAT BUBBLES AREA */}
      <div style={{ flexGrow: 1, padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {chatHistory.map((msg, index) => {
          const isUser = msg.sender === 'user';
          return (
            <div 
              key={index} 
              style={{ 
                display: 'flex', 
                justifyContent: isUser ? 'flex-end' : 'flex-start',
                width: '100%'
              }}
            >
              <div style={{ 
                maxWidth: '75%', 
                padding: '14px 18px', 
                borderRadius: isUser ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                background: isUser ? 'var(--grad-primary)' : 'rgba(255,255,255,0.03)',
                border: isUser ? 'none' : '1px solid var(--border-color)',
                color: isUser ? '#fff' : 'var(--text-primary)',
                fontSize: '15px',
                lineHeight: '150%',
                whiteSpace: 'pre-line',
                boxShadow: isUser ? 'var(--shadow-sm)' : 'none'
              }}>
                {msg.text}
              </div>
            </div>
          );
        })}

        {/* Typing indicator */}
        {isCoachLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', width: '100%' }}>
            <div style={{ 
              padding: '14px 18px', 
              borderRadius: '16px 16px 16px 2px',
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-muted)',
              fontSize: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>Coach is calculating</span>
              <span className="loading-dots" style={{ display: 'inline-flex', gap: '2px' }}>
                <span style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse 1s infinite' }} />
                <span style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse 1s infinite 0.2s' }} />
                <span style={{ width: '4px', height: '4px', borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse 1s infinite 0.4s' }} />
              </span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* 3. QUICK CHIPS (Only show if no user questions asked yet) */}
      {chatHistory.length <= 1 && !isCoachLoading && (
        <div style={{ padding: '0 24px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Suggested Questions:</span>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
            {quickQuestions.map((q, idx) => (
              <button 
                key={idx}
                className="btn btn-secondary"
                style={{ padding: '6px 12px', fontSize: '12px', borderRadius: '20px' }}
                onClick={() => handleQuickQuestion(q)}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 4. CHAT INPUT BAR */}
      <form onSubmit={handleSend} style={{ display: 'flex', padding: '18px 24px', borderTop: '1px solid var(--border-color)', gap: '12px', background: 'rgba(0,0,0,0.1)' }}>
        <input 
          type="text" 
          className="form-input" 
          style={{ flexGrow: 1, borderRadius: '12px' }}
          placeholder="Ask about meal timing, calorie targets, macros, or Indian food splits..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isCoachLoading}
        />
        <button 
          type="submit" 
          className="btn btn-primary"
          style={{ padding: '12px 24px', borderRadius: '12px' }}
          disabled={isCoachLoading || !input.trim()}
        >
          Send
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </form>

    </div>
  );
}
