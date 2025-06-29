import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './Chat.css';
import SendIcon from '@mui/icons-material/Send';

function Chat() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hi! Ask me anything about your ingested repo.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages([...messages, { sender: 'user', text: input }]);
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8080/get', `msg=${encodeURIComponent(input)}`, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      setMessages(prev => [...prev, { sender: 'bot', text: res.data }]);
    } catch {
      setMessages(prev => [...prev, { sender: 'bot', text: 'Error: Could not get response.' }]);
    }
    setInput('');
    setLoading(false);
  };

  return (
    <div className="chat-bg">
      <div className="chat-window">
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.sender}`}>{msg.text}</div>
          ))}
          <div ref={chatEndRef} />
        </div>
        <form className="chat-input-row" onSubmit={sendMessage}>
          <input
            className="chat-input"
            type="text"
            placeholder="Type your question..."
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={loading}
            autoFocus
          />
          <button className="send-btn" type="submit" disabled={loading || !input.trim()}>
            <SendIcon />
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chat;
