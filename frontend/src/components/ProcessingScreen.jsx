import { useState, useEffect } from "react";

const PROCESSING_STEPS = [
  "Fetching interview transcript...",
  "Running multi-agent evaluation...",
  "Tech Lead analyzing technical depth...",
  "HR evaluating communication skills...",
  "Hiring Manager synthesizing signals...",
  "Finalizing recommendations..."
];

function ProcessingScreen({ message = "Processing decision..." }) {
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStepIndex((prev) => Math.min(prev + 1, PROCESSING_STEPS.length - 1));
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  return (
    <article className="panel processing-panel" style={{ textAlign: "center", padding: "4rem" }}>
      <div className="spinner" style={{ marginBottom: "2rem" }}>
        {/* Simple CSS spinner if not defined in index.css */}
        <div style={{
          display: "inline-block",
          width: "50px",
          height: "50px",
          border: "4px solid rgba(0, 0, 0, 0.1)",
          borderLeftColor: "#09f",
          borderRadius: "50%",
          animation: "spin 1s linear infinite"
        }} />
        <style>{`
          @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        `}</style>
      </div>
      <h2>{message}</h2>
      <p style={{ marginTop: "1rem", color: "#666", minHeight: "24px", transition: "all 0.3s ease" }}>
        {PROCESSING_STEPS[stepIndex]}
      </p>
    </article>
  );
}

export default ProcessingScreen;
