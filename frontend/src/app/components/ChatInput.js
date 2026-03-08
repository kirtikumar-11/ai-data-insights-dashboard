"use client";
import { useState, useRef, useEffect } from "react";

export default function ChatInput({ onSend, isLoading }) {
    const [value, setValue] = useState("");
    const inputRef = useRef(null);

    useEffect(() => {
        inputRef.current?.focus();
    }, [isLoading]);

    const handleSubmit = (e) => {
        e.preventDefault();
        const question = value.trim();
        if (!question || isLoading) return;
        onSend(question);
        setValue("");
    };

    return (
        <div className="input-area">
            <form onSubmit={handleSubmit}>
                <div className="input-wrapper">
                    <input
                        ref={inputRef}
                        type="text"
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        placeholder="Ask a question about your data..."
                        disabled={isLoading}
                        id="chat-input"
                    />
                    <button
                        type="submit"
                        className="send-btn"
                        disabled={!value.trim() || isLoading}
                        id="send-button"
                    >
                        ➤
                    </button>
                </div>
            </form>
            <div className="input-hint">
                Press Enter to send • AI generates SQL from your question
            </div>
        </div>
    );
}
