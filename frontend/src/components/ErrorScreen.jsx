import React from "react";

function ErrorScreen({ error, onRetry, onNewAnalysis }) {
  return (
    <article className="panel error-panel" style={{ textAlign: "center", padding: "4rem", border: "2px solid #ff4d4f" }}>
      <h2 style={{ color: "#ff4d4f", marginBottom: "1rem" }}>An Error Occurred</h2>
      <p style={{ marginBottom: "2rem", fontSize: "1.1rem" }}>
        {typeof error === "string" ? error : JSON.stringify(error) || "Pipeline failed unexpectedly."}
      </p>
      
      <div style={{ display: "flex", gap: "1rem", justifyContent: "center" }}>
        {onRetry && (
          <button 
            onClick={onRetry}
            style={{ padding: "0.5rem 1rem", background: "#f0f0f0", color: "#333", border: "1px solid #ccc", borderRadius: "4px" }}
          >
            Retry Validation
          </button>
        )}
        <button 
          onClick={onNewAnalysis}
          style={{ padding: "0.5rem 1rem", background: "#09f", color: "#fff", border: "none", borderRadius: "4px" }}
        >
          Start New Analysis
        </button>
      </div>
    </article>
  );
}

export default ErrorScreen;
