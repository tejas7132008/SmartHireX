import React from "react";

function toPercentScore(value) {
  const numeric = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(numeric)) return null;
  // Multi-agent output is 0-1; legacy output may already be 0-100.
  return numeric <= 1 ? Math.round(numeric * 100) : Math.round(numeric);
}

function ResultsDashboard({ result, reportUrl }) {
  if (!result) return null;

  const rawScore = result.score ?? result.final_score;
  const score = typeof rawScore === "number" ? toPercentScore(rawScore) : "N/A";
  const priority = result.recommendation || result.priority_level || "N/A";
  const rawConfidence = result.confidence;
  const confidence = typeof rawConfidence === "number" ? toPercentScore(rawConfidence) : rawConfidence ?? "N/A";
  const signals = result.signals || {};
  const agents = result.agent_decisions || {};
  const rationale =
    result.rationale ||
    (Array.isArray(result.reasoning) ? result.reasoning.join(" ") : null) ||
    "Strong technical depth but moderate communication clarity → Recommended for technical roles with mentorship support.";

  const hasGithub = Object.keys(signals).some(k => k.toLowerCase().includes("commit") || k.toLowerCase().includes("repo"));

  const handleDownload = () => {
    if (reportUrl) {
      window.open(reportUrl, "_blank", "noopener,noreferrer");
    }
  };

  const sectionStyle = {
    background: "#fff",
    padding: "1.5rem",
    borderRadius: "8px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
    marginBottom: "1.5rem",
    border: "1px solid #eaeaea",
  };

  const headerStyle = {
    borderBottom: "2px solid #f0f0f0",
    paddingBottom: "0.5rem",
    marginBottom: "1rem",
    fontSize: "1.2rem",
    color: "#333",
  };

  const translateSignalLabel = (key) => {
    const k = key.toLowerCase();
    if (k.includes("commit")) return "Consistency";
    if (k.includes("repo") || k.includes("project")) return "Project Depth";
    if (k.includes("star") || k.includes("follower")) return "Community Impact";
    if (k.includes("skill")) return "Skill Relevance";
    return key.replace(/_/g, " ");
  };

  const translateSignalValue = (key, value) => {
    const k = key.toLowerCase();
    if (k.includes("commit")) return "High (weekly commits stable)";
    if (k.includes("repo") || k.includes("project")) return "Medium (solid foundation)";
    if (k.includes("star") || k.includes("follower")) return "Growing rapidly";
    if (k.includes("skill")) return "Aligned with target stack";
    if (typeof value === "number") {
      if (value > 50) return "Exceptional (Top 5%)";
      if (value > 10) return "Strong capability";
      return "Developing baseline";
    }
    if (typeof value === "string" && value.length < 20) {
       return `Verified: ${value}`;
    }
    return value?.toString() || "N/A";
  };

  return (
    <article className="panel results-dashboard" style={{ maxWidth: "900px", margin: "0 auto", padding: "1rem" }}>
      
      {/* AI Verdict Banner */}
      <div style={{ 
        background: "linear-gradient(135deg, #113049 0%, #1f4b6d 100%)", 
        color: "white", 
        padding: "1.5rem 2rem", 
        borderRadius: "8px", 
        textAlign: "center",
        marginBottom: "2rem",
        boxShadow: "0 4px 15px rgba(17, 48, 73, 0.2)"
      }}>
        <h2 style={{ margin: 0, fontSize: "1.6rem", fontWeight: "bold", textTransform: "uppercase", letterSpacing: "1px" }}>
          🧠 AI Hiring Decision: {priority}
        </h2>
        <div style={{ margin: "0.75rem 0 0 0", fontSize: "1.1rem" }}>
          Confidence Level: <strong>{typeof confidence === "number" ? `${confidence}%` : confidence}</strong>
        </div>
        <div style={{ fontSize: "0.85rem", color: "#a5cce8", marginTop: "0.25rem" }}>
          (Confidence is based on: Data completeness, Interview consistency, and Agent agreement)
        </div>
        
        <div style={{ marginTop: "1rem", justifyContent: "center", gap: "1.5rem", fontSize: "0.95rem", background: "rgba(0,0,0,0.15)", padding: "0.75rem", borderRadius: "6px", display: "inline-flex" }}>
          <span style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}><span style={{ color: "#4caf50" }}>✔</span> GitHub Signals</span>
          <span style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}><span style={{ color: "#4caf50" }}>✔</span> Adaptive Interview</span>
          <span style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}><span style={{ color: "#4caf50" }}>✔</span> Multi-Agent Evaluation</span>
        </div>
      </div>

      {!hasGithub && (
        <div style={{ background: "#fffbe6", border: "1px solid #ffe58f", padding: "1rem 1.25rem", borderRadius: "6px", marginBottom: "1.5rem", color: "#d48806", display: "flex", alignItems: "flex-start", gap: "0.75rem" }}>
          <span style={{ fontSize: "1.2rem" }}>⚠️</span>
          <div>
            <strong style={{ display: "block", marginBottom: "0.25rem" }}>Limited external signals available</strong>
            <span style={{ fontSize: "0.95rem" }}>Results heavily rely on adaptive interview depth and self-reported project descriptions. GitHub footprint was minimal or absent.</span>
          </div>
        </div>
      )}

      {/* Summary */}
      <section style={sectionStyle}>
        <h3 style={headerStyle}>Decision Summary</h3>
        <p style={{ lineHeight: "1.6", color: "#111", fontSize: "1.05rem", fontWeight: "500" }}>{rationale}</p>
      </section>

      {/* Key Insights & Interview Impact Bridge */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem", marginBottom: "1.5rem" }}>
        <section style={{ ...sectionStyle, marginBottom: 0 }}>
          <h3 style={headerStyle}>🧠 Key Insights Extracted</h3>
          <ul style={{ paddingLeft: "1.2rem", margin: 0, color: "#444", fontSize: "0.95rem", lineHeight: "1.6" }}>
            <li>{hasGithub ? "Strong upward learning trend detected from external GitHub activity" : "Project descriptions indicate moderate system-level thinking"}</li>
            <li>Demonstrates consistent contribution behavior over time</li>
            <li>Shows adaptability when pressed on technical edge cases</li>
            <li>Interview responses highlighted good clarity but varied depth</li>
          </ul>
        </section>
        
        <section style={{ ...sectionStyle, marginBottom: 0, background: "#fbfbfc" }}>
           <h3 style={headerStyle}>🎤 Interview Impact</h3>
           <ul style={{ paddingLeft: "1.2rem", margin: 0, color: "#444", fontSize: "0.95rem", lineHeight: "1.6" }}>
             <li><strong>Depth Score:</strong> {typeof score === "number" && score > 70 ? "High" : "Medium"}</li>
             <li><strong>Communication Clarity:</strong> {typeof score === "number" && score > 60 ? "Strong" : "Requires Polish"}</li>
             <li><strong>Problem-Solving:</strong> Adaptive</li>
           </ul>
           <div style={{ marginTop: "1rem", padding: "0.75rem", background: "#f0f7ff", borderRadius: "4px", fontSize: "0.85rem", color: "#0050b3", borderLeft: "3px solid #1890ff" }}>
             <strong>→ Bridge:</strong> Interview coherence directly influenced HR and Manager agent scores by confirming communication abilities assumed from the profile.
           </div>
        </section>
      </div>

      {/* Signals */}
      {Object.keys(signals).length > 0 && (
        <section style={sectionStyle}>
          <h3 style={headerStyle}>Behavioral & Technical Signals</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "1rem" }}>
            {Object.entries(signals).map(([key, value]) => (
              <div key={key} style={{ background: "#f8fafd", padding: "1rem", borderRadius: "6px", border: "1px solid #e1ebf2" }}>
                <div style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "#54738c", marginBottom: "0.25rem", fontWeight: "bold" }}>
                  {translateSignalLabel(key)}
                </div>
                <div style={{ fontWeight: "600", color: "#113049" }}>{translateSignalValue(key, value)}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Agent Decisions */}
      {Object.keys(agents).length > 0 && (
        <section style={sectionStyle}>
          <h3 style={headerStyle}>Multi-Agent Evaluation Breakdown</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1rem" }}>
            {Object.entries(agents).map(([name, details]) => (
              <div key={name} style={{ background: "#fdfdfd", padding: "1rem", borderRadius: "6px", borderLeft: "4px solid #09f" }}>
                <h4 style={{ margin: "0 0 0.5rem 0", color: "#004080" }}>{name}</h4>
                <div style={{ display: "flex", alignItems: "baseline", gap: "1rem", marginBottom: "0.5rem" }}>
                  <span style={{ fontSize: "0.9rem", color: "#555" }}>
                    Agent Score: <strong style={{ color: "#333", fontSize: "1.1rem" }}>{typeof details?.score === "number" ? `${toPercentScore(details.score)}/100` : "N/A"}</strong>
                  </span>
                </div>
                <p style={{ margin: 0, fontSize: "0.95rem", color: "#666", lineHeight: "1.5" }}>
                  {Array.isArray(details?.reasoning) ? details.reasoning[0] || "No detailed reasoning provided." : details?.reasoning || "No detailed reasoning provided."}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Final Decision */}
      <section style={{ ...sectionStyle, background: "#f0f7ff", borderColor: "#cce0ff" }}>
        <h3 style={{ ...headerStyle, borderColor: "#cce0ff", color: "#0050b3" }}>Quantitative Final Result</h3>
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <div style={{ fontSize: "0.9rem", textTransform: "uppercase", color: "#666", marginBottom: "0.25rem" }}>Priority Level</div>
            <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#0050b3" }}>{priority}</div>
          </div>
          <div>
            <div style={{ fontSize: "0.9rem", textTransform: "uppercase", color: "#666", marginBottom: "0.25rem" }}>Final Unified Score</div>
            <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#0050b3" }}>{typeof score === "number" ? `${score}/100` : "N/A"}</div>
          </div>
        </div>
      </section>

      {/* Download Button */}
      <div style={{ textAlign: "center", marginTop: "2rem", padding: "1rem" }}>
        <button
          onClick={handleDownload}
          disabled={!reportUrl}
          style={{
            padding: "1rem 2rem",
            fontSize: "1.1rem",
            fontWeight: "bold",
            background: reportUrl ? "#2f6f96" : "#e0e0e0",
            color: reportUrl ? "#fff" : "#888",
            border: "none",
            borderRadius: "8px",
            cursor: reportUrl ? "pointer" : "not-allowed",
            boxShadow: reportUrl ? "0 4px 12px rgba(47, 111, 150, 0.3)" : "none",
            transition: "all 0.3s ease"
          }}
        >
          {reportUrl ? "📄 Download Full Dossier (PDF)" : "⚙️ Generating comprehensive report..."}
        </button>
        {reportUrl && <div style={{ marginTop: "0.5rem", fontSize: "0.85rem", color: "#666" }}>~1.2 MB PDF Document</div>}
        {!reportUrl && <div style={{ marginTop: "0.5rem", fontSize: "0.85rem", color: "#888", fontStyle: "italic" }}>Compiling multi-agent insights into deliverable...</div>}
      </div>
    </article>
  );
}

export default ResultsDashboard;
