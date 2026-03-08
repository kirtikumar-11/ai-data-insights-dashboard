"use client";
import { useState } from "react";
import ChartRenderer from "./ChartRenderer";

export default function MessageBubble({ message }) {
    const [showSQL, setShowSQL] = useState(false);
    const isUser = message.role === "user";

    if (isUser) {
        return (
            <div className="message user">
                <div className="message-header">
                    <div className="message-avatar">👤</div>
                    <span className="message-sender">You</span>
                </div>
                <div className="message-content">{message.content}</div>
            </div>
        );
    }

    // Assistant message
    const { answer, insight, generated_sql, chart, execution_time, result_rows } =
        message.data || {};

    return (
        <div className="message assistant">
            <div className="message-header">
                <div className="message-avatar">🤖</div>
                <span className="message-sender">AI Assistant</span>
            </div>
            <div className="message-content">
                {/* Answer */}
                {answer && (
                    <div className="answer-section">
                        <div className="answer-label">Answer</div>
                        <div>{answer}</div>
                    </div>
                )}

                {/* Insight */}
                {insight && (
                    <div className="insight-section">
                        <div className="insight-label">💡 Insight</div>
                        <div className="insight-text">{insight}</div>
                    </div>
                )}

                {/* SQL toggle */}
                {generated_sql && (
                    <>
                        <button className="sql-toggle" onClick={() => setShowSQL(!showSQL)}>
                            {showSQL ? "▾" : "▸"} {showSQL ? "Hide" : "Show"} SQL Query
                        </button>
                        {showSQL && <div className="sql-block">{generated_sql}</div>}
                    </>
                )}

                {/* Meta info */}
                {(execution_time != null || result_rows != null) && (
                    <div className="message-meta">
                        {execution_time != null && (
                            <span className="meta-item">⚡ {execution_time}s</span>
                        )}
                        {result_rows != null && (
                            <span className="meta-item">📊 {result_rows.toLocaleString()} rows</span>
                        )}
                    </div>
                )}

                {/* Chart */}
                <ChartRenderer chart={chart} />
            </div>
        </div>
    );
}
