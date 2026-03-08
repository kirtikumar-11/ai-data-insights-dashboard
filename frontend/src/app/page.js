"use client";
import { useState, useRef, useEffect } from "react";
import MessageBubble from "./components/MessageBubble";
import ChatInput from "./components/ChatInput";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const SUGGESTIONS = [
  {
    icon: "📊",
    text: "Which product category has the highest total sales?",
  },
  {
    icon: "📈",
    text: "Show monthly order trends over time",
  },
  {
    icon: "🌍",
    text: "What are the top 10 cities by number of customers?",
  },
  {
    icon: "⭐",
    text: "What is the average review score by product category?",
  },
];

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const chatEndRef = useRef(null);

  // Load history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  // Auto-scroll on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_URL}/api/history?limit=30`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  };

  const handleSend = async (question) => {
    // Add user message
    const userMsg = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Request failed");
      }

      const data = await res.json();

      const assistantMsg = {
        role: "assistant",
        data: {
          answer: data.answer,
          insight: data.insight,
          generated_sql: data.generated_sql,
          chart: data.chart,
          execution_time: data.execution_time,
          result_rows: data.result_rows,
        },
      };
      setMessages((prev) => [...prev, assistantMsg]);

      // Refresh history
      fetchHistory();
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "error", content: err.message },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (text) => {
    handleSend(text);
  };

  const handleNewChat = () => {
    setMessages([]);
  };

  const handleHistoryClick = (item) => {
    handleSend(item.question);
  };

  const formatTime = (timestamp) => {
    try {
      const d = new Date(timestamp);
      const now = new Date();
      const diff = now - d;
      if (diff < 60000) return "Just now";
      if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
      return d.toLocaleDateString();
    } catch {
      return "";
    }
  };

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">🧠</div>
            <div>
              <h1>AI Data Insights</h1>
              <p>Natural Language Analytics</p>
            </div>
          </div>
          <button className="new-chat-btn" onClick={handleNewChat} id="new-chat-btn">
            ✦ New Conversation
          </button>
        </div>

        <div className="sidebar-section-title">Recent Queries</div>
        <div className="history-list">
          {history.map((item, i) => (
            <div
              key={item.id || i}
              className="history-item"
              onClick={() => handleHistoryClick(item)}
              style={{ animationDelay: `${i * 0.05}s` }}
            >
              <div className="history-item-question">{item.question}</div>
              <div className="history-item-time">
                {formatTime(item.timestamp)}
                {item.result_rows != null && ` • ${item.result_rows} rows`}
              </div>
            </div>
          ))}
          {history.length === 0 && (
            <div style={{ padding: "12px", fontSize: "13px", color: "var(--text-muted)" }}>
              No queries yet. Ask a question to get started!
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-area">
        {/* Header */}
        <header className="main-header">
          <h2>Chat Dashboard</h2>
          <div className="header-status">
            <div className="status-dot"></div>
            Connected to AI Engine
          </div>
        </header>

        {/* Chat Messages */}
        <div className="chat-area">
          {messages.length === 0 && !isLoading ? (
            <div className="welcome">
              <div className="welcome-icon">🔍</div>
              <h2>Ask anything about your data</h2>
              <p>
                I convert your natural language questions into SQL queries,
                execute them on your database, and generate visualizations
                with AI-powered insights.
              </p>
              <div className="suggestions">
                {SUGGESTIONS.map((s, i) => (
                  <div
                    key={i}
                    className="suggestion-card"
                    onClick={() => handleSuggestionClick(s.text)}
                  >
                    <div className="suggestion-card-icon">{s.icon}</div>
                    <p>{s.text}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, i) =>
                msg.role === "error" ? (
                  <div key={i} className="error-message">
                    ⚠️ {msg.content}
                  </div>
                ) : (
                  <MessageBubble key={i} message={msg} />
                )
              )}
              {isLoading && (
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              )}
              <div ref={chatEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        <ChatInput onSend={handleSend} isLoading={isLoading} />
      </main>
    </div>
  );
}
