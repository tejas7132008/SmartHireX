import { useState, useMemo } from "react";

const INITIAL_FORM_STATE = {
  name: "",
  education: "",
  experience: "",
  projects: "",
  github_url: "",
  portfolio_url: "",
};

function CandidateForm({ onSubmit, isLoading }) {
  const [formState, setFormState] = useState(INITIAL_FORM_STATE);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormState((previous) => ({ ...previous, [name]: value }));
  };

  const isValidGithub = useMemo(() => {
    if (!formState.github_url) return false;
    try {
      const url = new URL(formState.github_url);
      return url.hostname.includes("github.com") && url.pathname.length > 1;
    } catch {
      return false;
    }
  }, [formState.github_url]);

  const isValidProjects = useMemo(() => {
    return formState.projects.trim().length >= 50;
  }, [formState.projects]);

  const isFormValid = useMemo(() => {
    return (
      formState.name.trim().length > 0 &&
      formState.education.trim().length > 0 &&
      formState.experience !== "" &&
      isValidGithub &&
      isValidProjects
    );
  }, [formState, isValidGithub, isValidProjects]);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!isFormValid || isLoading) return;

    const payload = {
      ...formState,
      experience: Number(formState.experience || 0),
    };

    onSubmit(payload);
  };

  return (
    <form className="panel form-panel" onSubmit={handleSubmit} style={{ maxWidth: "600px", margin: "0 auto", padding: "2rem", borderRadius: "8px", background: "#fff", boxShadow: "0 2px 10px rgba(0,0,0,0.05)" }}>
      <h2 style={{ marginBottom: "1.5rem", color: "#333", borderBottom: "1px solid #eee", paddingBottom: "0.5rem" }}>Candidate Intake</h2>

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div>
          <label htmlFor="name" style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Full Name</label>
          <input id="name" name="name" value={formState.name} onChange={handleChange} required style={{ width: "100%", padding: "0.75rem", borderRadius: "4px", border: "1px solid #ccc" }} />
        </div>

        <div>
          <label htmlFor="education" style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Education</label>
          <input id="education" name="education" value={formState.education} onChange={handleChange} required style={{ width: "100%", padding: "0.75rem", borderRadius: "4px", border: "1px solid #ccc" }} />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div>
            <label htmlFor="experience" style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Years of Experience</label>
            <input
              id="experience"
              name="experience"
              type="number"
              min="0"
              step="0.1"
              value={formState.experience}
              onChange={handleChange}
              required
              style={{ width: "100%", padding: "0.75rem", borderRadius: "4px", border: "1px solid #ccc" }}
            />
          </div>
          <div>
             <label htmlFor="github_url" style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>
               GitHub URL
               {formState.github_url && !isValidGithub && <span style={{ color: "red", fontSize: "0.8rem", marginLeft: "0.5rem" }}>(Must be valid GitHub URL)</span>}
             </label>
             <input 
               id="github_url" 
               name="github_url" 
               type="url" 
               value={formState.github_url} 
               onChange={handleChange} 
               required 
               style={{ width: "100%", padding: "0.75rem", borderRadius: "4px", border: `1px solid ${formState.github_url && !isValidGithub ? "red" : "#ccc"}` }} 
             />
          </div>
        </div>
        
        <div>
          <label htmlFor="portfolio_url" style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>Portfolio URL (Optional)</label>
          <input id="portfolio_url" name="portfolio_url" type="url" value={formState.portfolio_url} onChange={handleChange} style={{ width: "100%", padding: "0.75rem", borderRadius: "4px", border: "1px solid #ccc" }} />
        </div>

        <div>
           <label htmlFor="projects" style={{ display: "block", marginBottom: "0.5rem", fontWeight: "600" }}>
             Projects Detail
             {formState.projects && !isValidProjects && <span style={{ color: "red", fontSize: "0.8rem", marginLeft: "0.5rem" }}>(At least 50 characters required)</span>}
           </label>
           <textarea
             id="projects"
             name="projects"
             rows="5"
             value={formState.projects}
             onChange={handleChange}
             required
             placeholder="Describe your relevant projects, tech stacks, and architecture decisions in detail..."
             style={{ width: "100%", padding: "0.75rem", borderRadius: "4px", border: `1px solid ${formState.projects && !isValidProjects ? "red" : "#ccc"}`, resize: "vertical", fontFamily: "inherit" }}
           />
        </div>

        <button 
          type="submit" 
          disabled={!isFormValid || isLoading}
          style={{ 
            marginTop: "1rem", 
            padding: "1rem", 
            backgroundColor: !isFormValid || isLoading ? "#ccc" : "#0066cc", 
            color: "#fff", 
            border: "none", 
            borderRadius: "4px", 
            fontWeight: "bold", 
            fontSize: "1.1rem", 
            cursor: !isFormValid || isLoading ? "not-allowed" : "pointer",
            transition: "all 0.2s"
          }}
        >
          {isLoading ? "Initiating Pipeline..." : "Evaluate Profile"}
        </button>
      </div>
    </form>
  );
}

export default CandidateForm;
