import React, { useState } from "react";

function InterviewChat({ data, jobId, onSubmitAnswer }) {
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (loading) return;
    
    const answer = draft.trim();
    if (!answer) return;

    setLoading(true);
    try {
      if (onSubmitAnswer) {
        await onSubmitAnswer(answer);
      }
      setDraft("");
    } finally {
      // Small delay for better UX before re-enabling if not completed immediately
      setTimeout(() => setLoading(false), 500);
    }
  };

  if (!data) return null;

  return (
    <article className="panel interview-panel">
      <h2>Adaptive Interview</h2>
      <p style={{ marginBottom: "1.5rem", color: "#666" }}>
        <span className="label">Progress:</span> {Math.min(data.transcript.length, data.max_questions)} / {data.max_questions} turns
      </p>

      <div className="chat-log" style={{ maxHeight: "400px", overflowY: "auto", marginBottom: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
        {data.transcript.map((turn, index) => (
          <div key={index} className="chat-turn" style={{ padding: "1rem", background: "#f9f9f9", borderRadius: "8px", border: "1px solid #eee" }}>
            <p className="chat-q" style={{ fontWeight: "600", marginBottom: "0.5rem", color: "#333" }}>
              Q{index + 1}: {turn.question.question}
            </p>
            <p className="chat-a" style={{ color: "#444" }}>
              <span style={{ fontWeight: "600", color: "#666" }}>Your Answer: </span>
              {turn.answer}
            </p>
          </div>
        ))}

        {!data.completed && data.current_question && (
          <div className="chat-turn active-question" style={{ padding: "1.25rem", background: "#f0f7ff", borderLeft: "4px solid #0066cc", borderRadius: "4px" }}>
            <p className="chat-q" style={{ fontWeight: "600", fontSize: "1.05rem", marginBottom: "0.5rem", color: "#004080" }}>
              Current Question: {data.current_question.question}
            </p>
            <p className="chat-meta" style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.75rem", display: "inline-block", background: "#e6f0fa", padding: "0.25rem 0.5rem", borderRadius: "4px" }}>
              <strong style={{ color: "#333" }}>Focus:</strong> {data.current_question.focus_area} &nbsp;|&nbsp; <strong style={{ color: "#333" }}>Difficulty:</strong> {data.current_question.difficulty}
            </p>
          </div>
        )}
      </div>

      {!data.completed ? (
        <form onSubmit={handleSubmit} style={{ marginTop: "1rem", borderTop: "1px solid #eaeaea", paddingTop: "1.5rem" }}>
          <label htmlFor="interview-answer" style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600", color: "#333" }}>
            Your Answer
          </label>
          <textarea
            id="interview-answer"
            rows="5"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Write your reasoning clearly with concrete examples..."
            disabled={loading}
            required
            style={{ 
              width: "100%", 
              padding: "0.75rem", 
              borderRadius: "6px", 
              border: "1px solid #ccc", 
              marginBottom: "1rem", 
              fontFamily: "inherit",
              resize: "vertical",
              backgroundColor: loading ? "#f5f5f5" : "#fff"
            }}
          />
          <button 
            type="submit" 
            disabled={loading || !draft.trim()}
            style={{ 
              padding: "0.75rem 1.5rem", 
              background: loading || !draft.trim() ? "#ccc" : "#09f", 
              color: "#fff", 
              border: "none", 
              borderRadius: "6px", 
              cursor: loading || !draft.trim() ? "not-allowed" : "pointer",
              fontWeight: "600",
              transition: "background 0.2s"
            }}
          >
            {loading ? "Analyzing response..." : "Submit Answer"}
          </button>
        </form>
      ) : (
        <div style={{ padding: "1.25rem", background: "#f6ffed", color: "#389e0d", borderRadius: "6px", border: "1px solid #b7eb8f", textAlign: "center", marginTop: "1rem" }}>
          <strong style={{ display: "block", marginBottom: "0.25rem", fontSize: "1.1rem" }}>Interview Complete.</strong> 
          Final decision is being processed...
        </div>
      )}
    </article>
  );
}

export default InterviewChat;
