import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import './index.css';

const API_BASE = 'http://localhost:8080';

function Glitter() {
  // Add 50 glitters randomly on the screen
  useEffect(() => {
    const glitterCount = 50;
    const container = document.body;
    const glitters = [];
    for (let i = 0; i < glitterCount; i++) {
      const glitter = document.createElement('div');
      glitter.className = 'glitter';
      glitter.style.top = `${Math.random() * 100}vh`;
      glitter.style.left = `${Math.random() * 100}vw`;
      glitter.style.animationDelay = `${Math.random() * 2}s`;
      container.appendChild(glitter);
      glitters.push(glitter);
    }
    return () => glitters.forEach(g => g.remove());
  }, []);
  return null;
}

function RepoForm({ onIngest }) {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await fetch(`${API_BASE}/chatbot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `question=${encodeURIComponent(repoUrl)}`
      });
      onIngest(repoUrl);
    } finally {
      setLoading(false);
    }
  };
  return (
    <form className="repo-form gradient-border" onSubmit={handleSubmit}>
      <input
        type="url"
        placeholder="Paste GitHub repo URL..."
        value={repoUrl}
        onChange={e => setRepoUrl(e.target.value)}
        required
        disabled={loading}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Ingesting...' : 'Ingest Repo'}
      </button>
    </form>
  );
}

function Chat() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Welcome! Ask me anything about your codebase.' }
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
    const userMsg = { sender: 'user', text: input };
    setMessages(msgs => [...msgs, userMsg]);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/get`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `msg=${encodeURIComponent(input)}`
      });
      const text = await res.text();
      setMessages(msgs => [...msgs, { sender: 'bot', text }]);
    } catch {
      setMessages(msgs => [...msgs, { sender: 'bot', text: 'Error: Could not get response.' }]);
    }
    setInput('');
    setLoading(false);
  };

  return (
    <div className="chat-container">
      {messages.map((msg, i) => (
        <div key={i} className={`message ${msg.sender}`}>{msg.text}</div>
      ))}
      <div ref={chatEndRef} />
      <form onSubmit={sendMessage} style={{ display: 'flex', gap: '1em', marginTop: '1em' }}>
        <textarea
          rows={1}
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Type your question..."
          disabled={loading}
          style={{ flex: 1 }}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

function App() {
  const [repo, setRepo] = useState(null);
  return (
    <div className="card gradient-border">
      <Glitter />
      <h1>CodeOracle</h1>
      <h2>Chat with your codebase</h2>
      <RepoForm onIngest={setRepo} />
      {repo && <Chat />}
      <footer style={{ marginTop: '2em', textAlign: 'center', opacity: 0.7 }}>
        <small>Powered by Gemini & Flask • Beautiful UI by Copilot</small>
      </footer>
    </div>
  );
}

export default App;
